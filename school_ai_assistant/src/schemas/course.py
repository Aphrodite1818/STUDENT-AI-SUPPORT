#==========================#
# COURSE SCRIPT
#==========================#

# schemas/course.py

from datetime import datetime
from typing import Optional

from pydantic import Field

from .common import BaseSchema


class CourseBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=120)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseSchema):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None


class CourseResponse(CourseBase):
    id: int
    created_at: datetime
