#======================================#
#            auth/service.py           #
#======================================#

from backend.app.config.security import verify_password, hash_password, create_access_token
from backend.app.core.exceptions import NotFoundException, UnauthorizedException, BadRequestException
from backend.app.modules.auth.schemas import LoginRequest, UpdatePassword, RequestOTP, VerifyOTP
from backend.app.modules.auth.models import OTP, OTPPurpose
from backend.app.core.utils.email import send_email
from backend.app.core.utils.email_templates import get_otp_email_html
from backend.app.config.settings import settings
from backend.app.modules.users.models import AccountStatus
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import random
import string
from jose import jwt, JWTError
from backend.app.modules.users.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.modules.users.models import User



class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, payload: LoginRequest) -> User:
        user_repo = UserRepository(db)
        
        # 1. Fetch user by email
        user = await user_repo.get_user_by_email(payload.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")
            
        # 2. Verify password hash
        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
            
        return user
    
    @staticmethod
    async def reset_password(db: AsyncSession, payload: UpdatePassword) -> None:
        # 1. Verify the reset token first
        try:
            token_payload = jwt.decode(payload.reset_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if token_payload.get("purpose") != "password_reset" or token_payload.get("email") != payload.email:
                raise UnauthorizedException("Invalid or expired reset token")
        except JWTError:
            raise UnauthorizedException("Invalid or expired reset token")

        user_repo = UserRepository(db)

        # 2. Fetch the user
        user = await user_repo.get_user_by_email(payload.email)
        if not user:
            raise NotFoundException("User email does not exist")
        
        # 3. Hash the new password
        hashed_pw = hash_password(payload.new_password)
        
        # 4. Update and commit
        user.password_hash = hashed_pw
        await db.commit() 


class OTPService:
    @staticmethod
    async def generate_otp(db: AsyncSession, payload: RequestOTP) -> None:
        user_repo = UserRepository(db)
        
        # Check if user exists for password reset
        if payload.purpose == OTPPurpose.PASSWORD_RESET:
            user = await user_repo.get_user_by_email(payload.email)
            if not user:
                raise NotFoundException("User with this email not found.")

        # Generate 6 digit code
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
        
        otp_record = OTP(
            email=payload.email,
            code=code,
            purpose=payload.purpose,
            expires_at=expires_at
        )
        
        db.add(otp_record)
        await db.commit()
        
        # Dispatch Email
        subject = "Your Verification Code"
        purpose_str = "verification"
        if payload.purpose == OTPPurpose.PASSWORD_RESET:
            subject = "Password Reset Code"
            purpose_str = "password reset"
            
        html_body = get_otp_email_html(
            code=code, 
            purpose=purpose_str, 
            expiration_minutes=settings.OTP_EXPIRATION_MINUTES
        )
        await send_email(to_email=payload.email, subject=subject, body=html_body, is_html=True)

    @staticmethod
    async def verify_otp(db: AsyncSession, payload: VerifyOTP) -> dict:
        # Look up the OTP
        result = await db.execute(
            select(OTP).where(
                OTP.email == payload.email,
                OTP.code == payload.code,
                OTP.purpose == payload.purpose,
                OTP.is_used == False
            ).order_by(OTP.created_at.desc())
        )
        otp_record = result.scalars().first()
        
        if not otp_record:
            raise BadRequestException("Invalid OTP")
            
        if otp_record.expires_at < datetime.now(timezone.utc):
            raise BadRequestException("OTP has expired")
            
        # Mark as used
        otp_record.is_used = True
        
        # Handle side effects based on purpose
        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_email(payload.email)
        
        if not user:
            raise NotFoundException("User not found")

        response_data = {"detail": "OTP verified successfully"}

        if payload.purpose == OTPPurpose.VERIFICATION:
            user.account_status = AccountStatus.ACTIVE
            
        elif payload.purpose == OTPPurpose.PASSWORD_RESET:
            # Generate a short-lived reset token (valid for 15 minutes)
            reset_token = create_access_token(
                data={"email": user.email, "purpose": "password_reset"},
                expires_delta=timedelta(minutes=15)
            )
            response_data["reset_token"] = reset_token
            
        await db.commit()
        return response_data
