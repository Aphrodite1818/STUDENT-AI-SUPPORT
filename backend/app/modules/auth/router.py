#======================================#
#            auth/router.py            #
#======================================#

from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.core.dependencies.db import DbSession, get_db
from backend.app.config.security import create_access_token
from backend.app.modules.auth.schemas import LoginRequest, Token, RequestOTP, VerifyOTP, UpdatePassword
from backend.app.modules.auth.service import AuthService, OTPService
from backend.app.core.exceptions import AccountNotVerifiedException, TooManyRequestsException

router = APIRouter()

class LoginResponse(Token):
    detail: str | None = None
    resend_otp_available: bool = False
    email: str | None = None

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: DbSession) -> LoginResponse:
    try:
        user = await AuthService.authenticate_user(db, payload)
    except AccountNotVerifiedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e.detail),
            headers={"X-Resend-OTP-Available": "true", "X-Email": payload.email},
        )
    except TooManyRequestsException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e.detail),
            headers={"Retry-After": str(e.retry_after)},
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
    }

    access_token = create_access_token(data=token_data)

    return LoginResponse(access_token=access_token, email=user.email)

@router.post("/request-otp")
async def request_otp(payload: RequestOTP, db: DbSession) -> dict[str, str]:
    try:
        await OTPService.generate_otp(db, payload)
    except TooManyRequestsException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e.detail),
            headers={"Retry-After": str(e.retry_after)},
        )
    return {"detail": f"OTP successfully sent to {payload.email}"}

@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTP, db: DbSession):
    return await OTPService.verify_otp(db, payload)

@router.post("/reset-password")
async def reset_password(payload: UpdatePassword, db: DbSession) -> dict[str, str]:
    await AuthService.reset_password(db, payload)
    return {"detail": "Password has been successfully reset. You may now log in."}
