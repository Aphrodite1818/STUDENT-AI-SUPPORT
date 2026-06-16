from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parents.models import Parent


class ParentRepository:
    """Database operations for parent profiles."""

    @staticmethod
    async def create_parent(
        db: AsyncSession,
        parent: Parent,
    ) -> Parent:
        """Create a parent profile."""
        db.add(parent)
        await db.flush()
        await db.refresh(parent)
        return parent

    @staticmethod
    async def get_parent_by_id(
        db: AsyncSession,
        tenant_id: UUID,
        parent_id: UUID,
    ) -> Parent | None:
        """Get parent profile by id within tenant."""
        result = await db.execute(
            select(Parent).where(
                Parent.id == parent_id,
                Parent.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_parent_by_user_id(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
    ) -> Parent | None:
        """Get parent profile by user id."""
        result = await db.execute(
            select(Parent).where(
                Parent.tenant_id == tenant_id,
                Parent.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_parents(
        db: AsyncSession,
        tenant_id: UUID,
        limit: int = 100,
        skip: int = 0,
    ) -> list[Parent]:
        """Get all parent profiles within tenant."""
        result = await db.execute(
            select(Parent)
            .where(Parent.tenant_id == tenant_id)
            .order_by(Parent.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_parents(
        db: AsyncSession,
        tenant_id: UUID,
    ) -> int:
        """Count parent profiles within tenant."""
        result = await db.execute(
            select(func.count()).select_from(Parent).where(Parent.tenant_id == tenant_id)
        )
        return result.scalar_one()

    @staticmethod
    async def update_parent(
        db: AsyncSession,
        parent: Parent,
    ) -> Parent:
        """Persist parent profile updates."""
        await db.flush()
        await db.refresh(parent)
        return parent

    @staticmethod
    async def delete_parent(
        db: AsyncSession,
        parent: Parent,
    ) -> None:
        """Delete a parent profile."""
        await db.delete(parent)
        await db.flush()
