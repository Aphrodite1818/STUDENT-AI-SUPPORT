#==========================#
# AI_SERVICE SCRIPT
#==========================#

from datetime import datetime
from google import genai
from google.genai import types

from ..core.config import get_settings
from ..core.logging import get_logger
from ..helpers.ai_helper import SYSTEM_PROMPT, _detect_intent
from  ..schemas.ai import(
    LLMIntent,
    LLMRequest,
    LLMResponse,
    LLMResponseStatus
)


logger = get_logger()



class AIService:
    """
    Central LLM brain, Accepts a normalized LLMRequest,
    calls Gemini, and returns a structured LLMResponse.

    Responsibilities:
    -Build the prompt from request context and history
    -calls Gemini
    -Detect intent from the user message
    -Return a structured LLMResponse

    NOT responsible for:
    -Twilio/WhatsApp sending (whatssap_service)
    -STT transcription (stt_service)
    -Database lookups (will be injected as tools later)
    """


    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.GEMINI_API_KEY
        self._timeout_seconds = settings.GEMINI_TIMEOUT_SECONDS
        self._max_retries = settings.GEMINI_MAX_RETRIES
        self._model_name = settings.GEMINI_MODEL
        self._client = self._build_client()
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        )

    def _build_client(self) -> genai.Client:
        return genai.Client(
            api_key=self._api_key,
            http_options=types.HttpOptions(
                timeout=int(self._timeout_seconds * 1000)
            ),
        )


    async def process(self , request: LLMRequest) -> LLMResponse:
        """Main entry point . Called by routes/webhook.py after normalizing the
        inbound Twilio message into an LLMRequest
        """

        try:
            prompt = self._build_prompt(request)
            raw_reply = await self._call_gemini(prompt)
            intent = _detect_intent(request.text or "")


            return LLMResponse(
                reply_text = raw_reply,
                status = LLMResponseStatus.SUCCESS,
                intent = intent,
                detected_language = "en",
                raw_llm_output = raw_reply,
                responded_at = datetime.now() 
            )
        

        except Exception as exc:
            logger.exception("AIService.process failed | error_type=%s | error=%s", type(exc).__name__, exc)
            return LLMResponse(
                reply_text = (
                    "sorry, i could not process your message right now"
                    "please try again in a moment"
                ),
                status = LLMResponseStatus.FAILED,
                intent = LLMIntent.UNKNOWN,
                responded_at = datetime.now()
            )


    def _build_prompt(self , request : LLMRequest) -> str:
        """
        Assembles the full prompt string sent to LLM


        Order 
        .Conversation History (if any)
        .Any STT transcriptions from audio attachments
        .The current text message
        """



        parts : list[str] = []

        #---conversation history ---

        for turn in request.context.conversation_history:
            role_label = "Parent" if turn.role == "user" else "Assistant"
            parts.append(f"{role_label} : {turn.content}")  


        #--audio transcripts (filled by stt_service) --
        for attachment in request.attachments:
            if attachment.transcript:
                parts.append(f"Parent(voice note) : {attachment.transcript}")


        #--current text message --
        if request.text:
            parts.append(f"Parent : {request.text}")
        return "\n".join(parts)
    

    async def _call_gemini(self , prompt : str)  -> str:
        """this method sends the assembled prompt to gemini """
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=self._config,
                )
                reply_text = (response.text or "").strip()
                if reply_text:
                    return reply_text

                raise RuntimeError("Gemini returned an empty text response")
            except Exception as exc:
                last_error = exc
                is_final_attempt = attempt >= self._max_retries

                if is_final_attempt or not self._is_retryable_error(exc):
                    raise

                logger.warning(
                    "Retrying Gemini request after transient error | attempt=%s/%s | error=%s",
                    attempt + 1,
                    self._max_retries + 1,
                    exc,
                )
                await self._reset_async_client()

        raise last_error or RuntimeError("Gemini request failed without an exception")

    def _is_retryable_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        retryable_markers = (
            "closed",
            "connection",
            "timeout",
            "timed out",
            "disconnect",
            "server disconnected",
            "pool",
            "transport",
        )
        return any(marker in message for marker in retryable_markers)

    async def _reset_async_client(self) -> None:
        try:
            await self._client.aio.aclose()
        except Exception:
            logger.debug("Gemini async client close skipped during reset", exc_info=True)
        self._client = self._build_client()

    async def aclose(self) -> None:
        try:
            await self._client.aio.aclose()
        except Exception:
            logger.debug("Gemini async client close skipped during shutdown", exc_info=True)
    

    







