from __future__ import annotations
import hashlib
import hmac
import secrets

class CSRFManager:
    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("CSRF secret cannot be empty.")

        self._secret = secret.encode("utf-8")

    def generate(self) -> str:
        nonce = secrets.token_urlsafe(32)
        signature = hmac.new(self._secret, nonce.encode("utf-8"), hashlib.sha256,).hexdigest()

        return f"{nonce}.{signature}"

    def verify(self, token: str) -> bool:
        if not token or "." not in token:
            return False

        nonce, signature = token.rsplit(".", 1)
        expected = hmac.new(self._secret, nonce.encode("utf-8"), hashlib.sha256,).hexdigest()

        return hmac.compare_digest(signature, expected)