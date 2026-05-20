#==========================#
# CONFIG SCRIPT
#==========================#

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path

from ..helpers.config_helper import get_settings, validate_env_value, validate_not_empty


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """
    Centralized configuration for the application.
    Fail-fast validation at startup.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore",
    )

    ENV: str = Field(..., description="type of env file")

    #SUPABASE_URL: str = Field(..., min_length=10)

    DATABASE_URL: str = Field(..., description="Async Postgres URL")
    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio auth token")
    TWILIO_WHATSAPP_FROM: str = Field(..., description="Twilio WhatsApp sandbox number")
    GEMINI_API_KEY :str = Field(..., description = "google gemini api key")
    GEMINI_MODEL: str = Field(
        "gemini-flash-lite-latest",
        description="Gemini model used for chatbot replies",
    )
    GEMINI_TIMEOUT_SECONDS: float = Field(
        90.0,
        gt=0,
        description="Timeout for Gemini API requests in seconds",
    )
    GEMINI_MAX_RETRIES: int = Field(
        1,
        ge=0,
        description="Number of retry attempts for transient Gemini errors",
    )

    @field_validator("ENV")
    @classmethod
    def validate_env(cls, v):
        return validate_env_value(v)

    @field_validator( "DATABASE_URL")
    @classmethod
    def no_empty_values(cls, v, field):
        return validate_not_empty(v, field.field_name)
