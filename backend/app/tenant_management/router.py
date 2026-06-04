#======================================#
#      tenant_management/router.py     #
#======================================#

from fastapi import APIRouter, Depends , status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.dependencies.db import DbSession , get_db
from backend.app.tenant_management.schemas import(
    TenantAdminResponse,
    TenantCreate,
    TenantUpdate,
    TenantPublicResponse,
    TenantRegisterRequest,
    TenantStatusUpdate
)
from backend.app.core.exceptions import ForbiddenException
from backend.app.core.dependencies.auth import (
    get_current_user,
    require_role,
    require_tenant_ownership
)
from backend.app.modules.users.models import User , UserRole
router = APIRouter()
