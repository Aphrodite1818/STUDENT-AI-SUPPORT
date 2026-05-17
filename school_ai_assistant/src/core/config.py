#==========================#
#  CONFIGURATIOIN SETTINGS #
#==========================#


from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    Centralized configuration for the application.
    Fail-fast validation at startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    ENV: str = Field(...)

    #SUPABASE_URL: str = Field(..., min_length=10)

    DATABASE_URL: str = Field(..., description="Async Postgres URL")

    @field_validator("ENV")
    @classmethod
    def validate_env(cls, v):
        allowed = {"dev", "staging", "prod"}
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v

    @field_validator( "DATABASE_URL")
    @classmethod
    def no_empty_values(cls, v, field):
        if not v or not str(v).strip():
            raise ValueError(f"{field.field_name} cannot be empty")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()