from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.permissions import require_admin
from app.schemas.catalog import PlanCreate, PlanResponse, PlanUpdate
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("", response_model=List[PlanResponse])
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    billing_interval: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    return CatalogService.list_plans(db, skip=skip, limit=limit, billing_interval=billing_interval, is_active=is_active)


@router.post(
    "",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_plan(data: PlanCreate, db: Session = Depends(get_db)):
    """Admin-only: Create a new recurring subscription plan."""
    return CatalogService.create_plan(db, data)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return CatalogService.get_plan(db, plan_id)


@router.put(
    "/{plan_id}",
    response_model=PlanResponse,
    dependencies=[Depends(require_admin)],
)
def update_plan(plan_id: int, data: PlanUpdate, db: Session = Depends(get_db)):
    """Admin-only: Update plan parameters."""
    return CatalogService.update_plan(db, plan_id, data)


@router.delete(
    "/{plan_id}",
    dependencies=[Depends(require_admin)],
)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """Admin-only: Delete a plan."""
    return CatalogService.delete_plan(db, plan_id)

