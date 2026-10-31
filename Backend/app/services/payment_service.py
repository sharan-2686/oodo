from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.billing import Invoice, Payment, PaymentAllocation
from app.schemas.billing import PaymentCreate


def record_payment(db: Session, payload: PaymentCreate) -> Payment:
    existing = db.scalar(select(Payment).where(Payment.idempotency_key == payload.idempotency_key))
    if existing:
        return existing

    try:
        with db.begin_nested():
            invoices = []
            requested_by_invoice: dict[int, Decimal] = {}
            for allocation in payload.allocations:
                invoice = db.scalar(select(Invoice).where(Invoice.id == allocation.invoice_id).with_for_update())
                if not invoice or invoice.customer_id != payload.customer_id:
                    raise HTTPException(422, "allocation invoice must belong to the payment customer")
                allocated = db.scalar(select(func.coalesce(func.sum(PaymentAllocation.amount_allocated), 0)).where(PaymentAllocation.invoice_id == invoice.id))
                requested = requested_by_invoice.get(invoice.id, Decimal("0"))
                if Decimal(allocated) + requested + allocation.amount > invoice.total_amount:
                    raise HTTPException(422, "allocation exceeds outstanding invoice balance")
                requested_by_invoice[invoice.id] = requested + allocation.amount
                invoices.append((invoice, allocation.amount, Decimal(allocated)))
            payment = Payment(
                payment_number=f"PAY-{uuid4().hex[:10].upper()}", customer_id=payload.customer_id,
                amount=payload.amount, payment_method=payload.payment_method,
                idempotency_key=payload.idempotency_key, status="succeeded", paid_at=datetime.now(timezone.utc),
            )
            db.add(payment)
            db.flush()
            for invoice, amount, already_allocated in invoices:
                payment.allocations.append(PaymentAllocation(invoice_id=invoice.id, amount_allocated=amount))
                total_after_this_request = already_allocated + requested_by_invoice[invoice.id]
                invoice.status = "paid" if total_after_this_request >= invoice.total_amount else "partially_paid"
        db.commit()
        db.refresh(payment)
        return payment
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(Payment).where(Payment.idempotency_key == payload.idempotency_key))
        if existing:
            return existing
        raise
