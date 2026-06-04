#======================================#
#     tenant_management/service.py     #
#======================================#

"""THIS IS WHERE THE BUSINESS LOGIC FOR TENANTS LIVE"""

from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone, timedelta

from backend.app.tenant_management.repository import TenantRepository
from backend.app.tenant_management.models import Tenant, TenantStatus
from backend.app.tenant_management.schemas import (
    TenantCreate,
    TenantUpdate,
    TenantStatusUpdate,
    TenantRegisterRequest
)

# 1. FIXED IMPORT PATH
from backend.app.core.exceptions import (
    NotFoundException,
    ConflictException,
)

from backend.app.core.utils.validators import generate_slug
from backend.app.config.security import hash_password

# Import the User model to create the Admin account
from backend.app.modules.users.models import User, UserRole, AccountStatus


class TenantService:
    @staticmethod
    async def register_tenant(db: AsyncSession, payload: TenantRegisterRequest) -> Tenant:
        # check for duplicate email
        if await TenantRepository.email_exists(db, payload.email):
            raise ConflictException("A school with this email already exists")
        
        slug = generate_slug(payload.school_name)
        password_hashed = hash_password(payload.password)

        # 2. FIXED TENANT CREATION (no hash_password field)
        tenant = Tenant(
            school_name=payload.school_name,
            slug=slug,
            email=payload.email
        )
        
        # Flush to get the new tenant ID (but don't commit yet)
        db.add(tenant)
        await db.flush()

        # 3. CREATE THE ADMIN USER
        admin_user = User(
            email=payload.email,
            password_hash=password_hashed,
            role=UserRole.ADMIN,
            account_status=AccountStatus.PENDING,
            tenant_id=tenant.id
        )
        
        db.add(admin_user)
        
        await db.commit()
        await db.refresh(tenant)

        return tenant


    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        return tenant
    

    @staticmethod
    async def superadmin_create_tenant(db: AsyncSession, payload: TenantCreate) -> Tenant:
        """superadmin can create a tenant and send them invite link to complete their user profile"""
        # 1. Check for duplicate email
        if await TenantRepository.email_exists(db, payload.email):
            raise ConflictException("A school with this email already exists")
            
        # 2. Check for duplicate bot number
        if payload.school_bot_whatssap_number:
            if await TenantRepository.school_bot_whatssap_number_exists(db, payload.school_bot_whatssap_number):
                raise ConflictException("This WhatsApp number is already in use by another school")

        # 3. Generate Slug
        slug = generate_slug(payload.school_name)
        
        # 4. Build the dictionary from the payload
        tenant_data = payload.model_dump()
        # Rename the whatsapp field to match the database model column name
        if "school_bot_whatssap_number" in tenant_data:
            tenant_data["school_bot_number"] = tenant_data.pop("school_bot_whatssap_number")

        # 5. Create Tenant (No user is created here, just the Tenant record)
        tenant = Tenant(**tenant_data, slug=slug)
        db.add(tenant)
        
        await db.commit()
        await db.refresh(tenant)
        return tenant

    @staticmethod
    async def get_all_tenants(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Tenant]:
        return await TenantRepository.get_all(db, skip=skip, limit=limit)
    

    @staticmethod
    async def update_tenant_profile(db: AsyncSession, tenant_id: uuid.UUID, payload: TenantUpdate) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
        

            
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return tenant # Nothing to update
            
        # If changing bot number, ensure no conflict
        if "school_bot_number" in update_data and update_data["school_bot_number"]:
            if await TenantRepository.school_bot_whatssap_number_exists(db, update_data["school_bot_number"]):
                raise ConflictException("This WhatsApp number is already in use by another school")
        updated_tenant = await TenantRepository.update(db, tenant_id, update_data)
        await db.commit()
        return updated_tenant
    


    
    @staticmethod
    async def update_tenant_status(db: AsyncSession, tenant_id: uuid.UUID, payload: TenantStatusUpdate) -> Tenant:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
            
        # Here you could log the `payload.reason` to an audit table if you wanted to track status changes!
        updated_tenant = await TenantRepository.update(db, tenant_id, {"status": payload.status})
        await db.commit()
        return updated_tenant
    



    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
        tenant = await TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise NotFoundException("Tenant not found")
            
        await TenantRepository.soft_delete(db, tenant_id)
        await db.commit()
        return {"detail": "Tenant successfully deleted"}

    