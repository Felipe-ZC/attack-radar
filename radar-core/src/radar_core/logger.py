import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from .constants import DEFAULT_LOG_LEVEL

LOG_LEVEL_MAP: dict[str, int] = {
    "DEBUG": logging.DEBUG,  # 10
    "INFO": logging.INFO,  # 20
    "WARNING": logging.WARNING,  # 30
    "ERROR": logging.ERROR,  # 40
    "CRITICAL": logging.CRITICAL,  # 50
}


def get_log_level_from_env() -> int:
    """Get log level from environment variable or use default"""
    log_level_str: str = os.getenv("LOG_LEVEL", "INFO").upper()
    return LOG_LEVEL_MAP.get(log_level_str, logging.INFO)


def setup_logger(
    name: str = "attack-radar", log_level_str: str = DEFAULT_LOG_LEVEL
) -> logging.Logger:
    print(f"log_level_str is {log_level_str}")
    """Setup app wide logging utiltity"""
    logger: logging.Logger = logging.getLogger(name)

    # If the logger has not been setup yet...
    if not logger.handlers:
        print(log_level_str)
        log_level = LOG_LEVEL_MAP.get(log_level_str)
        print(f"log_level is: {log_level}")
        logger.setLevel(log_level)

        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # For logging to stdout
        console_handler: logging.StreamHandler = logging.StreamHandler(
            sys.stdout
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # For logging to a file
        log_dir = os.getenv("LOG_DIR", "logs")
        log_file_path = os.path.join(log_dir, f"{name}.log")

        # Create the log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler: logging.RotatingFileHandler = RotatingFileHandler(
            filename=log_file_path, maxBytes=1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
