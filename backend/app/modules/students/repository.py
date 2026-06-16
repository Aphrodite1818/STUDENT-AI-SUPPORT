from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.students.models import AcademicStatus, Student, StudentLinkCode, StudentParentLink
from app.modules.users.models import User


class StudentRepository:
    """Database operations for student profiles."""

    @staticmethod
    async def create_student(
        db: AsyncSession,
        student: Student,
    ) -> Student:
        """Create a student profile."""
        db.add(student)
        await db.flush()
        await db.refresh(student)
        return student

    @staticmethod
    async def get_student_by_id(
        db: AsyncSession,
        tenant_id: UUID,
        student_id: UUID,
    ) -> Student | None:
        """Get a student profile by id within a tenant."""
        result = await db.execute(
            select(Student).where(
                Student.id == student_id,
                Student.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
    ) -> Student | None:
        """Get a student profile by user id within a tenant."""
        result = await db.execute(
            select(Student).where(
                Student.tenant_id == tenant_id,
                Student.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_admission_number(
        db: AsyncSession,
        tenant_id: UUID,
        admission_number: str,
    ) -> Student | None:
        """Get a student profile by admission number within a tenant."""
        result = await db.execute(
            select(Student).where(
                Student.tenant_id == tenant_id,
                Student.admission_number == admission_number,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _build_student_list_query(
        tenant_id: UUID,
        search: str | None = None,
        class_id: UUID | None = None,
        status: AcademicStatus | None = None,
    ) -> tuple:
        """Build the base query for filtered student listing."""
        conditions = [Student.tenant_id == tenant_id]

        if class_id is not None:
            conditions.append(Student.class_id == class_id)

        if status is not None:
            conditions.append(Student.status == status)

        if search:
            search_term = f"%{search.strip()}%"
            conditions.append(
                or_(
                    User.firstname.ilike(search_term),
                    User.lastname.ilike(search_term),
                    User.email.ilike(search_term),
                    Student.admission_number.ilike(search_term),
                )
            )

        query = select(Student).join(User, User.id == Student.user_id).where(*conditions)
        return query, conditions

    @staticmethod
    async def list_students(
        db: AsyncSession,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        class_id: UUID | None = None,
        status: AcademicStatus | None = None,
    ) -> tuple[list[Student], int]:
        """List student profiles with filters."""
        base_query, conditions = StudentRepository._build_student_list_query(
            tenant_id=tenant_id,
            search=search,
            class_id=class_id,
            status=status,
        )

        result = await db.execute(
            base_query
            .order_by(Student.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        students = list(result.scalars().unique().all())

        total_result = await db.execute(
            select(func.count())
            .select_from(Student)
            .join(User, User.id == Student.user_id)
            .where(*conditions)
        )
        total = total_result.scalar_one()

        return students, total

    @staticmethod
    async def get_all_students_by_class_id(
        db: AsyncSession,
        tenant_id: UUID,
        class_id: UUID,
        limit: int = 100,
        skip: int = 0,
    ) -> list[Student]:
        """Get all students by class id within a tenant."""
        result = await db.execute(
            select(Student)
            .where(
                Student.tenant_id == tenant_id,
                Student.class_id == class_id,
            )
            .offset(skip)
            .limit(limit)
            .order_by(Student.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_student(
        db: AsyncSession,
        student: Student,
    ) -> Student:
        """Persist student profile updates."""
        await db.flush()
        await db.refresh(student)
        return student

    @staticmethod
    async def delete_student(
        db: AsyncSession,
        student: Student,
    ) -> None:
        """Delete a student profile."""
        await db.delete(student)
        await db.flush()


class StudentParentLinkRepository:
    """Database operations for student-parent links."""

    @staticmethod
    async def create_student_parent_link(
        db: AsyncSession,
        link: StudentParentLink,
    ) -> StudentParentLink:
        """Create a student-parent link."""
        db.add(link)
        await db.flush()
        await db.refresh(link)
        return link

    @staticmethod
    async def get_parent_student_link_by_id(
        db: AsyncSession,
        tenant_id: UUID,
        link_id: UUID,
    ) -> StudentParentLink | None:
        """Get a student-parent link by id within a tenant."""
        result = await db.execute(
            select(StudentParentLink).where(
                StudentParentLink.id == link_id,
                StudentParentLink.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_and_parent(
        db: AsyncSession,
        student_id: UUID,
        tenant_id: UUID,
        parent_id: UUID,
    ) -> StudentParentLink | None:
        """Get a student-parent link by student and parent."""
        result = await db.execute(
            select(StudentParentLink).where(
                StudentParentLink.tenant_id == tenant_id,
                StudentParentLink.parent_id == parent_id,
                StudentParentLink.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_id(
        db: AsyncSession,
        student_id: UUID,
        tenant_id: UUID,
    ) -> list[StudentParentLink]:
        """Get all parent links for a student."""
        result = await db.execute(
            select(StudentParentLink)
            .options(selectinload(StudentParentLink.parent))
            .where(
                StudentParentLink.tenant_id == tenant_id,
                StudentParentLink.student_id == student_id,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_parent_id(
        db: AsyncSession,
        tenant_id: UUID,
        parent_id: UUID,
    ) -> list[StudentParentLink]:
        """Get all student links for a parent."""
        result = await db.execute(
            select(StudentParentLink)
            .options(
                selectinload(StudentParentLink.student).joinedload(Student.user),
                joinedload(StudentParentLink.parent),
            )
            .where(
                StudentParentLink.tenant_id == tenant_id,
                StudentParentLink.parent_id == parent_id,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_student_parent_link(
        db: AsyncSession,
        link: StudentParentLink,
    ) -> StudentParentLink:
        """Persist student-parent link updates."""
        await db.flush()
        await db.refresh(link)
        return link

    @staticmethod
    async def delete_student_parent_link(
        db: AsyncSession,
        link: StudentParentLink,
    ) -> None:
        """Delete a student-parent link."""
        await db.delete(link)
        await db.flush()


class StudentLinkCodeRepository:
    """Database operations for student link codes."""

    @staticmethod
    async def create(
        db: AsyncSession,
        link_code: StudentLinkCode,
    ) -> StudentLinkCode:
        """Create a student link code."""
        db.add(link_code)
        await db.flush()
        await db.refresh(link_code)
        return link_code

    @staticmethod
    async def get_code_by_id(
        db: AsyncSession,
        tenant_id: UUID,
        link_code_id: UUID,
    ) -> StudentLinkCode | None:
        """Get a student link code by id within a tenant."""
        result = await db.execute(
            select(StudentLinkCode).where(
                StudentLinkCode.tenant_id == tenant_id,
                StudentLinkCode.id == link_code_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_code(
        db: AsyncSession,
        tenant_id: UUID,
        code: str,
    ) -> StudentLinkCode | None:
        """Get a student link code by code within a tenant."""
        result = await db.execute(
            select(StudentLinkCode).where(
                StudentLinkCode.tenant_id == tenant_id,
                StudentLinkCode.code == code,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_id(
        db: AsyncSession,
        tenant_id: UUID,
        student_id: UUID,
    ) -> list[StudentLinkCode]:
        """Get all link codes generated for a student."""
        result = await db.execute(
            select(StudentLinkCode)
            .where(
                StudentLinkCode.tenant_id == tenant_id,
                StudentLinkCode.student_id == student_id,
            )
            .order_by(StudentLinkCode.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        link_code: StudentLinkCode,
    ) -> StudentLinkCode:
        """Persist student link code updates."""
        await db.flush()
        await db.refresh(link_code)
        return link_code

    @staticmethod
    async def delete(
        db: AsyncSession,
        link_code: StudentLinkCode,
    ) -> None:
        """Delete a student link code."""
        await db.delete(link_code)
        await db.flush()
