#======================================#
#            users schemas.py          #
#======================================#

import uuid
from pydantic import BaseModel, EmailStr, Field
from backend.app.modules.users.models import UserRole, AccountStatus


class UserBase(BaseModel):
    firstname: str = Field(..., max_length=100)
    lastname: str = Field(..., max_length=100)
    email: EmailStr | None = None
    phone_number: str = Field(..., max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=64)  
    role: UserRole
    whatsapp_id: str | None = Field(None, max_length=100)
    account_status: AccountStatus = AccountStatus.PENDING


class UserUpdate(BaseModel):
    firstname: str | None = Field(None, max_length=100)
    lastname: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone_number: str | None = Field(None, max_length=20)


class UserAdminUpdate(BaseModel):              
    role: UserRole | None = None
    account_status: AccountStatus | None = None


class UserResponse(UserBase):
    id: uuid.UUID                            
    role: UserRole
    account_status: AccountStatus
    whatsapp_id: str | None

    model_config = {"from_attributes": True}  