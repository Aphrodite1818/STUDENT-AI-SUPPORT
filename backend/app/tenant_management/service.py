#======================================#
#     tenant_management/service.py     #
#======================================#

"""Implement the tenant management service layer."""

import uuid
import secrets

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenant_management.repository import TenantRepository
from app.tenant_management.models import Tenant, TenantStatus, TenantVerificationStatus
from app.tenant_management.schemas import (
    TenantCreate,
    TenantUpdate,
    TenantStatusUpdate,
    TenantRegisterRequest
)

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
)

from app.core.utils.validators import generate_slug
from app.config.security import hash_password, verify_password
from app.config.logging import get_logger

from app.modules.users.models import User, UserRole, AccountStatus
from app.modules.users.repository import UserRepository
from app.modules.auth.service import OTPService, TenantActivationService
from app.modules.auth.models import AuthPurpose
from app.modules.auth.schemas import RequestOTP

logger = get_logger(__name__)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class TenantService:
    @staticmethod
    def _email_belongs_to_verified_account(
        user: User | None,
        tenant: Tenant | None,
    ) -> bool:
        if user is not None and user.account_status != AccountStatus.PENDING:
            return True
        return (
            tenant is not None
            and tenant.verification_status in (
                TenantVerificationStatus.ACTIVE,
                TenantVerificationStatus.REJECTED,
            )
        )

    @staticmethod
    def _email_belongs_to_unverified_account(
        user: User | None,
        tenant: Tenant | None,
    ) -> bool:
        if user is not None and user.account_status == AccountStatus.PENDING:
            return True
        return (
            tenant is not None
            and tenant.verification_status == TenantVerificationStatus.PENDING_VERIFICATION
        )

    @staticmethod
    def _matches_existing_unverified_registration(
        payload: TenantRegisterRequest,
        user: User | None,
        tenant: Tenant | None,
    ) -> bool:
        if user is None or tenant is None:
            return False

        return (
            tenant.school_name.strip().casefold() == payload.school_name.strip().casefold()
            and verify_password(payload.password, user.password_hash)
        )

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
    async def _unique_slug_for_tenant(
        db: AsyncSession,
        school_name: str,
        tenant_id: uuid.UUID,
    ) -> str:
        """Generate a unique slug while allowing the current tenant to keep its own slug."""
        base_slug = generate_slug(school_name)
        slug = base_slug
        counter = 1

        while True:
            existing_tenant = await TenantRepository.get_by_slug(db, slug)
            if existing_tenant is None or existing_tenant.id == tenant_id:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    @staticmethod
    async def register_tenant(
        db: AsyncSession,
        payload: TenantRegisterRequest,
        background_tasks: BackgroundTasks | None = None,
    ) -> dict:
        school_name = payload.school_name.strip()
        normalized_email = _normalize_email(payload.email)
        tenant: Tenant | None = None
        reused_pending_account = False

        async with db.begin():
            existing_tenant_by_name = await TenantRepository.get_by_school_name(
                db,
                school_name,
            )
            existing_user = await UserRepository.get_user_by_email(db, normalized_email)
            existing_tenant_by_email = await TenantRepository.get_by_email_including_deleted(
                db,
                normalized_email,
            )

            if (
                existing_tenant_by_name is not None
                and existing_tenant_by_email is not None
                and existing_tenant_by_name.id != existing_tenant_by_email.id
            ):
                raise ConflictException("A school with this name already exists")

            if existing_tenant_by_name is not None and existing_tenant_by_email is None:
                raise ConflictException("A school with this name already exists")

            if existing_tenant_by_email is not None and existing_tenant_by_email.is_deleted:
                raise ConflictException("A school or admin account with this email already exists")

            if TenantService._email_belongs_to_verified_account(
                existing_user,
                existing_tenant_by_email,
            ):
                raise ConflictException("A verified account with this email already exists")

            if TenantService._email_belongs_to_unverified_account(
                existing_user,
                existing_tenant_by_email,
            ):
                if not TenantService._matches_existing_unverified_registration(
                    payload,
                    existing_user,
                    existing_tenant_by_email,
                ):
                    raise ConflictException(
                        "An unverified account with this email already exists. "
                        "Please complete verification with the original registration details."
                    )

                logger.info(
                    "Tenant registration skipped for existing unverified account",
                    extra={"email": normalized_email},
                )
                tenant = existing_tenant_by_email
                reused_pending_account = True
            else:
                slug = await TenantService._unique_slug(db, school_name)
                password_hashed = hash_password(payload.password)

                tenant = Tenant(
                    school_name=school_name,
                    slug=slug,
                    email=normalized_email,
                    verification_status=TenantVerificationStatus.PENDING_VERIFICATION,
                )
                await TenantRepository.create(db, tenant)

                logger.info(
                    "Tenant created during registration",
                    extra={"tenant_id": str(tenant.id), "email": normalized_email},
                )

                admin_user = User(
                    email=normalized_email,
                    password_hash=password_hashed,
                    role=UserRole.ADMIN,
                    account_status=AccountStatus.PENDING,
                    tenant_id=tenant.id,
                    is_verified=False,
                )
                await UserRepository.create_user(db, admin_user)

                logger.info(
                    "Admin user created for tenant registration",
                    extra={
                        "tenant_id": str(tenant.id),
                        "admin_email": normalized_email,
                        "role": UserRole.ADMIN.value,
                    },
                )

        if tenant is None:
            raise ConflictException("Tenant registration could not be completed")

        await OTPService.generate_otp(
            db,
            RequestOTP(email=normalized_email, purpose=AuthPurpose.VERIFICATION),
            background_tasks=background_tasks,
        )
        await db.refresh(tenant)

        if reused_pending_account:
            logger.info(
                "OTP resent for existing unverified tenant registration",
                extra={"tenant_id": str(tenant.id), "email": normalized_email},
            )
            return {
                "created": False,
                "email": tenant.email,
                "message": (
                    "Your account is not verified yet. "
                    "We sent a new verification code to your email."
                ),
            }

        logger.info(
            "OTP sent to newly registered tenant admin",
            extra={"tenant_id": str(tenant.id), "email": normalized_email},
        )

        return {
            "created": True,
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
        }

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        return tenant

    @staticmethod
    async def superadmin_create_tenant(
        db: AsyncSession,
        payload: TenantCreate,
        background_tasks: BackgroundTasks | None = None,
        frontend_app_url: str | None = None,
    ) -> Tenant:
        normalized_email = _normalize_email(payload.email)
        existing_user = await UserRepository.get_user_by_email(db, normalized_email)
        existing_tenant = await TenantRepository.get_by_email_including_deleted(
            db,
            normalized_email,
        )
        if existing_user is not None or existing_tenant is not None:
            raise ConflictException("A school or admin account with this email already exists")

        if payload.school_bot_whatssap_number:
            if await TenantRepository.school_bot_whatssap_number_exists(db, payload.school_bot_whatssap_number):
                raise ConflictException("This WhatsApp number is already in use by another school")

        slug = await TenantService._unique_slug(db, payload.school_name)
        tenant_data = payload.model_dump(
            mode="json",
            exclude={"log_slug_preview"},
        )
        tenant_data["email"] = normalized_email

        tenant = Tenant(
            **tenant_data,
            slug=slug,
            status=TenantStatus.INACTIVE,
            verification_status=TenantVerificationStatus.PENDING_VERIFICATION,
        )
        db.add(tenant)
        await db.flush()

        admin_user = User(
            email=normalized_email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            role=UserRole.ADMIN,
            account_status=AccountStatus.PENDING,
            tenant_id=tenant.id,
            is_verified=False,
        )
        await UserRepository.create_user(db, admin_user)

        invite_link = await TenantActivationService.create_activation_record(
            db,
            tenant=tenant,
            admin_user=admin_user,
            frontend_app_url=frontend_app_url,
        )
        await db.commit()

        await db.refresh(tenant)
        await TenantActivationService.send_activation_email(
            email=normalized_email,
            school_name=tenant.school_name,
            invite_link=invite_link,
            background_tasks=background_tasks,
        )
        return tenant

    @staticmethod
    async def get_all_tenants(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Tenant]:
        return await TenantRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    async def update_tenant_profile(db: AsyncSession, tenant_id: uuid.UUID, payload: TenantUpdate) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")

        update_data = payload.model_dump(mode="json", exclude_unset=True)
        if not update_data:
            return tenant

        school_name = update_data.get("school_name")
        if school_name is not None:
            normalized_school_name = school_name.strip()
            if not normalized_school_name:
                raise BadRequestException("school_name cannot be empty")

            existing_tenant = await TenantRepository.get_by_school_name(
                db,
                normalized_school_name,
            )
            if existing_tenant and existing_tenant.id != tenant_id:
                raise ConflictException("A school with this name already exists")

            update_data["school_name"] = normalized_school_name

            if normalized_school_name.casefold() != tenant.school_name.strip().casefold():
                update_data["slug"] = await TenantService._unique_slug_for_tenant(
                    db,
                    normalized_school_name,
                    tenant_id,
                )

        email = update_data.get("email")
        if email is not None:
            normalized_email = _normalize_email(email)
            if normalized_email != _normalize_email(tenant.email):
                raise BadRequestException(
                    "Tenant email cannot be changed from this endpoint because it is tied to administrator onboarding."
                )
            update_data["email"] = normalized_email

        whatsapp = update_data.get("school_bot_whatssap_number")
        if whatsapp:
            existing = await TenantRepository.get_by_school_bot_number(db, whatsapp)
            if existing and existing.id != tenant_id:
                raise ConflictException("This WhatsApp number is already in use by another school")
        updated_tenant = await TenantRepository.update(db, tenant_id, update_data)
        await db.commit()
        await db.refresh(updated_tenant)
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

    @staticmethod
    async def restore_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await TenantRepository.get_by_id_including_deleted(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        if not tenant.is_deleted:
            raise BadRequestException("Tenant is not deleted")

        restored_tenant = await TenantRepository.restore(db, tenant_id)
        await db.commit()
        if not restored_tenant:
            raise NotFoundException("Tenant not found")
        await db.refresh(restored_tenant)
        return restored_tenant

