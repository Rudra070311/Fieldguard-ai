from __future__ import annotations
import json
import logging as std_logging
import sys
from typing import Any, Optional
from .settings import Settings

class JsonFormatter(std_logging.Formatter):
    def format(self, record: std_logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            payload["user_id"] = record.user_id

        return json.dumps(payload, default=str)

def configure_logging(settings: Optional[Settings] = None) -> None:
    settings = settings or Settings()
    level_name = settings.logging.level.upper()
    level = getattr(std_logging, level_name, None)

    if not isinstance(level, int):
        raise ValueError(f"Invalid logging level: {settings.logging.level}")

    handler = std_logging.StreamHandler(sys.stdout)

    if settings.logging.json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            std_logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )

    root_logger = std_logging.getLogger()
    root_logger.setLevel(level)

    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)

    root_logger.addHandler(handler)

    for logger_name in (
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "uvicorn.access",
    ):
        logger = std_logging.getLogger(logger_name)

        if settings.app.environment == "production":
            logger.setLevel(std_logging.WARNING)
        else:
            logger.setLevel(level)

def get_logger(name: str) -> std_logging.Logger:
    return std_logging.getLogger(name)