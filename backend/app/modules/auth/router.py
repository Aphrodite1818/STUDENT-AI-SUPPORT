#======================================#
#            auth/router.py            #
#======================================#

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.core.dependencies.db import DbSession
from app.config.security import create_access_token
from app.modules.auth.schemas import (
    LoginRequest,
    Token,
    RequestOTP,
    TenantActivationRequest,
    UserInviteAcceptanceRequest,
    VerifyOTP,
    UpdatePassword,
)
from app.modules.auth.service import (
    AuthService,
    OTPService,
    TenantActivationService,
    UserInviteService,
)
from app.core.exceptions import AccountNotVerifiedException, TooManyRequestsException

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
            headers=e.headers,
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
async def request_otp(payload: RequestOTP, db: DbSession, background_tasks: BackgroundTasks) -> dict[str, str]:
    try:
        await OTPService.generate_otp(db, payload, background_tasks=background_tasks)
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


@router.post("/activate-tenant")
async def activate_tenant(
    payload: TenantActivationRequest,
    db: DbSession,
) -> dict[str, str]:
    return await TenantActivationService.activate_tenant(db, payload)


@router.get("/invite-status")
async def get_invite_status(token: str, db: DbSession) -> dict[str, str | None]:
    return await UserInviteService.get_invite_status(db, token)


@router.post("/accept-invite")
async def accept_invite(
    payload: UserInviteAcceptanceRequest,
    db: DbSession,
) -> dict[str, str]:
    return await UserInviteService.accept_invite(db, payload)

