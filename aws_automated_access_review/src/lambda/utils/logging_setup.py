import logging
import json
import os
from typing import Optional


class _JsonFormatter(logging.Formatter):
    """Simple JSON log formatter suitable for CloudWatch Insights."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


def configure_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger configured for JSON output.

    The root logger is configured the first time this is called; subsequent
    calls simply return ``logging.getLogger(name)``.
    """

    logger = logging.getLogger(name)

    # Configure root logger only once
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        handler = logging.StreamHandler()
        handler.setFormatter(_JsonFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(level)

    return logger
