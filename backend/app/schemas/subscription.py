from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

class SubscriptionItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    description_snapshot: str = Field(..., max_length=255)
    quantity: Decimal = Field(default=Decimal("1.000"), gt=Decimal("0.000"))
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))

class SubscriptionItemCreate(SubscriptionItemBase):
    pass

class SubscriptionItemResponse(SubscriptionItemBase):
    id: int
    subscription_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionEventResponse(BaseModel):
    id: int
    subscription_id: int
    event_type: str
    from_status: Optional[str]
    to_status: Optional[str]
    event_data: Optional[Dict[str, Any]]
    actor_user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int
    quotation_id: Optional[int] = None
    discount_id: Optional[int] = None
    unit_price: Optional[Decimal] = None
    quantity: Decimal = Field(default=Decimal("1.000"), gt=Decimal("0.000"))
    billing_interval: str = Field("month", description="day, week, month, year")
    interval_count: int = Field(1, ge=1)
    start_date: Optional[date] = None
    items: Optional[List[SubscriptionItemCreate]] = None

class SubscriptionUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    cancel_at_period_end: Optional[bool] = None

class SubscriptionStatusTransition(BaseModel):
    action: str = Field(..., description="Action: confirm, activate, pause, resume, cancel, close, renew")
    reason: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: int
    subscription_number: str
    customer_id: int
    plan_id: int
    quotation_id: Optional[int]
    discount_id: Optional[int]
    status: str
    currency: str
    unit_price: Decimal
    quantity: Decimal
    billing_interval: str
    interval_count: int
    start_date: date
    trial_ends_at: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    next_billing_at: Optional[datetime] = None
    cancel_at_period_end: bool = False
    cancelled_at: Optional[datetime] = None
    created_by: Optional[int] = None
    items: List[SubscriptionItemResponse] = []
    events: List[SubscriptionEventResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
