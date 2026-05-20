#==========================#
# FEE_HELPER SCRIPT
#==========================#

from enum import Enum


class PaymentStatus(str, Enum):
    PAID = "paid"
    PARTIAL = "partial"
    UNPAID = "unpaid"
