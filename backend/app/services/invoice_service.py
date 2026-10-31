from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta
import uuid

from app.models.billing import Invoice, InvoiceItem, BillingRun
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.models.catalog import Discount, Product, ProductVariant, TaxRate
from app.models.audit import AuditLog
from app.schemas.invoice import InvoiceCreateOneTime, InvoiceGenerateFromSubscription
from app.services.pricing_service import PricingService, quantize_money

class InvoiceService:
    @staticmethod
    def generate_invoice_number() -> str:
        return f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def get_invoice(db: Session, invoice_id: int) -> Invoice:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")
        return invoice

    @staticmethod
    def list_invoices(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[int] = None,
        subscription_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Invoice]:
        query = db.query(Invoice)
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        if subscription_id:
            query = query.filter(Invoice.subscription_id == subscription_id)
        if status_filter:
            query = query.filter(Invoice.status == status_filter)
        return query.order_by(Invoice.issue_date.desc(), Invoice.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def generate_from_subscription(
        db: Session,
        req: InvoiceGenerateFromSubscription,
        actor_user_id: Optional[int] = None
    ) -> Invoice:
        sub = db.query(Subscription).filter(Subscription.id == req.subscription_id).with_for_update().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

        customer = sub.customer
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        p_start = req.billing_period_start or (sub.current_period_start.date() if sub.current_period_start else date.today())
        p_end = req.billing_period_end or (sub.current_period_end.date() if sub.current_period_end else (p_start + timedelta(days=30)))

        # Enforce unique billing period / prevent duplicate invoice generation
        existing_run = db.query(BillingRun).filter(
            BillingRun.subscription_id == sub.id,
            BillingRun.billing_period_start == p_start,
            BillingRun.billing_period_end == p_end,
            BillingRun.status == "succeeded"
        ).first()

        if existing_run:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invoice already generated for subscription {sub.id} covering period {p_start} to {p_end}"
            )

        issue_date = req.issue_date or date.today()
        terms_days = 15
        due_date = req.due_date or (issue_date + timedelta(days=terms_days))

        inv_number = InvoiceService.generate_invoice_number()

        address_snapshot = {
            "line1": customer.billing_address_line1,
            "line2": customer.billing_address_line2,
            "city": customer.billing_city,
            "state": customer.billing_state,
            "postal_code": customer.billing_postal_code,
            "country": customer.billing_country
        }

        invoice = Invoice(
            invoice_number=inv_number,
            customer_id=customer.id,
            subscription_id=sub.id,
            discount_id=sub.discount_id,
            invoice_type="subscription",
            status="issued",
            currency=sub.currency,
            issue_date=issue_date,
            due_date=due_date,
            billing_period_start=p_start,
            billing_period_end=p_end,
            customer_name_snapshot=customer.name,
            customer_email_snapshot=customer.email,
            billing_address_snapshot=address_snapshot,
            notes=f"Recurring billing for {sub.subscription_number}",
            created_by=actor_user_id,
            subtotal=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("0.00")
        )
        db.add(invoice)
        db.flush()

        total_subtotal = Decimal("0.00")
        total_tax = Decimal("0.00")
        total_qty = Decimal("0.000")

        # Snapshot items from subscription
        for item in sub.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            sku = product.sku if product else None
            
            line_subtotal, line_tax, line_total = PricingService.calculate_line_item(
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_percent=Decimal("0.0000"),
                is_inclusive=False
            )
            total_subtotal += line_subtotal
            total_tax += line_tax
            total_qty += Decimal(str(item.quantity))

            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                plan_id=sub.plan_id,
                description_snapshot=item.description_snapshot,
                sku_snapshot=sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_percent=Decimal("0.0000"),
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total
            )
            db.add(inv_item)

        # Evaluate Discount
        discount_amount = Decimal("0.00")
        if sub.discount:
            discount_amount = PricingService.evaluate_discount(sub.discount, total_subtotal, total_qty)
            invoice.discount_code_snapshot = sub.discount.code
            if discount_amount > 0:
                sub.discount.redemption_count += 1

        final_total = max(Decimal("0.00"), total_subtotal - discount_amount + total_tax)
        invoice.subtotal = total_subtotal
        invoice.discount_amount = discount_amount
        invoice.tax_amount = total_tax
        invoice.total_amount = final_total

        # Create BillingRun record
        billing_run = BillingRun(
            subscription_id=sub.id,
            invoice_id=invoice.id,
            billing_period_start=p_start,
            billing_period_end=p_end,
            status="succeeded",
            attempt_count=1,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(billing_run)

        # Audit
        audit = AuditLog(
            actor_user_id=actor_user_id,
            action="GENERATE_SUBSCRIPTION_INVOICE",
            entity_type="invoices",
            entity_id=invoice.id,
            after_data={"invoice_number": inv_number, "total": str(final_total)}
        )
        db.add(audit)

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def create_one_time_invoice(
        db: Session,
        data: InvoiceCreateOneTime,
        actor_user_id: Optional[int] = None
    ) -> Invoice:
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        discount = None
        if data.discount_id:
            discount = db.query(Discount).filter(Discount.id == data.discount_id).first()
            if not discount:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discount not found")

        issue_date = data.issue_date or date.today()
        due_date = data.due_date or (issue_date + timedelta(days=15))
        inv_number = InvoiceService.generate_invoice_number()

        address_snapshot = {
            "line1": customer.billing_address_line1,
            "line2": customer.billing_address_line2,
            "city": customer.billing_city,
            "state": customer.billing_state,
            "postal_code": customer.billing_postal_code,
            "country": customer.billing_country
        }

        invoice = Invoice(
            invoice_number=inv_number,
            customer_id=customer.id,
            discount_id=discount.id if discount else None,
            invoice_type="one_time",
            status="issued",
            currency=data.currency,
            issue_date=issue_date,
            due_date=due_date,
            customer_name_snapshot=customer.name,
            customer_email_snapshot=customer.email,
            billing_address_snapshot=address_snapshot,
            notes=data.notes,
            created_by=actor_user_id,
            subtotal=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("0.00")
        )
        db.add(invoice)
        db.flush()

        total_subtotal = Decimal("0.00")
        total_tax = Decimal("0.00")
        total_qty = Decimal("0.000")

        for item in data.items:
            line_subtotal, line_tax, line_total = PricingService.calculate_line_item(
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_percent=item.tax_rate_percent,
                is_inclusive=False
            )
            total_subtotal += line_subtotal
            total_tax += line_tax
            total_qty += Decimal(str(item.quantity))

            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                plan_id=item.plan_id,
                description_snapshot=item.description_snapshot,
                sku_snapshot=item.sku_snapshot,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_percent=item.tax_rate_percent,
                tax_name_snapshot=item.tax_name_snapshot,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total
            )
            db.add(inv_item)

        discount_amount = PricingService.evaluate_discount(discount, total_subtotal, total_qty)
        if discount and discount_amount > 0:
            invoice.discount_code_snapshot = discount.code
            discount.redemption_count += 1

        final_total = max(Decimal("0.00"), total_subtotal - discount_amount + total_tax)
        invoice.subtotal = total_subtotal
        invoice.discount_amount = discount_amount
        invoice.tax_amount = total_tax
        invoice.total_amount = final_total

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def transition_status(db: Session, invoice_id: int, action: str, actor_user_id: Optional[int] = None) -> Invoice:
        invoice = InvoiceService.get_invoice(db, invoice_id)
        action = action.lower()
        if action == "confirm":
            invoice.status = "issued"
        elif action == "void":
            if invoice.amount_paid > Decimal("0.00"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot void an invoice that has payments recorded")
            invoice.status = "void"
        elif action == "mark_overdue":
            if invoice.status not in ["paid", "void"]:
                invoice.status = "overdue"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown action '{action}'")

        db.commit()
        db.refresh(invoice)
        return invoice
