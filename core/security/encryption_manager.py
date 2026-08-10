from __future__ import annotations
import base64
from cryptography.fernet import Fernet, InvalidToken
from config.settings import Settings

class EncryptionManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        raw_key = settings.encryption_key_value().encode("utf-8")

        try:
            decoded = base64.urlsafe_b64decode(raw_key)
            if len(decoded) != 32:
                raise ValueError
        except Exception as exc:
            raise ValueError("encryption_key must be a valid Fernet key.") from exc

        self._fernet = Fernet(raw_key)

    def encrypt(self, value: str) -> str:
        if not value:
            raise ValueError("Value cannot be empty.")

        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_value: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Invalid encrypted value.") from exc