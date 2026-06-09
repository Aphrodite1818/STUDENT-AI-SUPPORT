# ====================================== #
#             auth/router.py             #
# ====================================== #

from fastapi import APIRouter, BackgroundTasks

from app.config.security import create_access_token
from app.core.dependencies.db import DbSession
from app.modules.auth.schemas import (
    LoginRequest,
    RequestOTP,
    TenantActivationRequest,
    Token,
    UpdatePassword,
    UserInviteAcceptanceRequest,
    VerifyOTP,
)
from app.modules.auth.service import (
    AuthService,
    OTPService,
    TenantActivationService,
    UserInviteService,
)

router = APIRouter()


class LoginResponse(Token):
    detail: str | None = None
    resend_otp_available: bool = False
    email: str | None = None
    role: str | None = None
    account_type: str | None = None


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: DbSession,
    background_tasks: BackgroundTasks,
) -> LoginResponse:
    actor = await AuthService.authenticate_actor(
        db,
        payload,
        background_tasks=background_tasks,
    )

    token_data = {
        "sub": str(actor.actor_id),
        "email": actor.email,
        "role": actor.role,
        "account_type": actor.account_type,
    }
    if actor.tenant_id is not None:
        token_data["tenant_id"] = str(actor.tenant_id)

    access_token = create_access_token(data=token_data)

    return LoginResponse(
        access_token=access_token,
        email=actor.email,
        role=actor.role,
        account_type=actor.account_type,
    )


@router.post("/request-otp")
async def request_otp(
    payload: RequestOTP,
    db: DbSession,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    await OTPService.generate_otp(
        db,
        payload,
        background_tasks=background_tasks,
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
