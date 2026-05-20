#==========================#
# PARENT SCRIPT
#==========================#

# schemas/parent.py

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ..helpers.parent_helper import LanguagePreference
from .common import BaseSchema
from .student import StudentSummary


class ParentBase(BaseSchema):
    full_name: str = Field(..., min_length=1, max_length=120)
    phone_number: str = Field(..., min_length=10, max_length=20)
    language_preference: LanguagePreference = LanguagePreference.ENGLISH


class ParentCreate(ParentBase):
    pass


class ParentUpdate(BaseSchema):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=20)
    language_preference: Optional[LanguagePreference] = None


class ParentResponse(ParentBase):
    id: int
    students: List[StudentSummary] = Field(default_factory=list)
    created_at: datetime


class ParentWhatsAppLookup(BaseSchema):
    phone_number: str = Field(..., min_length=10, max_length=20)
