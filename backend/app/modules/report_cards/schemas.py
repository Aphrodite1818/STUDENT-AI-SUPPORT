import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.modules.report_cards.models import ReportCardStatus


class InputBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, use_enum_values=True)


class OutputBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True, populate_by_name=True)


class ReportCardGenerateRequest(InputBase):
    student_id: uuid.UUID
    academic_session_id: uuid.UUID
    academic_term_id: uuid.UUID


class ReportCardSubjectLineResponse(OutputBase):
    id: uuid.UUID
    subject_id: uuid.UUID
    subject_name: str
    subject_code: str | None = None
    teacher_name: str | None = None
    test_score: Decimal
    assessment_score: Decimal
    exam_score: Decimal
    total_score: Decimal
    grade: str
    remark: str | None = None


class ReportCardResponse(OutputBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str | None = None
    admission_number: str | None = None
    student_passport_photo_url: str | None = None
    class_id: uuid.UUID
    class_name: str | None = None
    class_arm: str | None = None
    academic_session_id: uuid.UUID
    academic_session_name: str | None = None
    academic_term_id: uuid.UUID
    academic_term_name: str | None = None
    total_score: Decimal
    average_score: Decimal
    status: ReportCardStatus
    lines: list[ReportCardSubjectLineResponse] = []
    created_at: datetime
    updated_at: datetime


class ReportCardListResponse(OutputBase):
    items: list[ReportCardResponse]
    total: int
