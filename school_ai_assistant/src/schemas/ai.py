#==========================#
# AI SCRIPT
#==========================#

from datetime import datetime
from typing import Any , Dict , List , Optional 
from pydantic import Field
from .common import BaseSchema
from ..helpers.ai_helper import LLMChannel, LLMIntent, LLMResponseStatus


class ConversationTurn(BaseSchema):
    role : str = Field(..., min_length =1)
    content : str = Field(..., min_length = 2)
    timestamp : datetime


class LLMMediaAttachment(BaseSchema):
    media_url : str
    content_type : str
    transcript : Optional[str] = None   #filled by stt 
    #description: Optional[str] = None


LLMMediaAttacment = LLMMediaAttachment


class LLMContext(BaseSchema):
    """this schema highlights everything the llm needs to know about who is speaking"""

    sender_phone: str = Field(..., min_length=10, max_length=20)
    sender_name: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, gt=0)
    student_id: Optional[int] = Field(default=None, gt=0)
    session_id: Optional[str] = None
    channel: LLMChannel = LLMChannel.WHATSAPP
    conversation_history: List[ConversationTurn] = Field(default_factory=list)



class LLMRequest(BaseSchema):
    """this is a normalized input that the ai service receives built from NormalizedInboundMessage
    in the webhook route"""
 
    text : Optional[str] = None
    attachments : List[LLMMediaAttachment] = Field(default_factory=list)
    context : LLMContext
    message_id : str
    received_at : datetime  = Field(default_factory=datetime.now)



class LLMToolResult(BaseSchema):
    """the result of executing a tool """
    tool_name : str
    success : bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str]  = None


class LLMToolCall(BaseSchema):
    """Describes a tool the llm wants to invoke"""

    tool_name : str = Field(..., min_length =1)
    parameters: Dict[str, Any] = Field(default_factory=dict)



class LLMResponse(BaseSchema):
    """structured output of ai_service"""
    reply_text : str = Field(..., min_length = 1)
    status : LLMResponseStatus = LLMResponseStatus.SUCCESS
    intent: LLMIntent = LLMIntent.UNKNOWN
    confidence : float = Field(default = 0.0 , ge = 0 , le = 1)
    detected_language :str = Field(default= "en")
    data_sources_used: List[str] = Field(default_factory=list)
    tool_calls : List[LLMToolCall] =    Field(default_factory=list)
    follow_up_prompt : Optional[str] = None
    raw_llm_output : Optional[str] = None
    responded_at : datetime = Field(default_factory=datetime.now)


class STTRequest(BaseSchema):
    audio_url : str = Field(..., min_length = 1)
    language_hint : Optional[str] = None
    parent_phone : str = Field(..., min_length = 12)


class STTResponse(BaseSchema):
    transcript : str = Field(..., min_length=1)
    language_detected : Optional[str] = None
    confidence : float = Field(..., ge = 0 , le= 1)


class IntentClassification(BaseSchema):
    intent: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0, le=1)
    detected_language: str = Field(..., min_length=1)
    entities: Dict[str, Any]
