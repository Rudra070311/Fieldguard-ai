from __future__ import annotations
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from ..dependencies import (
    get_admin_service,
    require_admin,
)
from ..schemas.user import UserResponse

router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(require_admin)],
)

class AdminLockRequest(BaseModel):
    reason: str = Field(
        default="administrative_lock",
        min_length=1,
        max_length=256,
    )

class AdminDeviceRevokeRequest(BaseModel):
    reason: str = Field(
        default="administrative_revocation",
        min_length=1,
        max_length=256,
    )

@router.get(
    "/users",
    response_model=list[dict],
)

async def list_users(
    admin_service: Annotated[object, Depends(get_admin_service)],
    search: Optional[str] = Query(default=None, max_length=256),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await admin_service.list_users(
        search=search,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/users/{user_id}",
    response_model=dict,
)

async def get_user(
    user_id: UUID,
    admin_service: Annotated[object, Depends(get_admin_service)]
):
    user = await admin_service.get_user(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user

@router.post(
    "/users/{user_id}/lock",
    response_model=dict,
)

async def lock_user(
    user_id: UUID,
    request: AdminLockRequest,
    current_admin: Annotated[UserResponse, Depends(require_admin)],
    admin_service: Annotated[object, Depends(get_admin_service)],
):
    try:
        result = await admin_service.lock_user(
            user_id=user_id,
            admin_id=current_admin.id,
            reason=request.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "success": True,
        "result": result,
    }

@router.post(
    "/users/{user_id}/unlock",
    response_model=dict,
)

async def unlock_user(
    user_id: UUID,
    current_admin: Annotated[UserResponse, Depends(require_admin)],
    admin_service: Annotated[object, Depends(get_admin_service)],
):
    try:
        result = await admin_service.unlock_user(
            user_id=user_id,
            admin_id=current_admin.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "success": True,
        "result": result,
    }

@router.get(
    "/devices",
    response_model=list[dict],
)

async def list_devices(
    admin_service: Annotated[object, Depends(get_admin_service)],
    user_id: Optional[UUID] = Query(default=None),
    revoked: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await admin_service.list_devices(
        user_id=user_id,
        revoked=revoked,
        limit=limit,
        offset=offset,
    )

@router.post(
    "/devices/{device_id}/revoke",
    response_model=dict,
)

async def revoke_device(
    device_id: UUID,
    request: AdminDeviceRevokeRequest,
    current_admin: Annotated[UserResponse, Depends(require_admin)],
    admin_service: Annotated[object, Depends(get_admin_service)],
):
    try:
        result = await admin_service.revoke_device(
            device_id=device_id,
            admin_id=current_admin.id,
            reason=request.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "success": True,
        "result": result,
    }

@router.get(
    "/audit",
    response_model=list[dict],
)

async def admin_audit(
    admin_service: Annotated[object, Depends(get_admin_service)],
    user_id: Optional[UUID] = Query(default=None),
    event_type: Optional[str] = Query(default=None, max_length=128),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return await admin_service.list_audit_events(
        user_id=user_id,
        event_type=event_type,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/risk",
    response_model=list[dict],
)

async def risk_overview(
    admin_service: Annotated[object, Depends(get_admin_service)],
    user_id: Optional[UUID] = Query(default=None),
    device_id: Optional[UUID] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
):
    return await admin_service.get_risk_overview(
        user_id=user_id,
        device_id=device_id,
        limit=limit,
    )

__all__ = ["router"]