#======================================#
#     tenant_management/service.py     #
#======================================#

"""THIS IS WHERE THE BUSINESS LOGIC FOR TENANTS LIVE"""

from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone, timedelta

from backend.app.tenant_management.repository import TenantRepository
from backend.app.tenant_management.models import Tenant, TenantStatus, TenantVerificationStatus
from backend.app.tenant_management.schemas import (
    TenantCreate,
    TenantUpdate,
    TenantStatusUpdate,
    TenantRegisterRequest
)

from backend.app.core.exceptions import (
    NotFoundException,
    ConflictException,
)

from backend.app.core.utils.validators import generate_slug
from backend.app.config.security import hash_password
from backend.app.config.logging import get_logger

from backend.app.modules.users.models import User, UserRole, AccountStatus
from backend.app.modules.auth.service import OTPService
from backend.app.modules.auth.models import OTPPurpose
from backend.app.modules.auth.schemas import RequestOTP

logger = get_logger(__name__)


class TenantService:
    @staticmethod
    async def _unique_slug(db: AsyncSession, school_name: str) -> str:
        base_slug = generate_slug(school_name)
        slug = base_slug
        counter = 1
        while await TenantRepository.slug_exists(db, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @staticmethod
    async def register_tenant(db: AsyncSession, payload: TenantRegisterRequest) -> dict:
        existing_tenant = await TenantRepository.get_by_email(db, payload.email)

        if existing_tenant is not None:
            if existing_tenant.verification_status == TenantVerificationStatus.ACTIVE:
                raise ConflictException("A school with this email already exists")

            if existing_tenant.verification_status == TenantVerificationStatus.REJECTED:
                raise ConflictException(
                    "This account has been rejected. Please contact support."
                )

            if existing_tenant.verification_status == TenantVerificationStatus.PENDING_VERIFICATION:
                await OTPService.generate_otp(
                    db,
                    RequestOTP(email=payload.email, purpose=OTPPurpose.VERIFICATION),
                )

                logger.info(
                    f"OTP resent to existing pending tenant",
                    extra={"tenant_id": str(existing_tenant.id), "email": payload.email},
                )

                return {
                    "id": existing_tenant.id,
                    "school_name": existing_tenant.school_name,
                    "slug": existing_tenant.slug,
                    "email": existing_tenant.email,
                    "status": existing_tenant.status,
                    "plan": existing_tenant.plan,
                    "timezone": existing_tenant.timezone,
                    "language": existing_tenant.language,
                    "onboarding_completed": existing_tenant.onboarding_completed,
                    "verification_status": existing_tenant.verification_status,
                    "created_at": existing_tenant.created_at,
                    "updated_at": existing_tenant.updated_at,
                    "message": "Account already exists. A verification code has been sent to your email.",
                    "can_resend_otp": False,
                }

        slug = await TenantService._unique_slug(db, payload.school_name)
        password_hashed = hash_password(payload.password)

        tenant = Tenant(
            school_name=payload.school_name,
            slug=slug,
            email=payload.email,
            verification_status=TenantVerificationStatus.PENDING_VERIFICATION,
        )

        db.add(tenant)
        await db.flush()
        logger.info(f"Tenant created: {payload.school_name}", extra={"tenant_id": str(tenant.id), "email": payload.email})

        admin_user = User(
            email=payload.email,
            password_hash=password_hashed,
            role=UserRole.ADMIN,
            account_status=AccountStatus.PENDING,
            tenant_id=tenant.id,
        )

        db.add(admin_user)
        await db.flush()
        await db.refresh(tenant)
        logger.info(
            f"Admin user created for tenant",
            extra={"tenant_id": str(tenant.id), "admin_email": payload.email, "role": "ADMIN"},
        )

        await db.commit()
        logger.info(f"Tenant registration committed", extra={"tenant_id": str(tenant.id)})

        await OTPService.generate_otp(
            db,
            RequestOTP(email=payload.email, purpose=OTPPurpose.VERIFICATION),
        )
        logger.info(
            f"OTP sent to new tenant",
            extra={"tenant_id": str(tenant.id), "email": payload.email},
        )

        return {
            "id": tenant.id,
            "school_name": tenant.school_name,
            "slug": tenant.slug,
            "email": tenant.email,
            "status": tenant.status,
            "plan": tenant.plan,
            "timezone": tenant.timezone,
            "language": tenant.language,
            "onboarding_completed": tenant.onboarding_completed,
            "verification_status": tenant.verification_status,
            "created_at": tenant.created_at,
            "updated_at": tenant.updated_at,
            "message": "Registration successful. Please check your email for the verification code.",
            "can_resend_otp": True,
        }

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        return tenant

    @staticmethod
    async def superadmin_create_tenant(db: AsyncSession, payload: TenantCreate) -> Tenant:
        if await TenantRepository.email_exists(db, payload.email):
            raise ConflictException("A school with this email already exists")

        if payload.school_bot_whatssap_number:
            if await TenantRepository.school_bot_whatssap_number_exists(db, payload.school_bot_whatssap_number):
                raise ConflictException("This WhatsApp number is already in use by another school")

        slug = await TenantService._unique_slug(db, payload.school_name)
        tenant_data = payload.model_dump()
        tenant = Tenant(**tenant_data, slug=slug)
        db.add(tenant)

        await db.commit()
        await db.refresh(tenant)
        return tenant

    @staticmethod
    async def get_all_tenants(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Tenant]:
        return await TenantRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    async def update_tenant_profile(db: AsyncSession, tenant_id: uuid.UUID, payload: TenantUpdate) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return tenant

        whatsapp = update_data.get("school_bot_whatssap_number")
        if whatsapp:
            existing = await TenantRepository.get_by_school_bot_number(db, whatsapp)
            if existing and existing.id != tenant_id:
                raise ConflictException("This WhatsApp number is already in use by another school")
        updated_tenant = await TenantRepository.update(db, tenant_id, update_data)
        await db.commit()
        return updated_tenant

    @staticmethod
    async def update_tenant_status(db: AsyncSession, tenant_id: uuid.UUID, payload: TenantStatusUpdate) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")

        updated_tenant = await TenantRepository.update(db, tenant_id, {"status": payload.status})
        await db.commit()
        return updated_tenant

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")

        await TenantRepository.soft_delete(db, tenant_id)
        await db.commit()
        return {"detail": "Tenant successfully deleted"}
