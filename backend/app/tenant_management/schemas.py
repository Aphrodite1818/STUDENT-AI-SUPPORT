# ====================================== #
#     tenant_management/schemas.py       #
# ====================================== #

import uuid
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    computed_field,
    field_validator,
)

from app.core.utils.validators import generate_slug
from app.tenant_management.models import (
    SubscriptionPlan,
    TenantStatus,
    TenantVerificationStatus,
)


PHONE_PATTERN = r"^\+?[1-9]\d{7,14}$"


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


# ──────────────────────────────────────────────
# SHARED VALIDATORS
# ──────────────────────────────────────────────

def _clean_optional_string(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value or None


# ──────────────────────────────────────────────
# SCHEMAS
# ──────────────────────────────────────────────

class TenantBase(InputBase):
    school_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        examples=["GreenField Academy Lagos"],
    )
    email: EmailStr
    phone: str | None = Field(
        default=None,
        pattern=PHONE_PATTERN,
        examples=["+23470123457688"],
    )
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Nigeria", max_length=100)
    logo_url: HttpUrl | None = None
    timezone: str = Field(default="Africa/Lagos", max_length=50)
    language: str = Field(default="en", max_length=10)

    @field_validator("school_name")
    @classmethod
    def validate_school_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("school_name cannot be empty")
        return value.strip()

    @field_validator(
        "phone",
        "address",
        "city",
        "state",
        "country",
        "timezone",
        "language",
        mode="before",
    )
    @classmethod
    def clean_text_fields(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class TenantRegisterRequest(InputBase):
    school_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        examples=["GreenField Academy Lagos"],
    )
    email: EmailStr
    password: str = Field(..., min_length=8, description="Admin user password")
    slug: str | None = None

    @field_validator("school_name")
    @classmethod
    def validate_school_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("school_name cannot be empty")
        return value.strip()

    @field_validator("slug", mode="before")
    @classmethod
    def clean_slug(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class TenantCreate(TenantBase):
    school_bot_whatssap_number: str | None = Field(
        default=None,
        pattern=PHONE_PATTERN,
        description="The whatssap number the school bot would listen on",
    )

    plan: SubscriptionPlan = SubscriptionPlan.FREE
    max_students: int = Field(default=500, ge=1, le=100_000)
    max_teachers: int = Field(default=50, ge=1, le=100_000)

    @field_validator("school_bot_whatssap_number", mode="before")
    @classmethod
    def clean_school_bot_whatssap_number(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)

    @computed_field
    @property
    def log_slug_preview(self) -> str:
        """Return the generated slug preview without persisting it."""
        return generate_slug(self.school_name)


class TenantUpdate(InputBase):
    school_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Nigeria", max_length=100)
    logo_url: HttpUrl | None = None
    timezone: str = Field(default="Africa/Lagos", max_length=50)
    language: str = Field(default="en", max_length=10)

    school_bot_whatssap_number: str | None = Field(
        default=None,
        pattern=PHONE_PATTERN,
        description="The whatssap number the school bot would listen on",
    )

    onboarding_completed: bool | None = True

    plan: SubscriptionPlan | None = None
    max_students: int | None = Field(default=None, ge=1, le=100_000)
    max_teachers: int | None = Field(default=None, ge=1, le=100_000)
    feature_flags: dict[str, Any] | None = None

    @field_validator(
        "school_name",
        "phone",
        "address",
        "city",
        "state",
        "country",
        "timezone",
        "language",
        "school_bot_whatssap_number",
        mode="before",
    )
    @classmethod
    def clean_text_fields(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class TenantStatusUpdate(InputBase):
    status: TenantStatus
    reason: str | None = Field(
        default=None,
        max_length=500,
        description="reason why the tenant status update is happening",
    )

    @field_validator("reason", mode="before")
    @classmethod
    def clean_reason(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class TenantPublicResponse(OutputBase):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True,
        frozen=True,
    )

    id: uuid.UUID
    school_name: str
    slug: str
    email: EmailStr | None
    phone: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str
    logo_url: str | None
    school_bot_whatssap_number: str | None
    status: TenantStatus
    plan: SubscriptionPlan
    timezone: str
    language: str
    onboarding_completed: bool
    verification_status: TenantVerificationStatus
    created_at: datetime
    updated_at: datetime


class TenantAdminResponse(TenantPublicResponse):
    max_students: int
    max_teachers: int
    feature_flags: dict[str, Any] | None
    trial_ends_at: datetime | None
    subscription_ends_at: datetime | None
    is_deleted: bool
    deleted_at: datetime | None


class TenantContext(OutputBase):
    id: uuid.UUID
    slug: str
    school_name: str
    status: TenantStatus
    plan: SubscriptionPlan
    timezone: str
    language: str
    whatsapp_number: str | None
    max_students: int
    max_teachers: int
    feature_flags: dict[str, Any] | None

    @property
    def is_active(self) -> bool:
        return self.status == TenantStatus.ACTIVE

    @property
    def whatsapp_enabled(self) -> bool:
        return bool(self.feature_flags and self.feature_flags.get("whatsapp_bot"))