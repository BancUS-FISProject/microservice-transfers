import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from ..utils.LoggerColorFormatter import ColorFormatter
from .config import settings

def setup_logging() -> None:
    """
    Configures the application logging with console and rotating file handlers.
    """
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    # Avoid adding handlers multiple times if this function is called repeatedly
    if logger.hasHandlers():
        logger.handlers.clear()

    # --- Console Handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_format = ColorFormatter(
        "%(levelname)s:     %(message)s"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # --- File Handler (Rotating) ---
    file_handler = TimedRotatingFileHandler(
        settings.LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s:     %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
