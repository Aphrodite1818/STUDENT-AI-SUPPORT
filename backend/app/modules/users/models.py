#======================================#
#            user models.py            #
#======================================#

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Index , Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, PUBLIC_SCHEMA



class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"
    PARENT = "parent"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    BANNED = "banned"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    PENDING = "pending"


class User(BaseModel):
    __tablename__ = "users"

    firstname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True) 

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  

    account_status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus, name="accountstatus", schema=PUBLIC_SCHEMA),
        default=AccountStatus.PENDING, 
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="userrole", schema=PUBLIC_SCHEMA),
        nullable=False
    )

    whatsapp_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True) 


    is_verified : Mapped[bool] = mapped_column(Boolean , nullable = False , default = True)



    __table_args__ = (
        Index("ix_users_tenant_phone", "tenant_id", "phone_number"),
        Index("ix_users_tenant_role", "tenant_id", "role"),
    )#this creates additional index for faster db lookups 

