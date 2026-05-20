#==========================#
# USER SCRIPT
#==========================#

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from ..helpers.user_helper import UserRole
from .common import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=120)
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    hashed_password: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseSchema):
    email_or_phone: str
    password: str
