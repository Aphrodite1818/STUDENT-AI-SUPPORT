import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class InputBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class OutputBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SuperadminInviteCreate(InputBase):
    email: EmailStr


class SuperadminResponse(OutputBase):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
