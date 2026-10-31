from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.billing import PaymentCreate, PaymentRead
from app.services.payment_service import record_payment

router = APIRouter()


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create(payload: PaymentCreate, db: Session = Depends(get_db)):
    return record_payment(db, payload)
