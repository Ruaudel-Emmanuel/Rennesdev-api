import logging
import logging.config
from pathlib import Path
from typing import Union


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = LOG_DIR / "app.log"


def build_logging_config(
    log_level: str = DEFAULT_LOG_LEVEL,
    log_file: Union[str, Path] = DEFAULT_LOG_FILE,
) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": str(log_file),
                "maxBytes": 2_000_000,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": log_level,
        },
    }


def setup_logging(log_level: str = DEFAULT_LOG_LEVEL) -> None:
    logging.config.dictConfig(build_logging_config(log_level=log_level))


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)