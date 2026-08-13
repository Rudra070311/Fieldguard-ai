from __future__ import annotations
import re

class PinVerifier:
    def __init__(self, settings, pin_hasher,) -> None:
        self.settings = settings
        self.pin_hasher = pin_hasher

    def validate_pin_format(self, pin: str) -> None:
        if not isinstance(pin, str):
            raise ValueError("PIN must be a string.")

        if not pin:
            raise ValueError("PIN cannot be empty.")

        expected_length = self.settings.auth.pin_length

        if len(pin) != expected_length:
            raise ValueError(f"PIN must contain exactly {expected_length} digits.")

        if not re.fullmatch(r"\d+", pin):
            raise ValueError("PIN must contain only digits.")

        if len(set(pin)) == 1:
            raise ValueError("PIN cannot contain the same digit repeatedly.")

        if self._is_sequential(pin):
            raise ValueError("Sequential PINs are not allowed.")

    @staticmethod
    def _is_sequential(pin: str) -> bool:
        digits = [int(char) for char in pin]
        ascending = all(digits[index] + 1 == digits[index + 1] for index in range(len(digits) - 1))
        descending = all(digits[index] - 1 == digits[index + 1] for index in range(len(digits) - 1))

        return ascending or descending

    def verify(self, pin: str, stored_hash: str,) -> bool:
        if not pin or not stored_hash:
            return False

        try:
            return self.pin_hasher.verify(pin, stored_hash,)
        except Exception:
            return False