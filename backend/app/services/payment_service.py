from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timezone
import uuid

from app.models.billing import Payment, PaymentAllocation, Invoice
from app.models.customer import Customer
from app.models.audit import AuditLog
from app.schemas.payment import PaymentCreate
from app.services.pricing_service import quantize_money

class PaymentService:
    @staticmethod
    def generate_payment_number() -> str:
        return f"PAY-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def get_payment(db: Session, payment_id: int) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment {payment_id} not found")
        return payment

    @staticmethod
    def list_payments(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Payment]:
        query = db.query(Payment)
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        if status_filter:
            query = query.filter(Payment.status == status_filter)
        return query.order_by(Payment.paid_at.desc(), Payment.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def record_payment_and_allocations(
        db: Session,
        data: PaymentCreate,
        actor_user_id: Optional[int] = None
    ) -> Payment:
        if data.idempotency_key:
            existing = db.query(Payment).filter(Payment.idempotency_key == data.idempotency_key).first()
            if existing:
                return existing

        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        payment_amount = quantize_money(data.amount)
        if payment_amount <= Decimal("0.00"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount must be positive")

        total_allocated = Decimal("0.00")
        allocations_to_process = data.allocations or []
        validated_invoices: List[Tuple[Invoice, Decimal]] = []

        for alloc in allocations_to_process:
            alloc_amt = quantize_money(alloc.amount)
            if alloc_amt <= Decimal("0.00"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Allocation amount must be positive")
            total_allocated += alloc_amt

            invoice = db.query(Invoice).filter(Invoice.id == alloc.invoice_id).with_for_update().first()
            if not invoice:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {alloc.invoice_id} not found")

            if invoice.customer_id != customer.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invoice {invoice.id} belongs to customer {invoice.customer_id}, but payment is for customer {customer.id}"
                )

            remaining_balance = invoice.balance_due
            if alloc_amt > remaining_balance:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot allocate {alloc_amt} to Invoice {invoice.invoice_number}; balance due is {remaining_balance}"
                )

            validated_invoices.append((invoice, alloc_amt))

        if total_allocated > payment_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total allocated ({total_allocated}) cannot exceed payment amount ({payment_amount})"
            )

        try:
            payment_num = PaymentService.generate_payment_number()
            paid_at = data.paid_at or datetime.now(timezone.utc)

            payment = Payment(
                payment_number=payment_num,
                customer_id=customer.id,
                amount=payment_amount,
                currency=data.currency,
                payment_method=data.payment_method,
                status="succeeded",
                transaction_reference=data.transaction_reference,
                idempotency_key=data.idempotency_key,
                paid_at=paid_at,
                notes=data.notes,
                created_by=actor_user_id
            )
            db.add(payment)
            db.flush()

            for invoice, alloc_amt in validated_invoices:
                pa = PaymentAllocation(
                    payment_id=payment.id,
                    invoice_id=invoice.id,
                    amount_allocated=alloc_amt
                )
                db.add(pa)
                db.flush()

                # Refresh relationship to compute new balance_due
                db.expire(invoice, ["payment_allocations"])
                if invoice.balance_due <= Decimal("0.00"):
                    invoice.status = "paid"
                elif invoice.amount_paid > Decimal("0.00"):
                    invoice.status = "partially_paid"

            audit = AuditLog(
                actor_user_id=actor_user_id,
                action="RECORD_PAYMENT",
                entity_type="payments",
                entity_id=payment.id,
                after_data={
                    "payment_number": payment_num,
                    "amount": str(payment_amount),
                    "allocated": str(total_allocated)
                }
            )
            db.add(audit)

            db.commit()
            db.refresh(payment)
            return payment
        except Exception:
            db.rollback()
            raise
