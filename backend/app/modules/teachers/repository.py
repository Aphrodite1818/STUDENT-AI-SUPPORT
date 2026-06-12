#======================================#
#            repository.py             #
#======================================#

from uuid import UUID
from typing import Any

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.teachers.models import Teacher, TeacherStatus, TeacherSubject


class TeacherRepository:
    """Low level database queries for the teachers table"""

    @staticmethod
    async def create_teacher(
        db: AsyncSession,
        teacher: Teacher,
    ) -> Teacher:
        db.add(teacher)
        await db.flush()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def get_teacher_by_id(
        db: AsyncSession,
        tenant_id: UUID,
        teacher_id: UUID,
    ) -> Teacher | None:
        """used to retrieve the entire details of a teacher in the database"""
        result = await db.execute(
            select(Teacher)
            .options(
                selectinload(Teacher.subject_links).selectinload(
                    TeacherSubject.subject
                )
            )
            .where(
                Teacher.tenant_id == tenant_id,
                Teacher.id == teacher_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_teacher_by_user_id(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
    ) -> Teacher | None:
        """used to check if a teacher exists for a user in the database"""
        result = await db.execute(
            select(Teacher).where(
                Teacher.tenant_id == tenant_id,
                Teacher.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_teacher_by_staff_id(
        db: AsyncSession,
        tenant_id: UUID,
        staff_id: str,
    ) -> Teacher | None:
        """used to check if a teacher exists for a user in the database"""
        result = await db.execute(
            select(Teacher).where(
                Teacher.tenant_id == tenant_id,
                Teacher.staff_id == staff_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_teachers_by_ids(
        db: AsyncSession,
        teacher_ids: list[UUID],
        tenant_id: UUID,
        status: TeacherStatus | None = None,
    ) -> list[Teacher]:
        """returns a list of multiple teachers based on their ids"""
        filters = [
            Teacher.tenant_id == tenant_id,
            Teacher.id.in_(teacher_ids),
        ]
        if status is not None:
            filters.append(Teacher.status == status)

        result = await db.execute(select(Teacher).where(*filters))
        return list(result.scalars().all())

    @staticmethod
    async def list_all_teachers(
        db: AsyncSession,
        tenant_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> tuple[list[Teacher], int]:
        """returns a paginated list of all teachers available to tenant"""
        filters = [Teacher.tenant_id == tenant_id]

        if search:
            filters.append(
                or_(
                    Teacher.staff_id.ilike(f"%{search}%"),
                    Teacher.qualification.ilike(f"%{search}%"),
                    Teacher.specialization.ilike(f"%{search}%"),
                )
            )

        total_result = await db.execute(
            select(func.count()).select_from(Teacher).where(*filters)
        )

        total = total_result.scalar_one()

        result = await db.execute(
            select(Teacher)
            .options(
                selectinload(Teacher.subject_links).selectinload(
                    TeacherSubject.subject
                )
            )
            .where(*filters)
            .order_by(Teacher.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def update_teacher(
        db: AsyncSession,
        teacher: Teacher,
        update_data: dict[str, Any],
    ) -> Teacher:
        for field, value in update_data.items():
            setattr(teacher, field, value)

        await db.flush()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def update_teacher_status(
        db: AsyncSession,
        teacher: Teacher,
        status: TeacherStatus,
    ) -> Teacher:
        teacher.status = status
        await db.flush()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def create_teacher_subject_links(
        db: AsyncSession,
        tenant_id: UUID,
        teacher_id: UUID,
        subject_ids: list[UUID],
    ) -> list[TeacherSubject]:
        teacher_subject_links = [
            TeacherSubject(
                tenant_id=tenant_id,
                teacher_id=teacher_id,
                subject_id=subject_id,
            )
            for subject_id in subject_ids
        ]

        db.add_all(teacher_subject_links)
        await db.flush()
        return teacher_subject_links

    @staticmethod
    async def delete_teacher_subject_links(
        db: AsyncSession,
        tenant_id: UUID,
        teacher_id: UUID,
        subject_ids: list[UUID],
    ) -> None:
        await db.execute(
            delete(TeacherSubject).where(
                TeacherSubject.tenant_id == tenant_id,
                TeacherSubject.teacher_id == teacher_id,
                TeacherSubject.subject_id.in_(subject_ids),
            )
        )
        await db.flush()

    @staticmethod
    async def delete_all_teacher_subject_links(
        db: AsyncSession,
        tenant_id: UUID,
        teacher_id: UUID,
    ) -> None:
        await db.execute(
            delete(TeacherSubject).where(
                TeacherSubject.tenant_id == tenant_id,
                TeacherSubject.teacher_id == teacher_id,
            )
        )
        await db.flush()

    @staticmethod
    async def get_teacher_subject_ids(
        db: AsyncSession,
        tenant_id: UUID,
        teacher_id: UUID,
    ) -> list[UUID]:
        result = await db.execute(
            select(TeacherSubject.subject_id).where(
                TeacherSubject.tenant_id == tenant_id,
                TeacherSubject.teacher_id == teacher_id,
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def delete_teacher(
        db: AsyncSession,
        teacher: Teacher,
    ) -> None:
        teacher.status = TeacherStatus.ARCHIVED
        await db.execute(
            delete(TeacherSubject).where(
                TeacherSubject.tenant_id == teacher.tenant_id,
                TeacherSubject.teacher_id == teacher.id,
            )
        )
        await db.flush()
