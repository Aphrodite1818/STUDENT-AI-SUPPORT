import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class InputBase(BaseModel):
    """Pydantic schema for the superadmin domain."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class OutputBase(BaseModel):
    """Pydantic schema for the superadmin domain."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SuperadminInviteCreate(InputBase):
    """Pydantic schema for the superadmin domain."""
    email: EmailStr


class SuperadminResponse(OutputBase):
    """Pydantic schema for the superadmin domain."""
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
