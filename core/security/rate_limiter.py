from __future__ import annotations
from time import monotonic
from collections import defaultdict, deque
from threading import Lock

class RateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def is_allowed(self, key: str, limit: int, window_seconds: int,) -> bool:
        if not key:
            raise ValueError("Rate-limit key cannot be empty.")

        if limit < 1 or window_seconds < 1:
            raise ValueError("Limit and window must be positive.")

        now = monotonic()
        cutoff = now - window_seconds

        with self._lock:
            bucket = self._requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True

    def reset(self, key: str) -> None:
        with self._lock:
            self._requests.pop(key, None)