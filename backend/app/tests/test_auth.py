import pytest
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import (
    get_current_user_profile,
    login,
    logout,
    refresh_token,
)
from app.api.v1.endpoints.users import create_user, list_users
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.permissions import require_permission, require_role
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    UserCreateRequest,
)


def test_login_success(db_session: Session):
    """Test successful login with seeded admin credentials."""
    payload = LoginRequest(email="admin@brightloop.io", password="Admin@12345")
    token_response = login(payload=payload, db=db_session)

    assert token_response.access_token is not None
    assert token_response.refresh_token is not None
    assert token_response.token_type == "bearer"
    assert token_response.expires_in > 0
    assert token_response.user.email == "admin@brightloop.io"
    assert token_response.user.role.name == "Admin"
    assert "users:read" in token_response.user.permissions
    assert "invoice:read" in token_response.user.permissions


def test_login_invalid_password(db_session: Session):
    """Test login failure with incorrect password."""
    payload = LoginRequest(email="admin@brightloop.io", password="WrongPassword!")
    with pytest.raises(UnauthorizedError) as exc_info:
        login(payload=payload, db=db_session)

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401


def test_login_user_not_found(db_session: Session):
    """Test login failure with unregistered email address."""
    payload = LoginRequest(email="nonexistent@brightloop.io", password="Password123")
    with pytest.raises(UnauthorizedError) as exc_info:
        login(payload=payload, db=db_session)

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401


def test_login_deactivated_user(db_session: Session):
    """Test that deactivated accounts cannot log in."""
    user = db_session.query(User).filter_by(email="sales@brightloop.io").first()
    user.is_active = False
    db_session.commit()

    payload = LoginRequest(email="sales@brightloop.io", password="Sales@12345")
    with pytest.raises(UnauthorizedError) as exc_info:
        login(payload=payload, db=db_session)

    assert exc_info.value.code == "ACCOUNT_DEACTIVATED"

    # Reset
    user.is_active = True
    db_session.commit()


def test_get_current_user_profile(db_session: Session):
    """Test retrieving authenticated user profile using user ORM object."""
    admin = db_session.query(User).filter_by(email="admin@brightloop.io").first()
    profile = get_current_user_profile(current_user=admin)

    assert profile.email == "admin@brightloop.io"
    assert profile.role.name == "Admin"
    assert "users:read" in profile.permissions


def test_refresh_token_flow(db_session: Session):
    """Test refreshing an access token using a valid refresh token."""
    login_payload = LoginRequest(email="sales@brightloop.io", password="Sales@12345")
    token_resp = login(payload=login_payload, db=db_session)
    old_refresh_token = token_resp.refresh_token

    # Rotate refresh token
    refresh_payload = RefreshTokenRequest(refresh_token=old_refresh_token)
    new_token_resp = refresh_token(payload=refresh_payload, db=db_session)

    assert new_token_resp.access_token is not None
    assert new_token_resp.refresh_token is not None
    assert new_token_resp.refresh_token != old_refresh_token

    # Replaying the old token must fail
    with pytest.raises(UnauthorizedError) as exc_info:
        refresh_token(payload=refresh_payload, db=db_session)

    assert exc_info.value.code == "INVALID_REFRESH_TOKEN"


def test_logout_revokes_token(db_session: Session):
    """Test that logout successfully revokes refresh token."""
    login_payload = LoginRequest(email="finance@brightloop.io", password="Finance@12345")
    token_resp = login(payload=login_payload, db=db_session)
    rt = token_resp.refresh_token

    res = logout(payload=RefreshTokenRequest(refresh_token=rt), db=db_session)
    assert res["success"] is True

    # Re-using the revoked token to refresh must fail
    with pytest.raises(UnauthorizedError):
        refresh_token(payload=RefreshTokenRequest(refresh_token=rt), db=db_session)


def test_rbac_admin_allowed_sales_forbidden(db_session: Session):
    """Verify role and permission dependency checkers."""
    admin = db_session.query(User).filter_by(email="admin@brightloop.io").first()
    sales = db_session.query(User).filter_by(email="sales@brightloop.io").first()

    # Admin passes any permission check
    perm_checker = require_permission("users:read")
    assert perm_checker(current_user=admin) == admin

    # Sales lacks 'users:read'
    with pytest.raises(ForbiddenError) as exc_info:
        perm_checker(current_user=sales)
    assert exc_info.value.code == "INSUFFICIENT_PERMISSIONS"

    # Sales has 'quotation:write'
    quote_checker = require_permission("quotation:write")
    assert quote_checker(current_user=sales) == sales


def test_create_user_endpoint(db_session: Session):
    """Test creating a new user through the user endpoint."""
    payload = UserCreateRequest(
        email="newuser@brightloop.io",
        password="SecurePassword123",
        full_name="New Team Member",
        role_id=2,  # Sales
    )
    user_resp = create_user(payload=payload, db=db_session)
    assert user_resp.email == "newuser@brightloop.io"
    assert user_resp.role.id == 2
    assert "quotation:read" in user_resp.permissions
