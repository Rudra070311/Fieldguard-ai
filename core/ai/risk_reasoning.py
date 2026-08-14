from __future__ import annotations
from typing import Any, Mapping

class RiskReasoner:
    def __init__(self, flaw_adapter, risk_engine=None,):
        self.flaw_adapter = flaw_adapter
        self.risk_engine = risk_engine

    async def reason(self, *, risk_score: float, risk_level: str, risk_factors: Mapping[str, Any], event_type: str, context: Mapping[str, Any] | None = None,) -> dict[str, Any]:
        if not 0.0 <= risk_score <= 1.0:
            raise ValueError("risk_score must be between 0 and 1.")

        evidence = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": dict(risk_factors),
            "event_type": event_type,
        }

        if context:
            evidence["context"] = dict(context)

        explanation = await self.flaw_adapter.reason_about_risk(evidence)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "event_type": event_type,
            "factors": dict(risk_factors),
            "explanation": explanation,
        }

    async def explain_decision(self, decision: str, risk_score: float, risk_factors: Mapping[str, Any],) -> str:
        if not decision.strip():
            raise ValueError("Decision cannot be empty.")

        return await self.flaw_adapter.analyze(
            (
                "Explain the following authentication decision "
                "using only the supplied evidence."
            ),
            context={
                "decision": decision,
                "risk_score": risk_score,
                "risk_factors": dict(risk_factors),
            },
            temperature=0.0,
        )