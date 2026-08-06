from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional
import logging


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskSignals:
    face_match_score: float
    liveness_score: float
    device_trust_score: float
    location_anomaly: bool
    time_anomaly: bool
    vpn_detected: bool
    failed_attempts_last_hour: int
    known_device: bool
    known_face: bool
    embedding_version: str = "v1.0"
@dataclass
class RiskResult:
    risk_score: float
    risk_level: RiskLevel
    confidence: float
    contributions: Dict[str, float]
    signals: Dict[str, Any]
    metadata: Dict[str, Any]
class RiskEngine:
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
        logger=None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.weights = weights or {
            "face_match_score":0.30,
            "liveness_score":0.25,
            "device_trust_score":0.15,
            "location_anomaly":0.10,
            "vpn_detected":0.10,
            "time_anomaly":0.05,
            "failed_attempts_last_hour":0.05,
        }

        self.thresholds = thresholds or {
            "low":0.30,
            "medium":0.60,
            "high":0.80,
            "critical":0.95,
        }

    def evaluate(
        self,
        signals: RiskSignals
    ) -> RiskResult:
        risk = {}
        risk["face_match_score"] = 1-signals.face_match_score
        risk["liveness_score"] = 1-signals.liveness_score
        risk["device_trust_score"] = 1-signals.device_trust_score
        risk["location_anomaly"] = float(signals.location_anomaly)
        risk["vpn_detected"] = float(signals.vpn_detected)
        risk["time_anomaly"] = float(signals.time_anomaly)
        risk["failed_attempts_last_hour"] = min(
            signals.failed_attempts_last_hour/5,
            1.0
        )
        total = 0
        contributions = {}

        for key, weight in self.weights.items():
            value = risk.get(key,0)
            contributions[key]=round(value*weight,4)
            total += value*weight
        total=max(0,min(1,total))

        if total>=self.thresholds["critical"]:
            level=RiskLevel.CRITICAL

        elif total>=self.thresholds["high"]:
            level=RiskLevel.HIGH

        elif total>=self.thresholds["medium"]:
            level=RiskLevel.MEDIUM

        else:
            level=RiskLevel.LOW

        confidence=1-(0.05*(signals.failed_attempts_last_hour>0))

        return RiskResult(
            risk_score=round(total,4),
            risk_level=level,
            confidence=round(confidence,4),
            contributions=contributions,
            signals=asdict(signals),
            metadata={
                "engine":"iDeez Risk Engine",
                "version":"1.0",
            }
        )