from __future__ import annotations
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Mapping, Optional
from config.settings import Settings

@dataclass(frozen=True)
class DeviceFingerprint:
    value: str
    version: str

class FingerprintManager:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _normalize(value: Optional[str]) -> str:
        if value is None:
            return ""

        return " ".join(value.strip().lower().split())

    def canonicalize(self, signals: Mapping[str, Optional[str]],) -> str:
        normalized = {
            str(key): self._normalize(value)
            for key, value in signals.items()
            if value is not None
        }

        return json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def generate(self, signals: Mapping[str, Optional[str]], version: str = "v1",) -> DeviceFingerprint:
        canonical = self.canonicalize(signals)
        secret = self.settings.jwt_secret_value().encode("utf-8")

        digest = hmac.new(
            secret,
            f"{version}:{canonical}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return DeviceFingerprint(
            value=digest,
            version=version,
        )

    def verify(self, fingerprint: str, signals: Mapping[str, Optional[str]], version: str = "v1",) -> bool:
        expected = self.generate(
            signals=signals,
            version=version,
        )

        return hmac.compare_digest(fingerprint, expected.value,)

__all__ = [
    "DeviceFingerprint",
    "FingerprintManager",
]