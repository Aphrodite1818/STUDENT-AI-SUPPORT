#======================================#
#            repository.py             #
#======================================#

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.classes.models import ClassRoom


class ClassRoomRepository:
    """Database layer for classroom records."""

    @staticmethod
    async def create_classroom(
        db: AsyncSession,
        class_room: ClassRoom,
    ) -> ClassRoom:
        """Create classroom within tenant scope."""

        db.add(class_room)
        await db.flush()
        await db.refresh(class_room)
        return class_room

    @staticmethod
    async def get_classroom_by_id(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID,
    ) -> ClassRoom | None:
        """Get classroom by id within tenant scope."""

        result = await db.execute(
            select(ClassRoom).where(
                ClassRoom.tenant_id == tenant_id,
                ClassRoom.id == class_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_classroom_by_name_and_arm(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_name: str,
        class_arm: str,
    ) -> ClassRoom | None:
        """Get classroom by name and arm within tenant scope."""

        result = await db.execute(
            select(ClassRoom).where(
                ClassRoom.tenant_id == tenant_id,
                ClassRoom.name == class_name,
                ClassRoom.arm == class_arm,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_classrooms(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        limit: int = 100,
        skip: int = 0,
    ) -> list[ClassRoom]:
        """Get all classrooms within tenant scope."""

        result = await db.execute(
            select(ClassRoom)
            .where(ClassRoom.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_active_classrooms(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        limit: int = 100,
        skip: int = 0,
    ) -> list[ClassRoom]:
        """Get active classrooms within tenant scope."""

        result = await db.execute(
            select(ClassRoom)
            .where(
                ClassRoom.tenant_id == tenant_id,
                ClassRoom.is_active.is_(True),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_classroom(
        db: AsyncSession,
        classroom: ClassRoom,
    ) -> ClassRoom:
        """Persist classroom updates."""

        await db.flush()
        await db.refresh(classroom)
        return classroom

    @staticmethod
    async def deactivate_classroom(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID,
    ) -> ClassRoom | None:
        """Soft-delete classroom by setting is_active to False."""

        classroom = await ClassRoomRepository.get_classroom_by_id(
            db=db,
            tenant_id=tenant_id,
            class_id=class_id,
        )

        if classroom is None:
            return None

        classroom.is_active = False

        await db.flush()
        await db.refresh(classroom)

        return classroom

    @staticmethod
    async def classroom_exists_by_name_and_arm(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_name: str,
        class_arm: str,
    ) -> bool:
        """Check whether classroom already exists by name and arm."""

        result = await db.execute(
            select(ClassRoom.id).where(
                ClassRoom.tenant_id == tenant_id,
                ClassRoom.name == class_name,
                ClassRoom.arm == class_arm,
            )
        )

        return result.scalar_one_or_none() is not None