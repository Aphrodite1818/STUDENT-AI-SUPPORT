#======================================#
#              models.py               #
#======================================#


from __future__ import annotations
import uuid
from datetime import date , datetime , timezone
from enum import Enum
from secrets import token_urlsafe
from typing import TYPE_CHECKING

from sqlalchemy import Boolean , Date , DateTime , Enum as SQLEnum , ForeignKey, Index, String , UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped , mapped_column , relationship
from app.shared.base_model import BaseModel , PUBLIC_SCHEMA


if TYPE_CHECKING:
    from app.modules.parents.models import Parent
    from app.modules.users.models import User


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class AcademicStatus(str, Enum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"


class ParentRelationship(str, Enum):
    FATHER = "father"
    MOTHER = "mother"
    GUARDIAN = "guardian"
    OTHER = "other"


class Student(BaseModel):
    """student academic profile linked to a user account"""

    __tablename__ = "students"


    user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable = False,
        unique = True,
        index = True
    )


    admission_number : Mapped[str] = mapped_column(String(50) , nullable = False)


    date_of_birth : Mapped[date] = mapped_column(Date, nullable = False)

    gender : Mapped[Gender] = mapped_column(
        SQLEnum(Gender, name = "studentgender", schema = PUBLIC_SCHEMA),
        nullable = False
    )

    passport_photo_url : Mapped[str | None] = mapped_column(String(500), nullable = True)


    admission_date : Mapped[date] = mapped_column(Date , nullable = False)

    graduation_date : Mapped[date | None] = mapped_column(Date , nullable = True)


    class_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("classes.id", ondelete = "RESTRICT"),
        nullable = False
    )



    arm : Mapped[str | None] = mapped_column(String(20), nullable = True)

    status : Mapped[AcademicStatus] = mapped_column(
        SQLEnum(AcademicStatus, name="academicstatus", schema= PUBLIC_SCHEMA),
        nullable = False,
        default = AcademicStatus.ACTIVE
    )

    user : Mapped["User"] = relationship(
        "User",
        back_populates="student_profile",
        lazy = "joined"
    )

    parent_links : Mapped[list["StudentParentLink"]] = relationship(
        "StudentParentLink",
        back_populates="student",
        cascade="all , delete-orphan"
    )

    link_codes : Mapped[list["StudentLinkCode"]] = relationship(
        "StudentLinkCode",
        back_populates="student",
        cascade="all, delete-orphan"
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
    def parents(self) -> list["Parent"]:
        return [link.parent for link in self.parent_links if link.parent is not None]

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "admission_number",
            name="uq_students_tenant_admission_number",
        ),
        Index("ix_students_tenant_user", "tenant_id", "user_id"),
        Index("ix_students_tenant_class", "tenant_id", "class_id"),
        Index("ix_students_tenant_status", "tenant_id", "status"),
    )







class StudentParentLink(BaseModel):
    """Many-to-many link between students and parents"""

    __tablename__ = "student_parent_links"


    student_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable = False
    )


    parent_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("parents.id")
    )



    relationship_type : Mapped[ParentRelationship] = mapped_column(
        SQLEnum(ParentRelationship, name = "parentrelationship" , schema = PUBLIC_SCHEMA),
        nullable = False,
        default = ParentRelationship.GUARDIAN
    )


    is_primary_contact : Mapped[bool] = mapped_column(Boolean, default = False , nullable = False)

    receives_academic_updates :  Mapped[bool] = mapped_column(Boolean , default = True , nullable = False)


    receives_fee_updates: Mapped[bool] = mapped_column(Boolean, default = True , nullable = False)

    student : Mapped["Student"] = relationship(
        "Student", 
        back_populates="parent_links"
    )

    parent : Mapped["Parent"] = relationship(
        "Parent" ,
        back_populates="student_links"
    )




    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "student_id",
            "parent_id",
            name="uq_student_parent_tenant_student_parent",
        ),
        Index("ix_student_parent_links_tenant_student", "tenant_id", "student_id"),
        Index("ix_student_parent_links_tenant_parent", "tenant_id", "parent_id"),
    )



class StudentLinkCode(BaseModel):
    """Code used by parents to link themselves to student"""

    __tablename__ = "student_link_codes"

    student_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("students.id" , ondelete= "CASCADE"),
        nullable = False
    )

    code : Mapped[str] = mapped_column(String(80) , nullable = False , unique = True , index = True)

    expires_at : Mapped[datetime] = mapped_column(DateTime(timezone = True ) , nullable = False)

    used_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True) , nullable = True)

    max_users : Mapped[int] = mapped_column(default = 1 , nullable = False)

    use_count : Mapped[int] = mapped_column(default = 0, nullable = False)


    student : Mapped["Student"] = relationship(
        "Student",
        back_populates="link_codes"
    )

    @staticmethod
    def generate_code():
        return f"STU{token_urlsafe(6).upper()}"
    

    @property
    def is_expired(self):
        return datetime.now(timezone.utc) <= self.expires_at
    

    @property
    def is_exhausted(self):
        return self.use_count >= self.max_users
    


    @property
    def is_active(self):
        return self.used_at is None and not self.is_expired and not self.is_exhausted
    


    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_student_link_codes_tenant_code"),
        Index("ix_student_link_codes_tenant_student", "tenant_id", "student_id"),
        Index("ix_student_link_codes_tenant_code", "tenant_id", "code"),
    )
