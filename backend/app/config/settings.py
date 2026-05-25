#======================================#
#             settings.py              #
#======================================#


"""
Loads and validates all environment variables at startup using Pydantic BaseSettings.
If any required variable is missing or invalid the application will refuse to boot.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class EnvironmentType(str, Enum): 
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    STAGING = "stg"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    ENV: EnvironmentType = EnvironmentType.DEVELOPMENT  

    APP_NAME: str = "School Management System"
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")

    GEMINI_API_KEY: str = Field(..., description="Gemini API key for LLM")

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
    ]

    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio auth token")
    TWILIO_WHATSAPP_FROM: str = Field(..., description="Twilio WhatsApp number")


settings = Settings()