from __future__ import annotations
from typing import Final
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

class HashManager:
    ALGORITHM: Final[str] = "argon2id"

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, value: str) -> str:
        if not value:
            raise ValueError("Value cannot be empty.")
        return self._hasher.hash(value)

    def verify(self, hashed_value: str, value: str) -> bool:
        try:
            return self._hasher.verify(hashed_value, value)
        except (InvalidHashError, VerificationError):
            return False

    def needs_rehash(self, hashed_value: str) -> bool:
        try:
            return self._hasher.check_needs_rehash(hashed_value)
        except InvalidHashError:
            return True