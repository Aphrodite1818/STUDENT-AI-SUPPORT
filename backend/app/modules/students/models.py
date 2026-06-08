#======================================#
#              models.py               #
#======================================#
from enum import Enum
import uuid
from typing import TYPE_CHECKING

from app.shared.base_model import BaseModel, PUBLIC_SCHEMA
from sqlalchemy import String, UUID, Date, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import date

if TYPE_CHECKING:
    from app.modules.users.models import User



class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class AcademicStatus(str, Enum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"




class Students(BaseModel):
    __tablename__ = "students"

    firstname : Mapped[str] = mapped_column(String(100) , nullable = False)

    lastname : Mapped[str] = mapped_column(String(100) , nullable= False)

    date_of_birth : Mapped[date] = mapped_column(Date , nullable=False)

    gender : Mapped[Gender] = mapped_column(
        SQLEnum(Gender, name="gender", schema=PUBLIC_SCHEMA),
        nullable=False,
    )

    passport_photo_url : Mapped[str | None] = mapped_column(String(150) , nullable= True)

    admission_number : Mapped[str]  = mapped_column(String(50) , nullable= False)

    admission_date : Mapped[date] = mapped_column(Date , nullable=False)

    graduation_date : Mapped[date | None] = mapped_column(Date , nullable = True)


    class_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey(f"{PUBLIC_SCHEMA}.classes.id", ondelete="RESTRICT"),
        nullable=False
    )

    arm : Mapped[str | None] = mapped_column(String(20) , nullable=True )


    status : Mapped[AcademicStatus] = mapped_column(
        SQLEnum(AcademicStatus, name="academicstatus", schema=PUBLIC_SCHEMA),
        nullable=False,
        default=AcademicStatus.ACTIVE,
    )

    parent_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey(f"{PUBLIC_SCHEMA}.users.id" , ondelete="RESTRICT"),
        nullable=False
    )

    parent: Mapped["User"] = relationship(
        "User",
        back_populates="students",
        foreign_keys=[parent_id],
    )



    __table_args__ = (
        Index("ix_students_tenant_admission", "tenant_id", "admission_number"),
        Index("ix_students_tenant_status",    "tenant_id", "status"),
        Index("ix_students_tenant_class",     "tenant_id", "class_id"),
        Index("ix_students_tenant_parent",    "tenant_id", "parent_id"),
    )

