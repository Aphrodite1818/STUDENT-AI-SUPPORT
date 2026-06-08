#======================================#
#            base_model.py             #
#======================================#

import uuid

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.shared.mixins import UUIDMixin, TimestampMixin


PUBLIC_SCHEMA = "public"


class Base(DeclarativeBase):
    metadata = MetaData(schema=PUBLIC_SCHEMA)


class BaseModel(UUIDMixin, TimestampMixin, Base):
    __abstract__ = True #this line prevents creation of another table

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{PUBLIC_SCHEMA}.tenants.id"),
        nullable=False,
    )
