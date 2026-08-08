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

class RefreshTokenManager:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.repository = SessionRepository(session)

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(64)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def create(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        device_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        raw_token = self.generate_token()
        token_hash = self.hash_token(raw_token)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=self.settings.security.refresh_token_days)
        session = await self.repository.create(
            user_id=user_id,
            organization_id=organization_id,
            device_id=device_id,
            session_token_hash=token_hash,
            authentication_method="refresh_token",
            authentication_level="refresh",
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
            "refresh_token": raw_token,
            "expires_at": expires_at,
        }

    async def validate(
        self,
        refresh_token: str,
    ) -> Optional[SessionModel]:
        token_hash = self.hash_token(refresh_token)
        session = await self.repository.get_by_token_hash(token_hash)

        if session is None:
            return None

        now = datetime.now(timezone.utc)

        if session.revoked:
            return None
        if session.expires_at <= now:
            return None
        if session.authentication_method != "refresh_token":
            return None

        return session

    async def rotate(self, refresh_token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None,) -> Optional[Dict[str, Any]]:
        old_session = await self.validate(refresh_token)

        if old_session is None:
            return None

        now = datetime.now(timezone.utc)
        old_session.revoked = True
        old_session.revoked_at = now
        old_session.revocation_reason = "refresh_token_rotated"
        new_token = self.generate_token()
        new_token_hash = self.hash_token(new_token)
        new_expires_at = now + timedelta(days=self.settings.security.refresh_token_days)

        new_session = await self.repository.create(
            user_id=old_session.user_id,
            organization_id=old_session.organization_id,
            device_id=old_session.device_id,
            session_token_hash=new_token_hash,
            authentication_method="refresh_token",
            authentication_level="refresh",
            ip_address=ip_address or old_session.ip_address,
            user_agent=user_agent or old_session.user_agent,
            created_at=now,
            last_activity_at=now,
            expires_at=new_expires_at,
            revoked=False,
        )
        await self.session.commit()

        return {
            "session_id": new_session.id,
            "user_id": new_session.user_id,
            "refresh_token": new_token,
            "expires_at": new_expires_at,
        }

    async def revoke(self, refresh_token: str, reason: str = "refresh_token_revoked",) -> bool:
        session = await self.validate(refresh_token)

        if session is None:
            return False

        session.revoked = True
        session.revoked_at = datetime.now(timezone.utc)
        session.revocation_reason = reason
        await self.session.flush()
        await self.session.commit()

        return True

    async def revoke_all(self, user_id: UUID, reason: str = "all_refresh_tokens_revoked",) -> None:
        sessions = await self.repository.get_active_for_user(user_id)
        now = datetime.now(timezone.utc)
        for session in sessions:
            if session.authentication_method == "refresh_token":
                session.revoked = True
                session.revoked_at = now
                session.revocation_reason = reason

        await self.session.flush()
        await self.session.commit()