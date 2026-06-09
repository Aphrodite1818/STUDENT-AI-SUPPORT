import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logging import get_logger
from app.config.security import hash_auth_secret, hash_password, verify_password
from app.config.settings import settings
from app.core.exceptions import BadRequestException, ConflictException, NotFoundException, UnauthorizedException
from app.core.utils.email import send_email
from app.core.utils.email_templates import get_tenant_invite_email_html, get_user_invite_email_html
from app.modules.auth.models import AuthPurpose, AuthRecord
from app.modules.superadmin.models import SuperAdmin, SuperAdminInvite
from app.modules.superadmin.repository import SuperAdminRepository
from app.modules.superadmin.schemas import SuperadminInviteCreate
from app.modules.users.models import AccountStatus, User, UserRole
from app.modules.users.repository import UserRepository
from app.tenant_management.models import Tenant, TenantStatus, TenantVerificationStatus
from app.tenant_management.repository import TenantRepository
from app.tenant_management.schemas import TenantCreate, TenantStatusUpdate
from app.tenant_management.service import TenantService


logger = get_logger(__name__)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class SuperadminService:
    @staticmethod
    def _build_invite_link(raw_token: str, frontend_app_url: str | None = None) -> str:
        base_url = (frontend_app_url or settings.FRONTEND_APP_URL).strip().rstrip("/")
        return f"{base_url}/invite?token={quote(raw_token, safe='')}"

    @staticmethod
    async def get_email_conflicts(
        db: AsyncSession,
        email: str,
    ) -> tuple[User | None, Tenant | None, SuperAdmin | None]:
        normalized_email = _normalize_email(email)
        existing_user = await UserRepository.get_user_by_email(db, normalized_email)
        existing_tenant = await TenantRepository.get_by_email_including_deleted(db, normalized_email)
        existing_superadmin = await SuperAdminRepository.get_by_email(db, normalized_email)
        return existing_user, existing_tenant, existing_superadmin

    @staticmethod
    async def authenticate_superadmin(
        db: AsyncSession,
        *,
        email: str,
        password: str,
    ) -> SuperAdmin | None:
        superadmin = await SuperAdminRepository.get_by_email(db, email)
        if superadmin is None:
            return None
        if not verify_password(password, superadmin.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not superadmin.is_active:
            raise UnauthorizedException("Superadmin account is not active")

        await SuperAdminRepository.touch_last_login(
            db,
            superadmin,
            at=datetime.now(timezone.utc),
        )
        await db.commit()
        return superadmin

    @staticmethod
    async def list_superadmins(
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SuperAdmin]:
        return await SuperAdminRepository.list(db, skip=skip, limit=limit)

    @staticmethod
    async def create_tenant(
        db: AsyncSession,
        payload: TenantCreate,
        background_tasks: BackgroundTasks | None = None,
        frontend_app_url: str | None = None,
    ) -> Tenant:
        normalized_email = _normalize_email(payload.email)
        existing_user, existing_tenant, existing_superadmin = await SuperadminService.get_email_conflicts(
            db,
            normalized_email,
        )

        if existing_user or existing_superadmin or existing_tenant:
            raise ConflictException("A school or account with this email already exists")

        if payload.school_bot_whatssap_number:
            number_exists = await TenantRepository.school_bot_whatssap_number_exists(
                db,
                payload.school_bot_whatssap_number,
            )
            if number_exists:
                raise ConflictException("This WhatsApp number is already in use by another school")

        slug = await TenantService._unique_slug(db, payload.school_name)
        tenant_data = payload.model_dump(mode="json", exclude={"log_slug_preview"})
        tenant_data["email"] = normalized_email

        try:
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
            await db.flush()

            raw_token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=settings.TENANT_ACTIVATION_EXPIRATION_HOURS
            )
            db.add(
                AuthRecord(
                    email=admin_user.email,
                    hashed_value=hash_auth_secret(raw_token),
                    purpose=AuthPurpose.TENANT_ACTIVATION,
                    expires_at=expires_at,
                    tenant_id=tenant.id,
                )
            )
            invite_link = SuperadminService._build_invite_link(
                raw_token,
                frontend_app_url=frontend_app_url,
            )

            await db.commit()
            await db.refresh(tenant)
        except Exception:
            await db.rollback()
            logger.exception("Superadmin tenant creation failed", extra={"email": normalized_email})
            raise

        subject = f"Activate your {tenant.school_name} administrator account"
        html_body = get_tenant_invite_email_html(tenant.school_name, invite_link)
        if background_tasks is not None:
            background_tasks.add_task(
                send_email,
                to_email=normalized_email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
        else:
            email_sent = await send_email(
                to_email=normalized_email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
            if not email_sent:
                raise BadRequestException("Unable to send activation email. Please try again.")

        return tenant

    @staticmethod
    async def list_tenants(
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = True,
    ) -> list[Tenant]:
        return await TenantRepository.get_all(
            db,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

    @staticmethod
    async def get_tenant(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        *,
        include_deleted: bool = True,
    ) -> Tenant:
        tenant = (
            await TenantRepository.get_by_id_including_deleted(db, tenant_id)
            if include_deleted
            else await TenantRepository.get_by_id(db, tenant_id)
        )
        if not tenant:
            raise NotFoundException("Tenant not found")
        return tenant

    @staticmethod
    async def update_tenant_status(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: TenantStatusUpdate,
    ) -> Tenant:
        tenant = await TenantRepository.get_by_id_including_deleted(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        if tenant.is_deleted:
            raise BadRequestException("Deleted tenants must be restored before status updates.")

        updated_tenant = await TenantRepository.update(db, tenant_id, {"status": payload.status})
        await db.commit()
        await db.refresh(updated_tenant)
        return updated_tenant

    @staticmethod
    async def restore_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await TenantRepository.get_by_id_including_deleted(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        if not tenant.is_deleted:
            raise BadRequestException("Tenant is not deleted")

        restored_tenant = await TenantRepository.restore(db, tenant_id)
        if not restored_tenant:
            raise NotFoundException("Tenant not found")

        await db.commit()
        await db.refresh(restored_tenant)
        return restored_tenant

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> dict[str, str]:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        await TenantRepository.soft_delete(db, tenant_id)
        await db.commit()
        return {"detail": "Tenant successfully deleted"}

    @staticmethod
    async def invite_superadmin(
        db: AsyncSession,
        *,
        invited_by: SuperAdmin,
        payload: SuperadminInviteCreate,
        background_tasks: BackgroundTasks | None = None,
        frontend_app_url: str | None = None,
    ) -> dict[str, str]:
        normalized_email = _normalize_email(payload.email)
        existing_user, existing_tenant, existing_superadmin = await SuperadminService.get_email_conflicts(
            db,
            normalized_email,
        )

        if existing_user or existing_tenant:
            raise ConflictException("A school or account with this email already exists")
        if existing_superadmin is not None:
            raise ConflictException("A superadmin account with this email already exists")

        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.TENANT_ACTIVATION_EXPIRATION_HOURS
        )

        try:
            await SuperAdminRepository.delete_active_invites_for_email(db, normalized_email)
            await SuperAdminRepository.create_invite(
                db,
                SuperAdminInvite(
                    email=normalized_email,
                    hashed_token=hash_auth_secret(raw_token),
                    invited_by_superadmin_id=invited_by.id,
                    expires_at=expires_at,
                    is_used=False,
                ),
            )
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Superadmin invite failed", extra={"email": normalized_email})
            raise

        invite_link = SuperadminService._build_invite_link(raw_token, frontend_app_url=frontend_app_url)
        subject = f"Set up your {settings.APP_NAME} superadmin account"
        html_body = get_user_invite_email_html(normalized_email, settings.APP_NAME, invite_link)

        if background_tasks is not None:
            background_tasks.add_task(
                send_email,
                to_email=normalized_email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
        else:
            email_sent = await send_email(
                to_email=normalized_email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
            if not email_sent:
                raise BadRequestException("Unable to send invite email. Please try again.")

        return {"detail": "Superadmin invite created and emailed successfully."}
