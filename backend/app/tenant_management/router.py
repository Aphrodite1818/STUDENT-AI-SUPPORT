#======================================#
#      tenant_management/router.py     #
#======================================#

from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.dependencies.db import DbSession, get_db
from backend.app.config.logging import get_logger
from backend.app.modules.auth.service import OTPService
from backend.app.tenant_management.schemas import (
    TenantCreate,
    TenantUpdate,
    TenantPublicResponse,
    TenantRegisterRequest,
    TenantStatusUpdate,
    TenantAdminResponse
)
from backend.app.core.dependencies.route_guards import (
    get_current_user,
    require_role,
    require_tenant_ownership
)
from backend.app.modules.users.models import User, UserRole
from backend.app.tenant_management.service import TenantService

logger = get_logger(__name__)

router = APIRouter(tags=["Tenants"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new school (tenant) and its admin user",
)
async def register_tenant(
    payload: TenantRegisterRequest,
    db: DbSession,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Public endpoint to register a new school and automatically create
    an admin user account for it. Sends verification OTP to admin email.

    Returns 201 for new tenant, 200 for resend on existing pending account.
    """
    result = await TenantService.register_tenant(db, payload, background_tasks=background_tasks)
    if result.get("can_resend_otp") is False:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result),
        )
    return result

@router.post(
    "",
    response_model=TenantAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Superadmin: Create a new tenant directly",
    dependencies=[Depends(require_role([UserRole.SUPERADMIN]))]
)
async def create_tenant(
    payload: TenantCreate,
    db: DbSession
) -> TenantAdminResponse:
    """
    Superadmin only. Creates a tenant record directly without a corresponding user.
    """
    return await TenantService.superadmin_create_tenant(db, payload)


@router.get(
    "",
    response_model=list[TenantAdminResponse],
    status_code=status.HTTP_200_OK,
    summary="Superadmin: List all tenants",
    dependencies=[Depends(require_role([UserRole.SUPERADMIN]))]
)
async def list_tenants(
    db: DbSession,
    skip: int = 0,
    limit: int = 50,
) -> list[TenantAdminResponse]:
    """
    Superadmin only. Lists all tenants paginated.
    """
    return await TenantService.get_all_tenants(db, skip=skip, limit=limit)


@router.get(
    "/{tenant_id}",
    response_model=TenantAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tenant details by ID",
    dependencies=[Depends(require_role([UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.TEACHER]))]
)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: DbSession,
    current_user: User = Depends(require_tenant_ownership)
) -> TenantAdminResponse:
    """
    Fetch tenant details. User must belong to this tenant or be a superadmin.
    """
    return await TenantService.get_tenant_by_id(db, tenant_id)


@router.patch(
    "/{tenant_id}",
    response_model=TenantAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Update tenant profile",
    dependencies=[Depends(require_role([UserRole.SUPERADMIN, UserRole.ADMIN]))]
)
async def update_tenant(
    tenant_id: uuid.UUID,
    payload: TenantUpdate,
    db: DbSession,
    current_user: User = Depends(require_tenant_ownership)
) -> TenantAdminResponse:
    """
    Update tenant information. User must be an admin of this tenant or superadmin.
    """
    return await TenantService.update_tenant_profile(db, tenant_id, payload)


@router.patch(
    "/{tenant_id}/status",
    response_model=TenantAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Superadmin: Update tenant status",
    dependencies=[Depends(require_role([UserRole.SUPERADMIN]))]
)
async def update_tenant_status(
    tenant_id: uuid.UUID,
    payload: TenantStatusUpdate,
    db: DbSession
) -> TenantAdminResponse:
    """
    Superadmin only. Change the status of a tenant (e.g., suspend or activate).
    """
    return await TenantService.update_tenant_status(db, tenant_id, payload)



@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_200_OK,
    summary="Superadmin: Delete a tenant",
    dependencies=[Depends(require_role([UserRole.SUPERADMIN]))]
)
async def delete_tenant(
    tenant_id: uuid.UUID,
    db: DbSession
) -> dict:
    """
    Superadmin only. Soft deletes a tenant.
    """
    return await TenantService.delete_tenant(db, tenant_id)
