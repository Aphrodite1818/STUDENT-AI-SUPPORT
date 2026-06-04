#======================================#
#             auth/models.py           #
#======================================#

from enum import Enum
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.shared.base_model import BaseModel
from datetime import datetime

class OTPPurpose(str, Enum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"

class OTP(BaseModel):
    __tablename__ = "otps"

    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(255), nullable=False) # Hashed or plain (hashing recommended)
    purpose: Mapped[OTPPurpose] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
