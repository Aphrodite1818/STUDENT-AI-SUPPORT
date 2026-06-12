#==========================#
#   subjects/schemas.py    #
#==========================#

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InputBase(BaseModel):
    """Base for all request/input schemas."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=False,
        extra="forbid",
    )


class OutputBase(BaseModel):
    """Base for all response/output schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


def _clean_optional_string(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value or None


class SubjectCreate(InputBase):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="name of the subject",
        examples=["Mathematics"],
    )
    code: str | None = Field(
        default=None,
        max_length=30,
        examples=["MATH"],
        description="short code for subject",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        examples=["core mathematics subject for junior class"],
    )
    teacher_ids: list[uuid.UUID] = Field(
        default_factory=list,
        description="IDs of teachers assigned to this subject",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("name cannot be empty")

        return cleaned_value

    @field_validator("code", "description", mode="before")
    @classmethod
    def clean_optional_text_fields(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class SubjectUpdate(InputBase):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    code: str | None = Field(default=None, min_length=2, max_length=30)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        cleaned_value = _clean_optional_string(value)

        if cleaned_value is not None and len(cleaned_value) < 2:
            raise ValueError("name must be at least 2 characters long")

        return cleaned_value

    @field_validator("code", "description", mode="before")
    @classmethod
    def clean_optional_text_fields(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class SubjectStatusUpdate(InputBase):
    is_active: bool


class SubjectTeacherResponse(OutputBase):
    id: uuid.UUID
    user_id: uuid.UUID
    staff_id: str | None
    firstname: str | None
    lastname: str | None
    email: str


class SubjectResponse(OutputBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    code: str | None
    description: str | None
    is_active: bool
    teachers: list[SubjectTeacherResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class SubjectListResponse(OutputBase):
    items: list[SubjectResponse]
    total: int
