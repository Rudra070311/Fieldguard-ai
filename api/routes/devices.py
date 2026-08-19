from __future__ import annotations
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import (
    get_current_user,
    get_device_service,
)
from ..schemas.user import UserResponse

router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)

@router.get(
    "",
    response_model=list[dict],
)

async def list_devices(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    device_service: Annotated[object, Depends(get_device_service)],
):
    return await device_service.get_user_devices(current_user.id,)

@router.get(
    "/{device_id}",
    response_model=dict,
)

async def get_device(
    device_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    device_service: Annotated[object, Depends(get_device_service)],
):
    device = await device_service.get_device(
        user_id=current_user.id,
        device_id=device_id,
    )

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.",)

    return device

@router.post(
    "/{device_id}/remember",
    response_model=dict,
)

async def remember_device(
    device_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    device_service: Annotated[object, Depends(get_device_service)],
):
    result = await device_service.remember_device(
        user_id=current_user.id,
        device_id=device_id,
    )

    return result

@router.post(
    "/{device_id}/revoke",
    response_model=dict,
)

async def revoke_device(
    device_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    device_service: Annotated[object, Depends(get_device_service)],
):
    result = await device_service.revoke_device(
        user_id=current_user.id,
        device_id=device_id,
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.")

    return {
        "success": True,
        "message": "Device revoked.",
    }