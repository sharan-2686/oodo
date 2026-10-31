from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.billing import InvoiceCreate, InvoiceRead
from app.services.invoice_service import create_invoice

router = APIRouter()


@router.post("/", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create(payload: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = create_invoice(db, payload)
    db.commit()
    db.refresh(invoice)
    return invoice
