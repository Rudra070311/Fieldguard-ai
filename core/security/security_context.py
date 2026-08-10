from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass(frozen=True)
class SecurityContext:
    user_id: UUID
    session_id: Optional[UUID] = None
    device_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    authentication_method: Optional[str] = None
    authentication_level: Optional[str] = None
    risk_score: float = 0.0
    trusted_device: bool = False
    verified_email: bool = False
    verified_otp: bool = False
    biometric_verified: bool = False

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    @property
    def is_high_risk(self) -> bool:
        return self.risk_score >= 0.75

    @property
    def is_low_risk(self) -> bool:
        return self.risk_score < 0.30