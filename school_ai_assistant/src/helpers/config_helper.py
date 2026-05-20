#==========================#
# CONFIG_HELPER SCRIPT
#==========================#

from functools import lru_cache
from typing import Any

from ..core.exceptions import ConfigurationError


def validate_env_value(value: str) -> str:
    allowed = {"dev", "staging", "prod"}
    if value not in allowed:
        raise ConfigurationError(f"ENV must be one of {allowed}")
    return value


def validate_not_empty(value: Any, field_name: str) -> Any:
    if not value or not str(value).strip():
        raise ConfigurationError(f"{field_name} cannot be empty")
    return value


@lru_cache()
def get_settings():
    from ..core.config import Settings

    return Settings()
