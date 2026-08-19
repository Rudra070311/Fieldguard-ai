from __future__ import annotations
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import (
    get_current_user,
    get_user_service,
)
from ..schemas.user import (
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get(
    "/me",
    response_model=UserResponse,
)

async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    return current_user

@router.patch(
    "/me",
    response_model=UserResponse,
)

async def update_me(
    request: UserUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    user_service: Annotated[object, Depends(get_user_service)],
):
    try:
        user = await user_service.update(
            user_id=current_user.id,
            **request.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)

async def get_user(
    user_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    user_service: Annotated[object, Depends(get_user_service)],
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )

    user = await user_service.get_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user