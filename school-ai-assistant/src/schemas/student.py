# schemas/student.py

from datetime import date, datetime
from typing import Optional

from schemas.common import BaseSchema


class StudentBase(BaseSchema):
    full_name: str
    date_of_birth: date
    class_level: str
    admission_number: str


class StudentCreate(StudentBase):
    parent_id: int


class StudentUpdate(BaseSchema):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    class_level: Optional[str] = None
    admission_number: Optional[str] = None
    parent_id: Optional[int] = None


class StudentSummary(BaseSchema):
    id: int
    full_name: str
    class_level: str
    admission_number: str


class StudentOut(StudentBase):
    id: int
    parent_id: int
    parent_name: Optional[str] = None
    created_at: datetime