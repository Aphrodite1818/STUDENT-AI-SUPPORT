#==========================#
# ATTENDANCE SCRIPT
#==========================#

# schemas/attendance.py

from datetime import date
from typing import Optional

from pydantic import Field

from ..helpers.attendance_helper import AttendanceStatus
from .common import BaseSchema


class AttendanceBase(BaseSchema):
    student_id: int = Field(..., gt=0)
    date: date
    status: AttendanceStatus


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseSchema):
    status: Optional[AttendanceStatus] = None


class AttendanceResponse(AttendanceBase):
    id: int


class AttendanceSummary(BaseSchema):
    total_days: int = Field(..., ge=0)
    present_days: int = Field(..., ge=0)
    absent_days: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)
