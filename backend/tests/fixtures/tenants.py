"""Tenant fixtures for database-backed tests."""

from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenant_management.models import (
    SubscriptionPlan,
    Tenant,
    TenantStatus,
    TenantVerificationStatus,
)


@pytest_asyncio.fixture
async def tenant(db_session: AsyncSession) -> Tenant:
    """Create a valid active tenant for tests that need one."""
    suffix = uuid4().hex[:8]
    tenant = Tenant(
        school_name=f"Test School {suffix}",
        slug=f"test-school-{suffix}",
        email=f"tenant-{suffix}@example.com",
        status=TenantStatus.ACTIVE,
        plan=SubscriptionPlan.FREE,
        verification_status=TenantVerificationStatus.ACTIVE,
        onboarding_completed=True,
        country="Nigeria",
        timezone="Africa/Lagos",
        language="en",
    )

    db_session.add(tenant)
    await db_session.flush()
    await db_session.refresh(tenant)
    return tenant
