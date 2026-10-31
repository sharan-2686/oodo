from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import ForbiddenError
from app.core.permissions import get_optional_current_user
from app.models.customer import Customer
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=List[PaymentResponse])
def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[int] = Query(None),
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

    return PaymentService.list_payments(db, skip=skip, limit=limit, customer_id=customer_id, status_filter=status)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Customers pay their invoices; Staff and Admin record payments."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if cust:
            data.customer_id = cust.id

    user_id = current_user.id if current_user else None
    return PaymentService.record_payment_and_allocations(db, data, actor_user_id=user_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    pay = PaymentService.get_payment(db, payment_id)
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust or pay.customer_id != cust.id:
            raise ForbiddenError(message="Access denied to this payment record", code="FORBIDDEN_PAYMENT")
    return pay

