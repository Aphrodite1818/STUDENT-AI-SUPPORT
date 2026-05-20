#==========================#
#       WEBHOOK SCRIPT     #
#==========================#

from fastapi import APIRouter , Form
from ..core.logging import get_logger
from datetime import datetime, timedelta
from typing import Optional
from pydantic import ValidationError
from ..helpers.webhook_helper import UNSUPPORTED_TYPE_REPLY
from ..services.ai_service import AIService

logger = get_logger()

from ..schemas.webhook import(
    TwilioInboundMessage,
    NormalizedInboundMessage,
    WebhookAckResponse,
)

from ..services.whatsapp_service import WhatsAppService

whatsapp_service = WhatsAppService()
ai_service = AIService()
_PROCESSED_MESSAGES_TTL = timedelta(minutes=10)
_processed_message_ids: dict[str, datetime] = {}

router = APIRouter(prefix = "/webhook" , tags=['Webhook'])


def _purge_processed_messages(now: datetime) -> None:
    expired_ids = [
        message_id
        for message_id, processed_at in _processed_message_ids.items()
        if now - processed_at > _PROCESSED_MESSAGES_TTL
    ]
    for message_id in expired_ids:
        _processed_message_ids.pop(message_id, None)


def _is_duplicate_message(message_id: str) -> bool:
    now = datetime.utcnow()
    _purge_processed_messages(now)

    if message_id in _processed_message_ids:
        return True

    _processed_message_ids[message_id] = now
    return False

@router.post("")
async def twilio_webhook(
    From: str = Form(...),
    To: str = Form(...),
    MessageSid: str = Form(...),
    Body: Optional[str] = Form(default=None),
    NumMedia: Optional[str] = Form(default="0"),
    MediaUrl0: Optional[str] = Form(default=None),
    MediaContentType0: Optional[str] = Form(default=None),
    ProfileName: Optional[str] = Form(default=None),
    WaId: Optional[str] = Form(default=None),
) -> WebhookAckResponse:
    #validate payload
    try:
        payload = TwilioInboundMessage(
            From=From,
            To=To,
            Body=Body,
            MessageSid=MessageSid,
            NumMedia=NumMedia,
            MediaUrl0=MediaUrl0,
            MediaContentType0=MediaContentType0,
            ProfileName=ProfileName,
            WaId=WaId,
        )

    except ValidationError as exc:
        logger.warning("Unsupported media type from %s: %s", From, exc)
        sent = await whatsapp_service.send_text(to = From , body = UNSUPPORTED_TYPE_REPLY)
        if not sent:
            logger.warning("Failed to send unsupported media reply to %s", From)
        return WebhookAckResponse(success= True, message = "unsupported media type handled")
    
    #normalize the payload
    normalized = NormalizedInboundMessage.from_twilio(payload)

    if _is_duplicate_message(normalized.message_id):
        logger.info("Duplicate webhook ignored | sid=%s | from=%s", normalized.message_id, normalized.sender)
        return WebhookAckResponse(success=True, message="Duplicate message ignored")


    #build the llm request
    llm_request = normalized.to_llm_request()



    #calling the ai service
    llm_response = await ai_service.process(llm_request)


    #send reply
    sent = await whatsapp_service.send_text(to = normalized.sender , body = llm_response.reply_text)
    if not sent:
        logger.warning("Webhook processed but WhatsApp reply failed to send | sid=%s", normalized.message_id)


    logger.info(
        "Webhook handled | sid = %s | intent= %s| status= %s",
        normalized.message_id,
        llm_response.intent,
        llm_response.status
    )


    # ack to Twilio
    return WebhookAckResponse(success=True , message= "Message processed")
