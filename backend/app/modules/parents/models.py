#==========================#
#        models.py         #
#==========================#

from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Index
from app.shared.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.students.models import Student , StudentParentLink
    from app.modules.users.models import User





class Parent(BaseModel):
    """parent or guardian profile linked to a user account"""
    __tablename__ = "parents"


    user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id" , ondelete="CASCADE"),
        nullable = False ,
        unique=True ,
        index = True

    )

    occupation : Mapped[str | None] = mapped_column(String(100), nullable = True)

    address : Mapped[str | None] = mapped_column(String(500) , nullable = True)


    emergency_phone : Mapped[str | None] = mapped_column(String(20), nullable = True)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="parent_profile",
        lazy = "joined"
    )

    student_links : Mapped[list["StudentParentLink"]] = relationship(
        "StudentParentLink",
        back_populates="parent",
        cascade="all , delete-orphan"
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
    def phone_number(self) -> str | None:
        return self.user.phone_number if self.user else None

    @property
    def whatsapp_id(self) -> str | None:
        return self.user.whatsapp_id if self.user else None

    @property
    def students(self) -> list["Student"]:
        return [link.student for link in self.student_links if link.student is not None]

    __table_args__ = (
        Index("ix_parents_tenant_user", "tenant_id", "user_id"),
    )

