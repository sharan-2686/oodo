from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

# --- Variants ---
class ProductVariantBase(BaseModel):
    sku: str = Field(..., max_length=80)
    name: str = Field(..., max_length=180)
    attributes: Optional[Dict[str, Any]] = None
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    currency: str = Field("INR", max_length=3)
    is_active: bool = True

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantResponse(ProductVariantBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Products ---
class ProductBase(BaseModel):
    sku: str = Field(..., max_length=80)
    name: str = Field(..., max_length=180)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class ProductCreate(ProductBase):
    variants: Optional[List[ProductVariantCreate]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    variants: List[ProductVariantResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Plan Items ---
class PlanItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: Decimal = Field(default=Decimal("1.000"), gt=Decimal("0.000"))
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))

class PlanItemCreate(PlanItemBase):
    pass

class PlanItemResponse(PlanItemBase):
    id: int
    plan_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Plans ---
class PlanBase(BaseModel):
    code: str = Field(..., max_length=60)
    name: str = Field(..., max_length=180)
    description: Optional[str] = None
    billing_interval: str = Field("month", description="day, week, month, year")
    interval_count: int = Field(1, ge=1)
    base_price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    currency: str = Field("INR", max_length=3)
    trial_days: int = Field(0, ge=0)
    is_active: bool = True

class PlanCreate(PlanBase):
    items: Optional[List[PlanItemCreate]] = None

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    billing_interval: Optional[str] = None
    interval_count: Optional[int] = None
    base_price: Optional[Decimal] = None
    trial_days: Optional[int] = None
    is_active: Optional[bool] = None

class PlanResponse(PlanBase):
    id: int
    items: List[PlanItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
