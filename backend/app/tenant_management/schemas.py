#======================================#
#     tenant_management/schemas.py     #
#======================================#

import uuid
from datetime import datetime
from typing import Any

from pydantic import(
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    computed_field,
    field_validator,
    model_validator
)

from app.tenant_management.models import SubscriptionPlan , TenantStatus, TenantVerificationStatus
from app.core.utils.validators import generate_slug



class TenantBase(BaseModel):
    school_name : str = Field(..., min_length = 3 , max_length= 255 , examples=["GreenField Academy Lagos"])
    email : EmailStr
    phone : str | None = Field(default = None , pattern=r"^\+?[1-9]\d{7,14}$",examples=["+23470123457688"])
    address: str | None = Field(default=None , max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Nigeria", max_length=100)
    logo_url: HttpUrl | None = None
    timezone: str = Field(default="Africa/Lagos", max_length=50)
    language: str = Field(default="en", max_length=10)


class TenantRegisterRequest(BaseModel):
    school_name: str = Field(..., min_length=3, max_length=255, examples=["GreenField Academy Lagos"])
    email: EmailStr
    password: str = Field(..., min_length=8, description="Admin user password")
    slug : str | None = None


class TenantCreate(TenantBase):
    school_bot_whatssap_number : str | None = Field(
        default = None,
        pattern = r"^\+?[1-9]\d{7,14}$",
        description = "The whatssap number the school bot would listen on"
    )

    plan : SubscriptionPlan = SubscriptionPlan.FREE
    max_students : int = Field(default= 500 , ge=1 , le = 100_000)
    max_teachers: int = Field(default=50 , ge=1 , le=100_000)

    @field_validator("school_name")
    @classmethod
    def prevent_blank_name(cls , v:str):
        if not v.strip():
            raise ValueError("school_name cannot be empty")
        return v.strip()
    @computed_field
    @property
    def log_slug_preview(self) -> str:
        """Return the generated slug preview without persisting it."""
        return generate_slug(self.school_name)



class TenantUpdate(BaseModel):
    school_name : str | None = Field(default = None , min_length=2 , max_length = 255)
    email : EmailStr | None = None
    phone : str | None = Field(default = None , pattern=r"^\+?[1-9]\d{7,14}$")
    address : str | None = Field(default = None , max_length=500)
    city : str | None = Field(default = None , max_length = 100)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Nigeria", max_length=100)
    logo_url: HttpUrl | None = None
    timezone: str = Field(default="Africa/Lagos", max_length=50)
    language: str = Field(default="en", max_length=10)
    school_bot_whatssap_number : str | None = Field(
        default = None,
        pattern = r"^\+?[1-9]\d{7,14}$",
        description = "The whatssap number the school bot would listen on"
    )
    onboarding_completed : bool | None = True

    plan : SubscriptionPlan | None = None
    max_students : int | None = Field(default = None , ge=1 , le = 100_000)
    max_teachers : int | None = Field(default = None , ge = 1 , le = 100_000)
    feature_flags : dict[str , Any] | None = None #dictionary of any dtype
    model_config = ConfigDict(extra ="forbid")




#dedicated schema for updating tenant status
class TenantStatusUpdate(BaseModel):
    status : TenantStatus
    reason : str | None = Field(
        default = None ,
        max_length = 500,
        description=" reason why the tenant status update is happening"
    )



class TenantPublicResponse(BaseModel):
    """Public tenant response shown to school administrators."""
    model_config = ConfigDict(from_attributes=True)
    id : uuid.UUID
    school_name : str
    slug : str
    email : EmailStr | None
    phone : str | None
    address : str | None
    city : str | None
    state : str | None
    country : str
    logo_url : str | None
    school_bot_whatssap_number : str | None
    status : TenantStatus
    plan : SubscriptionPlan
    timezone : str
    language : str
    onboarding_completed : bool
    verification_status : TenantVerificationStatus
    created_at : datetime
    updated_at : datetime


class TenantAdminResponse(TenantPublicResponse):
    """Extended tenant response for super-admin and internal views."""
    max_students : int
    max_teachers : int
    feature_flags : dict[str , Any] | None
    trial_ends_at : datetime | None
    subscription_ends_at : datetime | None
    is_deleted: bool
    deleted_at : datetime | None



class TenantContext(BaseModel):
    """Cache core tenant details to avoid repeated database lookups."""
    
    model_config = ConfigDict(from_attributes=True)

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
        if not self.feature_flags:
            return False
        return bool(self.feature_flags.get("whatsapp_bot", False))
