#==========================#
#    subject/models.py     #
#==========================#

"""Tenant-scoped subject catalog for each school."""

from typing import Any

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel


class Subject(BaseModel):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    teacher_links = relationship(
        "TeacherSubject",
        back_populates="subject",
        cascade="all, delete-orphan",
    )

    @property
    def teachers(self) -> list[Any]:
        return [link.teacher for link in self.teacher_links if link.teacher is not None]

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_subject_tenant_name"),
        UniqueConstraint("tenant_id", "code", name="uq_subject_tenant_code"),
    )
