#======================================#
#              schemas.py              #
#======================================#

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InputBase(BaseModel):
    """Base schema for request payloads."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        str_to_lower=False,
    )


class OutputBase(BaseModel):
    """Base schema for response payloads."""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True,
    )


class ClassRoomBase(InputBase):
    """Shared classroom fields."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Class name e.g JSS 1",
    )

    level: str | None = Field(
        default=None,
        max_length=100,
        description="Academic level e.g Junior Secondary, Senior Secondary",
    )

    arm: str = Field(
        min_length=1,
        max_length=20,
        description="Class arm e.g A, B, Science",
    )

    teacher_id: uuid.UUID | None = Field(
        default=None,
        description="Optional class teacher ID",
    )


class ClassRoomCreate(ClassRoomBase):
    """Payload for creating a classroom."""

    pass


class ClassRoomUpdate(InputBase):
    """Payload for updating a classroom."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    level: str | None = Field(
        default=None,
        max_length=100,
    )

    arm: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    teacher_id: uuid.UUID | None = Field(default=None)

    is_active: bool | None = Field(default=None)


class ClassRoomResponse(OutputBase):
    """Classroom response schema."""

    id: uuid.UUID
    tenant_id: uuid.UUID

    name: str
    level: str | None
    arm: str

    teacher_id: uuid.UUID | None
    is_active: bool

    created_at: datetime
    updated_at: datetime