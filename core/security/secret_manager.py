from __future__ import annotations
from config.settings import Settings

class SecretManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get(self, name: str) -> str:
        if not name:
            raise ValueError("Secret name cannot be empty.")

        value = getattr(self.settings, name, None)

        if value is None:
            raise KeyError(f"Secret '{name}' was not configured.")

        if hasattr(value, "get_secret_value"):
            value = value.get_secret_value()

        if not value:
            raise ValueError(f"Secret '{name}' is empty.")

        return str(value)

    def require(self, name: str) -> str:
        return self.get(name)