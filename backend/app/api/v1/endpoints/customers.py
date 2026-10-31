from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import ForbiddenError
from app.core.permissions import get_optional_current_user
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        # Customer only sees their own profile
        items = db.query(Customer).filter(
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id)
        ).all()
        return CustomerListResponse(total=len(items), items=items)

    items = CustomerService.list_customers(db, skip=skip, limit=limit, search=search, is_active=is_active)
    total = CustomerService.count_customers(db, search=search, is_active=is_active)
    return CustomerListResponse(total=total, items=items)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        raise ForbiddenError(
            message="Customers cannot create company customer records. Use self-service signup.",
            code="CUSTOMER_OPERATION_NOT_ALLOWED",
        )
    creator_id = current_user.id if current_user else None
    return CustomerService.create_customer(db, data, creator_id=creator_id)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            Customer.id == customer_id,
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id),
        ).first()
        if not cust:
            raise ForbiddenError(message="Access denied to this customer profile", code="FORBIDDEN_PROFILE")
        return cust
    return CustomerService.get_by_id(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if current_user and current_user.role and current_user.role.name.lower() == "customer":
        cust = db.query(Customer).filter(
            Customer.id == customer_id,
            (Customer.email == current_user.email) | (Customer.created_by == current_user.id),
        ).first()
        if not cust:
            raise ForbiddenError(message="Cannot modify other customer profiles", code="FORBIDDEN_PROFILE")
    return CustomerService.update_customer(db, customer_id, data)

