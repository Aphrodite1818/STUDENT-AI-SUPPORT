#======================================#
#              service.py              #
#======================================#

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.classes.models import ClassRoom
from app.modules.classes.repository import ClassRoomRepository
from app.modules.classes.schemas import (
    ClassRoomCreate,
    ClassRoomResponse,
    ClassRoomUpdate,
)
from app.modules.teachers.repository import TeacherRepository


class ClassRoomService:
    """Business logic for classroom management."""

    @staticmethod
    async def create_classroom(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: ClassRoomCreate,
    ) -> ClassRoomResponse:
        """Create a tenant-scoped classroom."""

        existing_classroom = await ClassRoomRepository.get_classroom_by_name_and_arm(
            db=db,
            tenant_id=tenant_id,
            class_name=payload.name,
            class_arm=payload.arm,
        )

        if existing_classroom is not None:
            raise BadRequestException(
                "Classroom with this name and arm already exists"
            )

        if payload.teacher_id is not None:
            teacher = await TeacherRepository.get_teacher_by_id(
                db=db,
                tenant_id=tenant_id,
                teacher_id=payload.teacher_id,
            )

            if teacher is None:
                raise NotFoundException("Teacher not found")

            if hasattr(teacher, "is_active") and teacher.is_active is False:
                raise BadRequestException("Cannot assign an inactive teacher")

        classroom = ClassRoom(
            tenant_id=tenant_id,
            name=payload.name,
            level=payload.level,
            arm=payload.arm,
            teacher_id=payload.teacher_id,
            is_active=True,
        )

        created_classroom = await ClassRoomRepository.create_classroom(
            db=db,
            class_room=classroom,
        )

        return ClassRoomResponse.model_validate(created_classroom)

    @staticmethod
    async def get_classroom_by_id(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID,
    ) -> ClassRoomResponse:
        """Get classroom by ID."""

        classroom = await ClassRoomRepository.get_classroom_by_id(
            db=db,
            tenant_id=tenant_id,
            class_id=class_id,
        )

        if classroom is None:
            raise NotFoundException("Classroom not found")

        return ClassRoomResponse.model_validate(classroom)

    @staticmethod
    async def get_all_classrooms(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ClassRoomResponse]:
        """Get all classrooms for a tenant."""

        classrooms = await ClassRoomRepository.get_all_classrooms(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )

        return [
            ClassRoomResponse.model_validate(classroom)
            for classroom in classrooms
        ]

    @staticmethod
    async def get_active_classrooms(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ClassRoomResponse]:
        """Get active classrooms for a tenant."""

        classrooms = await ClassRoomRepository.get_active_classrooms(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )

        return [
            ClassRoomResponse.model_validate(classroom)
            for classroom in classrooms
        ]

    @staticmethod
    async def update_classroom(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID,
        payload: ClassRoomUpdate,
    ) -> ClassRoomResponse:
        """Update classroom details."""

        classroom = await ClassRoomRepository.get_classroom_by_id(
            db=db,
            tenant_id=tenant_id,
            class_id=class_id,
        )

        if classroom is None:
            raise NotFoundException("Classroom not found")

        update_data = payload.model_dump(exclude_unset=True)

        new_name = update_data.get("name", classroom.name)
        new_arm = update_data.get("arm", classroom.arm)

        if new_name != classroom.name or new_arm != classroom.arm:
            existing_classroom = await ClassRoomRepository.get_classroom_by_name_and_arm(
                db=db,
                tenant_id=tenant_id,
                class_name=new_name,
                class_arm=new_arm,
            )

            if (
                existing_classroom is not None
                and existing_classroom.id != classroom.id
            ):
                raise BadRequestException(
                    "Classroom with this name and arm already exists"
                )

        if "teacher_id" in update_data and update_data["teacher_id"] is not None:
            teacher = await TeacherRepository.get_teacher_by_id(
                db=db,
                tenant_id=tenant_id,
                teacher_id=update_data["teacher_id"],
            )

            if teacher is None:
                raise NotFoundException("Teacher not found")

            if hasattr(teacher, "is_active") and teacher.is_active is False:
                raise BadRequestException("Cannot assign an inactive teacher")

        for field, value in update_data.items():
            setattr(classroom, field, value)

        updated_classroom = await ClassRoomRepository.update_classroom(
            db=db,
            classroom=classroom,
        )

        return ClassRoomResponse.model_validate(updated_classroom)

    @staticmethod
    async def deactivate_classroom(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID,
    ) -> ClassRoomResponse:
        """Soft-delete classroom."""

        classroom = await ClassRoomRepository.deactivate_classroom(
            db=db,
            tenant_id=tenant_id,
            class_id=class_id,
        )

        if classroom is None:
            raise NotFoundException("Classroom not found")

        return ClassRoomResponse.model_validate(classroom)