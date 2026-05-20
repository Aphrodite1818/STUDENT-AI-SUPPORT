#==========================#
# RESULT SCRIPT
#==========================#

# schemas/result.py

from datetime import datetime
from typing import Optional

from pydantic import Field

from .common import BaseSchema


class ResultBase(BaseSchema):
    student_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)
    term: str = Field(..., min_length=1, max_length=50)
    score: float = Field(..., ge=0, le=100)
    grade: str = Field(..., min_length=1, max_length=5)
    remarks: Optional[str] = None


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseSchema):
    score: Optional[float] = Field(default=None, ge=0, le=100)
    grade: Optional[str] = Field(default=None, min_length=1, max_length=5)
    remarks: Optional[str] = None


class ResultResponse(ResultBase):
    id: int
    created_at: datetime


class ResultSummary(BaseSchema):
    student_id: int = Field(..., gt=0)
    student_name: str
    term: str
    average_score: float = Field(..., ge=0, le=100)
    gpa_equivalent: float = Field(..., ge=0)
