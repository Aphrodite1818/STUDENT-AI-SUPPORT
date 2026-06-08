#======================================#
#            auth/service.py           #
#======================================#

import random
import secrets
import string
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

from fastapi import BackgroundTasks
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.security import (
    hash_auth_secret,
    hash_otp,
    hash_password,
    verify_otp as verify_otp_hash,
    verify_password,
)
from app.core.exceptions import (
    AccountNotVerifiedException,
    BadRequestException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)
from app.core.utils.email import send_email
from app.core.utils.email_templates import (
    get_otp_email_html,
    get_tenant_invite_email_html,
    get_user_invite_email_html,
)
from app.config.settings import settings
from app.modules.auth.models import AuthPurpose, AuthRecord
from app.modules.auth.schemas import (
    LoginRequest,
    RequestOTP,
    TenantActivationRequest,
    UserInviteAcceptanceRequest,
    UpdatePassword,
    VerifyOTP,
)
from app.modules.users.models import AccountStatus, User, UserRole
from app.modules.users.repository import UserRepository
from app.tenant_management.models import Tenant, TenantStatus, TenantVerificationStatus
from app.tenant_management.repository import TenantRepository
from app.core.utils.otp_rate_limiter import OTPRateLimiter


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _tenant_allows_login(tenant: Tenant | None) -> bool:
    return (
        tenant is not None
        and not tenant.is_deleted
        and tenant.verification_status == TenantVerificationStatus.ACTIVE
        and tenant.status in (TenantStatus.ACTIVE, TenantStatus.TRIAL)
    )


def _tenant_allows_user_invite_completion(tenant: Tenant | None) -> bool:
    return _tenant_allows_login(tenant)


def _tenant_allows_activation_completion(tenant: Tenant | None) -> bool:
    return (
        tenant is not None
        and not tenant.is_deleted
        and tenant.verification_status == TenantVerificationStatus.PENDING_VERIFICATION
        and tenant.status == TenantStatus.INACTIVE
    )


def _tenant_allows_otp_verification(tenant: Tenant | None) -> bool:
    return (
        tenant is not None
        and not tenant.is_deleted
        and tenant.verification_status == TenantVerificationStatus.PENDING_VERIFICATION
        and tenant.status in (TenantStatus.ACTIVE, TenantStatus.TRIAL)
    )


def _user_can_reset_password(user: User | None, tenant: Tenant | None) -> bool:
    return (
        user is not None
        and user.account_status == AccountStatus.ACTIVE
        and user.is_verified
        and _tenant_allows_login(tenant)
    )


