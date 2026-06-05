#======================================#
#             settings.py              #
#======================================#


"""
Loads and validates all environment variables at startup using Pydantic BaseSettings.
If any required variable is missing or invalid the application will refuse to boot.
"""

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field
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

    # Optional override — set LOG_LEVEL=DEBUG in .env to see debug logs even when ENV=prod
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None

    APP_NAME: str = "School Management System"
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")

    GEMINI_API_KEY: str | None = Field(default=None, description="Api Key for Gemini")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    OPENAI_API_KEY: str | None = Field(default=None, description="Api Key for OpenAI")
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str | None = Field(default=None, description="Api Key for Anthropic")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    LLM_MAX_TOKENS: int = 1024
    

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:8501",
    ]

    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio auth token")
    TWILIO_WHATSAPP_FROM: str = Field(..., description="Twilio WhatsApp number")

    # SMTP Settings for Emails (Optional for local testing)
    SMTP_HOST: str | None = Field(default=None, description="SMTP Server Host")
    SMTP_PORT: int = Field(default=587, description="SMTP Server Port")
    SMTP_PASSWORD: str | None = Field(default=None, description="SMTP Password")
    SMTP_FROM_EMAIL: str | None = Field(default=None, description="Sender Email Address")

    # OTP Settings
    OTP_EXPIRATION_MINUTES: int = 10

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_development(self) -> bool:
        return self.ENV == EnvironmentType.DEVELOPMENT


settings = Settings()
