#======================================#
#      tenant_management/models.py     #
#======================================#

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import  Mapped, mapped_column
from backend.app.shared.mixins import TimestampMixin, UUIDMixin
from backend.app.shared.base_model import BaseModel, Base
from typing import List




class TenantStatus(str, Enum):
    """Represents the lifecycle of the tenant subscription plan"""
    ACTIVE    = "active"
    INACTIVE  = "inactive"
    SUSPENDED = "suspended"
    TRIAL     = "trial"          # schools evaluating the product
    EXPIRED   = "expired"        # subscription lapsed


class SubscriptionPlan(str, Enum):
    """Represents the subscription plan options for a tenant (school)."""
    FREE       = "free"
    STARTER    = "starter"
    PRO        = "pro"
    ENTERPRISE = "enterprise"



class TenantVerificationStatus(str , Enum):
    """represent the lifecycle of tenant account during registration process"""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    REJECTED = "rejected"


# ── 4. Tenant Model ──────────────────────────────────────────────────────────
class Tenant(UUIDMixin, TimestampMixin, Base):
    """
    record for how tenants(schools) are onboarded, their subscription status, limits, and feature flags.
    This is the central model for tenant management. All other models that are tenant-specific will have
    a foreign key referencing this model."""

    __tablename__ = "tenants"

    school_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="URL/subdomain slug e.g. 'greenfield-lagos'. "
                "Used by tenant middleware to resolve the school.",
    )


    # Whatsapp number the school's bot listens on
    school_bot_whatssap_number: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )

    # ── Contact / location ───────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="Nigeria"
    )
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status & subscription ────────────────────────────────────────────────
    status: Mapped[TenantStatus] = mapped_column(
        SQLEnum(TenantStatus, name="tenantstatus"),
        default=TenantStatus.TRIAL,   # new schools start on trial
        nullable=False,
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        SQLEnum(SubscriptionPlan, name="subscriptionplan"),
        default=SubscriptionPlan.FREE,
        nullable=False,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    subscription_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Soft-delete ──────────────────────────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Limits / feature flags ───────────────────────────────────────────────
    max_students: Mapped[int] = mapped_column(
        Integer, default=500, nullable=False,
        comment="Hard cap on student count for this tenant's plan.",
    )
    max_teachers: Mapped[int] = mapped_column(
        Integer, default=50, nullable=False
    )
    # Flexible bag for feature flags, e.g. {"whatsapp_bot": true, "stt": true}
    feature_flags: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, default=dict
    )

    # ── Timezone / locale ────────────────────────────────────────────────────
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="Africa/Lagos"
    )
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="en"
    )

    # ── Onboarding ───────────────────────────────────────────────────────────
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    branches : Mapped[list[str] | None] = mapped_column(ARRAY(String) , nullable = True , default = None) 

    verification_status : Mapped[TenantVerificationStatus] = mapped_column(
        SQLEnum(TenantVerificationStatus, name="tenantverificationstatus"),
        nullable=False,
        default=TenantVerificationStatus.PENDING_VERIFICATION,
    )




    def __repr__(self) -> str:
        return f"<Tenant id={self.id} slug={self.slug!r} status={self.status}>"

    @property
    def is_active(self) -> bool:
        return self.status == TenantStatus.ACTIVE and not self.is_deleted

    @property
    def whatsapp_enabled(self) -> bool:
        if not self.feature_flags:
            return False
        return bool(self.feature_flags.get("whatsapp_bot", False))