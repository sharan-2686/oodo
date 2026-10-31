from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class CustomerBase(BaseModel):
    customer_code: str = Field(..., description="Unique business customer code", max_length=40)
    customer_type: str = Field("business", description="individual or business")
    name: str = Field(..., min_length=1, max_length=180)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=180)
    tax_identifier: Optional[str] = Field(None, max_length=80)
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = Field("IN", max_length=2)
    notes: Optional[str] = None
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    customer_type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    tax_identifier: Optional[str] = None
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    total: int
    items: List[CustomerResponse]
