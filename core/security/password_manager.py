from __future__ import annotations
import secrets
from .hash_manager import HashManager

class PasswordManager:
    def __init__(self, hash_manager: HashManager | None = None) -> None:
        self.hash_manager = hash_manager or HashManager()

    @staticmethod
    def generate(length: int = 32) -> str:
        if length < 8:
            raise ValueError("Generated password length must be at least 8.")

        return secrets.token_urlsafe(length)

    def hash(self, password: str) -> str:
        if not password:
            raise ValueError("Password cannot be empty.")

        return self.hash_manager.hash(password)

    def verify(self, password: str, expected_hash: str) -> bool:
        if not password or not expected_hash:
            return False

        return self.hash_manager.verify(expected_hash, password,)

    def needs_rehash(self, password_hash: str) -> bool:
        return self.hash_manager.needs_rehash(password_hash)