# schemas/result.py

from datetime import datetime
from typing import Optional

from schemas.common import BaseSchema


class ResultBase(BaseSchema):
    student_id: int
    course_id: int
    term: str
    score: float
    grade: str
    remarks: Optional[str] = None


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseSchema):
    score: Optional[float] = None
    grade: Optional[str] = None
    remarks: Optional[str] = None


class ResultOut(ResultBase):
    id: int
    created_at: datetime


class ResultSummary(BaseSchema):
    student_id: int
    student_name: str
    term: str
    average_score: float
    gpa_equivalent: float