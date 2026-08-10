from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from .hash_manager import HashManager

class PinManager:
    def __init__(self, hash_manager: HashManager | None = None) -> None:
        self.hash_manager = hash_manager or HashManager()

    def hash_pin(self, pin: str) -> str:
        self._validate_pin(pin)
        return self.hash_manager.hash(pin)

    def verify_pin(self, pin: str, pin_hash: str) -> bool:
        if not pin or not pin_hash:
            return False

        return self.hash_manager.verify(pin_hash, pin,)

    @staticmethod
    def _validate_pin(pin: str) -> None:
        if not pin.isdigit():
            raise ValueError("PIN must contain digits only.")

        if len(pin) < 4 or len(pin) > 10:
            raise ValueError("PIN length must be between 4 and 10 digits.")

    @staticmethod
    def is_locked(locked_until: Optional[datetime]) -> bool:
        if locked_until is None:
            return False

        now = datetime.now(timezone.utc)

        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)

        return locked_until > now