#======================================#
#            users schemas.py          #
#======================================#

import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from app.modules.students.models import Gender, ParentRelationship
from app.modules.users.models import UserRole, AccountStatus
from app.tenant_management.schemas import TenantPublicResponse


# ──────────────────────────────────────────────
# SHARED BASE CONFIGS
# Define once, inherit everywhere — no repetition
# ──────────────────────────────────────────────

class InputBase(BaseModel):
    """Base for all request/input schemas."""
    model_config = ConfigDict(
        str_strip_whitespace=True,  # clean user input automatically
        str_to_lower=False,         # keep casing (names need capitals)
        extra="forbid",             # reject unknown fields in requests
    )


class OutputBase(BaseModel):
    """Base for all response/output schemas."""
    model_config = ConfigDict(
        from_attributes=True,       # read SQLAlchemy ORM objects directly
        use_enum_values=True,       # serialize enums as strings not objects
        populate_by_name=True,      # allow field name OR alias
    )


# ──────────────────────────────────────────────
# SCHEMAS
# ──────────────────────────────────────────────

class UserBase(InputBase):
    # inherits: str_strip_whitespace, extra=forbid
    """Pydantic schema for the users domain."""
    firstname: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(..., max_length=100)
    phone_number: str | None = Field(default = None, min_length=7, max_length=20)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """Validate phone number."""
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("phone_number must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("phone_number must contain only digits after country code")
        return cleaned_value


class UserCreate(UserBase):
    # inherits everything from UserBase → InputBase
    """Pydantic schema for the users domain."""
    tenant_id: uuid.UUID
    password: str = Field(..., min_length=8, max_length=64)
    role: UserRole
    whatsapp_id: str | None = Field(None, max_length=100)
    account_status: AccountStatus = AccountStatus.PENDING

    @field_validator("account_status")
    @classmethod
    def validate_account_status(cls, value: AccountStatus) -> AccountStatus:
        """Validate account status."""
        if value != AccountStatus.PENDING:
            raise ValueError("new users must be created with pending account status")
        return value

    @field_validator("whatsapp_id")
    @classmethod
    def validate_whatsapp_id(cls, value: str | None) -> str | None:
        """Validate whatsapp id."""
        if value is None:
            return value
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("whatsapp_id must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("whatsapp_id must contain only digits after country code")
        return cleaned_value


class UserInviteCreate(UserBase):
    """Pydantic schema for the users domain."""
    role: UserRole
    whatsapp_id: str | None = Field(None, max_length=100)
    parent_email: EmailStr | None = Field(default=None)
    parent_firstname: str | None = Field(default=None, min_length=2, max_length=100)
    parent_lastname: str | None = Field(default=None, min_length=2, max_length=100)
    parent_phone_number: str | None = Field(default=None, min_length=7, max_length=20)
    parent_whatsapp_id: str | None = Field(default=None, max_length=100)
    parent_relationship_type: ParentRelationship = ParentRelationship.GUARDIAN

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: UserRole) -> UserRole:
        """Validate role."""
        if value == UserRole.ADMIN:
            raise ValueError("tenant invite flow only supports normal tenant users")
        return value

    @field_validator("whatsapp_id", "parent_phone_number", "parent_whatsapp_id")
    @classmethod
    def validate_invite_whatsapp_id(cls, value: str | None) -> str | None:
        """Validate invite contact number."""
        if value is None:
            return value
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("contact number must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("contact number must contain only digits after country code")
        return cleaned_value

    @model_validator(mode="after")
    def validate_student_parent_link_fields(self) -> "UserInviteCreate":
        """Validate student invite parent-link fields."""
        parent_fields = (
            self.parent_email,
            self.parent_firstname,
            self.parent_lastname,
            self.parent_phone_number,
            self.parent_whatsapp_id,
        )

        if self.role == UserRole.STUDENT and not self.parent_email:
            raise ValueError("parent_email is required when inviting a student")

        if self.role != UserRole.STUDENT and any(parent_fields):
            raise ValueError(
                "parent link fields are only supported when inviting a student"
            )

        return self


class UserUpdate(InputBase):
    # inherits: str_strip_whitespace, extra=forbid
    # frozen=False intentionally — this is a mutable update schema
    """Pydantic schema for the users domain."""
    firstname: str | None = Field(None, min_length=2, max_length=100)
    lastname: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(None, min_length=7, max_length=20)
    whatsapp_id: str | None = Field(None, max_length=100)

    @field_validator("phone_number", "whatsapp_id")
    @classmethod
    def validate_contact_number(cls, value: str | None) -> str | None:
        """Validate contact number."""
        if value is None:
            return value
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("contact number must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("contact number must contain only digits after country code")
        return cleaned_value


class UserAdminUpdate(InputBase):
    # extra=forbid is critical here — admin endpoint must not accept
    # arbitrary fields. Only role and account_status are permitted.
    """Pydantic schema for the users domain."""
    role: UserRole | None = None
    account_status: AccountStatus | None = None


class ProfileCompletionUserDetails(InputBase):
    """Shared user fields required during profile completion."""

    firstname: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=7, max_length=20)
    whatsapp_id: str | None = Field(default=None, max_length=100)

    @field_validator("phone_number", "whatsapp_id")
    @classmethod
    def validate_profile_completion_contact_number(
        cls,
        value: str | None,
    ) -> str | None:
        """Validate contact numbers used by the onboarding flow."""
        if value is None:
            return value
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("contact number must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("contact number must contain only digits after country code")
        return cleaned_value


class ParentProfileCompletionDetails(InputBase):
    """Parent-specific fields used by the onboarding modal."""

    occupation: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    emergency_phone: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator("occupation", "address", "emergency_phone", mode="before")
    @classmethod
    def clean_parent_profile_completion_fields(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize parent profile completion text fields."""
        if value is None:
            return None
        cleaned_value = value.strip()
        return cleaned_value or None


class StudentProfileCompletionDetails(InputBase):
    """Student-specific fields used by the onboarding modal."""

    date_of_birth: date
    gender: Gender
    passport_photo_url: str | None = Field(default=None, max_length=500)

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def normalize_student_date_of_birth(
        cls,
        value: Any,
    ) -> Any:
        """Accept ISO date inputs without silently coercing blank strings."""
        if value == "":
            return None
        return value

    @field_validator("passport_photo_url", mode="before")
    @classmethod
    def clean_student_profile_completion_photo(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize optional passport photo url."""
        if value is None:
            return None
        cleaned_value = value.strip()
        return cleaned_value or None


class TeacherProfileCompletionDetails(InputBase):
    """Teacher-specific fields used by the onboarding modal."""

    staff_id: str | None = Field(default=None, max_length=50)
    qualification: str | None = Field(default=None, max_length=100)
    specialization: str | None = Field(default=None, max_length=150)

    @field_validator("staff_id", "qualification", "specialization", mode="before")
    @classmethod
    def clean_teacher_profile_completion_fields(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize teacher profile completion text fields."""
        if value is None:
            return None
        cleaned_value = value.strip()
        return cleaned_value or None


class AdminProfileCompletionTenantDetails(InputBase):
    """Administrator tenant fields used by the onboarding modal."""

    school_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    admission_number_prefix: str = Field(..., min_length=2, max_length=20)

    @field_validator(
        "school_name",
        "phone",
        "address",
        "city",
        "state",
        "country",
        "admission_number_prefix",
        mode="before",
    )
    @classmethod
    def clean_admin_profile_completion_fields(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize admin profile completion tenant fields."""
        if value is None:
            return None
        cleaned_value = value.strip()
        return cleaned_value or None

    @field_validator("phone")
    @classmethod
    def validate_admin_profile_completion_phone(
        cls,
        value: str | None,
    ) -> str | None:
        """Validate school contact phone."""
        if value is None:
            return None
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("phone must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("phone must contain only digits after country code")
        return cleaned_value

    @field_validator("admission_number_prefix")
    @classmethod
    def normalize_admin_profile_completion_prefix(
        cls,
        value: str,
    ) -> str:
        """Uppercase the admission number prefix."""
        return value.upper()


class ParentProfileCompletionSchema(InputBase):
    """Dedicated onboarding schema for parent users."""

    user: ProfileCompletionUserDetails
    role_profile: ParentProfileCompletionDetails


class StudentProfileCompletionSchema(InputBase):
    """Dedicated onboarding schema for student users."""

    user: ProfileCompletionUserDetails
    role_profile: StudentProfileCompletionDetails


class TeacherProfileCompletionSchema(InputBase):
    """Dedicated onboarding schema for teacher users."""

    user: ProfileCompletionUserDetails
    role_profile: TeacherProfileCompletionDetails


class AdminProfileCompletionSchema(InputBase):
    """Dedicated onboarding schema for admin users."""

    user: ProfileCompletionUserDetails
    tenant: AdminProfileCompletionTenantDetails


class ProfileCompletionFieldOption(OutputBase):
    """Single select option for dynamic onboarding fields."""

    value: str
    label: str


class ProfileCompletionFieldMetadata(OutputBase):
    """Frontend-facing field metadata for the onboarding modal."""

    source: Literal["user", "tenant", "role_profile"]
    name: str
    label: str
    required: bool = False
    type: str = "text"
    read_only: bool = False
    placeholder: str | None = None
    helper_text: str | None = None
    empty_label: str | None = None
    options: list[ProfileCompletionFieldOption] = Field(default_factory=list)


class ProfileCompletionSectionMetadata(OutputBase):
    """Group related onboarding fields for the frontend modal."""

    key: str
    title: str
    description: str | None = None
    fields: list[ProfileCompletionFieldMetadata]


class ProfileCompletionValues(OutputBase):
    """Current values grouped by source for the onboarding modal."""

    user: dict[str, Any]
    tenant: dict[str, Any] | None = None
    role_profile: dict[str, Any] | None = None


class UserResponse(OutputBase):
    # inherits: from_attributes, use_enum_values, populate_by_name
    # frozen=True — response objects should never be mutated after creation
    """Pydantic schema for the users domain."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True,
        frozen=True,            # response schemas are read-only by nature
    )

    id: uuid.UUID
    tenant_id: uuid.UUID
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime
    role: UserRole
    account_status: AccountStatus
    whatsapp_id: str | None = None
    profile_completed: bool = False


class AuthenticatedUserResponse(UserResponse):
    """Authenticated user payload enriched with tenant context."""

    tenant: TenantPublicResponse | None = None


class ProfileCompletionSchemaResponse(OutputBase):
    """Role-aware onboarding schema plus current values."""

    role: UserRole
    profile_completed: bool
    user: AuthenticatedUserResponse
    sections: list[ProfileCompletionSectionMetadata]
    values: ProfileCompletionValues


class UserPublicResponse(OutputBase):
    # frozen=True same reason as UserResponse
    # extra=forbid not needed here — this is output not input
    """Pydantic schema for the users domain."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        frozen=True,
    )

    id: uuid.UUID
    firstname: str
    lastname: str
    role: UserRole
    account_status: AccountStatus
