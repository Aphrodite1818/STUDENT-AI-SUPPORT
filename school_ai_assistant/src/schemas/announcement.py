#==========================#
# ANNOUNCEMENT SCRIPT
#==========================#

# schemas/announcement.py

from datetime import datetime
from typing import Optional

from pydantic import Field

from ..helpers.announcement_helper import TargetAudience
from .common import BaseSchema


class AnnouncementBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    target_audience: TargetAudience
    publish_date: datetime


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseSchema):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    body: Optional[str] = Field(default=None, min_length=1)
    target_audience: Optional[TargetAudience] = None
    publish_date: Optional[datetime] = None


class AnnouncementResponse(AnnouncementBase):
    id: int
    created_at: datetime
