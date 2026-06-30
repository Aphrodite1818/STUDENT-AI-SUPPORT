import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.classes.models import ClassRoom
from app.modules.parents.models import Parent
from app.modules.search.schemas import TenantSearchResult
from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.teachers.models import Teacher


class TenantSearchService:
    @staticmethod
    def _name(*parts: str | None) -> str:
        return " ".join(part for part in parts if part).strip() or "Unnamed"

    @staticmethod
    async def search(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        query: str,
        limit: int = 20,
    ) -> list[TenantSearchResult]:
        term = f"%{query.strip()}%"
        per_type_limit = max(1, min(limit, 50))
        items: list[TenantSearchResult] = []

        students = (
            await db.execute(
                select(Student, ClassRoom)
                .outerjoin(ClassRoom, ClassRoom.id == Student.class_id)
                .where(
                    Student.tenant_id == tenant_id,
                    or_(
                        Student.first_name.ilike(term),
                        Student.last_name.ilike(term),
                        Student.admission_number.ilike(term),
                        ClassRoom.name.ilike(term),
                        ClassRoom.arm.ilike(term),
                    ),
                )
                .limit(per_type_limit)
            )
        ).all()
        for student, classroom in students:
            class_label = (
                " ".join(part for part in [classroom.name, classroom.arm] if part).strip()
                if classroom
                else None
            )
            items.append(
                TenantSearchResult(
                    label=TenantSearchService._name(student.first_name, student.last_name),
                    role="student",
                    metadata=class_label,
                    admission_number=student.admission_number,
                    class_name=class_label,
                    href=f"/admin/students?admissionNumber={student.admission_number}",
                )
            )

        teachers = (
            await db.execute(
                select(Teacher).where(
                    Teacher.tenant_id == tenant_id,
                    or_(
                        Teacher.first_name.ilike(term),
                        Teacher.last_name.ilike(term),
                        Teacher.email.ilike(term),
                        Teacher.staff_id.ilike(term),
                    ),
                ).limit(per_type_limit)
            )
        ).scalars().all()
        for teacher in teachers:
            items.append(
                TenantSearchResult(
                    label=TenantSearchService._name(teacher.first_name, teacher.last_name),
                    role="teacher",
                    metadata=teacher.specialization,
                    staff_id=teacher.staff_id,
                    email=teacher.email,
                    href=f"/admin/teachers?staffId={teacher.staff_id or teacher.email}",
                )
            )

        parents = (
            await db.execute(
                select(Parent).where(
                    Parent.tenant_id == tenant_id,
                    or_(
                        Parent.first_name.ilike(term),
                        Parent.last_name.ilike(term),
                        Parent.email.ilike(term),
                    ),
                ).limit(per_type_limit)
            )
        ).scalars().all()
        for parent in parents:
            items.append(
                TenantSearchResult(
                    label=TenantSearchService._name(parent.first_name, parent.last_name),
                    role="parent",
                    metadata=parent.phone_number,
                    email=parent.email,
                    href=f"/admin/parents?email={parent.email}",
                )
            )

        classes = (
            await db.execute(
                select(ClassRoom).where(
                    ClassRoom.tenant_id == tenant_id,
                    or_(ClassRoom.name.ilike(term), ClassRoom.arm.ilike(term), ClassRoom.level.ilike(term)),
                ).limit(per_type_limit)
            )
        ).scalars().all()
        for classroom in classes:
            label = TenantSearchService._name(classroom.name, classroom.arm)
            items.append(
                TenantSearchResult(
                    label=label,
                    role="class",
                    metadata=classroom.level,
                    class_name=label,
                    href=f"/admin/classes?class={classroom.name}&arm={classroom.arm}",
                )
            )

        subjects = (
            await db.execute(
                select(Subject).where(
                    Subject.tenant_id == tenant_id,
                    or_(Subject.name.ilike(term), Subject.code.ilike(term)),
                ).limit(per_type_limit)
            )
        ).scalars().all()
        for subject in subjects:
            items.append(
                TenantSearchResult(
                    label=subject.name,
                    role="subject",
                    metadata=subject.code,
                    subject_name=subject.name,
                    href=f"/admin/subjects?code={subject.code or subject.name}",
                )
            )

        return items[:limit]
