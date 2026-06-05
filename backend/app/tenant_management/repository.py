#======================================#
#    tenant_management/repository.py   #
#======================================#
"""
Provides a reusable data access layer (Repository) for Tenant entities.

The TenantRepository class contains static methods that encapsulate database
CRUD operations for tenants. Using static methods allows services to execute 
queries without needing to instantiate the repository.
"""


import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , update
from backend.app.tenant_management.models import Tenant, TenantStatus, TenantVerificationStatus
from datetime import datetime , timezone




class TenantRepository:
    """READ METHODS"""
    @staticmethod
    async def get_by_id(db: AsyncSession , tenant_id : uuid.UUID) -> Tenant | None:
        result = await db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.is_deleted == False #returns tenant who are not soft deleted
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_slug(db : AsyncSession , slug : str) -> Tenant | None:
        result = await db.execute(
            select(Tenant).where(
                Tenant.slug == slug,
                Tenant.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db : AsyncSession , email : str) -> Tenant | None:
        result = await db.execute(
            select(Tenant).where(
                Tenant.email == email,
                Tenant.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_school_bot_number(db : AsyncSession , school_bot_whatssap_number : str) -> Tenant | None:
        result = await db.execute(
            select(Tenant).where(
                Tenant.school_bot_whatssap_number == school_bot_whatssap_number,
                Tenant.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    

    @staticmethod
    async def get_all(
        db : AsyncSession,
        skip : int = 0 ,
        limit : int = 50
    ) -> list[Tenant]:
        """Super admin only - list all tenants"""
        result = await db.execute(
            select(Tenant)
            .where(Tenant.is_deleted == False)
            .offset(skip) #where to start from
            .limit(limit) #limit of record to return
        )
        return list(result.scalars().all()) #.all converts records to a list
    

    """WRITE METHODS"""
    @staticmethod
    async def create(db : AsyncSession , tenant : Tenant ) -> Tenant:
        db.add(tenant)
        await db.flush() #temporary stores data
        return tenant
    

    @staticmethod
    async def update(db : AsyncSession , tenant_id : uuid.UUID , update_data : dict) -> Tenant | None:
        await db.execute(
            update(Tenant).where(
                Tenant.id == tenant_id)
                .values(**update_data) #provided fields to unpack and update
            )
        return await TenantRepository.get_by_id(db , tenant_id) #returns the entire row as response
    


    """DELELTE METHOD"""
    @staticmethod
    async def soft_delete(db : AsyncSession , tenant_id : uuid.UUID) -> int:
        await db.execute(
            update(Tenant).where(
                Tenant.id == tenant_id
            ).values(is_deleted = True , deleted_at = datetime.now(timezone.utc))
        )
    



    """EXISTENCE CHECK"""
    @staticmethod
    async def email_exists(db : AsyncSession , email: str) -> bool:
        result = await db.execute(
            select(Tenant.id).where(Tenant.email == email)

        )
        return result.scalar_one_or_none() is not None
    

    @staticmethod
    
    async def slug_exists(db : AsyncSession , slug: str) -> bool:
        result = await db.execute(
            select(Tenant.id).where(Tenant.slug == slug)

        )
        return result.scalar_one_or_none() is not None #this  returns True if the result is not None , but returns false if None
    
    @staticmethod
    async def school_bot_whatssap_number_exists(db : AsyncSession , whatssap_number : str) -> bool:
        result = await db.execute(
            select(Tenant.id).where(Tenant.school_bot_whatssap_number == whatssap_number)
        )
        return result.scalar_one_or_none() is not None
    

    @staticmethod
    async def is_verified(db : AsyncSession , email : str ):
        result = await db.execute(
            select(Tenant.verification_status).where(Tenant.email == email)
        )
        return result.scalar_one_or_none() == TenantVerificationStatus.ACTIVE

