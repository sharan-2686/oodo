from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class InvoiceLineCreate(BaseModel):
    description: str = Field(max_length=255)
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    tax_rate_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100, max_digits=7, decimal_places=4)


class InvoiceCreate(BaseModel):
    customer_id: int
    due_date: date
    items: list[InvoiceLineCreate] = Field(min_length=1)


class InvoiceRead(BaseModel):
    id: int
    invoice_number: str
    status: str
    total_amount: Decimal
    currency: str
    model_config = ConfigDict(from_attributes=True)


class AllocationCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class PaymentCreate(BaseModel):
    customer_id: int
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: str = Field(max_length=30)
    idempotency_key: str = Field(min_length=8, max_length=100)
    allocations: list[AllocationCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def allocations_do_not_exceed_payment(self):
        if sum((item.amount for item in self.allocations), Decimal("0")) > self.amount:
            raise ValueError("allocations cannot exceed payment amount")
        return self


class PaymentRead(BaseModel):
    id: int
    payment_number: str
    status: str
    amount: Decimal
    paid_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
