from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime, date

class TaxRateBase(BaseModel):
    name: str = Field(..., max_length=120)
    code: str = Field(..., max_length=40)
    rate_percent: Decimal = Field(..., ge=Decimal("0.0000"), le=Decimal("100.0000"))
    country: Optional[str] = Field("IN", max_length=2)
    region: Optional[str] = Field(None, max_length=100)
    is_inclusive: bool = False
    is_active: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

class TaxRateCreate(TaxRateBase):
    pass

class TaxRateUpdate(BaseModel):
    name: Optional[str] = None
    rate_percent: Optional[Decimal] = None
    country: Optional[str] = None
    region: Optional[str] = None
    is_inclusive: Optional[bool] = None
    is_active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

class TaxRateResponse(TaxRateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
