#======================================#
#            user models.py            #
#======================================#

from enum import Enum
from sqlalchemy import String, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.shared.base_model import BaseModel


class UserRole(str, Enum):
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

    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)

    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False) 

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  

    account_status: Mapped[AccountStatus] = mapped_column(
        default=AccountStatus.PENDING, 
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        nullable=False
    )

    whatsapp_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True) 

    # Relationships
    parent_profile = relationship("ParentProfile", back_populates="user", uselist=False)
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)

    __table_args__ = (
        Index("ix_users_tenant_phone", "tenant_id", "phone_number"),
        Index("ix_users_tenant_role", "tenant_id", "role"),
    )