# schemas/teacher.py

from datetime import datetime
from typing import List, Optional

from schemas.common import BaseSchema


class TeacherBase(BaseSchema):
    full_name: str
    employee_id: str
    subjects: List[str]


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseSchema):
    full_name: Optional[str] = None
    employee_id: Optional[str] = None
    subjects: Optional[List[str]] = None


class TeacherOut(TeacherBase):
    id: int
    created_at: datetime