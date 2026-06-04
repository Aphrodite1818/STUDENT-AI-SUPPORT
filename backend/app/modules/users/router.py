#======================================#
#          user router.py              #
#======================================#

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies.db import DbSession
from backend.app.config.logging import get_logger
from backend.app.modules.users.schemas import (
    UserAdminUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from backend.app.modules.users.service import UserService
from backend.app.core.dependencies.route_guards import get_current_active_user
from backend.app.modules.users.models import User


logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


# ── Dependency ────────────────────────────────────────────────────────────────

def get_user_service(session: DbSession) -> UserService:
    return UserService(session=session)


# ── Create ────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Register a new user account.

    - Rejects duplicate email or phone number.
    - Passwords are hashed before storage.
    """
    return await service.register_user(payload)


# ── Read ──────────────────────────────────────────────────────────────────────

@router.get(
    "/me",
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
async def list_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """
    Return a paginated list of all users.
    """
    return await service.get_all_users(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single user by ID",
)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Fetch a user by their UUID. Returns 404 if not found.
    """
    return await service.get_user_by_id(user_id)


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
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Partial update of a user's own profile fields.
    Only fields included in the request body are changed.
    """
    return await service.update_profile(user_id, payload)


@router.patch(
    "/{user_id}/admin",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin-level user update",
)
async def update_admin_status(
    user_id: uuid.UUID,
    payload: UserAdminUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Admin-only endpoint to update privileged fields
    (e.g. role, is_active, is_verified).
    """
    return await service.update_admin_status(user_id, payload)


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
)
async def delete_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    Permanently delete a user. Returns 404 if not found.
    """
    return await service.delete_user(user_id)