import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)

from app.modules.auth_identity.models import ActorType
from app.modules.students.models import Student
from app.modules.students.repository import StudentParentLinkRepository, StudentRepository
from app.modules.student_academics.models import (
    AcademicResultStatus,
    AcademicSession,
    AcademicTerm,
    ClassSubjectTeacher,
    GradingScale,
    StudentSubjectResult,
)

from app.modules.student_academics.repository import StudentAcademicRepository

from app.modules.student_academics.schemas import (
    AcademicSessionCreate,
    AcademicSessionUpdate,
    AcademicTermCreate,
    AcademicTermUpdate,
    ClassSubjectTeacherCreate,
    ClassSubjectTeacherUpdate,
    GradingScaleCreate,
    GradingScaleUpdate,
    StudentSubjectResultResponse,
    StudentSubjectResultStatusUpdate,
    StudentSubjectResultUpsert,
)

from app.modules.classes.repository import ClassRoomRepository
from app.modules.subjects.repository import SubjectRepository
from app.modules.teachers.repository import TeacherRepository
from app.modules.parents.models import Parent
from app.modules.teachers.models import Teacher
from app.modules.tenant_admins.models import TenantAdmin


class StudentAcademicService:
    @staticmethod
    def _ensure_session_not_future_when_current(session_name: str) -> None:
        start_year = int(session_name.split("/")[0])
        current_year = date.today().year

        if start_year > current_year:
            raise BadRequestException(
                "You cannot set a future academic session as current."
            )

    @staticmethod
    async def create_academic_session(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: AcademicSessionCreate,
    ) -> AcademicSession:
        existing_session = await StudentAcademicRepository.get_academic_session_by_name(
            db=db,
            tenant_id=tenant_id,
            name=payload.name,
        )

        if existing_session is not None:
            raise ConflictException(
                "Academic session already exists for this tenant."
            )

        if payload.is_current:
            StudentAcademicService._ensure_session_not_future_when_current(
                payload.name
            )

            current_session = (
                await StudentAcademicRepository.get_current_academic_session(
                    db=db,
                    tenant_id=tenant_id,
                )
            )

            if current_session is not None:
                current_session.is_current = False
                await StudentAcademicRepository.save_academic_session(
                    db=db,
                    academic_session=current_session,
                )

        academic_session = AcademicSession(
            tenant_id=tenant_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_current=payload.is_current,
            is_active=payload.is_active,
        )

        created_session = await StudentAcademicRepository.create_academic_session(
            db=db,
            academic_session=academic_session,
        )

        await db.commit()
        return created_session

    @staticmethod
    async def update_academic_session(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        academic_session_id: uuid.UUID,
        payload: AcademicSessionUpdate,
    ) -> AcademicSession:
        academic_session = await StudentAcademicRepository.get_academic_session_by_id(
            db=db,
            tenant_id=tenant_id,
            academic_session_id=academic_session_id,
        )

        if academic_session is None:
            raise NotFoundException("Academic session not found.")

        update_data = payload.model_dump(exclude_unset=True)

        new_name = update_data.get("name")

        if new_name is not None and new_name != academic_session.name:
            existing_session = (
                await StudentAcademicRepository.get_academic_session_by_name(
                    db=db,
                    tenant_id=tenant_id,
                    name=new_name,
                )
            )

            if existing_session is not None:
                raise ConflictException(
                    "Academic session already exists for this tenant."
                )

        wants_current = update_data.get("is_current") is True

        if wants_current:
            session_name_to_validate = update_data.get(
                "name",
                academic_session.name,
            )

            StudentAcademicService._ensure_session_not_future_when_current(
                session_name_to_validate
            )

            current_session = (
                await StudentAcademicRepository.get_current_academic_session(
                    db=db,
                    tenant_id=tenant_id,
                )
            )

            if current_session is not None and current_session.id != academic_session.id:
                current_session.is_current = False
                await StudentAcademicRepository.save_academic_session(
                    db=db,
                    academic_session=current_session,
                )

        for field, value in update_data.items():
            setattr(academic_session, field, value)

        updated_session = await StudentAcademicRepository.save_academic_session(
            db=db,
            academic_session=academic_session,
        )

        await db.commit()
        return updated_session

    @staticmethod
    async def list_academic_sessions(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AcademicSession], int]:
        return await StudentAcademicRepository.list_academic_sessions(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    async def create_academic_term(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: AcademicTermCreate,
    ) -> AcademicTerm:
        academic_session = await StudentAcademicRepository.get_academic_session_by_id(
            db=db,
            tenant_id=tenant_id,
            academic_session_id=payload.academic_session_id,
        )

        if academic_session is None:
            raise NotFoundException("Academic session not found.")

        existing_term = await StudentAcademicRepository.get_term_by_session_and_name(
            db=db,
            tenant_id=tenant_id,
            academic_session_id=payload.academic_session_id,
            name=payload.name,
        )

        if existing_term is not None:
            raise ConflictException(
                "Academic term already exists for this academic session."
            )

        if payload.is_current:
            current_term = await StudentAcademicRepository.get_current_term(
                db=db,
                tenant_id=tenant_id,
            )

            if current_term is not None:
                current_term.is_current = False
                await StudentAcademicRepository.save_academic_term(
                    db=db,
                    academic_term=current_term,
                )

        academic_term = AcademicTerm(
            tenant_id=tenant_id,
            academic_session_id=payload.academic_session_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_current=payload.is_current,
            is_active=payload.is_active,
        )

        created_term = await StudentAcademicRepository.create_academic_term(
            db=db,
            academic_term=academic_term,
        )

        await db.commit()
        return created_term

    @staticmethod
    async def update_academic_term(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        term_id: uuid.UUID,
        payload: AcademicTermUpdate,
    ) -> AcademicTerm:
        academic_term = await StudentAcademicRepository.get_term_by_id(
            db=db,
            tenant_id=tenant_id,
            term_id=term_id,
        )

        if academic_term is None:
            raise NotFoundException("Academic term not found.")

        update_data = payload.model_dump(exclude_unset=True)
        new_name = update_data.get("name")

        if new_name is not None and new_name != academic_term.name:
            existing_term = await StudentAcademicRepository.get_term_by_session_and_name(
                db=db,
                tenant_id=tenant_id,
                academic_session_id=academic_term.academic_session_id,
                name=new_name,
            )

            if existing_term is not None:
                raise ConflictException(
                    "Academic term already exists for this academic session."
                )

        wants_current = update_data.get("is_current") is True

        if wants_current:
            current_term = await StudentAcademicRepository.get_current_term(
                db=db,
                tenant_id=tenant_id,
            )

            if current_term is not None and current_term.id != academic_term.id:
                current_term.is_current = False
                await StudentAcademicRepository.save_academic_term(
                    db=db,
                    academic_term=current_term,
                )

        for field, value in update_data.items():
            setattr(academic_term, field, value)

        updated_term = await StudentAcademicRepository.save_academic_term(
            db=db,
            academic_term=academic_term,
        )

        await db.commit()
        return updated_term

    @staticmethod
    async def list_academic_terms(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        academic_session_id: uuid.UUID | None = None,
    ) -> tuple[list[AcademicTerm], int]:
        if academic_session_id is not None:
            return await StudentAcademicRepository.list_terms_by_session(
                db=db,
                tenant_id=tenant_id,
                academic_session_id=academic_session_id,
                skip=skip,
                limit=limit,
            )

        return await StudentAcademicRepository.list_terms(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    async def create_grading_scale(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: GradingScaleCreate,
    ) -> GradingScale:
        existing_grade = await StudentAcademicRepository.get_grading_scale_by_grade(
            db=db,
            tenant_id=tenant_id,
            grade=payload.grade,
        )

        if existing_grade is not None:
            raise ConflictException("A grading scale with this grade already exists.")

        active_scales, _ = await StudentAcademicRepository.list_grading_scales(
            db=db,
            tenant_id=tenant_id,
            active_only=True,
            limit=100,
        )

        for scale in active_scales:
            overlaps = (
                payload.min_score <= scale.max_score
                and payload.max_score >= scale.min_score
            )

            if overlaps:
                raise ConflictException(
                    "Grading scale range overlaps with an existing active range."
                )

        grading_scale = GradingScale(
            tenant_id=tenant_id,
            min_score=payload.min_score,
            max_score=payload.max_score,
            grade=payload.grade,
            remark=payload.remark,
            is_active=payload.is_active,
        )

        created_scale = await StudentAcademicRepository.create_grading_scale(
            db=db,
            grading_scale=grading_scale,
        )

        await db.commit()
        return created_scale

    @staticmethod
    async def update_grading_scale(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        grading_scale_id: uuid.UUID,
        payload: GradingScaleUpdate,
    ) -> GradingScale:
        grading_scale = await StudentAcademicRepository.get_grading_scale_by_id(
            db=db,
            tenant_id=tenant_id,
            grading_scale_id=grading_scale_id,
        )

        if grading_scale is None:
            raise NotFoundException("Grading scale not found.")

        update_data = payload.model_dump(exclude_unset=True)

        new_grade = update_data.get("grade")

        if new_grade is not None and new_grade != grading_scale.grade:
            existing_grade = await StudentAcademicRepository.get_grading_scale_by_grade(
                db=db,
                tenant_id=tenant_id,
                grade=new_grade,
            )

            if existing_grade is not None:
                raise ConflictException(
                    "A grading scale with this grade already exists."
                )

        final_min_score = update_data.get("min_score", grading_scale.min_score)
        final_max_score = update_data.get("max_score", grading_scale.max_score)

        if final_min_score > final_max_score:
            raise BadRequestException(
                "Minimum score cannot be greater than maximum score."
            )

        active_scales, _ = await StudentAcademicRepository.list_grading_scales(
            db=db,
            tenant_id=tenant_id,
            active_only=True,
            limit=100,
        )

        for scale in active_scales:
            if scale.id == grading_scale.id:
                continue

            overlaps = (
                final_min_score <= scale.max_score
                and final_max_score >= scale.min_score
            )

            if overlaps:
                raise ConflictException(
                    "Grading scale range overlaps with an existing active range."
                )

        for field, value in update_data.items():
            setattr(grading_scale, field, value)

        updated_scale = await StudentAcademicRepository.save_grading_scale(
            db=db,
            grading_scale=grading_scale,
        )

        await db.commit()
        return updated_scale

    @staticmethod
    async def list_grading_scales(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> tuple[list[GradingScale], int]:
        return await StudentAcademicRepository.list_grading_scales(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            active_only=active_only,
        )

    @staticmethod
    async def resolve_grade_for_score(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        score: Decimal,
    ) -> GradingScale:
        grading_scale = await StudentAcademicRepository.find_grade_for_score(
            db=db,
            tenant_id=tenant_id,
            score=score,
        )

        if grading_scale is None:
            raise NotFoundException("No grading scale found for the supplied score.")

        return grading_scale

    @staticmethod
    async def assign_subject_to_class(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: ClassSubjectTeacherCreate,
    ) -> ClassSubjectTeacher:
        # Adjust method names below if your repositories use different names.
        classroom = await ClassRoomRepository.get_classroom_by_id(
            db=db,
            tenant_id=tenant_id,
            class_id=payload.class_id,
        )

        if classroom is None:
            raise NotFoundException("Class not found.")

        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=tenant_id,
            subject_id=payload.subject_id,
        )

        if subject is None:
            raise NotFoundException("Subject not found.")

        teacher = await TeacherRepository.get_teacher_by_id(
            db=db,
            tenant_id=tenant_id,
            teacher_id=payload.teacher_id,
        )

        if teacher is None:
            raise NotFoundException("Teacher not found.")

        existing_assignment = (
            await StudentAcademicRepository.get_class_subject_teacher_by_class_subject(
                db=db,
                tenant_id=tenant_id,
                class_id=payload.class_id,
                subject_id=payload.subject_id,
            )
        )

        if existing_assignment is not None:
            raise ConflictException("This subject is already assigned to this class.")

        assignment = ClassSubjectTeacher(
            tenant_id=tenant_id,
            class_id=payload.class_id,
            subject_id=payload.subject_id,
            teacher_id=payload.teacher_id,
            is_core=payload.is_core,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )

        created_assignment = (
            await StudentAcademicRepository.create_class_subject_teacher(
                db=db,
                assignment=assignment,
            )
        )

        await db.commit()
        return created_assignment

    @staticmethod
    async def update_class_subject_teacher(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        assignment_id: uuid.UUID,
        payload: ClassSubjectTeacherUpdate,
    ) -> ClassSubjectTeacher:
        assignment = await StudentAcademicRepository.get_class_subject_teacher_by_id(
            db=db,
            tenant_id=tenant_id,
            assignment_id=assignment_id,
        )

        if assignment is None:
            raise NotFoundException("Class subject teacher assignment not found.")

        update_data = payload.model_dump(exclude_unset=True)

        new_teacher_id = update_data.get("teacher_id")

        if new_teacher_id is not None and new_teacher_id != assignment.teacher_id:
            teacher = await TeacherRepository.get_teacher_by_id(
                db=db,
                tenant_id=tenant_id,
                teacher_id=new_teacher_id,
            )

            if teacher is None:
                raise NotFoundException("Teacher not found.")

        for field, value in update_data.items():
            setattr(assignment, field, value)

        updated_assignment = await StudentAcademicRepository.save_class_subject_teacher(
            db=db,
            assignment=assignment,
        )

        await db.commit()
        return updated_assignment

    @staticmethod
    async def list_class_subject_teachers(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        class_id: uuid.UUID | None = None,
        subject_id: uuid.UUID | None = None,
        teacher_id: uuid.UUID | None = None,
        active_only: bool = False,
    ) -> tuple[list[ClassSubjectTeacher], int]:
        return await StudentAcademicRepository.list_class_subject_teachers(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            active_only=active_only,
        )

    @staticmethod
    async def deactivate_class_subject_teacher(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        assignment_id: uuid.UUID,
    ) -> ClassSubjectTeacher:
        assignment = await StudentAcademicRepository.get_class_subject_teacher_by_id(
            db=db,
            tenant_id=tenant_id,
            assignment_id=assignment_id,
        )

        if assignment is None:
            raise NotFoundException("Class subject teacher assignment not found.")

        assignment.is_active = False

        deactivated_assignment = (
            await StudentAcademicRepository.save_class_subject_teacher(
                db=db,
                assignment=assignment,
            )
        )

        await db.commit()
        return deactivated_assignment

    @staticmethod
    async def list_teacher_assignments(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        teacher_id: uuid.UUID,
        active_only: bool = True,
    ) -> list[ClassSubjectTeacher]:
        return await StudentAcademicRepository.list_teacher_assignments(
            db=db,
            tenant_id=tenant_id,
            teacher_id=teacher_id,
            active_only=active_only,
        )

    @staticmethod
    async def list_class_assignments(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID,
        active_only: bool = True,
    ) -> list[ClassSubjectTeacher]:
        return await StudentAcademicRepository.list_class_assignments(
            db=db,
            tenant_id=tenant_id,
            class_id=class_id,
            active_only=active_only,
        )

    @staticmethod
    async def list_student_subjects(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        class_id: uuid.UUID | None,
    ) -> list[ClassSubjectTeacher]:
        if class_id is None:
            return []

        return await StudentAcademicRepository.list_class_assignments(
            db=db,
            tenant_id=tenant_id,
            class_id=class_id,
            active_only=True,
        )

    @staticmethod
    async def _compute_grade(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        total_score: Decimal,
    ) -> tuple[str, str | None]:
        grading_scale = await StudentAcademicRepository.find_grade_for_score(
            db=db,
            tenant_id=tenant_id,
            score=total_score,
        )
        if grading_scale is None:
            raise NotFoundException("No grading scale found for the computed total score.")
        return grading_scale.grade, grading_scale.remark

    @staticmethod
    async def _build_result_response(
        db: AsyncSession,
        result: StudentSubjectResult,
    ) -> StudentSubjectResultResponse:
        student = await StudentRepository.get_student_by_id(
            db=db,
            tenant_id=result.tenant_id,
            student_id=result.student_id,
        )
        classroom = await ClassRoomRepository.get_classroom_by_id(
            db=db,
            tenant_id=result.tenant_id,
            class_id=result.class_id,
        )
        subject = await SubjectRepository.get_subject_by_id(
            db=db,
            tenant_id=result.tenant_id,
            subject_id=result.subject_id,
        )
        teacher = await TeacherRepository.get_teacher_by_id(
            db=db,
            tenant_id=result.tenant_id,
            teacher_id=result.teacher_id,
        )
        session = await StudentAcademicRepository.get_academic_session_by_id(
            db=db,
            tenant_id=result.tenant_id,
            academic_session_id=result.academic_session_id,
        )
        term = await StudentAcademicRepository.get_term_by_id(
            db=db,
            tenant_id=result.tenant_id,
            term_id=result.academic_term_id,
        )

        return StudentSubjectResultResponse(
            id=result.id,
            tenant_id=result.tenant_id,
            student_id=result.student_id,
            student_name=(
                " ".join(part for part in [student.first_name, student.last_name] if part).strip()
                if student
                else None
            ),
            admission_number=student.admission_number if student else None,
            class_id=result.class_id,
            class_name=classroom.name if classroom else None,
            class_arm=classroom.arm if classroom else None,
            subject_id=result.subject_id,
            subject_name=subject.name if subject else None,
            subject_code=subject.code if subject else None,
            teacher_id=result.teacher_id,
            teacher_name=(
                " ".join(part for part in [teacher.first_name, teacher.last_name] if part).strip()
                if teacher
                else None
            ),
            class_subject_teacher_id=result.class_subject_teacher_id,
            academic_session_id=result.academic_session_id,
            academic_session_name=session.name if session else None,
            academic_term_id=result.academic_term_id,
            academic_term_name=term.name.value if term else None,
            test_score=result.test_score,
            assessment_score=result.assessment_score,
            exam_score=result.exam_score,
            total_score=result.total_score,
            grade=result.grade,
            remark=result.remark,
            status=result.status,
            recorded_by_actor_type=result.recorded_by_actor_type,
            recorded_by_actor_id=result.recorded_by_actor_id,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    @staticmethod
    async def upsert_student_result(
        db: AsyncSession,
        actor: TenantAdmin | Teacher,
        payload: StudentSubjectResultUpsert,
    ) -> StudentSubjectResultResponse:
        tenant_id = actor.tenant_id
        assignment = await StudentAcademicRepository.get_class_subject_teacher_by_id(
            db=db,
            tenant_id=tenant_id,
            assignment_id=payload.class_subject_teacher_id,
        )
        if assignment is None or not assignment.is_active:
            raise NotFoundException("Class-subject teacher assignment not found.")

        if isinstance(actor, Teacher) and assignment.teacher_id != actor.id:
            raise ForbiddenException("You can only edit class-subjects assigned to you.")

        student = await StudentRepository.get_student_by_id(
            db=db,
            tenant_id=tenant_id,
            student_id=payload.student_id,
        )
        if student is None:
            raise NotFoundException("Student not found.")
        if student.class_id != assignment.class_id:
            raise BadRequestException("Student does not belong to the selected class.")

        if payload.status == AcademicResultStatus.LOCKED and isinstance(actor, Teacher):
            raise ForbiddenException("Teachers cannot lock results.")

        total_score = payload.test_score + payload.assessment_score + payload.exam_score
        grade, remark = await StudentAcademicService._compute_grade(
            db=db,
            tenant_id=tenant_id,
            total_score=total_score,
        )

        existing = await StudentAcademicRepository.get_result_by_scope(
            db=db,
            tenant_id=tenant_id,
            student_id=payload.student_id,
            class_subject_teacher_id=payload.class_subject_teacher_id,
            academic_session_id=payload.academic_session_id,
            academic_term_id=payload.academic_term_id,
        )
        if existing is not None:
            if existing.status == AcademicResultStatus.LOCKED:
                raise ForbiddenException("Locked results are not editable in normal workflows.")
            result = existing
        else:
            actor_type = (
                ActorType.TEACHER.value
                if isinstance(actor, Teacher)
                else ActorType.TENANT_ADMIN.value
            )
            result = StudentSubjectResult(
                tenant_id=tenant_id,
                student_id=payload.student_id,
                class_id=assignment.class_id,
                subject_id=assignment.subject_id,
                teacher_id=assignment.teacher_id,
                class_subject_teacher_id=assignment.id,
                academic_session_id=payload.academic_session_id,
                academic_term_id=payload.academic_term_id,
                recorded_by_actor_type=actor_type,
                recorded_by_actor_id=actor.id,
                test_score=payload.test_score,
                assessment_score=payload.assessment_score,
                exam_score=payload.exam_score,
                total_score=total_score,
                grade=grade,
                remark=remark,
                status=payload.status,
            )

        result.test_score = payload.test_score
        result.assessment_score = payload.assessment_score
        result.exam_score = payload.exam_score
        result.total_score = total_score
        result.grade = grade
        result.remark = remark
        result.status = payload.status

        saved = await StudentAcademicRepository.upsert_result(db=db, result=result)
        await db.commit()
        return await StudentAcademicService._build_result_response(db=db, result=saved)

    @staticmethod
    async def update_result_status(
        db: AsyncSession,
        actor: TenantAdmin,
        result_id: uuid.UUID,
        payload: StudentSubjectResultStatusUpdate,
    ) -> StudentSubjectResultResponse:
        result = await StudentAcademicRepository.get_result_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            result_id=result_id,
        )
        if result is None:
            raise NotFoundException("Result not found.")
        result.status = payload.status
        saved = await StudentAcademicRepository.upsert_result(db=db, result=result)
        await db.commit()
        return await StudentAcademicService._build_result_response(db=db, result=saved)

    @staticmethod
    async def list_results(
        db: AsyncSession,
        actor: TenantAdmin | Teacher | Student | Parent,
        *,
        skip: int = 0,
        limit: int = 100,
        student_id: uuid.UUID | None = None,
        class_id: uuid.UUID | None = None,
        academic_session_id: uuid.UUID | None = None,
        academic_term_id: uuid.UUID | None = None,
    ) -> tuple[list[StudentSubjectResultResponse], int]:
        tenant_id = actor.tenant_id
        teacher_id = None
        published_only = False

        if isinstance(actor, Teacher):
            teacher_id = actor.id
        elif isinstance(actor, Student):
            student_id = actor.id
            published_only = True
        elif isinstance(actor, Parent):
            if student_id is None:
                raise BadRequestException("student_id is required for parent academic results.")
            link = await StudentParentLinkRepository.get_by_student_and_parent(
                db=db,
                tenant_id=tenant_id,
                student_id=student_id,
                parent_id=actor.id,
            )
            if link is None:
                raise ForbiddenException("You cannot view academic records for this student.")
            published_only = True

        results, total = await StudentAcademicRepository.list_results(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=min(limit, 100),
            student_id=student_id,
            class_id=class_id,
            teacher_id=teacher_id,
            academic_session_id=academic_session_id,
            academic_term_id=academic_term_id,
            published_only=published_only,
        )
        return [
            await StudentAcademicService._build_result_response(db=db, result=result)
            for result in results
        ], total
