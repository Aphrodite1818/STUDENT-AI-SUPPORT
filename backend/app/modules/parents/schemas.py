from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.students.schemas import StudentParentLinkResponse, StudentResponse


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
        use_enum_values=True,
        populate_by_name=True,
    )


def _clean_optional_string(value: str | None) -> str | None:
    """Normalize optional string input."""
    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value or None


class ParentCreate(InputBase):
    """Schema for creating a parent profile."""

    user_id: UUID
    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator("occupation", "address", "emergency_phone", mode="before")
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class ParentUpdate(InputBase):
    """Schema for updating a parent profile."""

    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator("occupation", "address", "emergency_phone", mode="before")
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class ParentResponse(OutputBase):
    """Schema returned for parent profile data."""

    id: UUID
    tenant_id: UUID
    user_id: UUID

    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    phone_number: str | None = None
    whatsapp_id: str | None = None

    occupation: str | None = None
    address: str | None = None
    emergency_phone: str | None = None

    created_at: datetime
    updated_at: datetime


class ParentListResponse(OutputBase):
    """Paginated-style response container for parent lists."""

    items: list[ParentResponse]
    total: int


class ParentLinkedStudentResponse(OutputBase):
    """Student profile plus the relationship metadata for the current parent."""

    student: StudentResponse
    link: StudentParentLinkResponse


class ParentLinkedStudentListResponse(OutputBase):
    """Linked students visible to the current parent."""

    items: list[ParentLinkedStudentResponse]
    total: int
