from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    CustomerSignUpRequest,
    LoginRequest,
    RefreshTokenRequest,
    StaffSignUpRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    build_user_response,
    create_user_session,
    refresh_user_session,
    register_customer,
    register_staff,
    revoke_user_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup/customer",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer account and customer profile",
)
@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def signup_customer(
    payload: CustomerSignUpRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Register customer account, create customer profile, and return active session tokens."""
    access_token, refresh_token, expires_in, user = register_customer(db, payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=build_user_response(user),
    )


@router.post(
    "/signup/staff",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register an internal staff member (admin prohibited)",
)
def signup_staff(
    payload: StaffSignUpRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Register staff account with specified staff role (sales, finance, support) and return session tokens."""
    access_token, refresh_token, expires_in, user = register_staff(db, payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=build_user_response(user),
    )



@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT access and refresh tokens",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Validate user credentials and return access and refresh tokens with user permissions."""
    user = authenticate_user(db, email=payload.email, password=payload.password)
    access_token, refresh_token, expires_in = create_user_session(db, user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=build_user_response(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and issue new access token",
)
def refresh_token(
    payload: RefreshTokenRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Exchange valid refresh token for a newly issued access token and rotated refresh token."""
    access_token, new_refresh_token, expires_in, user = refresh_user_session(
        db, raw_refresh_token=payload.refresh_token
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=build_user_response(user),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke active refresh token",
)
def logout(
    payload: RefreshTokenRequest, db: Session = Depends(get_db)
) -> dict:
    """Revoke the provided refresh token so it can no longer be used."""
    revoke_user_token(db, raw_refresh_token=payload.refresh_token)
    return {"success": True, "message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get profile and permissions of authenticated user",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Return identity, role, and granted permissions for the active session user."""
    return build_user_response(current_user)

