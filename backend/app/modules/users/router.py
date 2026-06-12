# ====================================== #
#             user router.py             #
# ====================================== #

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status

from app.config.logging import get_logger
from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import (
    get_current_tenant_user,
    require_tenant_role,
)
from app.core.exceptions import ForbiddenException
from app.core.utils.frontend_urls import resolve_frontend_app_url
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import (
    UserAdminUpdate,
    UserInviteCreate,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UserService

logger = get_logger(__name__)

router = APIRouter(tags=["Users"])
CurrentTenantUser: TypeAlias = Annotated[User, Depends(get_current_tenant_user)]
TenantAdminUser: TypeAlias = Annotated[
    User,
    Depends(require_tenant_role([UserRole.ADMIN])),
]


# ── Create ────────────────────────────────────────────────────────────────────

@router.post(
    "/user-create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new tenant user",
)
async def register_user(
    payload: UserInviteCreate,
    db: DbSession,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: TenantAdminUser,
) -> User:
    """
    Create a normal tenant user and email an invite link.

    - Tenant admins can only invite users inside their own tenant.
    - Normal users complete setup from the emailed invite link.
    """
    return await UserService.register_user(
        db,
        current_user,
        payload,
        background_tasks=background_tasks,
        frontend_app_url=resolve_frontend_app_url(request),
    )


@router.post(
    "/{user_id}/resend-invite",
    status_code=status.HTTP_200_OK,
    summary="Resend a tenant user invite link",
)
async def resend_invite(
    user_id: uuid.UUID,
    db: DbSession,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: TenantAdminUser,
) -> dict[str, str]:
    return await UserService.resend_invite(
        db,
        current_user,
        user_id,
        background_tasks=background_tasks,
        frontend_app_url=resolve_frontend_app_url(request),
    )


# ── Read ──────────────────────────────────────────────────────────────────────

@router.get(
    "/get-authenticated-user",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
async def get_current_user_profile(
    current_user: CurrentTenantUser,
) -> User:
    """
    Fetch the currently authenticated user's profile.
    """
    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users (paginated)",
)
@router.get(
    "/list-users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def list_users(
    db: DbSession,
    current_user: TenantAdminUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
) -> list[User]:
    """
    Return a paginated list of all users.
    """
    return await UserService.get_all_users(
        db,
        skip=skip,
        limit=limit,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single user by ID",
)
async def get_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> User:
    """
    Fetch a user by their UUID. Returns 404 if not found.
    """
    user = await UserService.get_user_by_id(db, user_id)

    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise ForbiddenException("You can only access your own profile")

    if (
        current_user.role == UserRole.ADMIN
        and current_user.id != user_id
        and current_user.tenant_id != user.tenant_id
    ):
        raise ForbiddenException("You do not have access to this user")

    return user


# ── Update ────────────────────────────────────────────────────────────────────

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update own profile",
)
async def update_profile(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> User:
    """
    Partial update of a user's own profile fields.
    Only fields included in the request body are changed.
    """
    if current_user.id != user_id and current_user.role not in (
        UserRole.ADMIN,
    ):
        raise ForbiddenException("You can only update your own profile")

    if current_user.role == UserRole.ADMIN and current_user.id != user_id:
        target = await UserService.get_user_by_id(db, user_id)
        if target.tenant_id != current_user.tenant_id:
            raise ForbiddenException("You do not have access to this user")

    return await UserService.update_profile(db, user_id, payload)


@router.patch(
    "/{user_id}/admin",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin-level user update",
)
async def update_admin_status(
    user_id: uuid.UUID,
    payload: UserAdminUpdate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> User:
    """
    Admin-only endpoint to update privileged fields
    (e.g. role, is_active, is_verified).
    """
    target_user = await UserService.get_user_by_id(db, user_id)
    if target_user.tenant_id != current_user.tenant_id:
        raise ForbiddenException("You do not have access to this user")

    return await UserService.update_admin_status(db, current_user, user_id, payload)


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
)
async def delete_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_user: TenantAdminUser,
) -> dict[str, str]:
    """
    Permanently delete a user. Returns 404 if not found.
    """
    target_user = await UserService.get_user_by_id(db, user_id)
    if target_user.tenant_id != current_user.tenant_id:
        raise ForbiddenException("You do not have access to this user")
    if target_user.role == UserRole.ADMIN:
        raise ForbiddenException("Tenant admins cannot delete administrator accounts")

    return await UserService.delete_user(db, user_id)
