# schemas/ai.py

from datetime import datetime
from typing import Any, Dict, List, Optional

from schemas.common import BaseSchema


class IntentClassification(BaseSchema):
    intent: str
    confidence: float
    detected_language: str
    entities: Dict[str, Any]


class STTRequest(BaseSchema):
    audio_url: str
    language_hint: Optional[str] = None
    parent_phone: str


class STTResult(BaseSchema):
    transcript: str
    language_detected: str
    confidence: float


class AIQueryRequest(BaseSchema):
    transcript: str
    parent_id: int
    student_id: Optional[int] = None
    session_id: Optional[str] = None


class AIQueryResponse(BaseSchema):
    reply_text: str
    intent: str
    data_used: List[str]
    follow_up_prompt: Optional[str] = None


class ConversationTurn(BaseSchema):
    role: str
    content: str
    timestamp: datetime