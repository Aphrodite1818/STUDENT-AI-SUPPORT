#==========================#
# AI_HELPER SCRIPT
#==========================#

from enum import Enum


class LLMChannel(str, Enum):
    """Enumerates which surface the message came from."""

    WHATSAPP = "whatsapp"
    WHATSSAP = "whatssap"
    WEB = "web"
    ADMIN = "admin"


class LLMIntent(str, Enum):
    """Classifies parent intent into sections for easy querying."""

    ASSIGNMENT_QUERY = "assignment_query"
    RESULT_QUERY = "result_query"
    ATTENDANCE_QUERY = "attendance_query"
    FEE_QUERY = "fee_query"
    ANNOUNCEMENT_QUERY = "announcement_query"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class LLMResponseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TOOL_CALL = "tool_call"







SYSTEM_PROMPT = """
You are a helpful school assistant for parents.
You help parents get information about their children's assignments,
results, attendance, fees, and school announcements.
 
Rules:
- Always respond in the same language the parent used.
- If the parent wrote in Pidgin English, reply in Pidgin English.
- Be brief, warm, and clear.
- If you do not have enough information to answer, say so honestly.
- Never make up student data.
- If the parent's request is unclear, ask one clarifying question.
""".strip()
 
 
_INTENT_KEYWORDS: dict[LLMIntent, list[str]] = {
    LLMIntent.ASSIGNMENT_QUERY:   ["assignment", "homework", "classwork", "task"],
    LLMIntent.RESULT_QUERY:       ["result", "score", "grade", "mark", "report"],
    LLMIntent.ATTENDANCE_QUERY:   ["attendance", "absent", "present", "school today"],
    LLMIntent.FEE_QUERY:          ["fee", "payment", "invoice", "bill", "owe"],
    LLMIntent.ANNOUNCEMENT_QUERY: ["announcement", "notice", "event", "holiday", "news"],
    LLMIntent.GREETING:           ["hi", "hello", "good morning", "good afternoon", "hey"],
}
 
 
def _detect_intent(text: str) -> LLMIntent:
    """
    Simple keyword-based intent detection.
    Good enough for now — replace with LLM-based classification later.
    """
    lowered = text.lower()
    for intent, keywords in _INTENT_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return intent
    return LLMIntent.UNKNOWN