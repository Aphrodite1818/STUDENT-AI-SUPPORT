# schemas/fee.py

from datetime import date, datetime
from enum import Enum
from typing import Optional

from schemas.common import BaseSchema


class PaymentStatus(str, Enum):
    PAID = "paid"
    PARTIAL = "partial"
    UNPAID = "unpaid"


class FeeBase(BaseSchema):
    student_id: int
    amount: float
    description: str
    due_date: date
    term: str
    academic_year: str


class FeeCreate(FeeBase):
    pass


class FeeUpdate(BaseSchema):
    amount: Optional[float] = None
    description: Optional[str] = None
    due_date: Optional[date] = None


class FeeOut(FeeBase):
    id: int
    created_at: datetime


class FeeStatusOut(BaseSchema):
    outstanding_balance: float
    paid_amount: float
    payment_status: PaymentStatus


class PaymentRecordCreate(BaseSchema):
    amount_paid: float
    payment_date: date
    reference: str