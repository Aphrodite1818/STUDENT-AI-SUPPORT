#==========================#
# PARENT_HELPER SCRIPT
#==========================#

from enum import Enum


class LanguagePreference(str, Enum):
    ENGLISH = "english"
    PIDGIN = "pidgin"
    YORUBA = "yoruba"
    IGBO = "igbo"
    HAUSA = "hausa"
