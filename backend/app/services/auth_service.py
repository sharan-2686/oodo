from datetime import timedelta
from typing import Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.database import get_utc_now
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.customer import Customer, CustomerType
from app.models.user import Permission, RefreshToken, Role, User
from app.schemas.auth import (
    CustomerSignUpRequest,
    RoleResponse,
    StaffSignUpRequest,
    UserResponse,
)


def build_user_response(user: User) -> UserResponse:
    """Helper to convert a User ORM instance into UserResponse with permissions."""
    permission_codes = [p.code for p in user.role.permissions] if user.role and user.role.permissions else []
    role_resp = RoleResponse(
        id=user.role.id,
        name=user.role.name,
        description=user.role.description,
        permissions=permission_codes,
    )
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        role=role_resp,
        permissions=permission_codes,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user credentials and update last login timestamp."""
    stmt = (
        select(User)
        .options(
            selectinload(User.role).selectinload(Role.permissions)
        )
        .where(User.email == email.strip().lower())
    )
    user = db.scalar(stmt)

    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS",
        )

    if not user.is_active:
        raise UnauthorizedError(
            message="User account is deactivated",
            code="ACCOUNT_DEACTIVATED",
        )

    user.last_login_at = get_utc_now()
    db.commit()
    db.refresh(user)
    return user


def create_user_session(db: Session, user: User) -> Tuple[str, str, int]:
    """Create access token and store hashed refresh token in database."""
    permission_codes = [p.code for p in user.role.permissions] if user.role and user.role.permissions else []
    claims = {
        "email": user.email,
        "role": user.role.name if user.role else None,
        "permissions": permission_codes,
    }
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        claims=claims,
        expires_delta=expires_delta,
    )

    raw_refresh_token = generate_refresh_token()
    token_hash = hash_token(raw_refresh_token)
    refresh_expires_at = get_utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=refresh_expires_at,
        created_at=get_utc_now(),
    )
    db.add(db_token)
    db.commit()

    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return access_token, raw_refresh_token, expires_in_seconds


def refresh_user_session(db: Session, raw_refresh_token: str) -> Tuple[str, str, int, User]:
    """Validate refresh token, rotate it, and generate new session tokens."""
    token_hash = hash_token(raw_refresh_token)
    stmt = (
        select(RefreshToken)
        .options(
            selectinload(RefreshToken.user)
            .selectinload(User.role)
            .selectinload(Role.permissions)
        )
        .where(RefreshToken.token_hash == token_hash)
    )
    db_token = db.scalar(stmt)

    now = get_utc_now()
    if not db_token or db_token.revoked_at is not None or db_token.expires_at < now:
        raise UnauthorizedError(
            message="Refresh token is invalid or expired",
            code="INVALID_REFRESH_TOKEN",
        )

    user = db_token.user
    if not user or not user.is_active:
        raise UnauthorizedError(
            message="User associated with token is inactive",
            code="ACCOUNT_DEACTIVATED",
        )

    # Invalidate old refresh token (token rotation)
    db_token.revoked_at = now
    db.commit()

    # Issue new session
    access_token, new_refresh_token, expires_in = create_user_session(db, user)
    return access_token, new_refresh_token, expires_in, user


def revoke_user_token(db: Session, raw_refresh_token: str) -> bool:
    """Revoke an active refresh token on logout."""
    token_hash = hash_token(raw_refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    db_token = db.scalar(stmt)

    if db_token and db_token.revoked_at is None:
        db_token.revoked_at = get_utc_now()
        db.commit()
        return True
    return False


def register_customer(db: Session, payload: CustomerSignUpRequest) -> Tuple[str, str, int, User]:
    """Register a new customer account, create customer profile, and issue auth session."""
    email_clean = payload.email.strip().lower()
    existing = db.scalar(select(User).where(User.email == email_clean))
    if existing:
        raise ConflictError(
            message=f"An account with email '{payload.email}' already exists",
            code="USER_EMAIL_EXISTS",
        )

    # Resolve or create Customer role
    role = db.scalar(select(Role).where(func.lower(Role.name) == "customer"))
    if not role:
        role = Role(
            name="Customer",
            description="Registered customer portal access",
            created_at=get_utc_now(),
        )
        db.add(role)
        db.flush()
        cust_perm_codes = [
            "catalog:read",
            "quotation:read",
            "quotation:write",
            "subscription:read",
            "invoice:read",
            "payments:read",
            "payments:write",
        ]
        perms = db.scalars(select(Permission).where(Permission.code.in_(cust_perm_codes))).all()
        role.permissions = list(perms)
        db.flush()

    new_user = User(
        email=email_clean,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role_id=role.id,
        is_active=True,
        created_at=get_utc_now(),
        updated_at=get_utc_now(),
    )
    db.add(new_user)
    db.flush()

    # Create linked Customer record
    cust_code = f"CUST-{uuid.uuid4().hex[:8].upper()}"
    ctype = (
        CustomerType.BUSINESS
        if payload.customer_type.strip().lower() == "business"
        else CustomerType.INDIVIDUAL
    )
    customer = Customer(
        customer_code=cust_code,
        customer_type=ctype,
        name=payload.full_name.strip(),
        email=email_clean,
        phone=payload.phone,
        company_name=payload.company_name,
        tax_identifier=payload.tax_identifier,
        billing_address_line1=payload.billing_address_line1,
        billing_address_line2=payload.billing_address_line2,
        billing_city=payload.billing_city,
        billing_state=payload.billing_state,
        billing_postal_code=payload.billing_postal_code,
        billing_country=payload.billing_country or "IN",
        created_by=new_user.id,
        is_active=True,
        created_at=get_utc_now(),
        updated_at=get_utc_now(),
    )
    db.add(customer)
    db.commit()

    # Eager reload user
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == new_user.id)
    )
    user = db.scalar(stmt)
    access_token, refresh_token, expires_in = create_user_session(db, user)
    return access_token, refresh_token, expires_in, user


def register_staff(db: Session, payload: StaffSignUpRequest) -> Tuple[str, str, int, User]:
    """Register an internal staff member (excluding admin) and issue auth session."""
    target_role_name = payload.role.strip().lower()
    if target_role_name == "admin":
        raise ForbiddenError(
            message="Administrator accounts cannot be self-registered. Please contact system owner.",
            code="ADMIN_REGISTRATION_FORBIDDEN",
        )

    email_clean = payload.email.strip().lower()
    existing = db.scalar(select(User).where(User.email == email_clean))
    if existing:
        raise ConflictError(
            message=f"An account with email '{payload.email}' already exists",
            code="USER_EMAIL_EXISTS",
        )

    # Locate the target staff role or fallback to default 'staff'
    role = db.scalar(select(Role).where(func.lower(Role.name) == target_role_name))
    if not role:
        role = db.scalar(select(Role).where(func.lower(Role.name) == "staff"))
        if not role:
            role = Role(
                name="staff",
                description="Operational staff access",
                created_at=get_utc_now(),
            )
            db.add(role)
            db.flush()

    new_user = User(
        email=email_clean,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role_id=role.id,
        is_active=True,
        created_at=get_utc_now(),
        updated_at=get_utc_now(),
    )
    db.add(new_user)
    db.commit()

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == new_user.id)
    )
    user = db.scalar(stmt)
    access_token, refresh_token, expires_in = create_user_session(db, user)
    return access_token, refresh_token, expires_in, user