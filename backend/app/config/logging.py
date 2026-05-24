#======================================#
#              logging.py              #
#======================================#

import logging

from backend.app.config.settings import settings


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


LOG_LEVEL = (
    logging.DEBUG
    if settings.ENV == "dev"
    else logging.INFO
)


logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)


logging.getLogger("passlib").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)