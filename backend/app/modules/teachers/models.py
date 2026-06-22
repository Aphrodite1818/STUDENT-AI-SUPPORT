#======================================#
#          teacher/models.py           #
#======================================#

import uuid
from enum import Enum as PyEnum
from typing import Any, TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA

if TYPE_CHECKING:
    from app.modules.subjects.models import Subject
    from app.modules.users.models import User


class TeacherStatus(str, PyEnum):
    """Enumeration of supported teachers values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Teacher(BaseModel):
    """Represent the Teacher type."""
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
        SQLEnum(
            TeacherStatus,
            name="teacherstatus",
            schema=PUBLIC_SCHEMA,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TeacherStatus.ACTIVE,
        server_default=TeacherStatus.ACTIVE.value,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="teacher_profile",
        lazy="joined",
    )

    subject_links: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )

    @property
    def firstname(self) -> str | None:
        """Return the firstname value for the teacher."""
        return self.user.firstname if self.user else None

    @property
    def lastname(self) -> str | None:
        """Return the lastname value for the teacher."""
        return self.user.lastname if self.user else None

    @property
    def email(self) -> str | None:
        """Return the email value for the teacher."""
        return self.user.email if self.user else None

    @property
    def subjects(self) -> list[Any]:
        """Return the subjects value for the teacher."""
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

    teacher: Mapped["Teacher"] = relationship(
        "Teacher",
        back_populates="subject_links",
    )

    subject: Mapped["Subject"] = relationship(
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
