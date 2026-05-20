#==========================#
# FEE SCRIPT
#==========================#

# schemas/fee.py

from datetime import date, datetime
from typing import Optional

from pydantic import Field

from ..helpers.fee_helper import PaymentStatus
from .common import BaseSchema


class FeeBase(BaseSchema):
    student_id: int = Field(..., gt=0)
    amount: float = Field(..., ge=0)
    description: str = Field(..., min_length=1, max_length=255)
    due_date: date
    term: str = Field(..., min_length=1, max_length=50)
    academic_year: str = Field(..., min_length=4, max_length=20)


class FeeCreate(FeeBase):
    pass


class FeeUpdate(BaseSchema):
    amount: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    due_date: Optional[date] = None


class FeeResponse(FeeBase):
    id: int
    created_at: datetime


class FeeStatusResponse(BaseSchema):
    outstanding_balance: float = Field(..., ge=0)
    paid_amount: float = Field(..., ge=0)
    payment_status: PaymentStatus


class PaymentRecordCreate(BaseSchema):
    amount_paid: float = Field(..., gt=0)
    payment_date: date
    reference: str = Field(..., min_length=1, max_length=100)


class PaymentRecordResponse(PaymentRecordCreate):
    id: int
    fee_id: int
    created_at: datetime
