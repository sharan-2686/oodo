from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta
import uuid

from app.models.quotation import Quotation, QuotationItem
from app.models.subscription import Subscription, SubscriptionItem, SubscriptionEvent
from app.models.customer import Customer
from app.models.catalog import Product, ProductVariant, Plan, Discount
from app.models.audit import AuditLog
from app.schemas.quotation import QuotationCreate, QuotationUpdate, QuotationConvertRequest
from app.services.pricing_service import PricingService, quantize_money

class QuotationService:
    @staticmethod
    def generate_quote_number() -> str:
        return f"QT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def get_quotation(db: Session, quotation_id: int) -> Quotation:
        quote = db.query(Quotation).filter(Quotation.id == quotation_id).first()
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quotation {quotation_id} not found")
        return quote

    @staticmethod
    def list_quotations(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Quotation]:
        query = db.query(Quotation)
        if customer_id:
            query = query.filter(Quotation.customer_id == customer_id)
        if status_filter:
            query = query.filter(Quotation.status == status_filter)
        return query.order_by(Quotation.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_quotation(db: Session, data: QuotationCreate, user_id: Optional[int] = None) -> Quotation:
        if not data.customer_id and user_id:
            cust = db.query(Customer).filter((Customer.created_by == user_id)).first()
            if cust:
                data.customer_id = cust.id

        if not data.customer_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer ID is required")

        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer {data.customer_id} not found")


        discount = None
        if data.discount_id:
            discount = db.query(Discount).filter(Discount.id == data.discount_id).first()
            if not discount:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Discount {data.discount_id} not found")

        quote_number = QuotationService.generate_quote_number()
        issue_date = data.issue_date or date.today()
        valid_until = data.valid_until or (issue_date + timedelta(days=30))

        quotation = Quotation(
            quote_number=quote_number,
            customer_id=customer.id,
            created_by=user_id,
            discount_id=discount.id if discount else None,
            status="draft",
            issue_date=issue_date,
            valid_until=valid_until,
            currency=data.currency,
            terms=data.terms,
            notes=data.notes,
            subtotal=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("0.00")
        )
        db.add(quotation)
        db.flush()

        total_subtotal = Decimal("0.00")
        total_tax = Decimal("0.00")
        total_qty = Decimal("0.000")

        for item_in in data.items:
            if item_in.variant_id and item_in.product_id:
                variant = db.query(ProductVariant).filter(
                    ProductVariant.id == item_in.variant_id,
                    ProductVariant.product_id == item_in.product_id
                ).first()
                if not variant:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Variant {item_in.variant_id} does not belong to Product {item_in.product_id}"
                    )

            line_subtotal, line_tax, line_total = PricingService.calculate_line_item(
                quantity=item_in.quantity,
                unit_price=item_in.unit_price,
                tax_rate_percent=item_in.tax_rate_percent,
                is_inclusive=False
            )
            total_subtotal += line_subtotal
            total_tax += line_tax
            total_qty += Decimal(str(item_in.quantity))

            q_item = QuotationItem(
                quotation_id=quotation.id,
                product_id=item_in.product_id,
                variant_id=item_in.variant_id,
                plan_id=item_in.plan_id,
                description=item_in.description,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price,
                tax_rate_percent=item_in.tax_rate_percent,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total
            )
            db.add(q_item)

        discount_amount = PricingService.evaluate_discount(discount, total_subtotal, total_qty)
        final_total = max(Decimal("0.00"), total_subtotal - discount_amount + total_tax)

        quotation.subtotal = total_subtotal
        quotation.discount_amount = discount_amount
        quotation.tax_amount = total_tax
        quotation.total_amount = final_total

        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def update_quotation_status(db: Session, quotation_id: int, new_status: str) -> Quotation:
        quote = QuotationService.get_quotation(db, quotation_id)
        allowed_transitions = {
            "draft": ["sent", "accepted", "rejected", "expired"],
            "sent": ["accepted", "rejected", "expired"],
            "accepted": ["converted", "expired"],
            "rejected": [],
            "expired": [],
            "converted": []
        }
        if new_status not in allowed_transitions.get(quote.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition quotation from '{quote.status}' to '{new_status}'"
            )
        quote.status = new_status
        db.commit()
        db.refresh(quote)
        return quote

    @staticmethod
    def convert_to_subscription(
        db: Session,
        quotation_id: int,
        req: QuotationConvertRequest,
        actor_user_id: Optional[int] = None
    ) -> Subscription:
        quote = db.query(Quotation).filter(Quotation.id == quotation_id).with_for_update().first()
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")

        if quote.status == "converted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quotation has already been converted into a subscription"
            )

        if quote.status != "accepted":
            quote.status = "accepted"

        plan_id = req.plan_id
        if not plan_id:
            for item in quote.items:
                if item.plan_id:
                    plan_id = item.plan_id
                    break
        if not plan_id:
            plan = db.query(Plan).filter(Plan.is_active == True).first()
            if not plan:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Plan specified and none found")
            plan_id = plan.id
        else:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan {plan_id} not found")

        sub_number = f"SUB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        start_date = req.start_date or date.today()
        billing_interval = req.billing_interval or plan.billing_interval
        
        now_utc = datetime.now(timezone.utc)
        period_start = now_utc
        if billing_interval == "day":
            period_end = period_start + timedelta(days=1)
        elif billing_interval == "week":
            period_end = period_start + timedelta(weeks=1)
        elif billing_interval == "year":
            period_end = period_start + timedelta(days=365)
        else:
            period_end = period_start + timedelta(days=30)

        subscription = Subscription(
            subscription_number=sub_number,
            customer_id=quote.customer_id,
            plan_id=plan_id,
            quotation_id=quote.id,
            discount_id=quote.discount_id,
            status="active",
            currency=quote.currency,
            unit_price=plan.base_price if plan.base_price > 0 else quote.total_amount,
            quantity=Decimal("1.000"),
            billing_interval=billing_interval,
            interval_count=1,
            start_date=start_date,
            current_period_start=period_start,
            current_period_end=period_end,
            next_billing_at=period_end,
            created_by=actor_user_id
        )
        db.add(subscription)
        db.flush()

        for q_item in quote.items:
            if q_item.product_id:
                sub_item = SubscriptionItem(
                    subscription_id=subscription.id,
                    product_id=q_item.product_id,
                    variant_id=q_item.variant_id,
                    description_snapshot=q_item.description,
                    quantity=q_item.quantity,
                    unit_price=q_item.unit_price
                )
                db.add(sub_item)

        event = SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="CONVERTED_FROM_QUOTATION",
            from_status=None,
            to_status="active",
            event_data={"quotation_id": quote.id, "quote_number": quote.quote_number},
            actor_user_id=actor_user_id
        )
        db.add(event)

        quote.status = "converted"

        audit = AuditLog(
            actor_user_id=actor_user_id,
            action="CONVERT_QUOTATION",
            entity_type="quotations",
            entity_id=quote.id,
            after_data={"subscription_id": subscription.id, "subscription_number": sub_number}
        )
        db.add(audit)

        db.commit()
        db.refresh(subscription)
        return subscription
