"""
logging_config.py
------------------
Centralized logging configuration using Loguru.

Provides structured, leveled logging to both the console and a rotating
log file. Used by middleware for request/response logging and throughout
the service layer for execution and error logging.
"""

import sys
from pathlib import Path

from loguru import logger

from config import settings


def configure_logging() -> None:
    """
    Configure Loguru sinks (console + file) based on application settings.
    Should be called once at application startup.
    """
    logger.remove()  # remove default handler

    # Console sink: human-readable, colorized
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=False,
        diagnose=False,
    )

    # File sink: JSON-structured, rotating, retained for 14 days
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        serialize=True,  # JSON lines, ideal for log aggregation systems
        backtrace=False,
        diagnose=False,
        enqueue=True,  # thread/async-safe
    )

    logger.info(
        "Logging configured | environment={} | level={}",
        settings.ENVIRONMENT,
        settings.LOG_LEVEL,
    )


__all__ = ["logger", "configure_logging"]
