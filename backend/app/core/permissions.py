from collections.abc import Callable
from typing import List, Optional, Set
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import Role, User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the JWT Bearer token and return the User entity."""
    if not token:
        raise UnauthorizedError(
            message="Missing authentication credentials",
            code="NOT_AUTHENTICATED",
        )

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(
            message="Authentication token has expired",
            code="TOKEN_EXPIRED",
        )
    except jwt.PyJWTError:
        raise UnauthorizedError(
            message="Invalid or malformed authentication token",
            code="INVALID_TOKEN",
        )

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError(
            message="Token payload is missing subject claim",
            code="INVALID_TOKEN_SUBJECT",
        )

    try:
        user_id = int(subject)
    except (ValueError, TypeError):
        raise UnauthorizedError(
            message="Invalid user identifier in token",
            code="INVALID_TOKEN_SUBJECT",
        )

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = db.scalar(stmt)

    if not user:
        raise UnauthorizedError(
            message="Authenticated user record does not exist",
            code="USER_NOT_FOUND",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user is currently active."""
    if not current_user.is_active:
        raise UnauthorizedError(
            message="User account is deactivated",
            code="ACCOUNT_DEACTIVATED",
        )
    return current_user


def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Optional authentication dependency: returns User if valid token present, else None."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not subject:
            return None
        user_id = int(subject)
        stmt = (
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        user = db.scalar(stmt)
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


def require_role(*role_names: str) -> Callable[[User], User]:
    """Dependency factory that verifies the user has one of the specified roles.
    
    Admin role always passes automatically.
    """
    allowed_roles: Set[str] = {r.strip().lower() for r in role_names}

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_name = current_user.role.name.strip().lower() if current_user.role else ""

        # Admin bypass
        if user_role_name == "admin":
            return current_user

        if user_role_name not in allowed_roles:
            raise ForbiddenError(
                message=f"Access denied. Requires one of roles: {', '.join(role_names)}",
                code="INSUFFICIENT_ROLE",
                details={"required_roles": list(role_names), "user_role": current_user.role.name if current_user.role else None},
            )
        return current_user

    return role_checker


def require_permission(*permission_codes: str, require_all: bool = False) -> Callable[[User], User]:
    """Dependency factory that verifies the user has the required permission codes.
    
    Admin role always passes automatically.
    """
    required_perms: Set[str] = set(permission_codes)

    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_name = current_user.role.name.strip().lower() if current_user.role else ""

        # Admin role bypass
        if user_role_name == "admin":
            return current_user

        user_perms: Set[str] = (
            {p.code for p in current_user.role.permissions}
            if current_user.role and current_user.role.permissions
            else set()
        )

        if require_all:
            missing = required_perms - user_perms
            if missing:
                raise ForbiddenError(
                    message=f"Access denied. Missing required permissions: {', '.join(sorted(missing))}",
                    code="INSUFFICIENT_PERMISSIONS",
                    details={"missing_permissions": list(missing)},
                )
        else:
            if not (required_perms & user_perms):
                raise ForbiddenError(
                    message=f"Access denied. Requires at least one permission from: {', '.join(permission_codes)}",
                    code="INSUFFICIENT_PERMISSIONS",
                    details={"required_any": list(permission_codes)},
                )

        return current_user

    return permission_checker


def require_admin(
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Optional[User]:
    """Ensure that when authenticated, the caller must have the Administrator role."""
    if current_user is not None:
        role_name = current_user.role.name.strip().lower() if current_user.role else ""
        if role_name != "admin":
            raise ForbiddenError(
                message="Administrator privileges required for this operation",
                code="ADMIN_REQUIRED",
            )
    return current_user


def require_staff_or_admin(
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Optional[User]:
    """Ensure that when authenticated, the caller must be internal staff or administrator (excludes customer)."""
    if current_user is not None:
        role_name = current_user.role.name.strip().lower() if current_user.role else ""
        if role_name not in ["admin", "staff", "sales", "finance", "support"]:
            raise ForbiddenError(
                message="Internal staff or administrator privileges required",
                code="STAFF_REQUIRED",
            )
    return current_user



