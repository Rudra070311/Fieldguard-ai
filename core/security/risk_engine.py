from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from uuid import UUID

@dataclass(frozen=True)
class RiskResult:
    score: float
    level: str
    action: str
    factors: dict[str, float]
    explanation: dict[str, Any]

class RiskEngine:
    DEFAULT_WEIGHTS = {
        "face_match_score": 0.20,
        "liveness_score": 0.15,
        "device_trust_score": 0.15,
        "location_anomaly": 0.15,
        "time_anomaly": 0.10,
        "failed_attempts": 0.15,
        "known_device": 0.05,
        "known_face": 0.05,
    }

    def __init__(self, settings: Optional[Any] = None, weights: Optional[Mapping[str, float]] = None,) -> None:
        self.settings = settings
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)
        self._validate_weights()

    def _validate_weights(self) -> None:
        if not self.weights:
            raise ValueError("Risk weights cannot be empty.")

        if any(weight < 0 for weight in self.weights.values()):
            raise ValueError("Risk weights cannot be negative.")

        total = sum(self.weights.values())

        if total <= 0:
            raise ValueError("Risk weight total must be positive.")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _normalize_signal(self, name: str, value: Any,) -> float:
        if isinstance(value, bool):
            return 0.0 if value else 1.0

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = 0.0

        if name in {
            "face_match_score",
            "liveness_score",
            "device_trust_score",
        }:
            return 1.0 - self._clamp(numeric)

        return self._clamp(numeric)

    def calculate_score(self, signals: Mapping[str, Any],) -> float:
        total_weight = sum(self.weights.values())

        if total_weight <= 0:
            return 0.0

        weighted_score = 0.0

        for name, weight in self.weights.items():
            value = signals.get(name, 0.0)
            normalized = self._normalize_signal(name, value,)
            weighted_score += normalized * weight

        return self._clamp(weighted_score / total_weight)

    @staticmethod
    def classify(score: float) -> str:
        score = max(0.0, min(1.0, score))

        if score < 0.30:
            return "low"
        if score < 0.60:
            return "medium"
        if score < 0.80:
            return "high"
        return "critical"

    @staticmethod
    def recommended_action(level: str) -> str:
        actions = {
            "low": "allow",
            "medium": "allow_with_monitoring",
            "high": "step_up_verification",
            "critical": "deny",
        }

        return actions.get(level, "deny",)

    def evaluate(self, signals: Mapping[str, Any],) -> RiskResult:
        score = self.calculate_score(signals)
        level = self.classify(score)
        action = self.recommended_action(level)
        factors = {
            name: self._normalize_signal(name, signals.get(name, 0.0),)
            for name in self.weights
        }

        explanation = {
            "risk_score": score,
            "risk_level": level,
            "action": action,
            "active_factors": [name for name, value in factors.items() if value > 0],
        }

        return RiskResult(
            score=score,
            level=level,
            action=action,
            factors=factors,
            explanation=explanation,
        )

    def is_high_risk(self, signals: Mapping[str, Any],) -> bool:
        result = self.evaluate(signals)

        return result.level in {"high", "critical",}

    def is_critical(self, signals: Mapping[str, Any],) -> bool:
        result = self.evaluate(signals)

        return result.level == "critical"

    def update_device_risk_score(self, revoked: bool = False,) -> RiskResult:
        signals = {
            "device_trust_score": 0.0
            if revoked
            else 1.0,
            "known_device": False
            if revoked
            else True,
        }

        return self.evaluate(signals)