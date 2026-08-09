from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TrustScore:
    score: float
    level: str
    factors: dict[str, float]

class DeviceTrustManager:
    def __init__(self, trusted_threshold: float = 0.85,):
        if not 0.0 <= trusted_threshold <= 1.0:
            raise ValueError("trusted_threshold must be between 0 and 1")

        self.trusted_threshold = trusted_threshold

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def calculate(self, *, known_device: bool, revoked: bool, fingerprint_match: bool, successful_authentications: int = 0, recent_anomaly_score: float = 0.0,) -> TrustScore:
        if revoked:
            return TrustScore(
                score=0.0,
                level="revoked",
                factors={
                    "known_device": 0.0,
                    "fingerprint_match": 0.0,
                    "history": 0.0,
                    "anomaly": 0.0,
                },
            )

        known_factor = 1.0 if known_device else 0.0
        fingerprint_factor = 1.0 if fingerprint_match else 0.0
        history_factor = self._clamp(successful_authentications / 10.0)
        anomaly_factor = 1.0 - self._clamp(recent_anomaly_score)
        score = (known_factor * 0.35 + fingerprint_factor * 0.35 + history_factor * 0.15 + anomaly_factor * 0.15)
        score = self._clamp(score)

        if score >= self.trusted_threshold:
            level = "trusted"
        elif score >= 0.60:
            level = "familiar"
        elif score >= 0.30:
            level = "unknown"
        else:
            level = "untrusted"

        return TrustScore(
            score=score,
            level=level,
            factors={
                "known_device": known_factor,
                "fingerprint_match": fingerprint_factor,
                "history": history_factor,
                "anomaly": anomaly_factor,
            },
        )

__all__ = [
    "TrustScore",
    "DeviceTrustManager",
]