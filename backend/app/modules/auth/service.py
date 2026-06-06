#======================================#
#            auth/service.py           #
#======================================#


from backend.app.config.security import verify_password, hash_password, create_access_token, hash_otp, verify_otp as verify_otp_hash
from backend.app.core.exceptions import NotFoundException, UnauthorizedException, BadRequestException, AccountNotVerifiedException, TooManyRequestsException
from backend.app.modules.auth.schemas import LoginRequest, UpdatePassword, RequestOTP, VerifyOTP
from backend.app.modules.auth.models import OTP, OTPPurpose
from backend.app.core.utils.email import send_email
from backend.app.core.utils.email_templates import get_otp_email_html
from backend.app.config.settings import settings
from backend.app.modules.users.models import AccountStatus
from sqlalchemy import select, delete, update
from datetime import datetime, timezone, timedelta
import random
import string
from jose import jwt, JWTError
from backend.app.modules.users.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
from backend.app.modules.users.models import User
from backend.app.tenant_management.models import TenantVerificationStatus
from backend.app.tenant_management.models import TenantStatus
from backend.app.tenant_management.repository import TenantRepository
from backend.app.core.utils.otp_rate_limiter import OTPRateLimiter
class AuthService:
    @staticmethod
    def _user_repo(db: AsyncSession) -> UserRepository:
        return UserRepository(session=db)

    @staticmethod
    async def authenticate_user(db: AsyncSession, payload: LoginRequest) -> User:
        user = await AuthService._user_repo(db).get_user_by_email(payload.email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        tenant = await TenantRepository.get_by_id(db, user.tenant_id)
        if tenant is None:
            raise UnauthorizedException("Account not found")

        if tenant.is_deleted or tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
            raise UnauthorizedException("Account is not active")

        if tenant.verification_status == TenantVerificationStatus.PENDING_VERIFICATION:
            raise AccountNotVerifiedException(
                detail="Account not verified. Please check your email for the verification code.",
            )

        if tenant.verification_status == TenantVerificationStatus.REJECTED:
            raise UnauthorizedException("Account has been rejected. Please contact support.")

        if user.account_status != AccountStatus.ACTIVE:
            if user.account_status == AccountStatus.PENDING:
                raise AccountNotVerifiedException(
                    detail="Account not verified. Please check your email for the verification code.",
                )
            raise UnauthorizedException("Account is not active")

        return user

    @staticmethod
    async def reset_password(db: AsyncSession, payload: UpdatePassword) -> None:
        try:
            token_payload = jwt.decode(payload.reset_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if token_payload.get("purpose") != "password_reset" or token_payload.get("email") != payload.email:
                raise UnauthorizedException("Invalid or expired reset token")
        except JWTError:
            raise UnauthorizedException("Invalid or expired reset token")

        user = await AuthService._user_repo(db).get_user_by_email(payload.email)

        if not user:
            raise NotFoundException("User email does not exist")

        hashed_pw = hash_password(payload.new_password)

        user.password_hash = hashed_pw
        await db.commit()


class OTPService:
    @staticmethod
    async def generate_otp(
        db: AsyncSession,
        payload: RequestOTP,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        user = await AuthService._user_repo(db).get_user_by_email(payload.email)

        if not user:
            raise NotFoundException("User with this email not found.")

        rate_limiter = OTPRateLimiter()
        allowed, retry_after = rate_limiter.is_allowed(payload.email, payload.purpose)

        if not allowed:
            raise TooManyRequestsException(
                detail="Too many OTP requests. Please wait before trying again.",
                retry_after=retry_after,
            )

        await db.execute(
            delete(OTP).where(
                OTP.email == payload.email,
                OTP.purpose == payload.purpose,
                OTP.is_used == False,
            )
        )

        otp_code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
        hashed_otp = hash_otp(otp_code)

        otp_record = OTP(
            email=payload.email,
            hashed_code=hashed_otp,
            purpose=payload.purpose,
            expires_at=expires_at,
            tenant_id=user.tenant_id,
        )

        subject = "Your Verification Code"
        purpose_str = "verification"
        if payload.purpose == OTPPurpose.PASSWORD_RESET:
            subject = "Password Reset Code"
            purpose_str = "password reset"

        html_body = get_otp_email_html(
            code=otp_code,
            purpose=purpose_str,
            expiration_minutes=settings.OTP_EXPIRATION_MINUTES,
        )

        db.add(otp_record)
        await db.commit()

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

        result = await db.execute(
            select(OTP).where(
                OTP.email == payload.email,
                OTP.purpose == payload.purpose,
                OTP.is_used == False,
            ).order_by(OTP.created_at.desc())
        )
        otp_record = result.scalars().first()

        if not otp_record or not verify_otp_hash(payload.code, otp_record.hashed_code):
            raise BadRequestException("Invalid OTP")

        if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise BadRequestException("OTP has expired")

        mark_result = await db.execute(
            update(OTP).where(
                OTP.id == otp_record.id,
                OTP.is_used == False,
            ).values(is_used=True).execution_options(synchronize_session="fetch")
        )

        if mark_result.rowcount == 0:
            raise BadRequestException("OTP has already been used")

        user = await AuthService._user_repo(db).get_user_by_email(payload.email)
        tenant = await TenantRepository.get_by_email(db, payload.email)

        if not user:
            raise NotFoundException("User not found")

        if not tenant:
            raise NotFoundException("Tenant not found")

        response_data = {"detail": "OTP verified successfully"}

        if payload.purpose == OTPPurpose.VERIFICATION:
            user.account_status = AccountStatus.ACTIVE
            tenant.verification_status = TenantVerificationStatus.ACTIVE

        elif payload.purpose == OTPPurpose.PASSWORD_RESET:
            reset_token = create_access_token(
                data={"email": user.email, "purpose": "password_reset"},
                expires_delta=timedelta(minutes=15),
            )
            response_data["reset_token"] = reset_token

        else:
            raise BadRequestException(f"Unhandled OTP purpose : {payload.purpose}")

        await db.execute(delete(OTP).where(OTP.id == otp_record.id))

        await db.commit()

        return response_data
