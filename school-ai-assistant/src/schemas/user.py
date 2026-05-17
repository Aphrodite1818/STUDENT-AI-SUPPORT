# schemas/user.py

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field

from schemas.common import BaseSchema


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    PARENT = "parent"


class UserBase(BaseSchema):
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserInDB(UserOut):
    hashed_password: str


class TokenOut(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseSchema):
    email_or_phone: str
    password: str