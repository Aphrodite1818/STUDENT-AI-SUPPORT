#======================================#
#          user router.py              #
#======================================#

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status

from app.core.dependencies.db import DbSession
from app.config.logging import get_logger
from app.core.utils.frontend_urls import resolve_frontend_app_url
from app.modules.users.schemas import (
    UserAdminUpdate,
    UserInviteCreate,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UserService
from app.core.dependencies.route_guards import (
    get_current_active_user,
    require_role,
)
from app.core.exceptions import ForbiddenException
from app.modules.users.models import User, UserRole

logger = get_logger(__name__)

router = APIRouter(tags=["Users"])


# ── Dependency ────────────────────────────────────────────────────────────────



# ── Create ────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
@router.post(
    "/user-create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    payload: UserInviteCreate,
    db: DbSession,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
) -> UserResponse:
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
    summary="Resend a tenant user invite",
)
async def resend_invite(
    user_id: uuid.UUID,
    db: DbSession,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
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
    summary="Get current user profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
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
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERADMIN])),
) -> list[UserResponse]:
    """
    Return a paginated list of all users.
    """
    tenant_id = None if current_user.role == UserRole.SUPERADMIN else current_user.tenant_id
    return await UserService.get_all_users(
        db,
        skip=skip,
        limit=limit,
        tenant_id=tenant_id,
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
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Fetch a user by their UUID. Returns 404 if not found.
    """
    user = await UserService.get_user_by_id(db, user_id)
    if (
        current_user.role not in (UserRole.ADMIN, UserRole.SUPERADMIN)
        and current_user.id != user_id
    ):
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
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Partial update of a user's own profile fields.
    Only fields included in the request body are changed.
    """
    if current_user.id != user_id and current_user.role not in (
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ):
        raise ForbiddenException("You can only update your own profile")
    if (
        current_user.role == UserRole.ADMIN
        and current_user.id != user_id
    ):
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
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERADMIN])),
) -> UserResponse:
    """
    Admin-only endpoint to update privileged fields
    (e.g. role, is_active, is_verified).
    """
    if current_user.role != UserRole.SUPERADMIN:
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
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERADMIN])),
) -> dict:
    """
    Permanently delete a user. Returns 404 if not found.
    """
    if current_user.role != UserRole.SUPERADMIN:
        target_user = await UserService.get_user_by_id(db, user_id)
        if target_user.tenant_id != current_user.tenant_id:
            raise ForbiddenException("You do not have access to this user")
    return await UserService.delete_user(db, user_id)
