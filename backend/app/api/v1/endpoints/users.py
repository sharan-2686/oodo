from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db, get_utc_now
from app.core.exceptions import ConflictError, NotFoundError
from app.core.permissions import require_permission, require_role
from app.core.security import hash_password
from app.models.user import Role, User
from app.schemas.auth import RoleResponse, UserCreateRequest, UserResponse
from app.services.auth_service import build_user_response

router = APIRouter(prefix="/users", tags=["Users & Access Management"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users",
    dependencies=[Depends(require_permission("users:read"))],
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[UserResponse]:
    """Retrieve all users with their roles and permissions."""
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .offset(skip)
        .limit(limit)
    )
    users = db.scalars(stmt).all()
    return [build_user_response(u) for u in users]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
    dependencies=[Depends(require_permission("users:write"))],
)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Create a new user with specified role and hashed password."""
    # Check for existing email
    existing_stmt = select(User).where(User.email == payload.email.strip().lower())
    if db.scalar(existing_stmt):
        raise ConflictError(
            message=f"User with email '{payload.email}' already exists",
            code="USER_EMAIL_EXISTS",
        )

    # Validate role existence
    role = db.get(Role, payload.role_id)
    if not role:
        raise NotFoundError(
            message=f"Role with ID {payload.role_id} not found",
            code="ROLE_NOT_FOUND",
        )

    new_user = User(
        email=payload.email.strip().lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role_id=payload.role_id,
        is_active=True,
        created_at=get_utc_now(),
        updated_at=get_utc_now(),
    )
    db.add(new_user)
    db.commit()

    # Re-fetch with eager loaded role and permissions
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == new_user.id)
    )
    user = db.scalar(stmt)
    return build_user_response(user)


@router.get(
    "/roles",
    response_model=List[RoleResponse],
    summary="List available system roles",
)
def list_roles(db: Session = Depends(get_db)) -> List[RoleResponse]:
    """List all configured roles with their granted permission codes."""
    stmt = select(Role).options(selectinload(Role.permissions))
    roles = db.scalars(stmt).all()
    return [
        RoleResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            permissions=[p.code for p in r.permissions],
        )
        for r in roles
    ]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user details by ID",
    dependencies=[Depends(require_permission("users:read"))],
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Retrieve detailed user profile by unique user ID."""
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = db.scalar(stmt)
    if not user:
        raise NotFoundError(
            message=f"User with ID {user_id} not found",
            code="USER_NOT_FOUND",
        )
    return build_user_response(user)

