from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.user_repo import UserRepository
from database.repositories.session_repo import SessionRepository
from database.repositories.device_repo import DeviceRepository
from core.security.risk_engine import RiskEngine
from core.auth.jwt_handler import JWTHandler

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    pass

class InvalidCredentialsError(AuthenticationError):
    pass

class AccountLockedError(AuthenticationError):
    pass

class AuthenticationDeniedError(AuthenticationError):
    pass

class AuthService:
    def __init__(self, session: AsyncSession, jwt_handler: JWTHandler, risk_engine: RiskEngine,) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.sessions = SessionRepository(session)
        self.devices = DeviceRepository(session)
        self.jwt_handler = jwt_handler
        self.risk_engine = risk_engine

    async def authenticate(
        self,
        user_id: UUID,
        authentication_method: str,
        authentication_level: str,
        device_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        risk_factors: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("Authentication failed.")

        risk_result = self.risk_engine.evaluate(
            user_id=user_id,
            device_id=device_id,
            organization_id=organization_id,
            factors=risk_factors or {},
        )

        if risk_result["action"] in {"block", "escalate_to_human",}:
            logger.warning(
                "Authentication denied: user=%s risk=%s",
                user_id, risk_result["risk_score"],
            )
            raise AuthenticationDeniedError("Authentication denied by security policy.")

        session = await self.sessions.create(
            user_id=user_id,
            organization_id=organization_id,
            device_id=device_id,
            authentication_method=authentication_method,
            authentication_level=authentication_level,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        access_token = self.jwt_handler.create_access_token(
            user_id=user_id,
            session_id=session.id,
            organization_id=organization_id,
        )

        return {
            "authenticated": True,
            "access_token": access_token,
            "session_id": session.id,
            "user_id": user_id,
            "organization_id": organization_id,
            "risk": risk_result,
        }

    async def validate_access_token(self, token: str,) -> Dict[str, Any]:
        payload = self.jwt_handler.decode_access_token(token)
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["sid"])
        session = await self.sessions.get_by_id(session_id)

        if session is None:
            raise AuthenticationDeniedError("Session does not exist.")

        if session.revoked:
            raise AuthenticationDeniedError("Session has been revoked.")

        return {
            "valid": True,
            "user_id": user_id,
            "session_id": session_id,
            "organization_id": (
                UUID(payload["org"])
                if payload.get("org")
                else None),
            "claims": payload,
        }

    async def logout(self, session_id: UUID, reason: str = "user_logout",) -> bool:
        session = await self.sessions.get_by_id(session_id)
        if session is None:
            return False
        await self.sessions.revoke(
            session_id=session_id,
            reason=reason,
        )

        return True

    async def logout_all(self, user_id: UUID, reason: str = "global_logout",) -> None:
        await self.sessions.revoke_all_for_user(
            user_id=user_id,
            reason=reason,
        )

__all__ = [
    "AuthenticationError",
    "InvalidCredentialsError",
    "AccountLockedError",
    "AuthenticationDeniedError",
    "AuthService",
]