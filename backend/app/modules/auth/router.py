#======================================#
#            auth/router.py            #
#======================================#

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.dependencies.db import get_db
from backend.app.config.security import create_access_token
from backend.app.modules.auth.schemas import LoginRequest, Token, RequestOTP, VerifyOTP, UpdatePassword
from backend.app.modules.auth.service import AuthService, OTPService

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    # 1. Authenticate user
    user = await AuthService.authenticate_user(db, payload)
    
    # 2. Generate token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    }
    
    # Optional: could use a configurable expire time
    access_token = create_access_token(data=token_data)
    
    return Token(access_token=access_token)

@router.post("/request-otp")
async def request_otp(payload: RequestOTP, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await OTPService.generate_otp(db, payload)
    return {"detail": f"OTP successfully sent to {payload.email}"}

@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTP, db: AsyncSession = Depends(get_db)):
    # Returns {"detail": "..."} and optionally a "reset_token"
    return await OTPService.verify_otp(db, payload)

@router.post("/reset-password")
async def reset_password(payload: UpdatePassword, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await AuthService.reset_password(db, payload)
    return {"detail": "Password has been successfully reset. You may now log in."}
