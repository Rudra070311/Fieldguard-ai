from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import (
    get_current_user,
    get_pin_service,
)
from ..schemas.pin import (
    PinChangeRequest,
    PinCreateRequest,
    PinVerifyRequest,
)
from ..schemas.user import UserResponse

router = APIRouter(
    prefix="/pin",
    tags=["PIN"],
)

@router.post(
    "",
    response_model=dict,
)

async def create_pin(
    request: PinCreateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    pin_service: Annotated[object, Depends(get_pin_service)],
):
    try:
        await pin_service.create_pin(
            user_id=current_user.id,
            pin=request.pin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "success": True,
        "message": "PIN created successfully.",
    }

@router.post(
    "/verify",
    response_model=dict,
)

async def verify_pin(
    request: PinVerifyRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    pin_service: Annotated[object, Depends(get_pin_service)],
):
    try:
        valid = await pin_service.verify_pin(
            user_id=current_user.id,
            pin=request.pin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN.")

    return {
        "success": True,
        "message": "PIN verified successfully.",
    }

@router.post(
    "/change",
    response_model=dict,
)

async def change_pin(
    request: PinChangeRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    pin_service: Annotated[object, Depends(get_pin_service)],
):
    try:
        await pin_service.change_pin(
            user_id=current_user.id,
            current_pin=request.current_pin,
            new_pin=request.new_pin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "success": True,
        "message": "PIN changed successfully.",
    }