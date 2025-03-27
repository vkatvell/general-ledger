"""
File: logger.py
Author: Venkat Vellanki
Created: 2025-03-26
Last Modified: 2025-03-26
Description: Centralized logging setup for FastAPI services using dictConfig.
             Provides a reusable `setup_logging()` function for consistent,
             structured logging across the backend.
"""

import logging
import logging.config
from typing import Optional


def setup_logging(level: Optional[str] = "INFO") -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }

    logging.config.dictConfig(logging_config)
