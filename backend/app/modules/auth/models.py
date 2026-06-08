#======================================#
#             auth/models.py           #
#======================================#

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA


class AuthPurpose(str, Enum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    TENANT_ACTIVATION = "tenant_activation"
    USER_INVITE = "user_invite"


class AuthRecord(BaseModel):
    __tablename__ = "auth"

    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    hashed_value: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[AuthPurpose] = mapped_column(
        SQLEnum(AuthPurpose, name="otppurpose", schema=PUBLIC_SCHEMA),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

