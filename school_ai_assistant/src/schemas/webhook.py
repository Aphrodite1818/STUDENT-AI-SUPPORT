#==========================#
# WEBHOOK SCRIPT
#==========================#

from typing import List, Optional
from pydantic import model_validator, Field
from .common import BaseSchema
from .ai import LLMRequest
from ..helpers.webhook_helper import (
    MessageType,
    build_llm_request,
    build_normalized_inbound_message_data,
    resolve_message_type,
)


# =========================
# 3. RAW TWILIO PAYLOAD
# =========================
class TwilioInboundMessage(BaseSchema):
    """
    Mirrors exact Twilio POST fields.
    Stays at the boundary - never passed deeper into the system.
    """
    From: str
    To: str
    Body: Optional[str] = None
    MessageSid: str
    NumMedia: Optional[str] = "0"
    MediaUrl0: Optional[str] = None
    MediaContentType0: Optional[str] = None
    ProfileName: Optional[str] = None
    WaId: Optional[str] = None

    @model_validator(mode="after")
    def validate_supported_type(self) -> "TwilioInboundMessage":
        resolve_message_type(self.Body, self.MediaContentType0)
        return self


# =========================
# 4. NORMALIZED MESSAGE
# =========================
class NormalizedInboundMessage(BaseSchema):
    """
    Clean internal contract used everywhere in the system.
    Always built via .from_twilio() - never constructed manually.
    """
    sender: str
    recipient: str
    message_type: MessageType
    text: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    media_content_types: List[str] = Field(default_factory=list)
    message_id: str
    profile_name: Optional[str] = None

    @classmethod
    def from_twilio(cls, payload: TwilioInboundMessage) -> "NormalizedInboundMessage":
        return cls(**build_normalized_inbound_message_data(payload))

    def to_llm_request(self) -> LLMRequest:
        """
        Convert this normalized message into the LLMRequest contract
        that ai_service.py expects.

        The webhook route calls this after building a NormalizedInboundMessage,
        then passes the result straight to the AI service.

        parent_id / student_id are not resolved here - that is the AI service's job
        once it looks up the sender phone in the database.
        """
        return build_llm_request(self)


# =========================
# 5. RESPONSES
# =========================
class TwilioWebhookResponse(BaseSchema):
    message: str


class WebhookAckResponse(BaseSchema):
    success: bool = True
    message: str = "Webhook received"
