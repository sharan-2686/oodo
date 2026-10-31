"""
RazorpayService — Handles order creation, payment verification, and webhook processing.

Business rules enforced here:
  1. Server-side amount calculation only (never trust client-provided amounts).
  2. Checkout signature verification uses API Key Secret.
  3. Webhook signature verification uses Webhook Secret.
  4. A valid signature does NOT alone confirm payment — Razorpay API status is also checked.
  5. Duplicate payment and duplicate webhook events are detected and rejected.
  6. All financial operations run inside database transactions.
  7. Subscription status is NOT changed here (subscriptions activate at quote conversion).
"""

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.razorpay_client import (
    get_razorpay_client,
    verify_checkout_signature,
    verify_webhook_signature,
)
from app.models.billing import Invoice, Payment, RazorpayWebhookEvent
from app.models.customer import Customer
from app.models.user import User
from app.schemas.razorpay import RazorpayOrderCreateResponse, RazorpayVerifyRequest, RazorpayVerifyResponse
from app.schemas.payment import PaymentAllocationCreate, PaymentCreate
from app.services.payment_service import PaymentService
from app.core.config import settings
from app.core.database import get_utc_now

logger = logging.getLogger(__name__)


def _get_customer_for_user(db: Session, user: User) -> Customer:
    """Resolve the Customer record linked to an authenticated user."""
    customer = db.query(Customer).filter(
        (Customer.email == user.email) | (Customer.created_by == user.id)
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No customer profile found for this account"
        )
    return customer


