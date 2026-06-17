#======================================#
#            user models.py            #
#======================================#

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SQLEnum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA

if TYPE_CHECKING:
    from app.modules.teachers.models import Teacher
    from app.modules.parents.models import Parent
    from app.modules.students.models import Student


class UserRole(str, Enum):
    """Represent the UserRole type."""
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"
    PARENT = "parent"


class AccountStatus(str, Enum):
    """Enumeration of supported users values."""
    ACTIVE = "active"
    BANNED = "banned"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    PENDING = "pending"


class User(BaseModel):
    """Represent the User type."""
    __tablename__ = "users"

    firstname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    account_status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus, name="accountstatus", schema=PUBLIC_SCHEMA),
        default=AccountStatus.PENDING,
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="userrole", schema=PUBLIC_SCHEMA),
        nullable=False,
    )

    whatsapp_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )


    student_profile: Mapped["Student | None"] = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    parent_profile: Mapped["Parent | None"] = relationship(
        "Parent",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    teacher_profile: Mapped["Teacher | None"] = relationship(
        "Teacher",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_users_tenant_phone", "tenant_id", "phone_number"),
        Index("ix_users_tenant_role", "tenant_id", "role"),
    )  # this creates additional index for faster db lookups

