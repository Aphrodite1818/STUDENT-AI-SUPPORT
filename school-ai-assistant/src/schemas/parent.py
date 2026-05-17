# schemas/parent.py

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from schemas.common import BaseSchema
from schemas.student import StudentSummary


class LanguagePreference(str, Enum):
    ENGLISH = "english"
    PIDGIN = "pidgin"
    YORUBA = "yoruba"
    IGBO = "igbo"
    HAUSA = "hausa"


class ParentBase(BaseSchema):
    full_name: str
    phone_number: str = Field(..., min_length=10, max_length=20)
    language_preference: LanguagePreference = LanguagePreference.ENGLISH


class ParentCreate(ParentBase):
    pass


class ParentUpdate(BaseSchema):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    language_preference: Optional[LanguagePreference] = None


class ParentOut(ParentBase):
    id: int
    students: List[StudentSummary] = []
    created_at: datetime


class ParentWhatsAppLookup(BaseSchema):
    phone_number: str