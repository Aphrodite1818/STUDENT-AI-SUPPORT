#======================================#
#            auth/schemas.py           #
#======================================#

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdatePassword(BaseModel):
    email: EmailStr
    new_password: str
    reset_token: str

class RequestOTP(BaseModel):
    email: EmailStr
    purpose: Literal["verification", "password_reset"] # "verification" or "password_reset"

class VerifyOTP(BaseModel):
    email: EmailStr
    code: str
    purpose: Literal["verification", "password_reset"]


class TenantActivationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    token: str = Field(..., min_length=20)


class UserInviteAcceptanceRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    token: str = Field(..., min_length=20)
