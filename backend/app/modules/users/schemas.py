#======================================#
#            users schemas.py          #
#======================================#

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.modules.users.models import UserRole, AccountStatus


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
    phone_number: str = Field(..., min_length=7, max_length=20)

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

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: UserRole) -> UserRole:
        """Validate role."""
        if value == UserRole.ADMIN:
            raise ValueError("tenant invite flow only supports normal tenant users")
        return value

    @field_validator("whatsapp_id")
    @classmethod
    def validate_invite_whatsapp_id(cls, value: str | None) -> str | None:
        """Validate invite whatsapp id."""
        if value is None:
            return value
        cleaned_value = value.replace(" ", "").replace("-", "")
        if not cleaned_value.startswith("+"):
            raise ValueError("whatsapp_id must include country code")
        if not cleaned_value[1:].isdigit():
            raise ValueError("whatsapp_id must contain only digits after country code")
        return cleaned_value


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
