#==========================#
# CONVERSATION SCRIPT
#==========================#

# schemas/conversation.py

from datetime import datetime
from typing import Optional

from pydantic import Field

from ..helpers.conversation_helper import ContentType, MessageDirection, Platform
from .common import BaseSchema


class ConversationSessionCreate(BaseSchema):
    parent_id: int = Field(..., gt=0)
    platform: Platform = Platform.WHATSAPP


class ConversationSessionResponse(BaseSchema):
    id: int
    parent_id: int
    started_at: datetime
    last_active: datetime
    turn_count: int = Field(..., ge=0)


class MessageLogCreate(BaseSchema):
    session_id: int = Field(..., gt=0)
    direction: MessageDirection
    content_type: ContentType
    raw_content: str = Field(..., min_length=1)
    processed_content: Optional[str] = None


class MessageLogResponse(MessageLogCreate):
    id: int
    created_at: datetime
