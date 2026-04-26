# src/core/logger.py
import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercepts standard Python logs and routes them to Loguru."""
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        try:
            message = record.getMessage()
        except TypeError:
            message = str(record.msg)

        logger.opt(depth=depth, exception=record.exc_info).log(level, message)

def setup_logging():
    """Configures Loguru to handle all FastAPI and Uvicorn logs cleanly."""
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    loggers_to_hijack = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi"
    )

    for logger_name in loggers_to_hijack:
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [InterceptHandler()] 
        std_logger.propagate = False               