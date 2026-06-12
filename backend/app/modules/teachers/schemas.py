#======================================#
#              schemas.py              #
#======================================#

from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.teachers.models import TeacherStatus


class InputBase(BaseModel):
    """Base for all request/input schemas"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=False,
        extra="forbid",
    )


class OutputBase(BaseModel):
    """Base for all response/output schemas"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True,
    )


def _clean_optional_string(
    value: str | None,
) -> str | None:
    """Internal helper for clean optional string."""
    if value is None:
        return None

    cleaned_value = value.strip()

    return cleaned_value or None


class TeacherUpdate(InputBase):
    """Pydantic schema for the teachers domain."""
    staff_id: str | None = Field(
        default=None,
        max_length=50,
    )

    qualification: str | None = Field(
        default=None,
        max_length=100,
    )

    specialization: str | None = Field(
        default=None,
        max_length=150,
    )

    subject_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="Full replacement list of subject IDs assigned to this teacher",
    )

    @field_validator(
        "staff_id",
        "qualification",
        "specialization",
        mode="before",
    )
    @classmethod
    def clean_optional_text_fields(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class SubjectSummaryResponse(OutputBase):
    """Pydantic schema for the teachers domain."""
    id: uuid.UUID
    name: str
    code: str | None


class TeacherResponse(OutputBase):
    """Pydantic schema for the teachers domain."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID

    staff_id: str | None
    qualification: str | None
    specialization: str | None
    status: TeacherStatus

    subjects: list[SubjectSummaryResponse] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime


class TeacherListResponse(OutputBase):
    """Pydantic schema for the teachers domain."""
    items: list[TeacherResponse]
    total: int
