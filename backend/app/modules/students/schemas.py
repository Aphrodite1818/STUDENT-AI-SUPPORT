#======================================#
#              schemas.py              #
#======================================#


import uuid
from datetime import date, datetime

from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from backend.app.modules.students.models import Gender, AcademicStatus



class StudentBase(BaseModel):
    firstname : str = Field(min_length=3, max_length=100)

    lastname : str = Field(min_length=3, max_length=100)

    gender : Gender

    date_of_birth : date 

    passport_photo_url : Optional[str] = Field(default=None, max_length=150)

    parent_id : uuid.UUID

    class_id : uuid.UUID

    arm : Optional[str] = Field(default=None, max_length=20)

    graduation_date : Optional[date] = None

    model_config = {"str_strip_whitespace": True}

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return value


class StudentCreate(StudentBase):
    admission_number : str = Field(min_length=1, max_length=50)

    admission_date : date

    status : AcademicStatus = AcademicStatus.ACTIVE

    @model_validator(mode="after")
    def validate_student_create(self):
        if self.admission_date < self.date_of_birth:
            raise ValueError("admission_date cannot be before date_of_birth")

        if self.graduation_date and self.graduation_date < self.admission_date:
            raise ValueError("graduation_date cannot be before admission_date")

        if self.status == AcademicStatus.GRADUATED and self.graduation_date is None:
            raise ValueError("graduation_date is required when status is graduated")

        if self.status != AcademicStatus.GRADUATED and self.graduation_date is not None:
            raise ValueError("graduation_date should only be set for graduated students")

        return self




class StudentUpdate(BaseModel):
    firstname: Optional[str] = Field(default=None, min_length=3, max_length=100)

    lastname: Optional[str] = Field(default=None, min_length=3, max_length=100)

    gender: Optional[Gender] = None

    date_of_birth: Optional[date] = None

    passport_photo_url: Optional[str] = Field(default=None, max_length=150)

    parent_id: Optional[uuid.UUID] = None

    class_id: Optional[uuid.UUID] = None

    arm: Optional[str] = Field(default=None, max_length=20)

    graduation_date: Optional[date] = None

    model_config = {"str_strip_whitespace": True}

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return value




class StudentAcademicStatusUpdate(BaseModel):
    status : AcademicStatus

    graduation_date : Optional[date] = None

    @model_validator(mode="after")
    def validate_status_update(self):
        if self.status == AcademicStatus.GRADUATED and self.graduation_date is None:
            raise ValueError("graduation_date is required when status is graduated")

        if self.status != AcademicStatus.GRADUATED and self.graduation_date is not None:
            raise ValueError("graduation_date should only be set for graduated students")

        return self



class StudentResponse(StudentBase):
    id : uuid.UUID
    tenant_id : uuid.UUID
    created_at : datetime
    updated_at : datetime
    admission_number : str
    admission_date : date
    status : AcademicStatus

    model_config = {"from_attributes": True}


class StudentPublicResponse(BaseModel):
    id : uuid.UUID
    firstname : str
    lastname : str
    gender : Gender
    admission_number : str
    class_id : uuid.UUID
    arm : Optional[str] = None
    status : AcademicStatus

    model_config = {"from_attributes": True}
    






