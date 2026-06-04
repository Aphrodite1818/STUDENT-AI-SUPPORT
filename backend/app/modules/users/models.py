#======================================#
#            user models.py            #
#======================================#

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.shared.base_model import BaseModel



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
        default=AccountStatus.PENDING, 
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        nullable=False
    )

    whatsapp_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True) 



    __table_args__ = (
        Index("ix_users_tenant_phone", "tenant_id", "phone_number"),
        Index("ix_users_tenant_role", "tenant_id", "role"),
    )
