# schemas/announcement.py

from datetime import datetime
from enum import Enum
from typing import Optional

from schemas.common import BaseSchema


class TargetAudience(str, Enum):
    ALL = "all"
    PARENTS = "parents"
    TEACHERS = "teachers"


class AnnouncementBase(BaseSchema):
    title: str
    body: str
    target_audience: TargetAudience
    publish_date: datetime


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseSchema):
    title: Optional[str] = None
    body: Optional[str] = None
    target_audience: Optional[TargetAudience] = None
    publish_date: Optional[datetime] = None


class AnnouncementOut(AnnouncementBase):
    id: int
    created_at: datetime