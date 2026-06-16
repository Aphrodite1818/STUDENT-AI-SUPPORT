from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import get_current_tenant_user, require_tenant_role
from app.modules.parents.schemas import (
    ParentCreate,
    ParentLinkedStudentListResponse,
    ParentListResponse,
    ParentResponse,
    ParentUpdate,
)
from app.modules.parents.service import ParentService
from app.modules.users.models import User, UserRole


router = APIRouter(
    prefix="/parents",
    tags=["Parents"],
)
CurrentTenantUser: TypeAlias = Annotated[User, Depends(get_current_tenant_user)]
TenantAdminUser: TypeAlias = Annotated[
    User,
    Depends(require_tenant_role([UserRole.ADMIN])),
]


@router.post(
    "",
    response_model=ParentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a parent profile",
)
async def create_parent_profile(
    payload: ParentCreate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> ParentResponse:
    """Create a parent profile."""
    return await ParentService.create_parent_profile(
        db=db,
        actor=current_user,
        payload=payload,
    )


@router.get(
    "",
    response_model=ParentListResponse,
    summary="List parent profiles",
)
async def get_all_parents(
    db: DbSession,
    current_user: TenantAdminUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ParentListResponse:
    """Get all parent profiles for the current tenant."""
    parents, total = await ParentService.get_all_parents(
        db=db,
        actor=current_user,
        skip=skip,
        limit=limit,
    )
    return ParentListResponse(items=parents, total=total)


@router.get(
    "/me",
    response_model=ParentResponse,
    summary="Get my parent profile",
)
async def get_my_parent_profile(
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ParentResponse:
    """Get the logged-in parent's profile."""
    return await ParentService.get_parent_by_user_id(
        db=db,
        actor=current_user,
        user_id=current_user.id,
    )


@router.patch(
    "/me/profile",
    response_model=ParentResponse,
    summary="Update my parent profile",
)
async def update_my_parent_profile(
    payload: ParentUpdate,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ParentResponse:
    """Allow the logged-in parent to update their own profile."""
    return await ParentService.update_my_parent_profile(
        db=db,
        actor=current_user,
        payload=payload,
    )


@router.get(
    "/me/students",
    response_model=ParentLinkedStudentListResponse,
    summary="Get my linked students",
)
async def get_my_linked_students(
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ParentLinkedStudentListResponse:
    """Get students linked to the logged-in parent."""
    students, total = await ParentService.get_my_linked_students(
        db=db,
        actor=current_user,
    )
    return ParentLinkedStudentListResponse(items=students, total=total)


@router.get(
    "/{parent_id}",
    response_model=ParentResponse,
    summary="Get a parent profile",
)
async def get_parent_profile(
    parent_id: UUID,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ParentResponse:
    """Get a parent profile by id."""
    return await ParentService.get_parent_profile(
        db=db,
        actor=current_user,
        parent_id=parent_id,
    )


@router.patch(
    "/{parent_id}",
    response_model=ParentResponse,
    summary="Update a parent profile",
)
async def update_parent_profile(
    parent_id: UUID,
    payload: ParentUpdate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> ParentResponse:
    """Update a parent profile."""
    return await ParentService.update_parent_profile(
        db=db,
        actor=current_user,
        parent_id=parent_id,
        payload=payload,
    )


@router.delete(
    "/{parent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a parent profile",
)
async def delete_parent_profile(
    parent_id: UUID,
    db: DbSession,
    current_user: TenantAdminUser,
) -> None:
    """Delete a parent profile."""
    await ParentService.delete_parent_profile(
        db=db,
        actor=current_user,
        parent_id=parent_id,
    )
