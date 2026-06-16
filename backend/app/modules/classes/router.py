#======================================#
#              router.py               #
#======================================#

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import get_current_tenant_user
from app.modules.classes.schemas import (
    ClassRoomCreate,
    ClassRoomResponse,
    ClassRoomUpdate,
)
from app.modules.classes.service import ClassRoomService
from app.modules.users.models import User


router = APIRouter(
    prefix="/classes",
    tags=["Classes"],
)
CurrentTenantUser: TypeAlias = Annotated[User, Depends(get_current_tenant_user)]


@router.post(
    "/",
    response_model=ClassRoomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_classroom(
    payload: ClassRoomCreate,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ClassRoomResponse:
    """Create a new classroom."""

    return await ClassRoomService.create_classroom(
        db=db,
        tenant_id=current_user.tenant_id,
        payload=payload,
    )


@router.get(
    "/",
    response_model=list[ClassRoomResponse],
)
async def get_all_classrooms(
    db: DbSession,
    current_user: CurrentTenantUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    active_only: bool = Query(default=False),
) -> list[ClassRoomResponse]:
    """Get classrooms within tenant scope."""

    if active_only:
        return await ClassRoomService.get_active_classrooms(
            db=db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
        )

    return await ClassRoomService.get_all_classrooms(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{class_id}",
    response_model=ClassRoomResponse,
)
async def get_classroom_by_id(
    class_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ClassRoomResponse:
    """Get classroom by ID."""

    return await ClassRoomService.get_classroom_by_id(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
    )


@router.patch(
    "/{class_id}",
    response_model=ClassRoomResponse,
)
async def update_classroom(
    class_id: uuid.UUID,
    payload: ClassRoomUpdate,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ClassRoomResponse:
    """Update classroom."""

    return await ClassRoomService.update_classroom(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
        payload=payload,
    )


@router.delete(
    "/{class_id}",
    response_model=ClassRoomResponse,
)
async def deactivate_classroom(
    class_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> ClassRoomResponse:
    """Soft delete classroom."""

    return await ClassRoomService.deactivate_classroom(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
    )
