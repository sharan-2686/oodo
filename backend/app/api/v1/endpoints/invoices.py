from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import ForbiddenError
from app.core.permissions import get_optional_current_user, require_staff_or_admin
from app.models.customer import Customer
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreateOneTime, InvoiceGenerateFromSubscription, InvoiceResponse, InvoiceStatusAction
)
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[int] = Query(None),
    subscription_id: Optional[int] = Query(None),
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

    return InvoiceService.list_invoices(
        db, skip=skip, limit=limit, customer_id=customer_id, subscription_id=subscription_id, status_filter=status
    )


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_one_time_invoice(
    data: InvoiceCreateOneTime,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Staff and Admin manage daily invoice generation."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(message="Direct invoice creation is restricted to billing staff and administrators", code="STAFF_REQUIRED")

    user_id = current_user.id if current_user else None
    return InvoiceService.create_one_time_invoice(db, data, actor_user_id=user_id)


@router.post("/generate-from-subscription", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def generate_subscription_invoice(
    data: InvoiceGenerateFromSubscription,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Staff and Admin run automated/manual subscription billing runs."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(message="Subscription invoice generation is restricted to staff", code="STAFF_REQUIRED")

    user_id = current_user.id if current_user else None
    return InvoiceService.generate_from_subscription(db, data, actor_user_id=user_id)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    inv = InvoiceService.get_invoice(db, invoice_id)
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).first()
        if not cust or inv.customer_id != cust.id:
            raise ForbiddenError(message="Access denied to this invoice", code="FORBIDDEN_INVOICE")
    return inv


@router.post("/{invoice_id}/actions", response_model=InvoiceResponse)
def execute_invoice_action(
    invoice_id: int,
    action_in: InvoiceStatusAction,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Staff and Admin perform invoice actions (confirm, void, mark overdue)."""
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(message="Invoice status actions are restricted to billing staff and administrators", code="STAFF_REQUIRED")

    user_id = current_user.id if current_user else None
    return InvoiceService.transition_status(db, invoice_id, action_in.action, actor_user_id=user_id)

