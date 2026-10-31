from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

class QuotationItemBase(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    plan_id: Optional[int] = None
    description: str = Field(..., max_length=255)
    quantity: Decimal = Field(default=Decimal("1.000"), gt=Decimal("0.000"))
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    tax_rate_percent: Decimal = Field(default=Decimal("0.0000"), ge=Decimal("0.0000"))

class QuotationItemCreate(QuotationItemBase):
    pass

class QuotationItemResponse(QuotationItemBase):
    id: int
    quotation_id: int
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True

class QuotationCreate(BaseModel):
    customer_id: Optional[int] = None
    discount_id: Optional[int] = None
    issue_date: Optional[date] = None
    valid_until: Optional[date] = None
    currency: str = Field("INR", max_length=3)
    terms: Optional[str] = None
    notes: Optional[str] = None
    items: List[QuotationItemCreate] = Field(..., min_length=1)

class QuotationUpdate(BaseModel):
    valid_until: Optional[date] = None
    discount_id: Optional[int] = None
    status: Optional[str] = None # draft, sent, accepted, rejected, expired
    terms: Optional[str] = None
    notes: Optional[str] = None

class QuotationResponse(BaseModel):
    id: int
    quote_number: str
    customer_id: int
    created_by: Optional[int]
    discount_id: Optional[int]
    status: str
    issue_date: date
    valid_until: Optional[date]
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    terms: Optional[str]
    notes: Optional[str]
    items: List[QuotationItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuotationConvertRequest(BaseModel):
    plan_id: Optional[int] = Field(None, description="Plan to associate with the subscription if not inferred from quotation")
    start_date: Optional[date] = None
    billing_interval: Optional[str] = Field("month", description="day, week, month, year")
    payment_terms: Optional[str] = "Net 15"
