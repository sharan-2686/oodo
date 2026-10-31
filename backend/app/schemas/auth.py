from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """User credentials for authentication."""
    email: EmailStr
    password: str = Field(..., min_length=1, description="Account password")


class RefreshTokenRequest(BaseModel):
    """Request payload to rotate refresh token."""
    refresh_token: str = Field(..., description="Active refresh token string")


class PermissionResponse(BaseModel):
    """Permission detail."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """Role information with associated permission codes."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)


class UserResponse(BaseModel):
    """User profile data returned upon authentication or profile query."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    is_active: bool
    role: RoleResponse
    permissions: List[str] = Field(
        default_factory=list,
        description="Flattened list of permission codes granted to the user",
    )
    last_login_at: Optional[datetime] = None
    created_at: datetime


class TokenResponse(BaseModel):
    """Token response returned upon successful authentication or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifespan in seconds")
    user: UserResponse


class UserCreateRequest(BaseModel):
    """Payload to create a new user (admin operation)."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Initial password")
    full_name: str = Field(..., min_length=2, max_length=160)
    role_id: int

