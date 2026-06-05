#======================================#
#            users schemas.py          #
#======================================#

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator
from backend.app.modules.users.models import UserRole, AccountStatus


class UserBase(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone_number: str = Field(..., min_length=7, max_length=20)

    model_config = {"str_strip_whitespace": True}

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("phone_number must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("phone_number must contain only digits after country code")
        return cleaned_value


class UserCreate(UserBase):
    tenant_id: uuid.UUID
    password: str = Field(..., min_length=8, max_length=64)  
    role: UserRole
    whatsapp_id: str | None = Field(None, max_length=100)
    account_status: AccountStatus = AccountStatus.PENDING

    @field_validator("account_status")
    @classmethod
    def validate_account_status(cls, value: AccountStatus) -> AccountStatus:
        if value != AccountStatus.PENDING:
            raise ValueError("new users must be created with pending account status")
        return value

    @field_validator("whatsapp_id")
    @classmethod
    def validate_whatsapp_id(cls, value: str | None) -> str | None:
        if value is None:
            return value

        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("whatsapp_id must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("whatsapp_id must contain only digits after country code")
        return cleaned_value


class UserUpdate(BaseModel):
    firstname: str | None = Field(None, min_length=2, max_length=100)
    lastname: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(None, min_length=7, max_length=20)
    whatsapp_id: str | None = Field(None, max_length=100)

    model_config = {"str_strip_whitespace": True}

    @field_validator("phone_number", "whatsapp_id")
    @classmethod
    def validate_contact_number(cls, value: str | None) -> str | None:
        if value is None:
            return value

        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("contact number must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("contact number must contain only digits after country code")
        return cleaned_value


class UserAdminUpdate(BaseModel):              
    role: UserRole | None = None
    account_status: AccountStatus | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime
    role: UserRole
    account_status: AccountStatus
    whatsapp_id: str | None = None

    model_config = {"from_attributes": True}  


class UserPublicResponse(BaseModel):
    id: uuid.UUID
    firstname: str
    lastname: str
    role: UserRole
    account_status: AccountStatus

    model_config = {"from_attributes": True}
