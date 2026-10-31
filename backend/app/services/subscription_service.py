from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta
import uuid

from app.models.subscription import Subscription, SubscriptionItem, SubscriptionEvent
from app.models.catalog import Plan, Product, ProductVariant, Discount
from app.models.customer import Customer
from app.models.audit import AuditLog
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionStatusTransition

class SubscriptionService:
    @staticmethod
    def generate_sub_number() -> str:
        return f"SUB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def calculate_period(start_dt: datetime, interval: str, count: int = 1) -> datetime:
        if interval == "day":
            return start_dt + timedelta(days=count)
        elif interval == "week":
            return start_dt + timedelta(weeks=count)
        elif interval == "year":
            return start_dt + timedelta(days=365 * count)
        else: # month
            return start_dt + timedelta(days=30 * count)

    @staticmethod
    def get_subscription(db: Session, sub_id: int) -> Subscription:
        sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscription {sub_id} not found")
        return sub

    @staticmethod
    def list_subscriptions(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[int] = None,
        plan_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Subscription]:
        query = db.query(Subscription)
        if customer_id:
            query = query.filter(Subscription.customer_id == customer_id)
        if plan_id:
            query = query.filter(Subscription.plan_id == plan_id)
        if status_filter:
            query = query.filter(Subscription.status == status_filter)
        return query.order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_subscription(
        db: Session,
        data: SubscriptionCreate,
        actor_user_id: Optional[int] = None
    ) -> Subscription:
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        plan = db.query(Plan).filter(Plan.id == data.plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        if data.discount_id:
            discount = db.query(Discount).filter(Discount.id == data.discount_id).first()
            if not discount:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discount not found")

        sub_number = SubscriptionService.generate_sub_number()
        start_date = data.start_date or date.today()
        now_utc = datetime.now(timezone.utc)
        period_start = now_utc
        period_end = SubscriptionService.calculate_period(period_start, data.billing_interval, data.interval_count)

        unit_price = data.unit_price if data.unit_price is not None else plan.base_price

        subscription = Subscription(
            subscription_number=sub_number,
            customer_id=customer.id,
            plan_id=plan.id,
            quotation_id=data.quotation_id,
            discount_id=data.discount_id,
            status="active",
            currency=plan.currency,
            unit_price=unit_price,
            quantity=data.quantity,
            billing_interval=data.billing_interval,
            interval_count=data.interval_count,
            start_date=start_date,
            current_period_start=period_start,
            current_period_end=period_end,
            next_billing_at=period_end,
            created_by=actor_user_id
        )
        db.add(subscription)
        db.flush()

        if data.items:
            for item in data.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if not product:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found")
                sub_item = SubscriptionItem(
                    subscription_id=subscription.id,
                    product_id=product.id,
                    variant_id=item.variant_id,
                    description_snapshot=item.description_snapshot,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                db.add(sub_item)
        elif plan.items:
            for p_item in plan.items:
                sub_item = SubscriptionItem(
                    subscription_id=subscription.id,
                    product_id=p_item.product_id,
                    variant_id=p_item.variant_id,
                    description_snapshot=f"{plan.name} - {p_item.product.name}",
                    quantity=p_item.quantity * data.quantity,
                    unit_price=p_item.unit_price
                )
                db.add(sub_item)

        event = SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="CREATED",
            from_status=None,
            to_status="active",
            event_data={"subscription_number": sub_number, "plan": plan.name},
            actor_user_id=actor_user_id
        )
        db.add(event)

        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def transition_status(
        db: Session,
        sub_id: int,
        req: SubscriptionStatusTransition,
        actor_user_id: Optional[int] = None
    ) -> Subscription:
        sub = db.query(Subscription).filter(Subscription.id == sub_id).with_for_update().first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

        old_status = sub.status
        action = req.action.lower()

        if action == "confirm":
            if old_status not in ["draft", "quotation"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot confirm subscription in '{old_status}' state")
            new_status = "active"
        elif action == "activate":
            if old_status not in ["confirmed", "draft", "quotation"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot activate subscription in '{old_status}' state")
            new_status = "active"
        elif action == "pause":
            if old_status != "active":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only active subscriptions can be paused")
            new_status = "paused"
        elif action == "resume":
            if old_status != "paused":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only paused subscriptions can be resumed")
            new_status = "active"
        elif action == "cancel":
            if old_status in ["cancelled", "expired"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Subscription is already {old_status}")
            new_status = "cancelled"
            sub.cancelled_at = datetime.now(timezone.utc)
        elif action == "close":
            if old_status in ["cancelled", "expired"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Subscription is already {old_status}")
            new_status = "cancelled" # Person 1 enum has 'cancelled' and 'expired'
            sub.cancelled_at = datetime.now(timezone.utc)
        elif action == "renew":
            if old_status not in ["active", "paused", "cancelled"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot renew subscription")
            new_status = "active"
            start_ref = sub.current_period_end or datetime.now(timezone.utc)
            sub.current_period_start = start_ref
            sub.current_period_end = SubscriptionService.calculate_period(start_ref, sub.billing_interval, sub.interval_count)
            sub.next_billing_at = sub.current_period_end
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown lifecycle action '{action}'")

        sub.status = new_status

        event = SubscriptionEvent(
            subscription_id=sub.id,
            event_type=f"LIFECYCLE_{action.upper()}",
            from_status=old_status,
            to_status=new_status,
            event_data={"reason": req.reason},
            actor_user_id=actor_user_id
        )
        db.add(event)

        audit = AuditLog(
            actor_user_id=actor_user_id,
            action=f"SUBSCRIPTION_{action.upper()}",
            entity_type="subscriptions",
            entity_id=sub.id,
            before_data={"status": old_status},
            after_data={"status": new_status, "reason": req.reason}
        )
        db.add(audit)

        db.commit()
        db.refresh(sub)
        return sub
