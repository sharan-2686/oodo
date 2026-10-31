from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class DiscountBase(BaseModel):
    code: str = Field(..., max_length=60)
    name: str = Field(..., max_length=150)
    discount_type: str = Field("percentage", description="percentage or fixed")
    discount_value: Decimal = Field(..., gt=Decimal("0.00"))
    currency: Optional[str] = Field("INR", max_length=3)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    max_redemptions: Optional[int] = Field(None, ge=1)
    is_active: bool = True

class DiscountCreate(DiscountBase):
    pass

class DiscountUpdate(BaseModel):
    name: Optional[str] = None
    discount_value: Optional[Decimal] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    is_active: Optional[bool] = None

class DiscountResponse(DiscountBase):
    id: int
    redemption_count: int
    created_at: datetime

    class Config:
        from_attributes = True
