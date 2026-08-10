from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .security_context import SecurityContext

class SecurityDecision(str, Enum):
    ALLOW = "allow"
    STEP_UP = "step_up"
    DENY = "deny"

@dataclass(frozen=True)
class PolicyResult:
    decision: SecurityDecision
    reason: str

class SecurityPolicy:
    def evaluate(self, context: SecurityContext, action: str,) -> PolicyResult:
        if context.is_high_risk:
            return PolicyResult(
                SecurityDecision.STEP_UP,
                "High risk authentication context.",
            )

        if action in {
            "change_password",
            "change_pin",
            "disable_mfa",
            "revoke_all_devices",
        } and not context.verified_otp:
            return PolicyResult(SecurityDecision.STEP_UP, "Additional verification required.",)

        return PolicyResult(SecurityDecision.ALLOW, "Security policy satisfied.",)