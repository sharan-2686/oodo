from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.catalog import TaxRate
from app.schemas.tax import TaxRateCreate, TaxRateResponse

router = APIRouter(prefix="/taxes", tags=["Tax Rates"])


@router.get("", response_model=List[TaxRateResponse])
def list_tax_rates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    country: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TaxRate)
    if is_active is not None:
        query = query.filter(TaxRate.is_active == is_active)
    if country:
        query = query.filter(TaxRate.country == country)
    return query.order_by(TaxRate.name.asc()).offset(skip).limit(limit).all()

@router.post(
    "",
    response_model=TaxRateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_tax_rate(data: TaxRateCreate, db: Session = Depends(get_db)):
    existing = db.query(TaxRate).filter(TaxRate.code == data.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"TaxRate code '{data.code}' already exists")

    tax = TaxRate(
        name=data.name,
        code=data.code,
        rate_percent=data.rate_percent,
        country=data.country,
        region=data.region,
        is_inclusive=data.is_inclusive,
        is_active=data.is_active,
        effective_from=data.effective_from,
        effective_to=data.effective_to
    )
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax

@router.get("/{tax_id}", response_model=TaxRateResponse)
def get_tax_rate(tax_id: int, db: Session = Depends(get_db)):
    tax = db.query(TaxRate).filter(TaxRate.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tax rate not found")
    return tax
