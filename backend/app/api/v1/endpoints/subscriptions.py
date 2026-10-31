from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import ForbiddenError
from app.core.permissions import get_optional_current_user, require_staff_or_admin
from app.models.customer import Customer
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse, SubscriptionStatusTransition
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("", response_model=List[SubscriptionResponse])
def list_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[int] = Query(None),
    plan_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust:
            return []
        customer_id = cust.id

    return SubscriptionService.list_subscriptions(
        db, skip=skip, limit=limit, customer_id=customer_id, plan_id=plan_id, status_filter=status
    )


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Staff and Admin manage daily subscription configurations."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(message="Direct subscription provisioning is handled by staff via quotations", code="STAFF_REQUIRED")

    user_id = current_user.id if current_user else None
    return SubscriptionService.create_subscription(db, data, actor_user_id=user_id)


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    sub = SubscriptionService.get_subscription(db, subscription_id)
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust or sub.customer_id != cust.id:
            raise ForbiddenError(message="Access denied to this subscription", code="FORBIDDEN_SUBSCRIPTION")
    return sub


@router.post("/{subscription_id}/lifecycle", response_model=SubscriptionResponse)
def transition_subscription_lifecycle(
    subscription_id: int,
    req: SubscriptionStatusTransition,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(message="Lifecycle transitions are restricted to staff and administrators", code="STAFF_REQUIRED")

    user_id = current_user.id if current_user else None
    return SubscriptionService.transition_status(db, subscription_id, req, actor_user_id=user_id)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: int,
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    sub = SubscriptionService.get_subscription(db, subscription_id)
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust or sub.customer_id != cust.id:
            raise ForbiddenError(message="Access denied to cancel this subscription", code="FORBIDDEN_SUBSCRIPTION")

    user_id = current_user.id if current_user else None
    req = SubscriptionStatusTransition(action="cancel", reason=reason)
    return SubscriptionService.transition_status(db, subscription_id, req, actor_user_id=user_id)

