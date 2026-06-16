#==========================#
#    students/schemas.py   #
#==========================#

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.students.models import AcademicStatus, Gender, ParentRelationship, StudentProfileStatus


# ──────────────────────────────────────────────
# SHARED BASE CONFIGS
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# STUDENT SCHEMAS
# ──────────────────────────────────────────────

class StudentInputBase(InputBase):
    """Base input schema for student academic profile data."""

    user_id: uuid.UUID
    admission_number: str | None = Field(default=None, min_length=1, max_length=50)
    date_of_birth: date | None = None
    gender: Gender | None = None
    passport_photo_url: str | None = Field(default=None, max_length=500)
    graduation_date: date | None = None
    class_id: uuid.UUID | None = None
    arm: str | None = Field(default=None, max_length=20)
    status: AcademicStatus = AcademicStatus.ACTIVE

    @field_validator("admission_number", "passport_photo_url", "arm", mode="before")
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class StudentCreate(StudentInputBase):
    """Schema for creating a student profile."""

    pass


class StudentProfileComplete(InputBase):
    """Schema for completing an incomplete student profile."""

    date_of_birth: date
    gender: Gender
    class_id: uuid.UUID
    arm: str | None = Field(default=None, max_length=20)
    passport_photo_url: str | None = Field(default=None, max_length=500)

    @field_validator("arm", "passport_photo_url", mode="before")
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class StudentUpdate(InputBase):
    """Schema for updating a student profile."""

    admission_number: str | None = Field(default=None, min_length=1, max_length=50)
    date_of_birth: date | None = None
    gender: Gender | None = None
    passport_photo_url: str | None = Field(default=None, max_length=500)
    graduation_date: date | None = None
    class_id: uuid.UUID | None = None
    arm: str | None = Field(default=None, max_length=20)
    status: AcademicStatus | None = None
    profile_status: StudentProfileStatus | None = None

    @field_validator("admission_number", "passport_photo_url", "arm", mode="before")
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class StudentSelfUpdate(InputBase):
    """Schema for a student updating their own profile fields."""

    date_of_birth: date | None = None
    gender: Gender | None = None
    passport_photo_url: str | None = Field(default=None, max_length=500)

    @field_validator("passport_photo_url", mode="before")
    @classmethod
    def clean_self_service_fields(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        return _clean_optional_string(value)


class StudentOutputBase(OutputBase):
    """Base output schema for student academic profile data."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID

    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None

    admission_number: str | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None
    passport_photo_url: str | None = None
    admission_date: date
    graduation_date: date | None = None
    class_id: uuid.UUID | None = None
    arm: str | None = None
    status: AcademicStatus
    profile_status: StudentProfileStatus

    created_at: datetime
    updated_at: datetime


class StudentResponse(StudentOutputBase):
    """Schema returned for student profile data."""

    pass


class StudentListResponse(OutputBase):
    """Paginated-style response container for student lists."""

    items: list[StudentResponse]
    total: int


# ──────────────────────────────────────────────
# STUDENT-PARENT LINK SCHEMAS
# ──────────────────────────────────────────────

class StudentParentLinkInputBase(InputBase):
    """Base input schema for linking a student to a parent."""

    student_id: uuid.UUID
    parent_id: uuid.UUID
    relationship_type: ParentRelationship = ParentRelationship.GUARDIAN
    is_primary_contact: bool = False
    receives_academic_updates: bool = True
    receives_fee_updates: bool = True


class StudentParentLinkCreate(StudentParentLinkInputBase):
    """Schema for creating a student-parent link."""

    pass


class StudentParentLinkUpdate(InputBase):
    """Schema for updating a student-parent link."""

    relationship_type: ParentRelationship | None = None
    is_primary_contact: bool | None = None
    receives_academic_updates: bool | None = None
    receives_fee_updates: bool | None = None


class StudentParentLinkOutputBase(OutputBase):
    """Base output schema for a student-parent relationship."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    student_id: uuid.UUID
    parent_id: uuid.UUID
    relationship_type: ParentRelationship
    is_primary_contact: bool
    receives_academic_updates: bool
    receives_fee_updates: bool
    created_at: datetime
    updated_at: datetime


class StudentParentLinkResponse(StudentParentLinkOutputBase):
    """Schema returned for a student-parent relationship."""

    pass


class StudentParentLinkListResponse(OutputBase):
    """Paginated-style response container for student-parent links."""

    items: list[StudentParentLinkResponse]
    total: int


# ──────────────────────────────────────────────
# STUDENT LINK CODE SCHEMAS
# ──────────────────────────────────────────────

class StudentLinkCodeInputBase(InputBase):
    """Base input schema for creating a student link code."""

    student_id: uuid.UUID
    max_use: int = Field(default=1, ge=1, le=5)


class StudentLinkCodeCreate(StudentLinkCodeInputBase):
    """Schema for generating a student link code."""

    pass


class StudentLinkCodeRedeem(InputBase):
    """Schema for a parent linking themselves to a student with a code."""

    code: str = Field(min_length=4, max_length=80)
    relationship_type: ParentRelationship = ParentRelationship.GUARDIAN
    is_primary_contact: bool = False
    receives_academic_updates: bool = True
    receives_fee_updates: bool = True

    @field_validator("code", mode="before")
    @classmethod
    def clean_code(cls, value: str) -> str:
        """Normalize a pairing code before lookup."""
        if not isinstance(value, str):
            return value
        return value.strip().upper()


class StudentLinkCodeOutputBase(OutputBase):
    """Base output schema for student link code data."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    student_id: uuid.UUID
    code: str
    expires_at: datetime
    used_at: datetime | None = None
    max_use: int
    use_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class StudentLinkCodeResponse(StudentLinkCodeOutputBase):
    """Schema returned after generating a student link code."""

    pass
