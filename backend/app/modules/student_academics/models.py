import uuid
from datetime import date
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    UUID,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA


class AcademicTermName(str, PyEnum):
    FIRST_TERM = "first_term"
    SECOND_TERM = "second_term"
    THIRD_TERM = "third_term"


class AcademicResultStatus(str, PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    LOCKED = "locked"


class AcademicSession(BaseModel):
    __tablename__ = "academic_sessions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "name",
            name="uq_academic_session_tenant_name",
        ),
    )

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )


class AcademicTerm(BaseModel):
    __tablename__ = "academic_terms"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "academic_session_id",
            "name",
            name="uq_academic_term_tenant_session_name",
        ),
    )

    academic_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("academic_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[AcademicTermName] = mapped_column(
        SQLEnum(
            AcademicTermName,
            name="academic_term_name",
            schema=PUBLIC_SCHEMA,
        ),
        nullable=False,
    )

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )


class GradingScale(BaseModel):
    __tablename__ = "grading_scales"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "grade",
            name="uq_grading_scale_tenant_grade",
        ),
    )

    min_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    max_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    remark: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )


class ClassSubjectTeacher(BaseModel):
    __tablename__ = "class_subject_teachers"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "class_id",
            "subject_id",
            name="uq_class_subject_teacher_tenant_class_subject",
        ),
    )

    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    is_core: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )