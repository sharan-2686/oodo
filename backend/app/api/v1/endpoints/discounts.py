from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.catalog import Discount, DiscountType
from app.schemas.discount import DiscountCreate, DiscountResponse

router = APIRouter(prefix="/discounts", tags=["Discounts"])


@router.get("", response_model=List[DiscountResponse])
def list_discounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Discount)
    if is_active is not None:
        query = query.filter(Discount.is_active == is_active)
    return query.order_by(Discount.created_at.desc()).offset(skip).limit(limit).all()


@router.post(
    "",
    response_model=DiscountResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_discount(data: DiscountCreate, db: Session = Depends(get_db)):
    existing = db.query(Discount).filter(Discount.code == data.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Discount code '{data.code}' already exists")
    
    discount = Discount(
        code=data.code,
        name=data.name,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        currency=data.currency,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        max_redemptions=data.max_redemptions,
        is_active=data.is_active
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount

@router.get("/{discount_id}", response_model=DiscountResponse)
def get_discount(discount_id: int, db: Session = Depends(get_db)):
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discount not found")
    return discount
