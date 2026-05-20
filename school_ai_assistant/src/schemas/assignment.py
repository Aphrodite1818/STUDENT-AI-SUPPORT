#==========================#
# ASSIGNMENT SCRIPT
#==========================#

# schemas/assignment.py

from datetime import date, datetime
from typing import Optional

from pydantic import Field

from .common import BaseSchema


class AssignmentBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    due_date: date
    course_id: int = Field(..., gt=0)
    class_level: str = Field(..., min_length=1, max_length=50)


class AssignmentCreate(AssignmentBase):
    teacher_id: int = Field(..., gt=0)
    file_url: Optional[str] = None


class AssignmentUpdate(BaseSchema):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=1)
    due_date: Optional[date] = None
    class_level: Optional[str] = Field(default=None, min_length=1, max_length=50)
    file_url: Optional[str] = None


class AssignmentResponse(AssignmentBase):
    id: int
    teacher_id: int
    teacher_name: str
    course_name: str
    file_url: Optional[str] = None
    created_at: datetime


class AssignmentSummaryResponse(BaseSchema):
    id: int
    title: str
    due_date: date
    class_level: str
