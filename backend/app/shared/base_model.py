#======================================#
#            base_model.py             #
#======================================#



from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedColumn
from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True #this line prevents creation of another table

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now()    # ✅ also add default here, not just onupdate
    )