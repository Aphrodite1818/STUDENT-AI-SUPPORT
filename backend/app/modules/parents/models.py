from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA

if TYPE_CHECKING:
    from app.modules.students.models import Student, StudentParentLink, StudentParentLinkRequest


class ParentAccountStatus(str, PyEnum):
    """Parent account lifecycle status."""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Parent(BaseModel):
    """Parent or guardian actor account and profile."""

    __tablename__ = "parents"

    email: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    occupation: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    emergency_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    account_status: Mapped[ParentAccountStatus] = mapped_column(
        SQLEnum(
            ParentAccountStatus,
            name="parent_account_status",
            schema=PUBLIC_SCHEMA,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=ParentAccountStatus.PENDING,
        server_default=ParentAccountStatus.PENDING.value,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student_links: Mapped[list["StudentParentLink"]] = relationship(
        "StudentParentLink",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    student_link_requests: Mapped[list["StudentParentLinkRequest"]] = relationship(
        "StudentParentLinkRequest",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    @property
    def students(self) -> list["Student"]:
        """Return linked students."""

        return [link.student for link in self.student_links if link.student is not None]

    __table_args__ = (
        Index("ix_parents_tenant_email", "tenant_id", "email"),
        Index("ix_parents_tenant_account_status", "tenant_id", "account_status"),
    )

    @property
    def profile_completed(self) -> bool:
        """Return whether the parent completed the required self-service fields."""

        return bool(
            self.first_name
            and self.first_name.strip()
            and self.last_name
            and self.last_name.strip()
        )
