"""Authentication and authorization dependencies for tenant users and superadmins."""

import uuid
from collections.abc import Callable, Coroutine
from typing import Annotated, Any, TypeAlias

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.dependencies.db import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.modules.auth_identity.models import ActorType
from app.modules.superadmin.models import SuperAdmin
from app.modules.superadmin.repository import SuperAdminRepository
from app.modules.tenant_admins.models import TenantAdmin, TenantAdminStatus
from app.modules.tenant_admins.repository import TenantAdminRepository
from app.modules.users.models import AccountStatus, User, UserRole
from app.modules.users.repository import UserRepository
from app.tenant_management.models import TenantStatus, TenantVerificationStatus
from app.tenant_management.repository import TenantRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
TokenDependency: TypeAlias = Annotated[str, Depends(oauth2_scheme)]
DbDependency: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


async def get_current_actor(
    token: TokenDependency,
    db: DbDependency,
) -> User | TenantAdmin | SuperAdmin:
    """Return current actor."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        actor_id_str: str | None = payload.get("sub")
        actor_type: str | None = payload.get("actor_type")
        account_type: str | None = payload.get("account_type")
        if actor_id_str is None:
            raise UnauthorizedException("Could not validate credentials")

        actor_id = uuid.UUID(actor_id_str)
        if actor_type is None and account_type is None:
            account_type = "superadmin" if payload.get("role") == "superadmin" else "tenant_user"
    except (JWTError, ValueError):
        raise UnauthorizedException("Could not validate credentials")

    if actor_type == ActorType.TENANT_ADMIN.value:
        tenant_admin = await TenantAdminRepository.get_by_id(db, actor_id)
        if tenant_admin is None:
            raise UnauthorizedException("Tenant admin not found")
        return tenant_admin

    if account_type == "superadmin":
        superadmin = await SuperAdminRepository.get_by_id(db, actor_id)
        if superadmin is None:
            raise UnauthorizedException("Superadmin not found")
        return superadmin

    tenant_user = await UserRepository.get_user_by_id(db, actor_id)
    if tenant_user is None:
        raise UnauthorizedException("User not found")
    return tenant_user







async def get_current_tenant_user(
    actor: Annotated[User | TenantAdmin | SuperAdmin, Depends(get_current_actor)],
    db: DbDependency,
) -> User:
    """Return current tenant user."""
    if isinstance(actor, SuperAdmin):
        raise ForbiddenException("Tenant user credentials are required for this operation")

    if isinstance(actor, TenantAdmin):
        if not actor.is_active or actor.account_status != TenantAdminStatus.ACTIVE:
            raise ForbiddenException("Inactive account")

        tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
        if tenant is None or tenant.is_deleted:
            raise ForbiddenException("Inactive tenant")
        if tenant.verification_status != TenantVerificationStatus.ACTIVE:
            raise ForbiddenException("Tenant is not verified")
        if tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
            raise ForbiddenException("Inactive tenant")

        raise ForbiddenException("Tenant user credentials are required for this operation")

    if actor.account_status != AccountStatus.ACTIVE:
        raise ForbiddenException("Inactive account")

    tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
    if tenant is None or tenant.is_deleted:
        raise ForbiddenException("Inactive tenant")
    if tenant.verification_status != TenantVerificationStatus.ACTIVE:
        raise ForbiddenException("Tenant is not verified")
    if tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
        raise ForbiddenException("Inactive tenant")

    return actor










async def get_current_tenant_admin(
    actor: Annotated[User | TenantAdmin | SuperAdmin, Depends(get_current_actor)],
    db: DbDependency,
) -> TenantAdmin:
    """Return current tenant admin."""
    if isinstance(actor, SuperAdmin):
        raise ForbiddenException("Tenant admin credentials are required for this operation")

    if isinstance(actor, User):
        raise ForbiddenException("Tenant admin credentials are required for this operation")

    if not actor.is_active:
        raise ForbiddenException("Inactive account")
    if not actor.is_verified:
        raise ForbiddenException("Tenant admin account is not verified")
    if actor.account_status != TenantAdminStatus.ACTIVE:
        raise ForbiddenException("Inactive account")

    tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
    if tenant is None or tenant.is_deleted:
        raise ForbiddenException("Inactive tenant")
    if tenant.verification_status != TenantVerificationStatus.ACTIVE:
        raise ForbiddenException("Tenant is not verified")
    if tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
        raise ForbiddenException("Inactive tenant")

    return actor


async def get_current_tenant_member(
    actor: Annotated[User | TenantAdmin | SuperAdmin, Depends(get_current_actor)],
    db: DbDependency,
) -> User | TenantAdmin:
    """Return the current tenant-scoped actor."""
    if isinstance(actor, SuperAdmin):
        raise ForbiddenException("Tenant credentials are required for this operation")

    if isinstance(actor, TenantAdmin):
        return await get_current_tenant_admin(actor, db)

    if actor.account_status != AccountStatus.ACTIVE:
        raise ForbiddenException("Inactive account")

    tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
    if tenant is None or tenant.is_deleted:
        raise ForbiddenException("Inactive tenant")
    if tenant.verification_status != TenantVerificationStatus.ACTIVE:
        raise ForbiddenException("Tenant is not verified")
    if tenant.status not in (TenantStatus.ACTIVE, TenantStatus.TRIAL):
        raise ForbiddenException("Inactive tenant")

    return actor


async def get_current_superadmin(
    actor: Annotated[User | TenantAdmin | SuperAdmin, Depends(get_current_actor)],
) -> SuperAdmin:
    """Return current superadmin."""
    if isinstance(actor, (User, TenantAdmin)):
        raise ForbiddenException("Superadmin credentials are required for this operation")
    if not actor.is_active:
        raise ForbiddenException("Inactive superadmin account")
    return actor







async def require_superadmin(
    current_superadmin: Annotated[SuperAdmin, Depends(get_current_superadmin)],
) -> SuperAdmin:
    """Return a dependency that requires superadmin."""
    return current_superadmin








def require_tenant_role(
    allowed_roles: list[UserRole],
) -> Callable[..., Coroutine[Any, Any, User]]:
    """Return a dependency that requires tenant role."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_tenant_user)],
    ) -> User:
        """Check whether the current user has one of the allowed roles."""
        if current_user.role not in allowed_roles:
            roles_str = ", ".join(role.value for role in allowed_roles)
            raise ForbiddenException(
                f"Operation not permitted. Required roles: {roles_str}"
            )
        return current_user

    return role_checker






async def require_tenant_ownership(
    tenant_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_tenant_user)],
) -> User:
    """Return a dependency that requires tenant ownership."""
    if current_user.tenant_id != tenant_id:
        raise ForbiddenException("You do not have access to this tenant's resources")
    return current_user
