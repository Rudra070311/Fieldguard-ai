from __future__ import annotations
from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import Settings
from database.session import get_db
from core.auth.email_verifier import EmailVerifier
from core.auth.magic_link import MagicLinkManager
from core.auth.otp import OTPManager
from core.auth.refresh_tokens import RefreshTokenManager
from core.auth.session_manager import SessionManager
from core.devices.remember_device import RememberDeviceManager
from core.devices.revoke import DeviceRevocationManager
from core.pin.lockout import LockoutManager
from core.pin.pin_service import PinService
from core.pin.pin_verify import PinVerifier
from core.pin.recovery import RecoveryManager
from core.security.risk_engine import RiskEngine
from core.security.secure_delete import SecureDeleteManager
from database.repositories.device_repo import DeviceRepository
from database.repositories.organization_repo import OrganizationRepository
from database.repositories.session_repo import SessionRepository
from database.repositories.user_repo import UserRepository

def get_settings(request: Request) -> Settings:
    return request.app.state.settings

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session

def get_user_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UserRepository:
    return UserRepository(session)

def get_device_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> DeviceRepository:
    return DeviceRepository(session)

def get_session_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> SessionRepository:
    return SessionRepository(session)

def get_organization_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> OrganizationRepository:
    return OrganizationRepository(session)

def get_session_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> SessionManager:
    return SessionManager(
        session=session,
        settings=settings,
    )

def get_refresh_token_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> RefreshTokenManager:
    return RefreshTokenManager(
        session=session,
        settings=settings,
    )

def get_risk_engine(settings: Annotated[Settings, Depends(get_settings)]) -> RiskEngine:
    return RiskEngine(settings=settings)

def get_pin_service(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> PinService:
    return PinService(
        session=session,
        settings=settings,
    )

def get_pin_verifier(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> PinVerifier:
    return PinVerifier(
        session=session,
        settings=settings,
    )

def get_lockout_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> LockoutManager:
    return LockoutManager(
        session=session,
        settings=settings,
    )

def get_recovery_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> RecoveryManager:
    return RecoveryManager(
        session=session,
        settings=settings,
    )

def get_otp_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)],) -> OTPManager:
    raise NotImplementedError("Wire OTPManager with the project's notification and rate-limit services.")

def get_magic_link_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> MagicLinkManager:
    raise NotImplementedError(
        "Wire MagicLinkManager with the project's notification, "
        "rate-limit, and risk services."
    )

def get_email_verifier(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> EmailVerifier:
    raise NotImplementedError("Wire EmailVerifier with the project's email sender.")

def get_remember_device_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> RememberDeviceManager:
    raise NotImplementedError(
        "Wire RememberDeviceManager with trust, fingerprint, "
        "audit, and risk services."
    )

def get_device_revocation_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> DeviceRevocationManager:
    raise NotImplementedError("Wire DeviceRevocationManager with audit and risk services.")

def get_secure_delete_manager(session: Annotated[AsyncSession, Depends(get_db_session)], settings: Annotated[Settings, Depends(get_settings)]) -> SecureDeleteManager:
    return SecureDeleteManager(
        session=session,
        settings=settings,
    )

async def get_current_session(
    authorization: Annotated[str | None, Header(alias="Authorization")],
    manager: Annotated[SessionManager, Depends(get_session_manager)],
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header.",
        )

    session = await manager.get_session(token)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    return session

async def get_current_user(current_session=Depends(get_current_session), user_repository: UserRepository = Depends(get_user_repository)):
    user = await user_repository.get_by_id(current_session.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
        )

    return user

__all__ = [
    "get_settings",
    "get_db_session",
    "get_user_repository",
    "get_device_repository",
    "get_session_repository",
    "get_organization_repository",
    "get_session_manager",
    "get_refresh_token_manager",
    "get_risk_engine",
    "get_pin_service",
    "get_pin_verifier",
    "get_lockout_manager",
    "get_recovery_manager",
    "get_otp_manager",
    "get_magic_link_manager",
    "get_email_verifier",
    "get_remember_device_manager",
    "get_device_revocation_manager",
    "get_secure_delete_manager",
    "get_current_session",
    "get_current_user",
]