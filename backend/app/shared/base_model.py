#======================================#
#            base_model.py             #
#======================================#



from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedColumn
from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


from backend.app.shared.mixins import UUIDMixin, TimestampMixin

class Base(DeclarativeBase):
    pass


class BaseModel(UUIDMixin, TimestampMixin, Base):
    __abstract__ = True #this line prevents creation of another table

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False
    )