class AuthService:
    @staticmethod
    def _otp_verification_headers(email: str) -> dict[str, str]:
        return {
            "X-Resend-OTP-Available": "true",
            "X-Email": email,
        }

    @staticmethod
    async def authenticate_user(db: AsyncSession, payload: LoginRequest) -> User:
        user = await UserRepository.get_user_by_email(db, payload.email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if user.role == UserRole.SUPERADMIN:
            if user.account_status != AccountStatus.ACTIVE:
                raise UnauthorizedException("Account is not active")
            return user

        tenant = await TenantRepository.get_by_id(db, user.tenant_id)
        if tenant is None:
            raise UnauthorizedException("Account not found")

        if tenant.verification_status == TenantVerificationStatus.PENDING_VERIFICATION:
            if tenant.status == TenantStatus.INACTIVE:
                raise AccountNotVerifiedException(
                    detail="Account not activated. Please use the activation link sent to your email.",
                )
            raise AccountNotVerifiedException(
                detail="Account not verified. Please check your email for the verification code.",
                headers=AuthService._otp_verification_headers(payload.email),
            )

        if tenant.verification_status == TenantVerificationStatus.REJECTED:
            raise UnauthorizedException("Account has been rejected. Please contact support.")

        if tenant.is_deleted or tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
            raise UnauthorizedException("Account is not active")

        if user.account_status != AccountStatus.ACTIVE:
            if user.account_status == AccountStatus.PENDING:
                if user.role == UserRole.ADMIN and tenant.email.strip().lower() == user.email.strip().lower():
                    raise AccountNotVerifiedException(
                        detail="Account not verified. Please check your email for the verification code.",
                        headers=AuthService._otp_verification_headers(payload.email),
                    )
                raise AccountNotVerifiedException(
                    detail=(
                        "Your account setup is not complete yet. "
                        "Please use the invite link sent to your email or request a new invite from your school admin."
                    ),
                )
            raise UnauthorizedException("Account is not active")

        return user

    @staticmethod
    async def reset_password(db: AsyncSession, payload: UpdatePassword) -> None:
        normalized_email = _normalize_email(payload.email)
        hashed_token = hash_auth_secret(payload.reset_token)
        now = datetime.now(timezone.utc)

        token_result = await db.execute(
            select(AuthRecord).where(
                func.lower(AuthRecord.email) == normalized_email,
                AuthRecord.purpose == AuthPurpose.PASSWORD_RESET,
                AuthRecord.hashed_value == hashed_token,
                AuthRecord.is_used == False,
            ).with_for_update()
        )
        reset_record = token_result.scalar_one_or_none()

        if reset_record is None:
            raise UnauthorizedException("Invalid or expired reset token")

        if reset_record.expires_at.replace(tzinfo=timezone.utc) < now:
            await db.delete(reset_record)
            await db.commit()
            raise UnauthorizedException("Invalid or expired reset token")

        user_result = await db.execute(
            select(User).where(func.lower(User.email) == normalized_email).with_for_update()
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User email does not exist")

        tenant = await TenantRepository.get_by_id(db, user.tenant_id)
        if not _user_can_reset_password(user, tenant):
            raise UnauthorizedException("Password reset is not available for this account")

        hashed_pw = hash_password(payload.new_password)

        user.password_hash = hashed_pw
        await db.delete(reset_record)
        await db.commit()


class TenantActivationService:
    @staticmethod
    def _build_invite_link(
        raw_token: str,
        frontend_app_url: str | None = None,
    ) -> str:
        base_url = (frontend_app_url or settings.FRONTEND_APP_URL).strip().rstrip("/")
        return f"{base_url}/invite?token={quote(raw_token, safe='')}"

    @staticmethod
    async def create_activation_record(
        db: AsyncSession,
        *,
        tenant: Tenant,
        admin_user: User,
        frontend_app_url: str | None = None,
    ) -> str:
        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.TENANT_ACTIVATION_EXPIRATION_HOURS
        )

        await db.execute(
            delete(AuthRecord).where(
                func.lower(AuthRecord.email) == _normalize_email(admin_user.email),
                AuthRecord.purpose == AuthPurpose.TENANT_ACTIVATION,
            )
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
        await db.flush()

        return TenantActivationService._build_invite_link(
            raw_token,
            frontend_app_url=frontend_app_url,
        )

    @staticmethod
    async def send_activation_email(
        *,
        email: str,
        school_name: str,
        invite_link: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        subject = f"Activate your {school_name} administrator account"
        html_body = get_tenant_invite_email_html(school_name, invite_link)

        if background_tasks is not None:
            background_tasks.add_task(
                send_email,
                to_email=email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
            return

        email_sent = await send_email(
            to_email=email,
            subject=subject,
            body=html_body,
            is_html=True,
        )
        if not email_sent:
            raise BadRequestException(
                "Unable to send activation email. Please try again."
            )

    @staticmethod
    async def activate_tenant(
        db: AsyncSession,
        payload: TenantActivationRequest,
    ) -> dict[str, str]:
        hashed_token = hash_auth_secret(payload.token)
        now = datetime.now(timezone.utc)

        record_result = await db.execute(
            select(AuthRecord).where(
                AuthRecord.hashed_value == hashed_token,
                AuthRecord.purpose == AuthPurpose.TENANT_ACTIVATION,
                AuthRecord.is_used == False,
            ).with_for_update()
        )
        activation_record = record_result.scalar_one_or_none()

        if activation_record is None:
            raise BadRequestException("Invalid or expired activation link.")

        if activation_record.expires_at.replace(tzinfo=timezone.utc) < now:
            await db.delete(activation_record)
            await db.commit()
            raise BadRequestException("Invalid or expired activation link.")

        normalized_email = payload.email.strip().lower()
        if activation_record.email.strip().lower() != normalized_email:
            await db.rollback()
            raise BadRequestException(
                "Activation link does not match this email address."
            )

        user_result = await db.execute(
            select(User).where(
                func.lower(User.email) == _normalize_email(activation_record.email)
            ).with_for_update()
        )
        user = user_result.scalar_one_or_none()

        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == activation_record.tenant_id).with_for_update()
        )
        tenant = tenant_result.scalar_one_or_none()

        if user is None or tenant is None:
            await db.delete(activation_record)
            await db.commit()
            raise BadRequestException("Activation link is no longer valid.")

        if user.tenant_id != tenant.id or user.role != UserRole.ADMIN:
            await db.delete(activation_record)
            await db.commit()
            raise BadRequestException("Activation link is no longer valid.")

        if not _tenant_allows_activation_completion(tenant):
            await db.rollback()
            raise BadRequestException("Activation link is no longer valid.")

        user.password_hash = hash_password(payload.password)
        user.account_status = AccountStatus.ACTIVE
        user.is_verified = True

        tenant.verification_status = TenantVerificationStatus.ACTIVE
        if tenant.status == TenantStatus.INACTIVE:
            tenant.status = TenantStatus.TRIAL

        await db.delete(activation_record)
        await db.commit()

        return {"detail": "Account activated successfully. You may now log in."}


class UserInviteService:
    @staticmethod
    def _build_invite_link(
        raw_token: str,
        frontend_app_url: str | None = None,
    ) -> str:
        base_url = (frontend_app_url or settings.FRONTEND_APP_URL).strip().rstrip("/")
        return f"{base_url}/invite?token={quote(raw_token, safe='')}"

    @staticmethod
    async def create_invite_record(
        db: AsyncSession,
        *,
        user: User,
        frontend_app_url: str | None = None,
    ) -> str:
        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.TENANT_ACTIVATION_EXPIRATION_HOURS
        )

        await db.execute(
            delete(AuthRecord).where(
                func.lower(AuthRecord.email) == _normalize_email(user.email),
                AuthRecord.purpose == AuthPurpose.USER_INVITE,
                AuthRecord.is_used == False,
            )
        )

        db.add(
            AuthRecord(
                email=user.email,
                hashed_value=hash_auth_secret(raw_token),
                purpose=AuthPurpose.USER_INVITE,
                expires_at=expires_at,
                tenant_id=user.tenant_id,
            )
        )
        await db.flush()

        return UserInviteService._build_invite_link(
            raw_token,
            frontend_app_url=frontend_app_url,
        )

    @staticmethod
    async def send_invite_email(
        *,
        email: str,
        user_name: str,
        school_name: str,
        invite_link: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        subject = f"Set up your {school_name} account"
        html_body = get_user_invite_email_html(user_name, school_name, invite_link)

        if background_tasks is not None:
            background_tasks.add_task(
                send_email,
                to_email=email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
            return

        email_sent = await send_email(
            to_email=email,
            subject=subject,
            body=html_body,
            is_html=True,
        )
        if not email_sent:
            raise BadRequestException(
                "Unable to send invite email. Please try again."
            )

    @staticmethod
    async def get_invite_status(
        db: AsyncSession,
        token: str,
    ) -> dict[str, str | None]:
        hashed_token = hash_auth_secret(token)
        now = datetime.now(timezone.utc)

        result = await db.execute(
            select(AuthRecord).where(
                AuthRecord.hashed_value == hashed_token,
                AuthRecord.purpose.in_(
                    (AuthPurpose.TENANT_ACTIVATION, AuthPurpose.USER_INVITE)
                ),
            ).order_by(AuthRecord.created_at.desc())
        )
        record = result.scalars().first()

        if record is None:
            return {"status": "invalid", "purpose": None}

        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == record.tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()

        if record.purpose == AuthPurpose.USER_INVITE and not _tenant_allows_user_invite_completion(tenant):
            return {"status": "invalid", "purpose": None}

        if record.purpose == AuthPurpose.TENANT_ACTIVATION and not _tenant_allows_activation_completion(tenant):
            return {"status": "invalid", "purpose": None}

        if record.is_used:
            return {"status": "used", "purpose": record.purpose.value}

        if record.expires_at.replace(tzinfo=timezone.utc) < now:
            return {"status": "expired", "purpose": record.purpose.value}

        return {"status": "valid", "purpose": record.purpose.value}

    @staticmethod
    async def accept_invite(
        db: AsyncSession,
        payload: UserInviteAcceptanceRequest,
    ) -> dict[str, str]:
        hashed_token = hash_auth_secret(payload.token)
        now = datetime.now(timezone.utc)

        invite_result = await db.execute(
            select(AuthRecord).where(
                AuthRecord.hashed_value == hashed_token,
                AuthRecord.purpose == AuthPurpose.USER_INVITE,
            ).with_for_update()
        )
        invite_record = invite_result.scalar_one_or_none()

        if invite_record is None:
            raise BadRequestException(
                "This invite link is invalid or has expired. Please request a new invite from your school admin."
            )

        if invite_record.is_used:
            raise BadRequestException(
                "This invite link has already been used. Please log in instead."
            )

        if invite_record.expires_at.replace(tzinfo=timezone.utc) < now:
            raise BadRequestException(
                "This invite link has expired. Please request a new invite from your school admin."
            )

        normalized_email = payload.email.strip().lower()
        if invite_record.email.strip().lower() != normalized_email:
            raise BadRequestException(
                "Invite link does not match this email address."
            )

        user_result = await db.execute(
            select(User).where(
                func.lower(User.email) == _normalize_email(invite_record.email)
            ).with_for_update()
        )
        user = user_result.scalar_one_or_none()

        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == invite_record.tenant_id).with_for_update()
        )
        tenant = tenant_result.scalar_one_or_none()

        if user is None or tenant is None or user.tenant_id != tenant.id:
            raise BadRequestException(
                "This invite link is invalid or has expired. Please request a new invite from your school admin."
            )

        if not _tenant_allows_user_invite_completion(tenant):
            raise BadRequestException(
                "This invite link is invalid or has expired. Please request a new invite from your school admin."
            )

        if user.role in (UserRole.ADMIN, UserRole.SUPERADMIN):
            raise BadRequestException("This invite link is not valid for administrator setup.")

        if user.account_status != AccountStatus.PENDING or user.is_verified:
            invite_record.is_used = True
            await db.commit()
            raise BadRequestException(
                "This invite link has already been used. Please log in instead."
            )

        user.password_hash = hash_password(payload.password)
        user.account_status = AccountStatus.ACTIVE
        user.is_verified = True
        invite_record.is_used = True

        await db.execute(
            delete(AuthRecord).where(
                func.lower(AuthRecord.email) == _normalize_email(user.email),
                AuthRecord.purpose == AuthPurpose.USER_INVITE,
                AuthRecord.id != invite_record.id,
                AuthRecord.is_used == False,
            )
        )
        await db.commit()

        return {"detail": "Account setup completed successfully. You may now log in."}


class OTPService:
    @staticmethod
    async def _replace_otp_record(
        db: AsyncSession,
        payload: RequestOTP,
        otp_code: str,
        expires_at: datetime,
    ) -> User:
        normalized_email = _normalize_email(payload.email)
        result = await db.execute(
            select(User).where(func.lower(User.email) == normalized_email).with_for_update()
        )
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User with this email not found.")

        await db.execute(
            delete(AuthRecord).where(
                func.lower(AuthRecord.email) == normalized_email,
                AuthRecord.purpose == payload.purpose,
            )
        )

        db.add(
            AuthRecord(
                email=user.email,
                hashed_value=hash_otp(otp_code),
                purpose=payload.purpose,
                expires_at=expires_at,
                tenant_id=user.tenant_id,
            )
        )
        await db.flush()
        return user

    @staticmethod
    async def generate_otp(
        db: AsyncSession,
        payload: RequestOTP,
        background_tasks: BackgroundTasks | None = None,
        *,
        commit: bool = True,
    ) -> None:
        existing_user = await UserRepository.get_user_by_email(db, payload.email)
        if not existing_user:
            raise NotFoundException("User with this email not found.")

        tenant = await TenantRepository.get_by_id(db, existing_user.tenant_id)
        if tenant is None:
            raise NotFoundException("Tenant not found.")

        if payload.purpose == AuthPurpose.VERIFICATION:
            is_public_tenant_admin = (
                existing_user.role == UserRole.ADMIN
                and tenant.email.strip().lower() == existing_user.email.strip().lower()
            )
            if not is_public_tenant_admin:
                raise BadRequestException(
                    "OTP verification is only available for public tenant signup accounts."
                )
            if tenant.status == TenantStatus.INACTIVE:
                raise BadRequestException(
                    "Account activation must be completed from the invite link sent to your email."
                )
            if not _tenant_allows_otp_verification(tenant):
                raise BadRequestException(
                    "OTP verification is not available for this account."
                )

        if payload.purpose == AuthPurpose.PASSWORD_RESET:
            if not _user_can_reset_password(existing_user, tenant):
                raise BadRequestException(
                    "Password reset is not available for this account."
                )

        rate_limiter = OTPRateLimiter()
        allowed, retry_after = rate_limiter.is_allowed(
            _normalize_email(payload.email),
            payload.purpose,
        )

        if not allowed:
            raise TooManyRequestsException(
                detail="Too many OTP requests. Please wait before trying again.",
                retry_after=retry_after,
            )

        otp_code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)

        await OTPService._replace_otp_record(db, payload, otp_code, expires_at)
        if commit:
            await db.commit()

        subject = "Your Verification Code"
        purpose_str = "verification"
        if payload.purpose == AuthPurpose.PASSWORD_RESET:
            subject = "Password Reset Code"
            purpose_str = "password reset"

        html_body = get_otp_email_html(
            code=otp_code,
            purpose=purpose_str,
            expiration_minutes=settings.OTP_EXPIRATION_MINUTES,
        )

        if background_tasks is not None:
            background_tasks.add_task(
                send_email,
                to_email=payload.email,
                subject=subject,
                body=html_body,
                is_html=True,
            )
            return

        email_sent = await send_email(
            to_email=payload.email,
            subject=subject,
            body=html_body,
            is_html=True,
        )

        if not email_sent:
            raise BadRequestException("Unable to send OTP email. Please try again.")

    @staticmethod
    async def verify_otp(db: AsyncSession, payload: VerifyOTP) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        normalized_email = _normalize_email(payload.email)

        result = await db.execute(
            select(AuthRecord).where(
                func.lower(AuthRecord.email) == normalized_email,
                AuthRecord.purpose == payload.purpose,
                AuthRecord.is_used == False,
            ).order_by(AuthRecord.created_at.desc()).with_for_update()
        )
        otp_record = result.scalars().first()

        if not otp_record or not verify_otp_hash(payload.code, otp_record.hashed_value):
            raise BadRequestException("Invalid OTP")

        if otp_record.expires_at.replace(tzinfo=timezone.utc) < now:
            raise BadRequestException("OTP has expired")

        user = await UserRepository.get_user_by_email(db, payload.email)
        if not user:
            raise NotFoundException("User not found")

        tenant = await TenantRepository.get_by_id(db, user.tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")

        response_data = {"detail": "OTP verified successfully"}

        if payload.purpose == AuthPurpose.VERIFICATION:
            is_public_tenant_admin = (
                user.role == UserRole.ADMIN
                and tenant.email.strip().lower() == user.email.strip().lower()
            )
            if not is_public_tenant_admin:
                raise BadRequestException(
                    "OTP verification is only available for public tenant signup accounts."
                )

            if not _tenant_allows_otp_verification(tenant):
                raise BadRequestException("OTP verification is not available for this account.")

            if tenant.verification_status == TenantVerificationStatus.REJECTED:
                raise BadRequestException("Tenant verification has been rejected.")

            user.account_status = AccountStatus.ACTIVE
            user.is_verified = True
            tenant.verification_status = TenantVerificationStatus.ACTIVE
            if tenant.status == TenantStatus.INACTIVE:
                tenant.status = TenantStatus.TRIAL
            otp_record.is_used = True

        elif payload.purpose == AuthPurpose.PASSWORD_RESET:
            if not _user_can_reset_password(user, tenant):
                raise BadRequestException("Password reset is not available for this account.")

            reset_token = secrets.token_urlsafe(32)
            reset_token_expires_at = now + timedelta(minutes=15)

            # Replace any previous reset token so only the latest one remains valid.
            await db.execute(
                delete(AuthRecord).where(
                    func.lower(AuthRecord.email) == _normalize_email(user.email),
                    AuthRecord.purpose == AuthPurpose.PASSWORD_RESET,
                )
            )
            db.add(
                AuthRecord(
                    email=user.email,
                    hashed_value=hash_auth_secret(reset_token),
                    purpose=AuthPurpose.PASSWORD_RESET,
                    expires_at=reset_token_expires_at,
                    tenant_id=user.tenant_id,
                )
            )
            response_data["reset_token"] = reset_token

        else:
            raise BadRequestException(f"Unhandled OTP purpose : {payload.purpose}")

        await db.commit()

        return response_data

