#======================================#
#             settings.py              #
#======================================#


"""Load and validate application settings from environment variables."""

import os
from enum import Enum
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_ENV_VALUES = dotenv_values(BASE_DIR / ".env")
ACTIVE_ENV = (
    os.getenv("ENV")
    or os.getenv("APP_ENV")
    or BASE_ENV_VALUES.get("ENV")
    or "dev"
).lower()

ENV_FILE_BY_NAME = {
    "dev": ".env.development",
    "development": ".env.development",
    "prod": ".env.production",
    "production": ".env.production",
    "stg": ".env.staging",
    "staging": ".env.staging",
}
ACTIVE_ENV_FILE = ENV_FILE_BY_NAME.get(ACTIVE_ENV, f".env.{ACTIVE_ENV}")


class EnvironmentType(str, Enum): 
    """Supported application environments."""
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    STAGING = "stg"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env",
            BASE_DIR / ACTIVE_ENV_FILE,
        ),
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

    DATABASE_URL: str | None = Field(
        default=None,
        description="PostgreSQL connection URL",
    )

    GEMINI_API_KEY: str | None = Field(default=None, description="Api Key for Gemini")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    OPENAI_API_KEY: str | None = Field(default=None, description="Api Key for OpenAI")
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str | None = Field(default=None, description="Api Key for Anthropic")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    LLM_MAX_TOKENS: int = 1024
    

    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)

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
    TENANT_ACTIVATION_EXPIRATION_HOURS: int = 48

    FRONTEND_APP_URL: str = Field(..., description="Frontend application URL")
    DEFAULT_STUDENT_PASSWORD: str = "default"

    APP_SCRIPT_URL: str = Field(...)

    @model_validator(mode="after")
    def apply_database_url_for_environment(self) -> "Settings":
        """Select the correct database URL for the active environment."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set for the active environment.")

        return self

    @property
    def is_development(self) -> bool:
        """Return whether the application is running in development mode."""
        return self.ENV == EnvironmentType.DEVELOPMENT  # returns True if dev


settings = Settings()  # pyright: ignore[reportCallIssue]
