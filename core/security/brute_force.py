from __future__ import annotations
from datetime import datetime, timedelta, timezone
from collections import defaultdict

class BruteForceManager:
    def __init__(self, max_attempts: int = 5, lock_minutes: int = 30,) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive.")

        self.max_attempts = max_attempts
        self.lock_minutes = lock_minutes
        self._failures: dict[str, int] = defaultdict(int)
        self._locked_until: dict[str, datetime] = {}

    def record_failure(self, key: str) -> bool:
        if self.is_locked(key):
            return True

        self._failures[key] += 1

        if self._failures[key] >= self.max_attempts:
            self._locked_until[key] = (datetime.now(timezone.utc) + timedelta(minutes=self.lock_minutes))
            return True

        return False

    def record_success(self, key: str) -> None:
        self._failures.pop(key, None)
        self._locked_until.pop(key, None)

    def is_locked(self, key: str) -> bool:
        locked_until = self._locked_until.get(key)

        if locked_until is None:
            return False

        if locked_until <= datetime.now(timezone.utc):
            self._locked_until.pop(key, None)
            self._failures.pop(key, None)
            return False

        return True

    def failures(self, key: str) -> int:
        return self._failures.get(key, 0)