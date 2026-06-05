#======================================#
#            auth/schemas.py           #
#======================================#

from typing import Literal

from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdatePassword(BaseModel):
    email: EmailStr
    new_password: str
    reset_token: str

class RequestOTP(BaseModel):
    email: EmailStr
    purpose: Literal["verification", "password_reset"] # "verification" or "password_reset"

class VerifyOTP(BaseModel):
    email: EmailStr
    code: str
    purpose: Literal["verification", "password_reset"]