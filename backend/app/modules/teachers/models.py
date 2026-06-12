#======================================#
#          teacher/models.py           #
#======================================#

import uuid
from enum import Enum
from typing import Any

from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA


class TeacherStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Teacher(BaseModel):
    __tablename__ = "teachers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    staff_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    qualification: Mapped[str | None] = mapped_column(String(100), nullable=True)

    specialization: Mapped[str | None] = mapped_column(String(150), nullable=True)

    status: Mapped[TeacherStatus] = mapped_column(
        SQLEnum(TeacherStatus, name="teacherstatus", schema=PUBLIC_SCHEMA),
        default=TeacherStatus.ACTIVE,
        server_default=TeacherStatus.ACTIVE.name,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="teacher_profile",
        lazy="joined",
    )

    subject_links = relationship(
        "TeacherSubject",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )

    @property
    def firstname(self) -> str | None:
        return self.user.firstname if self.user else None

    @property
    def lastname(self) -> str | None:
        return self.user.lastname if self.user else None

    @property
    def email(self) -> str | None:
        return self.user.email if self.user else None

    @property
    def subjects(self) -> list[Any]:
        return [link.subject for link in self.subject_links if link.subject is not None]

    __table_args__ = (
        UniqueConstraint("tenant_id", "staff_id", name="uq_teachers_tenant_staff_id"),
        Index("ix_teachers_tenant_user", "tenant_id", "user_id"),
        Index("ix_teachers_tenant_status", "tenant_id", "status"),
    )


class TeacherSubject(BaseModel):
    """Join table for the teacher-to-subject many-to-many relationship."""

    __tablename__ = "teacher_subjects"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )

    teacher = relationship(
        "Teacher",
        back_populates="subject_links",
    )

    subject = relationship(
        "Subject",
        back_populates="teacher_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "teacher_id",
            "subject_id",
            name="uq_teacher_subject_tenant_teacher_subject",
        ),
        Index("ix_teacher_subjects_tenant_teacher", "tenant_id", "teacher_id"),
        Index("ix_teacher_subjects_tenant_subject", "tenant_id", "subject_id"),
    )
