#======================================#
#              logging.py              #
#======================================#


import logging
import logging.handlers
import sys
from typing import Any

from backend.app.config.settings import BASE_DIR, EnvironmentType, settings


LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "backend.app.log"

_CONFIGURED_ATTR = "_nhs_logging_configured"

_STANDARD_RECORD_ATTRS = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
) | frozenset({"message", "asctime"})


def is_development() -> bool:
    return settings.ENV == EnvironmentType.DEVELOPMENT


def _level_from_name(name: str) -> int:
    level = getattr(logging, name.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f"Invalid log level: {name}")
    return level


def resolve_log_level() -> int:
    if settings.LOG_LEVEL:
        return _level_from_name(settings.LOG_LEVEL)
    return logging.DEBUG if is_development() else logging.INFO


class ContextFormatter(logging.Formatter):
    """Appends structured `extra={...}` fields to each log line."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_ATTRS
        }
        if not extras:
            return message
        extra_part = " | ".join(f"{key}={value!r}" for key, value in sorted(extras.items()))
        return f"{message} | {extra_part}"


def _build_handlers(console_level: int) -> tuple[logging.Handler, logging.Handler]:
    console_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(
        ContextFormatter(console_format, datefmt="%Y-%m-%d %H:%M:%S")
    )

    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        ContextFormatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
    )

    return console_handler, file_handler


def _attach_handlers(logger: logging.Logger, *handlers: logging.Handler) -> None:
    logger.handlers.clear()
    for handler in handlers:
        logger.addHandler(handler)
    logger.propagate = False


def configure_logging() -> None:
    app_logger = logging.getLogger("backend")
    if getattr(app_logger, _CONFIGURED_ATTR, False):
        return

    console_level = resolve_log_level()
    console_handler, file_handler = _build_handlers(console_level)

    app_logger.setLevel(logging.DEBUG)
    _attach_handlers(app_logger, console_handler, file_handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.setLevel(logging.DEBUG)
        _attach_handlers(uvicorn_logger, console_handler, file_handler)

    if is_development() or console_level <= logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    setattr(app_logger, _CONFIGURED_ATTR, True)

    app_logger.info(
        "Logging configured",
        extra={
            "env": settings.ENV.value,
            "console_level": logging.getLevelName(console_level),
            "log_file": str(LOG_FILE),
        },
    )


configure_logging()


def get_logger(name: str) -> logging.Logger:
    if not name.startswith("backend."):
        name = f"backend.{name.lstrip('.')}"
    return logging.getLogger(name)
