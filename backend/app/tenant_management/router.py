# ====================================== #
#       tenant_management/router.py      #
# ====================================== #

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import (
    require_tenant_role,
    require_tenant_ownership,
)
from app.modules.users.models import User, UserRole
from app.tenant_management.models import Tenant
from app.tenant_management.schemas import (
    TenantAdminResponse,
    TenantRegisterRequest,
    TenantUpdate,
)
from app.tenant_management.service import TenantService


router = APIRouter(tags=["Tenants"])
TenantAdminUser: TypeAlias = Annotated[
    User,
    Depends(require_tenant_role([UserRole.ADMIN])),
]
TenantAdminOrTeacherUser: TypeAlias = Annotated[
    User,
    Depends(require_tenant_role([UserRole.ADMIN, UserRole.TEACHER])),
]
TenantOwnedUser: TypeAlias = Annotated[User, Depends(require_tenant_ownership)]


@router.post(
    "/register",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new school tenant",
)
async def register_tenant(
    payload: TenantRegisterRequest,
    db: DbSession,
    background_tasks: BackgroundTasks,
) -> dict | JSONResponse:
    """Perform register tenant."""
    result = await TenantService.register_tenant(
        db,
        payload,
        background_tasks=background_tasks,
    )

    if result.get("created") is False:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result),
        )

    return result


@router.get(
    "/{tenant_id}",
    response_model=TenantAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tenant details by ID",
)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: DbSession,
    current_user: TenantAdminOrTeacherUser,
    owned_user: TenantOwnedUser,
) -> Tenant:
    """Return tenant."""
    return await TenantService.get_tenant_by_id(db, tenant_id)


@router.patch(
    "/{tenant_id}",
    response_model=TenantAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Update tenant profile",
)
async def update_tenant(
    tenant_id: uuid.UUID,
    payload: TenantUpdate,
    db: DbSession,
    current_user: TenantAdminUser,
    owned_user: TenantOwnedUser,
) -> Tenant:
    """Update tenant."""
    return await TenantService.update_tenant_profile(
        db,
        tenant_id,
        payload,
    )
