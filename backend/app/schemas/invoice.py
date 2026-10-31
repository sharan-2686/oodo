from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

class InvoiceItemBase(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    plan_id: Optional[int] = None
    description_snapshot: str = Field(..., max_length=255)
    sku_snapshot: Optional[str] = None
    quantity: Decimal = Field(default=Decimal("1.000"), gt=Decimal("0.000"))
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    tax_rate_percent: Decimal = Field(default=Decimal("0.0000"), ge=Decimal("0.0000"))
    tax_name_snapshot: Optional[str] = None

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True

class InvoiceCreateOneTime(BaseModel):
    customer_id: int
    discount_id: Optional[int] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: str = Field("INR", max_length=3)
    notes: Optional[str] = None
    items: List[InvoiceItemCreate] = Field(..., min_length=1)

class InvoiceGenerateFromSubscription(BaseModel):
    subscription_id: int
    billing_period_start: Optional[date] = None
    billing_period_end: Optional[date] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None

class InvoiceStatusAction(BaseModel):
    action: str = Field(..., description="Action: confirm, void, mark_overdue")
    notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    subscription_id: Optional[int]
    discount_id: Optional[int]
    invoice_type: str
    status: str
    currency: str
    issue_date: date
    due_date: date
    billing_period_start: Optional[date]
    billing_period_end: Optional[date]
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal = Decimal("0.00")
    balance_due: Decimal = Decimal("0.00")
    discount_code_snapshot: Optional[str]
    customer_name_snapshot: str
    customer_email_snapshot: Optional[str]
    billing_address_snapshot: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_by: Optional[int]
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
