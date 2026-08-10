from __future__ import annotations
import logging
from typing import Any, Mapping
from uuid import UUID

class SecurityAuditLogger:
    def __init__(self, logger: logging.Logger | None = None,) -> None:
        self.logger = logger or logging.getLogger("ideez.security.audit")

    def log(self, user_id: UUID | None, event_type: str, result: str, metadata: Mapping[str, Any] | None = None,) -> None:
        self.logger.info(
            "security_event",
            extra={
                "user_id": str(user_id) if user_id else None,
                "event_type": event_type,
                "result": result,
                "metadata": dict(metadata or {}),
            },
        )