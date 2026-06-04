#======================================#
#    core/dependencies/route_guards.py #
#======================================#
"""
THIS FILE HANDLES PROTECTION OF ROUTES (MIDDLEWARE).
It consumes and verifies tokens to ensure users are authenticated and authorized
to access specific endpoints. Business logic for auth (like login) lives in modules/auth.
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import uuid

from backend.app.config.settings import settings
from backend.app.core.dependencies.db import get_db
from backend.app.core.exceptions import UnauthorizedException, ForbiddenException
from backend.app.modules.users.models import User, AccountStatus, UserRole
from backend.app.modules.users.repository import UserRepository

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
        
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id)
    
    if user is None:
        raise UnauthorizedException("User not found")
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.account_status in [AccountStatus.BANNED, AccountStatus.DEACTIVATED, AccountStatus.SUSPENDED]:
        raise ForbiddenException("Inactive account")
    return current_user

def require_role(allowed_roles: list[UserRole]):
    """
    Dependency to enforce role-based access control.
    Usage: Depends(require_role([UserRole.ADMIN, UserRole.SUPERADMIN]))
    """
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
    """
    Dependency to ensure the user belongs to the requested tenant or is a superadmin.
    """
    if current_user.role == UserRole.SUPERADMIN:
        return current_user
    if current_user.tenant_id != tenant_id:
        raise ForbiddenException("You do not have access to this tenant's resources")
    return current_user
