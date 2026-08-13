from __future__ import annotations
from typing import Final
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

class PinHasher:
    algorithm: Final[str] = "argon2id"
    version: Final[str] = "1"

    def __init__(self, settings,) -> None:
        self.settings = settings
        self._hasher = PasswordHasher(
            time_cost=3,
            memory_cost=64 * 1024,
            parallelism=2,
            hash_len=32,
            salt_len=16,
        )

    def hash(self, pin: str) -> str:
        self._validate_input(pin)
        return self._hasher.hash(pin)

    def verify(self, pin: str, stored_hash: str,) -> bool:
        if not pin or not stored_hash:
            return False

        try:
            return self._hasher.verify(stored_hash, pin,)
        except (
            VerifyMismatchError,
            VerificationError,
            InvalidHashError,
        ):
            return False

    def needs_rehash(self, stored_hash: str,) -> bool:
        if not stored_hash:
            return False

        try:
            return self._hasher.check_needs_rehash(stored_hash)
        except (
            InvalidHashError,
            VerificationError,
        ):
            return False

    @staticmethod
    def _validate_input(pin: str) -> None:
        if not isinstance(pin, str):
            raise TypeError("PIN must be a string.")
        if not pin:
            raise ValueError("PIN cannot be empty.")