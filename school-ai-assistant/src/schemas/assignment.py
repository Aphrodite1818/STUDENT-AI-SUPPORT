# schemas/assignment.py

from datetime import date, datetime
from typing import Optional

from schemas.common import BaseSchema


class AssignmentBase(BaseSchema):
    title: str
    description: str
    due_date: date
    course_id: int
    class_level: str


class AssignmentCreate(AssignmentBase):
    teacher_id: int
    file_url: Optional[str] = None


class AssignmentUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    class_level: Optional[str] = None
    file_url: Optional[str] = None


class AssignmentOut(AssignmentBase):
    id: int
    teacher_id: int
    teacher_name: str
    course_name: str
    file_url: Optional[str] = None
    created_at: datetime


class AssignmentListOut(BaseSchema):
    id: int
    title: str
    due_date: date
    class_level: str