#==========================#
# WHATSAPP_SERVICE SCRIPT
#==========================#



from ..core.logging import get_logger
from requests.exceptions import RequestException
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from ..core.config import get_settings

logger = get_logger()


class WhatsAppService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self._from = settings.TWILIO_WHATSAPP_FROM

    async def send_text(self , to:str , body: str) -> bool:
        recipient = to if to.startswith("whatsapp") else f"whatsapp:{to}"
        sender = self._from if self._from.startswith("whatsapp")  else f"whatsapp:{self._from}"


        try:
            message = self._client.messages.create(
                body = body,
                from_ = sender,
                to = recipient
            )
            logger.info("WhatsApp message sent | sid=%s | to=%s", message.sid, recipient)
            return True

        except TwilioRestException as exc:
            logger.exception("Failed to send WhatsApp message to %s: %s", recipient, exc)
            return False
        except RequestException as exc:
            logger.exception("Transport error sending WhatsApp message to %s: %s", recipient, exc)
            return False
