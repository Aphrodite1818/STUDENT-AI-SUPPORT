#==========================#
# USER_HELPER SCRIPT
#==========================#

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    PARENT = "parent"
