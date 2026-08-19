from __future__ import annotations
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import (
    get_current_user,
    get_session_manager,
)
from ..schemas.session import SessionResponse, SessionRevokeRequest
from ..schemas.user import UserResponse

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)

@router.get(
    "",
    response_model=list[SessionResponse],
)

async def list_sessions(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session_manager: Annotated[object, Depends(get_session_manager)],
):
    return await session_manager.repository.get_active_for_user(current_user.id)

@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)

async def get_session(
    session_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session_manager: Annotated[object, Depends(get_session_manager)],
):
    session = await session_manager.repository.get_by_id(session_id)

    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.",)

    return session


@router.post(
    "/{session_id}/revoke",
    response_model=dict,
)

async def revoke_session(
    session_id: UUID,
    request: SessionRevokeRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session_manager: Annotated[object, Depends(get_session_manager)],
):
    session = await session_manager.repository.get_by_id(session_id)

    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.",)

    success = await session_manager.revoke_session(
        session_id=session_id,
        reason=request.reason or "manual_revocation",
    )

    return {
        "success": success,
        "message": "Session revoked.",
    }

@router.post(
    "/revoke-all",
    response_model=dict,
)

async def revoke_all_sessions(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session_manager: Annotated[object, Depends(get_session_manager)],
):
    await session_manager.revoke_all_for_user(current_user.id,)

    return {
        "success": True,
        "message": "All sessions revoked.",
    }