def _get_and_validate_invoice(
    db: Session,
    invoice_id: int,
    customer: Customer,
) -> Invoice:
    """
    Load and validate an invoice for payment eligibility.
    Raises appropriate HTTP errors for any violation.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).with_for_update().first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")

    # Ownership check
    if invoice.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this invoice"
        )

    # Status eligibility
    unpayable_statuses = {"paid", "void", "uncollectible"}
    if invoice.status in unpayable_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice {invoice.invoice_number} cannot be paid (status: {invoice.status})"
        )

    # Balance check
    if invoice.balance_due <= Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice {invoice.invoice_number} has no outstanding balance"
        )

    return invoice


class RazorpayService:

    # ------------------------------------------------------------------
    # Order Creation
    # ------------------------------------------------------------------

    @staticmethod
    def create_order(
        db: Session,
        invoice_id: int,
        current_user: User,
    ) -> RazorpayOrderCreateResponse:
        """
        Create a Razorpay order for an invoice's outstanding balance.
        Amount is ALWAYS calculated server-side from database values.
        """
        customer = _get_customer_for_user(db, current_user)
        invoice = _get_and_validate_invoice(db, invoice_id, customer)

        # Server-side amount (never trust client)
        balance_due = invoice.balance_due
        amount_paise = int(balance_due * 100)  # INR → paise

        if amount_paise <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Computed amount is zero")

        try:
            client = get_razorpay_client()
            rz_order = client.order.create({
                "amount": amount_paise,
                "currency": invoice.currency or "INR",
                "receipt": invoice.invoice_number,
                "notes": {
                    "invoice_id": str(invoice.id),
                    "customer_id": str(customer.id),
                    "brightloop_app": "1"
                }
            })
        except Exception as exc:
            logger.exception("Razorpay order creation failed for invoice %s", invoice.invoice_number)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Razorpay order creation failed: {str(exc)}"
            )

        razorpay_order_id = rz_order["id"]

        # Create an internal PENDING payment record
        try:
            payment = Payment(
                payment_number=PaymentService.generate_payment_number(),
                customer_id=customer.id,
                amount=balance_due,
                currency=invoice.currency or "INR",
                payment_method="gateway",
                status="pending",
                razorpay_order_id=razorpay_order_id,
                transaction_reference=razorpay_order_id,
                notes=f"Razorpay order for invoice {invoice.invoice_number}",
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
        except Exception:
            db.rollback()
            logger.exception("Failed to create pending Payment record for order %s", razorpay_order_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record payment order internally"
            )

        logger.info(
            "Razorpay order created: order_id=%s invoice=%s amount_paise=%d",
            razorpay_order_id, invoice.invoice_number, amount_paise
        )

        return RazorpayOrderCreateResponse(
            razorpay_order_id=razorpay_order_id,
            amount_paise=amount_paise,
            currency=invoice.currency or "INR",
            key_id=settings.RAZORPAY_KEY_ID,
            internal_payment_id=payment.id,
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number,
            balance_due=balance_due,
        )

    # ------------------------------------------------------------------
    # Payment Verification (Checkout Callback)
    # ------------------------------------------------------------------

    @staticmethod
    def verify_and_capture(
        db: Session,
        data: RazorpayVerifyRequest,
        current_user: User,
    ) -> RazorpayVerifyResponse:
        """
        Verify HMAC signature from Razorpay checkout and confirm payment capture.
        A valid signature alone is NOT sufficient — the payment status is also
        verified through the Razorpay API.
        """
        customer = _get_customer_for_user(db, current_user)
        invoice = _get_and_validate_invoice(db, data.invoice_id, customer)

        # 1. Verify HMAC-SHA256 checkout signature using API Key Secret
        if not verify_checkout_signature(
            data.razorpay_order_id,
            data.razorpay_payment_id,
            data.razorpay_signature,
        ):
            logger.warning(
                "Invalid checkout signature for order=%s payment=%s",
                data.razorpay_order_id, data.razorpay_payment_id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment signature verification failed"
            )

        # 2. Find internal payment record
        internal_payment = db.query(Payment).filter(
            Payment.razorpay_order_id == data.razorpay_order_id
        ).with_for_update().first()

        if not internal_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No internal payment record found for Razorpay order {data.razorpay_order_id}"
            )

        # 3. Idempotency — already processed?
        if internal_payment.status == "succeeded":
            db.refresh(invoice)
            return RazorpayVerifyResponse(
                success=True,
                message="Payment already processed",
                payment_id=internal_payment.id,
                payment_number=internal_payment.payment_number,
                invoice_id=invoice.id,
                invoice_status=invoice.status,
                amount_paid=invoice.amount_paid,
                balance_due=invoice.balance_due,
            )

        # 4. Verify actual payment status with Razorpay API (never trust signature alone)
        try:
            client = get_razorpay_client()
            rz_payment = client.payment.fetch(data.razorpay_payment_id)
        except Exception as exc:
            logger.exception("Failed to fetch payment %s from Razorpay", data.razorpay_payment_id)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not verify payment status with Razorpay: {str(exc)}"
            )

        rz_status = rz_payment.get("status", "")

        # 5. If not yet captured, attempt capture (for manual-capture mode)
        if rz_status == "authorized":
            try:
                amount_paise = int(internal_payment.amount * 100)
                client.payment.capture(data.razorpay_payment_id, amount_paise)
                rz_status = "captured"
            except Exception as exc:
                logger.exception("Payment capture failed for %s", data.razorpay_payment_id)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Payment capture failed: {str(exc)}"
                )
        elif rz_status != "captured":
            logger.warning(
                "Payment %s has status '%s' — rejecting",
                data.razorpay_payment_id, rz_status
            )
            # Mark internal record failed
            internal_payment.status = "failed"
            internal_payment.failure_reason = f"Razorpay payment status: {rz_status}"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment was not captured (status: {rz_status}). Not marking invoice as paid."
            )

        # 6. Update internal payment record and allocate to invoice
        try:
            internal_payment.razorpay_payment_id = data.razorpay_payment_id
            internal_payment.status = "succeeded"
            internal_payment.paid_at = get_utc_now()
            internal_payment.transaction_reference = data.razorpay_payment_id
            db.flush()

            # Allocate the payment to the invoice (uses existing allocation logic)
            from app.models.billing import PaymentAllocation
            from app.services.pricing_service import quantize_money

            alloc_amount = min(internal_payment.amount, invoice.balance_due)
            pa = PaymentAllocation(
                payment_id=internal_payment.id,
                invoice_id=invoice.id,
                amount_allocated=alloc_amount,
            )
            db.add(pa)
            db.flush()

            # Recompute invoice status
            db.expire(invoice, ["payment_allocations"])
            if invoice.balance_due <= Decimal("0.00"):
                invoice.status = "paid"
            elif invoice.amount_paid > Decimal("0.00"):
                invoice.status = "partially_paid"

            db.commit()
            db.refresh(invoice)
            db.refresh(internal_payment)

        except Exception:
            db.rollback()
            logger.exception("Failed to record payment capture for order %s", data.razorpay_order_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment captured by Razorpay but failed to record internally. Contact support."
            )

        logger.info(
            "Payment verified and recorded: order=%s payment=%s invoice=%s status=%s",
            data.razorpay_order_id, data.razorpay_payment_id,
            invoice.invoice_number, invoice.status
        )

        return RazorpayVerifyResponse(
            success=True,
            message="Payment verified and recorded successfully",
            payment_id=internal_payment.id,
            payment_number=internal_payment.payment_number,
            invoice_id=invoice.id,
            invoice_status=invoice.status,
            amount_paid=invoice.amount_paid,
            balance_due=invoice.balance_due,
        )

    # ------------------------------------------------------------------
    # Webhook Handler
    # ------------------------------------------------------------------

    @staticmethod
    def handle_webhook_event(
        db: Session,
        raw_body: bytes,
        signature_header: Optional[str],
    ) -> Dict[str, Any]:
        """
        Process server-to-server webhook events from Razorpay.

        Security: Webhook secret signature is MANDATORY. Invalid signatures are
        rejected before any payload parsing or database access.
        Idempotency: Each Razorpay event ID is stored; duplicate events return 200
        without reprocessing.
        """
        # 1. Verify webhook signature FIRST (before parsing payload)
        if not verify_webhook_signature(raw_body, signature_header):
            logger.warning("Webhook received with invalid signature")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )

        # 2. Parse payload
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.error("Webhook payload JSON parse error: %s", exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

        event_type = payload.get("event", "")
        event_id = payload.get("id", "")  # e.g. "evt_xxx"

        if not event_id:
            logger.warning("Webhook payload missing event ID — skipping")
            return {"status": "skipped", "reason": "missing_event_id"}

        # 3. Idempotency check — has this event been processed before?
        existing = db.query(RazorpayWebhookEvent).filter(
            RazorpayWebhookEvent.razorpay_event_id == event_id
        ).first()
        if existing:
            logger.info("Duplicate webhook event %s (type=%s) — skipping", event_id, event_type)
            return {"status": "skipped", "reason": "duplicate_event"}

        # 4. Store the event record (even if we can't fully process it, avoid re-delivery loops)
        webhook_record = RazorpayWebhookEvent(
            razorpay_event_id=event_id,
            event_type=event_type,
            payload=payload,
            status="processing",
        )
        db.add(webhook_record)
        db.flush()

        # 5. Route event type
        result = {"status": "skipped", "event": event_type}
        try:
            if event_type == "payment.captured":
                result = RazorpayService._handle_payment_captured(db, payload)
            elif event_type == "payment.failed":
                result = RazorpayService._handle_payment_failed(db, payload)
            elif event_type == "order.paid":
                # order.paid fires alongside payment.captured — treat as idempotent ACK only
                # Primary logic is in payment.captured to avoid duplicate allocation
                logger.info("order.paid event %s received — acknowledged (handled via payment.captured)", event_id)
                result = {"status": "acknowledged", "event": event_type}
            else:
                logger.info("Unhandled webhook event type: %s", event_type)
                result = {"status": "unhandled", "event": event_type}

            webhook_record.status = "processed"
        except Exception as exc:
            logger.exception("Error processing webhook event %s (type=%s)", event_id, event_type)
            webhook_record.status = "failed"
            webhook_record.error_message = str(exc)
            result = {"status": "failed", "event": event_type, "error": str(exc)}

        db.commit()
        return result

    @staticmethod
    def _handle_payment_captured(db: Session, payload: Dict) -> Dict:
        """Handle payment.captured webhook — update internal payment and invoice."""
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_order_id = payment_entity.get("order_id")
        razorpay_payment_id = payment_entity.get("id")
        amount_paise = payment_entity.get("amount", 0)

        if not razorpay_order_id or not razorpay_payment_id:
            logger.error("payment.captured payload missing order_id or payment_id")
            return {"status": "error", "reason": "missing_ids"}

        # Find internal payment record
        payment = db.query(Payment).filter(
            Payment.razorpay_order_id == razorpay_order_id
        ).with_for_update().first()

        if not payment:
            logger.warning("No internal Payment found for Razorpay order %s", razorpay_order_id)
            return {"status": "skipped", "reason": "no_internal_payment_record"}

        # Idempotency — already succeeded?
        if payment.status == "succeeded":
            logger.info("Payment for order %s already succeeded — skipping webhook", razorpay_order_id)
            return {"status": "skipped", "reason": "already_processed"}

        # Update payment record
        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = "succeeded"
        payment.paid_at = get_utc_now()
        payment.transaction_reference = razorpay_payment_id
        db.flush()

        # Find associated invoice and allocate
        from app.models.billing import PaymentAllocation
        invoice = db.query(Invoice).filter(
            Invoice.id == db.query(Invoice.id).filter(
                Invoice.customer_id == payment.customer_id,
                Invoice.status.notin_(["paid", "void", "uncollectible"])
            ).order_by(Invoice.created_at.desc()).limit(1).scalar_subquery()
        ).with_for_update().first()

        # Better: find invoice via the order receipt (stored as invoice_number in Razorpay order)
        # Fall back to finding any open invoice for this customer
        # The primary path is via verify_and_capture; webhook is the safety net
        if invoice and invoice.balance_due > Decimal("0.00"):
            alloc_amount = min(payment.amount, invoice.balance_due)
            # Check if allocation already exists
            existing_alloc = db.query(PaymentAllocation).filter(
                PaymentAllocation.payment_id == payment.id,
                PaymentAllocation.invoice_id == invoice.id,
            ).first()
            if not existing_alloc:
                pa = PaymentAllocation(
                    payment_id=payment.id,
                    invoice_id=invoice.id,
                    amount_allocated=alloc_amount,
                )
                db.add(pa)
                db.flush()
                db.expire(invoice, ["payment_allocations"])
                if invoice.balance_due <= Decimal("0.00"):
                    invoice.status = "paid"
                elif invoice.amount_paid > Decimal("0.00"):
                    invoice.status = "partially_paid"

        logger.info("payment.captured webhook processed: order=%s payment=%s", razorpay_order_id, razorpay_payment_id)
        return {"status": "processed", "event": "payment.captured", "razorpay_payment_id": razorpay_payment_id}

    @staticmethod
    def _handle_payment_failed(db: Session, payload: Dict) -> Dict:
        """Handle payment.failed webhook — mark internal payment as failed."""
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_order_id = payment_entity.get("order_id")
        razorpay_payment_id = payment_entity.get("id")
        error_description = payment_entity.get("error_description", "Payment failed")
        error_code = payment_entity.get("error_code", "")

        if not razorpay_order_id:
            return {"status": "error", "reason": "missing_order_id"}

        payment = db.query(Payment).filter(
            Payment.razorpay_order_id == razorpay_order_id
        ).with_for_update().first()

        if not payment:
            logger.warning("No internal Payment found for failed Razorpay order %s", razorpay_order_id)
            return {"status": "skipped", "reason": "no_internal_payment_record"}

        if payment.status in ("succeeded", "failed"):
            logger.info("Payment for order %s already in terminal status '%s'", razorpay_order_id, payment.status)
            return {"status": "skipped", "reason": "already_terminal"}

        payment.status = "failed"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.failure_reason = f"[{error_code}] {error_description}" if error_code else error_description
        db.flush()

        # A failed payment MUST NEVER mark the invoice as paid — no invoice update here
        logger.info(
            "payment.failed webhook processed: order=%s reason=%s",
            razorpay_order_id, payment.failure_reason
        )
        return {
            "status": "processed",
            "event": "payment.failed",
            "razorpay_order_id": razorpay_order_id,
            "failure_reason": payment.failure_reason,
        }
