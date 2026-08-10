from __future__ import annotations
from typing import Any

class AnomalyDetector:
    def __init__(self, threshold: float = 0.75) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0 and 1.")

        self.threshold = threshold

    def calculate_score(
        self,
        *,
        location_anomaly: float = 0.0,
        time_anomaly: float = 0.0,
        device_anomaly: float = 0.0,
        failed_attempts: float = 0.0,
    ) -> float:
        factors = [
            location_anomaly,
            time_anomaly,
            device_anomaly,
            failed_attempts,
        ]

        normalized = [
            max(0.0, min(1.0, factor))
            for factor in factors
        ]

        return sum(normalized) / len(normalized)

    def is_anomalous(self, score: float) -> bool:
        return score >= self.threshold

    def analyze(self, signals: dict[str, Any]) -> dict[str, Any]:
        score = self.calculate_score(
            location_anomaly=float(signals.get("location_anomaly", 0.0)),
            time_anomaly=float(signals.get("time_anomaly", 0.0)),
            device_anomaly=float(signals.get("device_anomaly", 0.0)),
            failed_attempts=float(signals.get("failed_attempts", 0.0)),
        )

        return {
            "score": score,
            "anomalous": self.is_anomalous(score),
        }