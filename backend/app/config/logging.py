#======================================#
#              logging.py              #
#======================================#

import logging
import logging.handlers
import sys
from pathlib import Path


try:
    from app.config.settings import BASE_DIR, EnvironmentType, settings
except Exception:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    class EnvironmentType:
        DEVELOPMENT = "dev"
        PRODUCTION = "prod"
        STAGING = "stg"

    class _FallbackSettings:
        ENV = EnvironmentType.DEVELOPMENT
        LOG_LEVEL = None

        @property
        def is_development(self) -> bool:
            return self.ENV == EnvironmentType.DEVELOPMENT

    settings = _FallbackSettings()


LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

_CONFIGURED_ATTR = "_learnlyai_logging_configured"

_STANDARD_RECORD_ATTRS = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
) | frozenset({"message", "asctime"})


def is_development() -> bool:
    return getattr(settings, "is_development", False)


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
    """Adds custom extra={...} fields to log lines."""

    def format(self, record: logging.LogRecord) -> str:
        record.source = self._source_path(record)
        message = super().format(record)

        extras = [
            (key, value)
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_ATTRS
        ]

        if not extras:
            return message

        extra_part = " | ".join(
            f"{key}={value!r}"
            for key, value in sorted(extras)
        )

        return f"{message} | {extra_part}"

    @staticmethod
    def _source_path(record: logging.LogRecord) -> str:
        try:
            path = Path(record.pathname).resolve().relative_to(BASE_DIR)
        except ValueError:
            path = Path(record.pathname).name

        return f"{path}:{record.lineno}"


def _build_console_handler(console_level: int) -> logging.Handler:
    console_format = (
        "%(asctime)s | %(levelname)-8s | source=%(source)s | "
        "%(name)s | %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(console_level)
    handler.setFormatter(
        ContextFormatter(console_format, datefmt="%Y-%m-%d %H:%M:%S")
    )

    return handler


def _build_file_handler() -> logging.Handler:
    LOG_DIR.mkdir(exist_ok=True)

    file_format = (
        "%(asctime)s | %(levelname)-8s | source=%(source)s | "
        "%(name)s | %(message)s"
    )

    handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        ContextFormatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
    )

    return handler


def _build_handlers(console_level: int) -> list[logging.Handler]:
    handlers: list[logging.Handler] = [
        _build_console_handler(console_level)
    ]

    if is_development():
        handlers.append(_build_file_handler())

    return handlers


def _attach_handlers(logger: logging.Logger, handlers: list[logging.Handler]) -> None:
    logger.handlers.clear()

    for handler in handlers:
        logger.addHandler(handler)

    logger.propagate = False


def configure_logging() -> None:
    app_logger = logging.getLogger("backend")

    if getattr(app_logger, _CONFIGURED_ATTR, False):
        return

    console_level = resolve_log_level()
    handlers = _build_handlers(console_level)

    app_logger.setLevel(logging.DEBUG)
    _attach_handlers(app_logger, handlers)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.setLevel(logging.DEBUG)
        _attach_handlers(uvicorn_logger, handlers)

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
            "env": settings.ENV,
            "console_level": logging.getLevelName(console_level),
            "file_logging": is_development(),
        },
    )

configure_logging()

def get_logger(name: str) -> logging.Logger:
    if not name.startswith("backend."):
        name = f"backend.{name.lstrip('.')}"

    return logging.getLogger(name)

