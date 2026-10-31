from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.permissions import require_admin
from app.schemas.catalog import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    return CatalogService.list_products(db, skip=skip, limit=limit, category=category, is_active=is_active)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Admin-only: Create product and optional initial variants."""
    return CatalogService.create_product(db, data)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return CatalogService.get_product(db, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)],
)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    """Admin-only: Update product information."""
    return CatalogService.update_product(db, product_id, data)


@router.delete(
    "/{product_id}",
    dependencies=[Depends(require_admin)],
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Admin-only: Delete a product and its associated variants."""
    return CatalogService.delete_product(db, product_id)


@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def add_product_variant(product_id: int, data: ProductVariantCreate, db: Session = Depends(get_db)):
    """Admin-only: Add a new variant to an existing product."""
    return CatalogService.add_variant(db, product_id, data)


@router.delete(
    "/variants/{variant_id}",
    dependencies=[Depends(require_admin)],
)
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    """Admin-only: Delete a product variant."""
    return CatalogService.delete_variant(db, variant_id)

