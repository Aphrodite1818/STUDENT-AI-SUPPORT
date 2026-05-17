# schemas/attendance.py

from datetime import date
from enum import Enum
from typing import Optional

from schemas.common import BaseSchema


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class AttendanceBase(BaseSchema):
    student_id: int
    date: date
    status: AttendanceStatus


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseSchema):
    status: Optional[AttendanceStatus] = None


class AttendanceOut(AttendanceBase):
    id: int


class AttendanceSummary(BaseSchema):
    total_days: int
    present_days: int
    absent_days: int
    percentage: float