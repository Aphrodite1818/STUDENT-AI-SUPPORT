import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base
from app.shared.mixins import TimestampMixin, UUIDMixin


class SuperAdmin(UUIDMixin, TimestampMixin, Base):
    """Represent the SuperAdmin type."""
    __tablename__ = "superadmins"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SuperAdminInvite(UUIDMixin, TimestampMixin, Base):
    """Represent the SuperAdminInvite type."""
    __tablename__ = "superadmin_invites"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    invited_by_superadmin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public.superadmins.id"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
