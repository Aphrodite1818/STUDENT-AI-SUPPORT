#==========================#
#      AI SCHEMAS.PY       #
#==========================#

"""PURE PURPOSE IS FOR DATA TRANSFER OBJECT"""
from attr import field
from pydantic import BaseModel , field_validator
from typing import List , Optional , Any , Dict
from enum import Enum
import re

class Role(str , Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ConversationMessage(BaseModel):
    role : Role
    content : str
    tool_name: Optional[str] = None 
    tool_call_id : Optional[str] = None


class AIChatRequest(BaseModel):
    message : str
    phone_number : str
    tenant_id : Optional[str] = None
    provider: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value : str):
        pattern = r'^\+?[1-9]\d{6,14}$'
        cleaned = re.sub(r'[\s\-().]+', '', value.strip())

        if not re.match(pattern , cleaned):
            raise ValueError(f"invalid phone number: {value}")
        return cleaned
    

def validate_phone_number(phone_number):
        pattern = r'^\+?[1-9]\d{6,14}$'
        cleaned = re.sub(r'[\s\-().]+', '', phone_number.strip())

        if not re.match(pattern , cleaned):
            # raise ValueError(f"invalud phone number: {phone_number}")
            print("weird number format")
        return cleaned