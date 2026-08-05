from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
from enum import Enum
import json

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Action(Enum):
    ALLOW = "allow"
    VERIFY_DEVICE = "verify_trusted_device"
    OTP_PIN = "require_OTP_and_PIN"
    BLOCK = "block"
    ESCALATE = "escalate_to_human"

@dataclass
class FacialFactors:
    face_match_score: float       
    liveness_score: float          
    device_trust_score: float        
    location_anomaly: bool           
    time_anomaly: bool               
    failed_attempts_last_hour: int
    is_known_face: bool      
    embedding_version: str 

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FacialLoginExplainer:
    def __init__(
        self,
        policy: str = "normal",
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.policy = policy
        self.logger = logger or logging.getLogger(__name__)
        self.default_weights = {
            "face_match_score": 0.35,
            "liveness_score": 0.25,
            "device_trust_score": 0.15,
            "location_anomaly": 0.10,
            "time_anomaly": 0.05,
            "failed_attempts_last_hour": 0.10,
        }
        self.weights = weights or self.default_weights

        base_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95,
        }
        if policy == "strict":
            base_thresholds = {k: v * 0.85 for k, v in base_thresholds.items()}
        elif policy == "lenient":
            base_thresholds = {k: v * 1.15 for k, v in base_thresholds.items()}
        self.thresholds = thresholds or base_thresholds
        self.action_map = {
            RiskLevel.LOW: Action.ALLOW,
            RiskLevel.MEDIUM: Action.VERIFY_DEVICE,
            RiskLevel.HIGH: Action.OTP_PIN,
            RiskLevel.CRITICAL: Action.BLOCK,
        }

    def _compute_risk_score(self, factors: FacialFactors) -> float:
        risk_contrib = {}
        risk_contrib["face_match_score"] = 1.0 - factors.face_match_score
        risk_contrib["liveness_score"] = 1.0 - factors.liveness_score
        risk_contrib["device_trust_score"] = 1.0 - factors.device_trust_score
        risk_contrib["location_anomaly"] = 1.0 if factors.location_anomaly else 0.0
        risk_contrib["time_anomaly"] = 1.0 if factors.time_anomaly else 0.0
        risk_contrib["failed_attempts_last_hour"] = min(factors.failed_attempts_last_hour / 5.0, 1.0)
        total_risk = 0.0
        for key, weight in self.weights.items():
            total_risk += risk_contrib.get(key, 0.0) * weight

        return max(0.0, min(1.0, total_risk))

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        if risk_score >= self.thresholds["critical"]:
            return RiskLevel.CRITICAL
        elif risk_score >= self.thresholds["high"]:
            return RiskLevel.HIGH
        elif risk_score >= self.thresholds["medium"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_explanation(
        self,
        risk_score: float,
        risk_level: RiskLevel,
        factors: FacialFactors,
        contributions: Dict[str, float],
    ) -> Dict[str, Any]:
        messages = {
            RiskLevel.LOW: "Low-risk facial login – all signals are normal.",
            RiskLevel.MEDIUM: "Medium-risk: some signals deviate from usual patterns.",
            RiskLevel.HIGH: "High-risk: multiple strong anomalies detected.",
            RiskLevel.CRITICAL: "CRITICAL risk – immediate action required.",
        }
        
        reasons = []
        if factors.face_match_score < 0.6:
            reasons.append(f"Face match score is low ({factors.face_match_score:.2f}).")
        if factors.liveness_score < 0.7:
            reasons.append(f"Liveness confidence is low ({factors.liveness_score:.2f}) – possible spoof.")
        if factors.device_trust_score < 0.5:
            reasons.append("Untrusted or unrecognized device.")
        if factors.location_anomaly:
            reasons.append("Login location is unusual for this user.")
        if factors.time_anomaly:
            reasons.append("Login time is outside typical hours.")
        if factors.failed_attempts_last_hour > 2:
            reasons.append(f"{factors.failed_attempts_last_hour} failed attempts in the last hour.")

        action = self.action_map[risk_level]
        if factors.face_match_score < 0.3 and factors.liveness_score > 0.9:
            action = Action.OTP_PIN 

        return {
            "risk_level": risk_level.value,
            "risk_score": round(risk_score, 4),
            "message": messages[risk_level],
            "reasons": reasons,
            "action": action.value,
            "action_description": self._action_description(action),
            "factor_contributions": contributions,
            "policy": self.policy,
            "embedding_version": factors.embedding_version,
        }

    def _action_description(self, action: Action) -> str:
        desc = {
            Action.ALLOW: "Proceed with login.",
            Action.VERIFY_DEVICE: "Verify device via push notification or trusted certificate.",
            Action.OTP_PIN: "Require one‑time password (OTP) and PIN entry.",
            Action.BLOCK: "Block the login attempt and notify security.",
            Action.ESCALATE: "Escalate to a human security analyst.",
        }
        return desc.get(action, "No action specified.")

    def explain(self, risk: float = None, factors: Dict[str, Any] = None) -> Dict[str, Any]:
        if factors is None:
            factors = {}
        f = FacialFactors(
            face_match_score=factors.get("face_match_score", 0.0),
            liveness_score=factors.get("liveness_score", 0.0),
            device_trust_score=factors.get("device_trust_score", 0.5),
            location_anomaly=factors.get("location_anomaly", False),
            time_anomaly=factors.get("time_anomaly", False),
            failed_attempts_last_hour=factors.get("failed_attempts_last_hour", 0),
            is_known_face=factors.get("is_known_face", True),
            embedding_version=factors.get("embedding_version", "v1.0"),
        )

        if risk is not None:
            risk_score = max(0.0, min(1.0, risk))
        else:
            risk_score = self._compute_risk_score(f)

        risk_level = self._determine_risk_level(risk_score)
        contributions = {}

        risk_contrib = {
            "face_match_score": 1.0 - f.face_match_score,
            "liveness_score": 1.0 - f.liveness_score,
            "device_trust_score": 1.0 - f.device_trust_score,
            "location_anomaly": 1.0 if f.location_anomaly else 0.0,
            "time_anomaly": 1.0 if f.time_anomaly else 0.0,
            "failed_attempts_last_hour": min(f.failed_attempts_last_hour / 5.0, 1.0),
        }
        for key, weight in self.weights.items():
            contributions[key] = round(risk_contrib.get(key, 0.0) * weight, 4)
            
        result = self._generate_explanation(
            risk_score, risk_level, f, contributions
        )
        self.logger.info(
            f"Facial login decision: level={risk_level.value}, "
            f"score={risk_score:.4f}, action={result['action']}"
        )

        return result

if __name__ == "__main__":
    class DummyFaceModel:
        def verify(self, face_embedding, template):
            return 0.92

    model = DummyFaceModel()
    explainer = FacialLoginExplainer(model, policy="strict")

    factors = {
        "face_match_score": 0.45,
        "liveness_score": 0.98,
        "device_trust_score": 0.3,
        "location_anomaly": True,
        "time_anomaly": False,
        "failed_attempts_last_hour": 3,
        "is_known_face": True,
        "embedding_version": "v2.3",
    }

    decision = explainer.explain(factors=factors)
    print(json.dumps(decision, indent=2))