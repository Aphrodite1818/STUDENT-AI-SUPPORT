#==========================#
# ANNOUNCEMENT_HELPER SCRIPT
#==========================#

from enum import Enum


class TargetAudience(str, Enum):
    ALL = "all"
    PARENTS = "parents"
    TEACHERS = "teachers"
