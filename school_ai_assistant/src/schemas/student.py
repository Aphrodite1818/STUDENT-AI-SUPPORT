#==========================#
# STUDENT SCRIPT
#==========================#

# schemas/student.py

from datetime import date, datetime
from typing import Optional

from pydantic import Field

from .common import BaseSchema


class StudentBase(BaseSchema):
    full_name: str = Field(..., min_length=1, max_length=120)
    date_of_birth: date
    class_level: str = Field(..., min_length=1, max_length=50)
    admission_number: str = Field(..., min_length=1, max_length=50)


class StudentCreate(StudentBase):
    parent_id: int = Field(..., gt=0)


class StudentUpdate(BaseSchema):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    date_of_birth: Optional[date] = None
    class_level: Optional[str] = Field(default=None, min_length=1, max_length=50)
    admission_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    parent_id: Optional[int] = Field(default=None, gt=0)


class StudentSummary(BaseSchema):
    id: int
    full_name: str
    class_level: str
    admission_number: str


class StudentResponse(StudentBase):
    id: int
    parent_id: int
    parent_name: Optional[str] = None
    created_at: datetime
