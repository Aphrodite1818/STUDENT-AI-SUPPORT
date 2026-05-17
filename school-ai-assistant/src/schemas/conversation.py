# schemas/conversation.py

from datetime import datetime
from enum import Enum
from typing import Optional

from schemas.common import BaseSchema


class Platform(str, Enum):
    WHATSAPP = "whatsapp"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ContentType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class ConversationSessionCreate(BaseSchema):
    parent_id: int
    platform: Platform = Platform.WHATSAPP


class ConversationSessionOut(BaseSchema):
    id: int
    parent_id: int
    started_at: datetime
    last_active: datetime
    turn_count: int


class MessageLogCreate(BaseSchema):
    session_id: int
    direction: MessageDirection
    content_type: ContentType
    raw_content: str
    processed_content: Optional[str] = None


class MessageLogOut(MessageLogCreate):
    id: int
    created_at: datetime