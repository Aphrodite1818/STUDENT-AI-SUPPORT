#======================================#
#    core/dependencies/route_guards.py #
#======================================#
"""Provide authentication and authorization dependencies for protected routes."""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import uuid

from app.config.settings import settings
from app.core.dependencies.db import get_db
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.modules.users.models import User, AccountStatus, UserRole
from app.modules.users.repository import UserRepository
from app.tenant_management.models import TenantStatus, TenantVerificationStatus
from app.tenant_management.repository import TenantRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException("Could not validate credentials")
            
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise UnauthorizedException("Could not validate credentials")
        
    user = await UserRepository.get_user_by_id(db, user_id)
    
    if user is None:
        raise UnauthorizedException("User not found")
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    if current_user.account_status != AccountStatus.ACTIVE:
        raise ForbiddenException("Inactive account")

    if current_user.role == UserRole.SUPERADMIN:
        return current_user

    tenant = await TenantRepository.get_by_id(db, current_user.tenant_id)
    if tenant is None or tenant.is_deleted:
        raise ForbiddenException("Inactive tenant")

    if tenant.verification_status != TenantVerificationStatus.ACTIVE:
        raise ForbiddenException("Tenant is not verified")

    if tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
        raise ForbiddenException("Inactive tenant")

    return current_user

def require_role(allowed_roles: list[UserRole]):
    """Return a dependency that restricts access to the given user roles."""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            roles_str = ", ".join([r.value for r in allowed_roles])
            raise ForbiddenException(f"Operation not permitted. Required roles: {roles_str}")
        return current_user
    return role_checker



async def require_tenant_ownership(
    tenant_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure the current user owns the tenant or is a superadmin."""
    if current_user.role == UserRole.SUPERADMIN:
        return current_user
    if current_user.tenant_id != tenant_id:
        raise ForbiddenException("You do not have access to this tenant's resources")
    return current_user

