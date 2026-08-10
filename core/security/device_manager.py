from __future__ import annotations
import hashlib
import hmac
from typing import Mapping

class DeviceFingerprintManager:
    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("Fingerprint secret cannot be empty.")

        self._secret = secret.encode("utf-8")

    def generate(self, attributes: Mapping[str, object]) -> str:
        normalized = "|".join(f"{key}={attributes[key]}" for key in sorted(attributes) if attributes[key] is not None)

        return hmac.new(self._secret, normalized.encode("utf-8"), hashlib.sha256,).hexdigest()

    def verify(self, fingerprint: str, attributes: Mapping[str, object],) -> bool:
        expected = self.generate(attributes)

        return hmac.compare_digest(fingerprint, expected,)