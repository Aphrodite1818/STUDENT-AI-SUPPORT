#======================================#
#            auth/schemas.py           #
#======================================#

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
    purpose: str # "verification" or "password_reset"

class VerifyOTP(BaseModel):
    email: EmailStr
    code: str
    purpose: str