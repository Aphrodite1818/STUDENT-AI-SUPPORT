#======================================#
#              logging.py              #
#======================================#



import logging
import logging.handlers
import sys
from pathlib import Path

from backend.app.config.settings import settings, BASE_DIR



LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "backend.app.log"

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

LOG_FORMAT_DEBUG = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s:%(lineno)d | "
    "%(message)s"
)

APP_LOG_LEVEL = logging.DEBUG if settings.ENV == "dev" else logging.INFO


_console_formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
_file_formatter    = logging.Formatter(LOG_FORMAT_DEBUG, datefmt="%Y-%m-%d %H:%M:%S")


# Console — INFO and above always, DEBUG only in dev
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setLevel(logging.DEBUG if settings.ENV == "dev" else logging.INFO)
_console_handler.setFormatter(_console_formatter)

# Rotating file — always writes DEBUG and above so you have full history on disk
_file_handler = logging.handlers.RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=5 * 1024 * 1024,   
    backupCount=5,              
    encoding="utf-8",
)
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(_file_formatter)



_root_app_logger = logging.getLogger("backend")
_root_app_logger.setLevel(logging.DEBUG)          
_root_app_logger.addHandler(_console_handler)
_root_app_logger.addHandler(_file_handler)
_root_app_logger.propagate = False               


logging.getLogger("passlib").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(
    logging.INFO if settings.ENV == "dev" else logging.WARNING
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


logging.getLogger("uvicorn").addHandler(_file_handler)
logging.getLogger("uvicorn.error").addHandler(_file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)