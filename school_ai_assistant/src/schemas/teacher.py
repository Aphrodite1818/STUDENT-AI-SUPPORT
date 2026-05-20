#==========================#
# TEACHER SCRIPT
#==========================#

# schemas/teacher.py

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .common import BaseSchema


class TeacherBase(BaseSchema):
    full_name: str = Field(..., min_length=1, max_length=120)
    employee_id: str = Field(..., min_length=1, max_length=50)
    subjects: List[str] = Field(default_factory=list)


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseSchema):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    employee_id: Optional[str] = Field(default=None, min_length=1, max_length=50)
    subjects: Optional[List[str]] = None


class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
