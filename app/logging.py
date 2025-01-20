# Code taken (with modifications) from: https://docs.python.org/3/howto/logging-cookbook.html#custom-handling-of-levels
import logging
import logging.config
import os

def filter_maker(level:str):
    level = getattr(logging, level)

    def filter(record):
        return record.levelno <= level

    return filter

config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    },
    "filters": {
        "warning_and_lower": {
            "()": filter_maker,
            "level": "WARNING"
        }
    },
    "handlers": {
        "app_log": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "logs/app.log"
        },
        "warning_log": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "default",
            "filename": "logs/warning.log",
            "filters": ["warning_and_lower"]
        },
        "debug_log": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "logs/debug.log"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["app_log", "warning_log", "debug_log"]
    }
}

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured.")
