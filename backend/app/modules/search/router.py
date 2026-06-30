from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import get_current_tenant_admin
from app.modules.search.schemas import TenantSearchResponse
from app.modules.search.service import TenantSearchService
from app.modules.tenant_admins.models import TenantAdmin


router = APIRouter(prefix="/tenant-admin/search", tags=["Tenant Search"])
CurrentTenantAdmin: TypeAlias = Annotated[TenantAdmin, Depends(get_current_tenant_admin)]


@router.get("", response_model=TenantSearchResponse)
async def search_tenant(
    db: DbSession,
    current_admin: CurrentTenantAdmin,
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
) -> TenantSearchResponse:
    items = await TenantSearchService.search(
        db=db,
        tenant_id=current_admin.tenant_id,
        query=q,
        limit=limit,
    )
    return TenantSearchResponse(items=items, total=len(items))
