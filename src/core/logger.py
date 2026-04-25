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

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    """Configures Loguru to handle all FastAPI and Uvicorn logs cleanly."""
    import logging
    import sys

    # 1. Remove default Loguru configuration
    logger.remove()

    # 2. Add our beautiful console logger
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # 3. The list of stubborn loggers we need to hijack
    loggers_to_hijack = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi"
    )

    # 4. Force them all to use ONLY Loguru and stop bubbling up
    for logger_name in loggers_to_hijack:
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [InterceptHandler()] # Overwrite default printers
        std_logger.propagate = False               # Prevent double-printing