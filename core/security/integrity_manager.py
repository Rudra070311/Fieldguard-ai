from __future__ import annotations
import hashlib
import hmac

class IntegrityManager:
    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("Integrity secret cannot be empty.")

        self._secret = secret.encode("utf-8")

    def sign(self, payload: str) -> str:
        return hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256,).hexdigest()

    def verify(self, payload: str, signature: str) -> bool:
        expected = self.sign(payload)

        return hmac.compare_digest(expected, signature,)

    @staticmethod
    def sha256(payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()