#======================================#
#              service.py              #
#======================================#

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.subjects.repository import SubjectRepository
from app.modules.teachers.models import Teacher, TeacherStatus
from app.modules.teachers.repository import TeacherRepository
from app.modules.teachers.schemas import TeacherUpdate
from app.modules.users.models import User, UserRole


class TeacherService:
    """Business logic for tenant teacher profiles"""

    @staticmethod
    def _ensure_tenant_user(actor: User) -> None:
        if not actor.tenant_id:
            raise ForbiddenException(detail="User is not attached to a tenant")

    @staticmethod
    def _ensure_admin(actor: User) -> None:
        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(detail="Only tenant admins can perform this action")

        TeacherService._ensure_tenant_user(actor)

    @staticmethod
    async def get_teacher(
        db: AsyncSession,
        actor: User,
        teacher_id: UUID,
    ) -> Teacher:
        TeacherService._ensure_tenant_user(actor)

        if actor.role not in (UserRole.ADMIN, UserRole.TEACHER):
            raise ForbiddenException(detail="You are not allowed to view teacher")

        teacher = await TeacherRepository.get_teacher_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            teacher_id=teacher_id,
        )

        if not teacher:
            raise NotFoundException(detail="Teacher not found")

        if actor.role == UserRole.TEACHER and teacher.user_id != actor.id:
            raise ForbiddenException(detail="You are not allowed to view this teacher")

        return teacher

    @staticmethod
    async def list_teachers(
        db: AsyncSession,
        actor: User,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> tuple[list[Teacher], int]:
        TeacherService._ensure_admin(actor)
        limit = min(limit, 100)

        return await TeacherRepository.list_all_teachers(
            db=db,
            tenant_id=actor.tenant_id,
            skip=skip,
            limit=limit,
            search=search,
        )

    @staticmethod
    async def update_teacher(
        db: AsyncSession,
        actor: User,
        teacher_id: UUID,
        teacher_data: TeacherUpdate,
    ) -> Teacher:
        TeacherService._ensure_admin(actor)

        teacher = await TeacherRepository.get_teacher_by_id(
            db=db,
            teacher_id=teacher_id,
            tenant_id=actor.tenant_id,
        )

        if not teacher:
            raise NotFoundException(detail="Teacher not found")

        update_data = teacher_data.model_dump(exclude_unset=True)

        if not update_data:
            raise BadRequestException(detail="No update data provided")

        subject_ids = update_data.pop("subject_ids", None)

        if subject_ids and teacher.status != TeacherStatus.ACTIVE:
            raise BadRequestException(
                detail="Only active teachers can be assigned to subjects."
            )

        if (
            "staff_id" in update_data
            and update_data["staff_id"] is not None
            and update_data["staff_id"] != teacher.staff_id
        ):
            existing_staff_id = await TeacherRepository.get_teacher_by_staff_id(
                db=db,
                tenant_id=actor.tenant_id,
                staff_id=update_data["staff_id"],
            )

            if existing_staff_id:
                raise BadRequestException(
                    detail="A teacher with this staff ID already exists"
                )

        try:
            if update_data:
                teacher = await TeacherRepository.update_teacher(
                    db=db,
                    teacher=teacher,
                    update_data=update_data,
                )

            if subject_ids is not None:
                unique_subject_ids = list(set(subject_ids))

                if unique_subject_ids:
                    subjects = await SubjectRepository.get_subjects_by_id(
                        db=db,
                        tenant_id=actor.tenant_id,
                        subject_ids=unique_subject_ids,
                    )

                    if len(subjects) != len(unique_subject_ids):
                        raise BadRequestException(
                            detail="One or more selected subjects do not exist in this school."
                        )

                existing_subject_ids = await TeacherRepository.get_teacher_subject_ids(
                    db=db,
                    tenant_id=actor.tenant_id,
                    teacher_id=teacher.id,
                )

                existing_subject_id_set = set(existing_subject_ids)
                incoming_subject_id_set = set(unique_subject_ids)

                subject_ids_to_add = list(
                    incoming_subject_id_set - existing_subject_id_set
                )
                subject_ids_to_remove = list(
                    existing_subject_id_set - incoming_subject_id_set
                )

                if subject_ids_to_add:
                    await TeacherRepository.create_teacher_subject_links(
                        db=db,
                        tenant_id=actor.tenant_id,
                        teacher_id=teacher.id,
                        subject_ids=subject_ids_to_add,
                    )

                if subject_ids_to_remove:
                    await TeacherRepository.delete_teacher_subject_links(
                        db=db,
                        tenant_id=actor.tenant_id,
                        teacher_id=teacher.id,
                        subject_ids=subject_ids_to_remove,
                    )

            await db.commit()

            updated_teacher = await TeacherRepository.get_teacher_by_id(
                db=db,
                tenant_id=actor.tenant_id,
                teacher_id=teacher.id,
            )

            if not updated_teacher:
                raise NotFoundException(detail="Teacher not found after update.")

            return updated_teacher

        except IntegrityError as exc:
            await db.rollback()
            raise BadRequestException(
                detail="Teacher update failed because of a duplicate or invalid value."
            ) from exc

    @staticmethod
    async def delete_teacher(
        db: AsyncSession,
        actor: User,
        teacher_id: UUID,
    ) -> None:
        TeacherService._ensure_admin(actor)

        teacher = await TeacherRepository.get_teacher_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            teacher_id=teacher_id,
        )

        if not teacher:
            raise NotFoundException(detail="Teacher not found")

        await TeacherRepository.update_teacher_status(
            db=db,
            teacher=teacher,
            status=TeacherStatus.ARCHIVED,
        )
        await TeacherRepository.delete_all_teacher_subject_links(
            db=db,
            tenant_id=actor.tenant_id,
            teacher_id=teacher.id,
        )
        await db.commit()
