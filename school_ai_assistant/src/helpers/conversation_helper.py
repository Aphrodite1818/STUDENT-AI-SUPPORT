#==========================#
# CONVERSATION_HELPER SCRIPT
#==========================#

from enum import Enum


class Platform(str, Enum):
    WHATSAPP = "whatsapp"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ContentType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
