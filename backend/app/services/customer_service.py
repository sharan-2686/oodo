from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Customer:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer {customer_id} not found")
        return customer

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.customer_code == code).first()

    @staticmethod
    def list_customers(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Customer]:
        query = db.query(Customer)
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Customer.name.ilike(search_filter)) |
                (Customer.customer_code.ilike(search_filter)) |
                (Customer.email.ilike(search_filter)) |
                (Customer.company_name.ilike(search_filter))
            )
        return query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_customers(
        db: Session,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        query = db.query(Customer)
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Customer.name.ilike(search_filter)) |
                (Customer.customer_code.ilike(search_filter)) |
                (Customer.email.ilike(search_filter)) |
                (Customer.company_name.ilike(search_filter))
            )
        return query.count()

    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, creator_id: Optional[int] = None) -> Customer:
        existing = db.query(Customer).filter(Customer.customer_code == data.customer_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with code '{data.customer_code}' already exists"
            )
        
        customer = Customer(
            customer_code=data.customer_code,
            customer_type=data.customer_type,
            name=data.name,
            email=data.email,
            phone=data.phone,
            company_name=data.company_name,
            tax_identifier=data.tax_identifier,
            billing_address_line1=data.billing_address_line1,
            billing_address_line2=data.billing_address_line2,
            billing_city=data.billing_city,
            billing_state=data.billing_state,
            billing_postal_code=data.billing_postal_code,
            billing_country=data.billing_country,
            notes=data.notes,
            is_active=data.is_active,
            created_by=creator_id
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate) -> Customer:
        customer = CustomerService.get_by_id(db, customer_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        db.commit()
        db.refresh(customer)
        return customer
