#======================================#
#            auth/schemas.py           #
#======================================#

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    """Represent the Token type."""
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    """Pydantic schema for the auth domain."""
    email: EmailStr
    password: str


class UpdatePassword(BaseModel):
    """Represent the UpdatePassword type."""
    email: EmailStr
    new_password: str
    reset_token: str

class RequestOTP(BaseModel):
    """Represent the RequestOTP type."""
    email: EmailStr
    purpose: Literal["verification", "password_reset"] # "verification" or "password_reset"

class VerifyOTP(BaseModel):
    """Represent the VerifyOTP type."""
    email: EmailStr
    code: str
    purpose: Literal["verification", "password_reset"]


class TenantActivationRequest(BaseModel):
    """Pydantic schema for the auth domain."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    token: str = Field(..., min_length=20)


class UserInviteAcceptanceRequest(BaseModel):
    """Pydantic schema for the auth domain."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    token: str = Field(..., min_length=20)
