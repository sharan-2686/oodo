from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class PaymentAllocationCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(..., gt=Decimal("0.00"))

class PaymentAllocationResponse(BaseModel):
    id: int
    payment_id: int
    invoice_id: int
    amount_allocated: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    customer_id: int
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    currency: str = Field("INR", max_length=3)
    payment_method: str = Field("bank_transfer", description="cash, bank_transfer, card, upi, gateway, other")
    transaction_reference: Optional[str] = Field(None, max_length=150)
    idempotency_key: Optional[str] = Field(None, max_length=100)
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    allocations: Optional[List[PaymentAllocationCreate]] = None

class PaymentResponse(BaseModel):
    id: int
    payment_number: str
    customer_id: int
    amount: Decimal
    currency: str
    payment_method: str
    status: str
    transaction_reference: Optional[str]
    idempotency_key: Optional[str]
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    total_allocated: Decimal = Decimal("0.00")
    unallocated_amount: Decimal = Decimal("0.00")
    allocations: List[PaymentAllocationResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
