from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.parents.models import ParentAccountStatus
from app.modules.students.schemas import StudentParentLinkResponse, StudentResponse


class InputBase(BaseModel):
    """Base for all request/input schemas."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=False,
        extra="forbid",
        use_enum_values=True,
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
    """Schema for creating a parent actor."""

    email: EmailStr
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, min_length=7, max_length=20)
    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator(
        "first_name",
        "last_name",
        "phone_number",
        "occupation",
        "address",
        "emergency_phone",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""

        return _clean_optional_string(value)


class ParentUpdate(InputBase):
    """Schema for admin updating a parent actor."""

    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=64)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, min_length=7, max_length=20)
    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)
    account_status: ParentAccountStatus | None = None
    is_verified: bool | None = None
    is_active: bool | None = None
    last_login_at: datetime | None = None

    @field_validator(
        "first_name",
        "last_name",
        "phone_number",
        "occupation",
        "address",
        "emergency_phone",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""

        return _clean_optional_string(value)


class ParentSelfUpdate(InputBase):
    """Self-service parent profile update schema."""

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, min_length=7, max_length=20)
    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator(
        "first_name",
        "last_name",
        "phone_number",
        "occupation",
        "address",
        "emergency_phone",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""

        return _clean_optional_string(value)


class ParentOnboardingUpdate(InputBase):
    """Schema for parent onboarding and self-service profile completion."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, min_length=7, max_length=20)
    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator(
        "first_name",
        "last_name",
        "phone_number",
        "occupation",
        "address",
        "emergency_phone",
        mode="before",
    )
    @classmethod
    def clean_onboarding_fields(cls, value: str | None) -> str | None:
        """Normalize onboarding fields."""

        return _clean_optional_string(value)


class ParentResponse(OutputBase):
    """Schema returned for parent profile data."""

    id: UUID
    tenant_id: UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    occupation: str | None = None
    address: str | None = None
    emergency_phone: str | None = None
    account_status: ParentAccountStatus
    profile_completed: bool
    is_verified: bool
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ParentLoginProfile(OutputBase):
    """Compact parent profile used after authentication."""

    id: UUID
    tenant_id: UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    account_status: ParentAccountStatus
    is_verified: bool
    is_active: bool


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


class ParentOnboardingStatusResponse(OutputBase):
    """Parent onboarding status response."""

    actor_type: Literal["parent"]
    parent_id: UUID
    onboarding_required: bool
    profile_completed: bool
    completion_target: Literal["parent"]
    required_fields: list[str]
    current_values: dict[str, Any]
