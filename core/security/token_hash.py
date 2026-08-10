from __future__ import annotations
import hashlib
import hmac
import secrets

class TokenHashManager:
    @staticmethod
    def generate(length: int = 64) -> str:
        if length < 32:
            raise ValueError("Token length must be at least 32.")

        return secrets.token_urlsafe(length)

    @staticmethod
    def hash(token: str) -> str:
        if not token:
            raise ValueError("Token cannot be empty.")

        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def verify(token: str, expected_hash: str) -> bool:
        if not token or not expected_hash:
            return False

        actual_hash = TokenHashManager.hash(token)

        return hmac.compare_digest(actual_hash, expected_hash,)