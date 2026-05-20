#==========================#
# LOGGING SCRIPT
#==========================#


import logging
from typing import Optional


DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(
    level: int = logging.INFO,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: Optional[str] = None,
) -> None:
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        force=True,
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
