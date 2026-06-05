#======================================#
#            auth/service.py           #
#======================================#

from pickle import FALSE
from threading import activeCount

from backend.app.config.security import verify_password, hash_password, create_access_token , hash_otp , verify_otp as verify_otp_hash
from backend.app.core.exceptions import NotFoundException, UnauthorizedException, BadRequestException
from backend.app.modules.auth.schemas import LoginRequest, UpdatePassword, RequestOTP, VerifyOTP
from backend.app.modules.auth.models import OTP, OTPPurpose
from backend.app.core.utils.email import send_email
from backend.app.core.utils.email_templates import get_otp_email_html
from backend.app.config.settings import settings
from backend.app.modules.users.models import AccountStatus
from sqlalchemy import select, delete , update
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

        user = await user_repo.get_user_by_email(payload.email)
        if not user:
            raise NotFoundException("User with this email not found.")
        

        await db.execute(
            delete(OTP).where(OTP.email == payload.email ,
                    OTP.expires_at < datetime.now(timezone.utc), 
                    OTP.purpose == payload.purpose, 
                    OTP.is_used == False
            )
        )

        # Generate 6 digit code
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
        
        db.add(otp_record)
        await db.commit()
        
        # Dispatch Email
        subject = "Your Verification Code"
        purpose_str = "verification"
        if payload.purpose == OTPPurpose.PASSWORD_RESET:
            subject = "Password Reset Code"
            purpose_str = "password reset"
            
        html_body = get_otp_email_html(
            code=otp_code, 
            purpose=purpose_str, 
            expiration_minutes=settings.OTP_EXPIRATION_MINUTES
        )
        await send_email(to_email=payload.email, subject=subject, body=html_body, is_html=True)
        

    @staticmethod
    async def verify_otp(db : AsyncSession , payload : VerifyOTP) -> dict[str, str]:

        result = await db.execute(
            select(OTP).where(
                OTP.email == payload.email,
                OTP.purpose == payload.purpose,
                OTP.is_used == False
            ).order_by(OTP.created_at.desc())
        )
        otp_record = result.scalar_one_or_none()


        #check for correct otp
        if not otp_record or not verify_otp_hash(payload.code , otp_record.hashed_code):
            raise BadRequestException("Invalid OTP")
        
        #check if otp is expired
        if otp_record.expires_at.replace(tzinfo = timezone.utc) < datetime.now(timezone.utc):
            raise BadRequestException("OTP has expired")
        
        #atomically mark otp as used at DB level to prevent race conditions
        mark_result = await db.execute(update(OTP).where(
            OTP.id == otp_record.id , 
            OTP.is_used == False,
        ).values(is_used = True).execution_options(synchronize_session = "fetch")
        )

        #checking if another request beat us to it 
        if mark_result.rowcount == 0 :
            raise BadRequestException("OTP has already been used")
        
        #fetching the user 
        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_email(payload.email)

        if not user:
            raise NotFoundException("user not found")
        
        response_data = {"detail" : "OTP verified successfully"}

        if payload.purpose == OTPPurpose.VERIFICATION:
            user.account_status = AccountStatus.ACTIVE

        elif payload.purpose == OTPPurpose.PASSWORD_RESET:
            reset_token = create_access_token(
                data = {"email": user.email , "purpose" : "password_reset"},
                expires_delta=timedelta(minutes = 15)
            )
            response_data["reset_token"] = reset_token

        else:
            raise BadRequestException(f"Unhandled OTP purpose : {payload.purpose}")
        
        #silently delete this specific otp record (preserve audit trail for others)
        await db.execute(delete(OTP).where(OTP.id == otp_record.id))

        #commit 
        await db.commit()

        return response_data