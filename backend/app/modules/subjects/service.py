#==========================#
#    subjects/service.py   #
#==========================#

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.subjects.models import Subject
from app.modules.subjects.repository import SubjectRepository
from app.modules.subjects.schemas import SubjectCreate, SubjectUpdate
from app.modules.teachers.models import TeacherStatus
from app.modules.teachers.repository import TeacherRepository
from app.modules.users.models import User, UserRole


class SubjectService:
    """Business logic for tenant-configured subjects."""

    @staticmethod
    def _ensure_admin(actor: User) -> None:
        """Internal helper for ensure admin."""
        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(detail="Only tenant admins can perform this action.")

        if not actor.tenant_id:
            raise ForbiddenException(detail="User is not attached to a tenant.")

    @staticmethod
    async def create_subject(
        db: AsyncSession,
        actor: User,
        subject_data: SubjectCreate,
    ) -> Subject:
        """Create subject."""
        SubjectService._ensure_admin(actor)

        existing_name = await SubjectRepository.get_subject_by_name(
            db=db,
            tenant_id=actor.tenant_id,
            subject_name=subject_data.name,
        )

        if existing_name:
            raise BadRequestException(detail="A subject with this name already exists.")

        if subject_data.code:
            existing_code = await SubjectRepository.get_subject_by_code(
                db=db,
                tenant_id=actor.tenant_id,
                subject_code=subject_data.code,
            )

            if existing_code:
                raise BadRequestException(detail="A subject with this code already exists.")

        unique_teacher_ids = list(dict.fromkeys(subject_data.teacher_ids))

        if unique_teacher_ids:
            teachers = await TeacherRepository.get_teachers_by_ids(
                db=db,
                tenant_id=actor.tenant_id,
                teacher_ids=unique_teacher_ids,
                status=TeacherStatus.ACTIVE,
            )

            if len(teachers) != len(unique_teacher_ids):
                raise BadRequestException(
                    detail="One or more selected teachers are not active in this school."
                )

        subject = Subject(
            tenant_id=actor.tenant_id,
            name=subject_data.name,
            code=subject_data.code,
            description=subject_data.description,
        )

        try:
            created_subject = await SubjectRepository.create_subject(
                db=db,
                subject=subject,
            )

            if unique_teacher_ids:
                await SubjectRepository.create_teacher_subject_links(
                    db=db,
                    tenant_id=actor.tenant_id,
                    subject_id=created_subject.id,
                    teacher_ids=unique_teacher_ids,
                )

            await db.commit()
            await db.refresh(created_subject)

            subject_with_teachers = await SubjectRepository.get_subject_by_id(
                db=db,
                tenant_id=actor.tenant_id,
                subject_id=created_subject.id,
            )

            if not subject_with_teachers:
                raise NotFoundException(detail="Subject not found after creation.")

            return subject_with_teachers

        except IntegrityError as exc:
            await db.rollback()
            raise BadRequestException(
                detail="Subject creation failed because of a duplicate or invalid value."
            ) from exc

    @staticmethod
    async def get_subject(
        db: AsyncSession,
        actor: User,
        subject_id: UUID,
    ) -> Subject:
        """Return subject."""
        if actor.role not in (UserRole.ADMIN, UserRole.TEACHER):
            raise ForbiddenException(detail="You are not allowed to view subjects.")

        if not actor.tenant_id:
            raise ForbiddenException(detail="User is not attached to a tenant.")

        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=subject_id,
        )

        if not subject:
            raise NotFoundException(detail="Subject not found.")

        return subject

    @staticmethod
    async def list_subjects(
        db: AsyncSession,
        actor: User,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Subject], int]:
        """List subjects."""
        if actor.role not in (UserRole.ADMIN, UserRole.TEACHER):
            raise ForbiddenException(detail="You are not allowed to view subjects.")

        if not actor.tenant_id:
            raise ForbiddenException(detail="User is not attached to a tenant.")

        limit = min(limit, 100)

        return await SubjectRepository.list_all_subjects(
            db=db,
            tenant_id=actor.tenant_id,
            skip=skip,
            limit=limit,
            is_active=is_active,
            search=search,
        )

    @staticmethod
    async def update_subject(
        db: AsyncSession,
        actor: User,
        subject_id: UUID,
        subject_data: SubjectUpdate,
    ) -> Subject:
        """Update subject."""
        SubjectService._ensure_admin(actor)

        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=subject_id,
        )

        if not subject:
            raise NotFoundException(detail="Subject not found.")

        update_data = subject_data.model_dump(exclude_unset=True)

        if not update_data:
            raise BadRequestException(detail="No update data provided.")

        if "name" in update_data and update_data["name"] is None:
            raise BadRequestException(detail="Subject name cannot be empty.")

        teacher_ids = update_data.pop("teacher_ids", None)

        if teacher_ids is not None:
            unique_teacher_ids = list(dict.fromkeys(teacher_ids))

            if unique_teacher_ids:
                teachers = await TeacherRepository.get_teachers_by_ids(
                    db=db,
                    tenant_id=actor.tenant_id,
                    teacher_ids=unique_teacher_ids,
                    status=TeacherStatus.ACTIVE,
                )

                if len(teachers) != len(unique_teacher_ids):
                    raise BadRequestException(
                        detail="One or more selected teachers are not active in this school."
                    )
        else:
            unique_teacher_ids = []

        if "name" in update_data and update_data["name"] != subject.name:
            existing_name = await SubjectRepository.get_subject_by_name(
                db=db,
                tenant_id=actor.tenant_id,
                subject_name=update_data["name"],
            )

            if existing_name:
                raise BadRequestException(detail="A subject with this name already exists.")

        if (
            "code" in update_data
            and update_data["code"] is not None
            and update_data["code"] != subject.code
        ):
            existing_code = await SubjectRepository.get_subject_by_code(
                db=db,
                tenant_id=actor.tenant_id,
                subject_code=update_data["code"],
            )

            if existing_code:
                raise BadRequestException(detail="A subject with this code already exists.")

        try:
            for field, value in update_data.items():
                setattr(subject, field, value)

            updated_subject = await SubjectRepository.update_subject(
                db=db,
                subject=subject,
            )

            if teacher_ids is not None:
                existing_teacher_ids = await SubjectRepository.get_subject_teacher_ids(
                    db=db,
                    tenant_id=actor.tenant_id,
                    subject_id=subject.id,
                )

                existing_teacher_id_set = set(existing_teacher_ids)
                incoming_teacher_id_set = set(unique_teacher_ids)

                teacher_ids_to_add = list(
                    incoming_teacher_id_set - existing_teacher_id_set
                )
                teacher_ids_to_remove = list(
                    existing_teacher_id_set - incoming_teacher_id_set
                )

                if teacher_ids_to_add:
                    await SubjectRepository.create_teacher_subject_links(
                        db=db,
                        tenant_id=actor.tenant_id,
                        subject_id=subject.id,
                        teacher_ids=teacher_ids_to_add,
                    )

                if teacher_ids_to_remove:
                    await SubjectRepository.delete_teacher_subject_links(
                        db=db,
                        tenant_id=actor.tenant_id,
                        subject_id=subject.id,
                        teacher_ids=teacher_ids_to_remove,
                    )

            await db.commit()
            await db.refresh(updated_subject)

            subject_with_teachers = await SubjectRepository.get_subject_by_id(
                db=db,
                tenant_id=actor.tenant_id,
                subject_id=updated_subject.id,
            )

            if not subject_with_teachers:
                raise NotFoundException(detail="Subject not found after update.")

            return subject_with_teachers

        except IntegrityError as exc:
            await db.rollback()
            raise BadRequestException(
                detail="Subject update failed because of a duplicate or invalid value."
            ) from exc

    @staticmethod
    async def activate_subject(
        db: AsyncSession,
        actor: User,
        subject_id: UUID,
    ) -> Subject:
        """Perform activate subject."""
        SubjectService._ensure_admin(actor)

        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=subject_id,
        )

        if not subject:
            raise NotFoundException(detail="Subject not found.")

        if subject.is_active:
            return subject

        subject.is_active = True
        updated_subject = await SubjectRepository.update_subject(db=db, subject=subject)

        await db.commit()
        await db.refresh(updated_subject)

        subject_with_teachers = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=updated_subject.id,
        )

        if not subject_with_teachers:
            raise NotFoundException(detail="Subject not found after activation.")

        return subject_with_teachers

    @staticmethod
    async def deactivate_subject(
        db: AsyncSession,
        actor: User,
        subject_id: UUID,
    ) -> Subject:
        """Perform deactivate subject."""
        SubjectService._ensure_admin(actor)

        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=subject_id,
        )

        if not subject:
            raise NotFoundException(detail="Subject not found.")

        if not subject.is_active:
            return subject

        subject.is_active = False
        updated_subject = await SubjectRepository.update_subject(db=db, subject=subject)

        await db.commit()
        await db.refresh(updated_subject)

        subject_with_teachers = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=updated_subject.id,
        )

        if not subject_with_teachers:
            raise NotFoundException(detail="Subject not found after deactivation.")

        return subject_with_teachers

    @staticmethod
    async def delete_subject(
        db: AsyncSession,
        actor: User,
        subject_id: UUID,
    ) -> None:
        """Delete subject."""
        SubjectService._ensure_admin(actor)

        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            subject_id=subject_id,
        )

        if not subject:
            raise NotFoundException(detail="Subject not found.")

        await SubjectRepository.delete_subject(db=db, subject=subject)
        await db.commit()
