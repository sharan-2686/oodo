from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import ForbiddenError
from app.core.permissions import get_optional_current_user, require_staff_or_admin
from app.models.customer import Customer
from app.models.user import User
from app.schemas.quotation import (
    QuotationCreate, QuotationResponse, QuotationConvertRequest
)
from app.schemas.subscription import SubscriptionResponse
from app.services.quotation_service import QuotationService

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.get("", response_model=List[QuotationResponse])
def list_quotations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    # Customer data isolation
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust:
            return []
        customer_id = cust.id

    return QuotationService.list_quotations(db, skip=skip, limit=limit, customer_id=customer_id, status_filter=status)


@router.post("", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def create_quotation(
    data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Customers can buy products by creating quotes; Staff/Admin can draft quotes for any customer."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if cust:
            data.customer_id = cust.id

    user_id = current_user.id if current_user else None
    return QuotationService.create_quotation(db, data, user_id=user_id)


@router.get("/{quotation_id}", response_model=QuotationResponse)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    quote = QuotationService.get_quotation(db, quotation_id)
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust or quote.customer_id != cust.id:
            raise ForbiddenError(message="Access denied to this quotation", code="FORBIDDEN_QUOTATION")
    return quote


@router.post("/{quotation_id}/status", response_model=QuotationResponse)
def update_quotation_status(
    quotation_id: int,
    status_value: str = Query(..., description="Target status: sent, accepted, rejected, expired"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    # Customer can accept/reject their quote; staff/admin can change any status
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        quote = QuotationService.get_quotation(db, quotation_id)
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust or quote.customer_id != cust.id:
            raise ForbiddenError(message="Access denied to this quotation", code="FORBIDDEN_QUOTATION")
        if status_value.lower() not in ["accepted", "rejected"]:
            raise ForbiddenError(message="Customers can only accept or reject quotations", code="INVALID_STATUS_ACTION")

    return QuotationService.update_quotation_status(db, quotation_id, status_value)


@router.post("/{quotation_id}/convert", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def convert_quotation(
    quotation_id: int,
    req: QuotationConvertRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Staff and Admin convert accepted quotations to active subscriptions."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(message="Subscription conversion must be processed by staff or administrator", code="STAFF_REQUIRED")

    user_id = current_user.id if current_user else None
    return QuotationService.convert_to_subscription(db, quotation_id, req, actor_user_id=user_id)

