#==========================#
# WEBHOOK_HELPER SCRIPT
#==========================#

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from ..core.exceptions import EmptyMessageError, UnsupportedMessageTypeError
from .ai_helper import LLMChannel

if TYPE_CHECKING:
    from ..schemas.ai import LLMRequest


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


AUDIO_CONTENT_TYPES = {"audio/ogg", "audio/mpeg", "audio/mp4", "audio/amr", "audio/wav"}
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
DOCUMENT_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

UNSUPPORTED_TYPE_REPLY = (
    "Hi! I can only receive text messages, voice notes, images, and documents. "
    "Please try again with one of those"
)


def resolve_message_type(
    body: Optional[str],
    media_content_type: Optional[str],
) -> MessageType:
    if media_content_type:
        mime = media_content_type.lower().split(";")[0].strip()
        if mime in AUDIO_CONTENT_TYPES:
            return MessageType.AUDIO
        if mime in IMAGE_CONTENT_TYPES:
            return MessageType.IMAGE
        if mime in DOCUMENT_CONTENT_TYPES:
            return MessageType.DOCUMENT
        raise UnsupportedMessageTypeError(f"Unsupported media type received: {mime}")

    if body and body.strip():
        return MessageType.TEXT

    raise EmptyMessageError("Message has no body and no recognized media.")


def normalize_whatsapp_address(value: Optional[str], waid: Optional[str] = None) -> str:
    """
    Convert Twilio WhatsApp addresses like ``whatsapp:+234...`` into plain E.164.

    If Twilio provides a WaId, use it as a fallback and prefix it with ``+`` so
    downstream schemas always receive a predictable phone format.
    """
    if value:
        normalized = value.strip()
        if normalized.lower().startswith("whatsapp:"):
            normalized = normalized.split(":", 1)[1].strip()
        if normalized:
            return normalized

    if waid:
        digits = waid.strip()
        if digits:
            return digits if digits.startswith("+") else f"+{digits}"

    return ""


def build_normalized_inbound_message_data(payload: Any) -> dict[str, Any]:
    message_type = resolve_message_type(payload.Body, payload.MediaContentType0)
    return {
        "sender": normalize_whatsapp_address(payload.From, payload.WaId),
        "recipient": normalize_whatsapp_address(payload.To),
        "message_type": message_type,
        "text": payload.Body if message_type == MessageType.TEXT else None,
        "media_urls": [payload.MediaUrl0] if payload.MediaUrl0 else [],
        "media_content_types": [payload.MediaContentType0] if payload.MediaContentType0 else [],
        "message_id": payload.MessageSid,
        "profile_name": payload.ProfileName,
    }


def build_llm_request(message: Any) -> "LLMRequest":
    from ..schemas.ai import LLMContext, LLMMediaAttachment, LLMRequest

    attachments = [
        LLMMediaAttachment(
            media_url=url,
            content_type=content_type,
        )
        for url, content_type in zip(message.media_urls, message.media_content_types)
    ]

    context = LLMContext(
        sender_phone=message.sender,
        sender_name=message.profile_name,
        channel=LLMChannel.WHATSAPP,
    )

    return LLMRequest(
        text=message.text,
        attachments=attachments,
        context=context,
        message_id=message.message_id,
    )
