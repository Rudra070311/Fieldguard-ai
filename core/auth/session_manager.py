from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID
import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import Settings
from database.models import Session as SessionModel
from database.repositories.session_repo import SessionRepository

class SessionManager:
    def __init__(self, session: AsyncSession, settings: Settings,):
        self.session = session
        self.settings = settings
        self.repository = SessionRepository(session)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(48)

    async def create_session(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        device_id: Optional[UUID] = None,
        authentication_method: Optional[str] = None,
        authentication_level: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:

        raw_token = self.generate_token()
        token_hash = self.hash_token(raw_token)
        now = datetime.now(timezone.utc)

        if expires_at is None:
            expires_at = now + timedelta(
                days=self.settings.security.refresh_token_days
            )

        session = await self.repository.create(
            user_id=user_id,
            organization_id=organization_id,
            device_id=device_id,
            session_token_hash=token_hash,
            authentication_method=authentication_method,
            authentication_level=authentication_level,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            last_activity_at=now,
            expires_at=expires_at,
            revoked=False,
        )
        await self.session.commit()

        return {
            "session_id": session.id,
            "session_token": raw_token,
            "expires_at": expires_at,
        }

    async def get_session(self, session_token: str,) -> Optional[SessionModel]:
        token_hash = self.hash_token(session_token)
        session = await self.repository.get_by_token_hash(token_hash)

        if session is None:
            return None

        now = datetime.now(timezone.utc)

        if session.revoked:
            return None
        if session.expires_at <= now:
            return None

        return session

    async def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        session = await self.get_session(session_token)

        if session is None:
            return None

        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "organization_id": session.organization_id,
            "device_id": session.device_id,
            "authentication_method": session.authentication_method,
            "authentication_level": session.authentication_level,
            "ip_address": session.ip_address,
            "created_at": session.created_at,
            "last_activity_at": session.last_activity_at,
            "expires_at": session.expires_at,
        }

    async def touch(self, session_id: UUID,) -> Optional[SessionModel]:
        session = await self.repository.get_by_id(session_id)

        if session is None or session.revoked:
            return None

        session.last_activity_at = datetime.now(timezone.utc)
        await self.session.flush()

        return session

    async def revoke_session(self, session_id: UUID, reason: str = "manual_revocation",) -> bool:
        session = await self.repository.get_by_id(session_id)

        if session is None:
            return False
        if session.revoked:
            return True
        
        session.revoked = True
        session.revoked_at = datetime.now(timezone.utc)
        session.revocation_reason = reason
        await self.session.flush()
        await self.session.commit()

        return True

    async def revoke_by_token(self, session_token: str, reason: str = "token_revocation",) -> bool:
        session = await self.get_session(session_token)
        if session is None:
            return False
        return await self.revoke_session(
            session.id,
            reason=reason,
        )

    async def revoke_all_for_user(self, user_id: UUID, reason: str = "user_sessions_revoked",) -> None:
        sessions = await self.repository.get_active_for_user(user_id)
        now = datetime.now(timezone.utc)
        for session in sessions:
            session.revoked = True
            session.revoked_at = now
            session.revocation_reason = reason
        await self.session.flush()
        await self.session.commit()

    async def cleanup_expired(self) -> None:
        await self.repository.delete_expired()