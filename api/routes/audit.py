from __future__ import annotations
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..dependencies import (
    get_audit_service,
    get_current_user,
)
from ..schemas.user import UserResponse

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)

@router.get(
    "",
    response_model=list[dict],
)

async def list_audit_events(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    audit_service: Annotated[object, Depends(get_audit_service)],
    organization_id: Optional[UUID] = Query(default=None),
    event_type: Optional[str] = Query(default=None, max_length=128),
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date must not be after end_date.")

    return await audit_service.list_events(
        user_id=current_user.id,
        organization_id=organization_id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{audit_id}",
    response_model=dict,
)

async def get_audit_event(
    audit_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    audit_service: Annotated[object, Depends(get_audit_service)],
):
    event = await audit_service.get_event(
        audit_id=audit_id,
        user_id=current_user.id,
    )

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit event not found.")

    return event

__all__ = ["router"]