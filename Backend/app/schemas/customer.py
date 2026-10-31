from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    customer_code: str = Field(max_length=40)
    name: str = Field(max_length=180)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)


class CustomerRead(CustomerCreate):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
