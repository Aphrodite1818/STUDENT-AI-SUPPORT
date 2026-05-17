# schemas/webhook.py

from typing import Optional

from schemas.common import BaseSchema


class TwilioInboundMessage(BaseSchema):
    From: str
    To: str
    Body: str
    MessageSid: str
    NumMedia: int


class TwilioMediaMessage(TwilioInboundMessage):
    MediaUrl0: Optional[str] = None
    MediaContentType0: Optional[str] = None


class TwilioWebhookResponse(BaseSchema):
    message: str


class WebhookAckResponse(BaseSchema):
    success: bool = True
    message: str = "Webhook received"