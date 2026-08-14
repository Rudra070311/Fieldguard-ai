from __future__ import annotations
import base64
import hashlib
import secrets

class SecretManager:
    @staticmethod
    def generate_token(length: int = 64) -> str:
        if length < 32:
            raise ValueError("Token length must be at least 32 bytes.")

        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_secret(length: int = 64) -> str:
        if length < 32:
            raise ValueError("Secret length must be at least 32 bytes.")

        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_hex_secret(length: int = 64) -> str:
        if length < 32:
            raise ValueError("Secret length must be at least 32 bytes.")

        return secrets.token_hex(length)

    @staticmethod
    def generate_encryption_key() -> str:
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")

    @staticmethod
    def hash_secret(value: str) -> str:
        if not value:
            raise ValueError("Secret cannot be empty.")

        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def compare_secret(value: str, expected_hash: str) -> bool:
        if not value or not expected_hash:
            return False

        actual_hash = SecretManager.hash_secret(value)

        return secrets.compare_digest(
            actual_hash,
            expected_hash,
        )

    @staticmethod
    def validate_secret(secret: str, minimum_length: int = 32) -> None:
        if not secret:
            raise ValueError("Secret cannot be empty.")

        if len(secret) < minimum_length:
            raise ValueError(f"Secret must contain at least {minimum_length} characters.")