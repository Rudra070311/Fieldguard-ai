from __future__ import annotations
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import (
    get_current_user,
    get_organization_service,
)
from ..schemas.organization import (
    OrganizationCreateRequest,
    OrganizationListResponse,
    OrganizationMemberRequest,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from ..schemas.user import UserResponse

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)

@router.get(
    "",
    response_model=OrganizationListResponse,
)

async def list_organizations(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[
        object,
        Depends(get_organization_service),
    ],
):
    organizations = await organization_service.get_for_user(current_user.id,)

    return {"organizations": organizations,}

@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)

async def create_organization(
    request: OrganizationCreateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[object, Depends(get_organization_service),],
):
    try:
        return await organization_service.create(
            user_id=current_user.id,
            org_name=request.org_name,
            slug=request.slug,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),) from exc

@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)

async def get_organization(
    organization_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[object, Depends(get_organization_service),],
):
    organization = await organization_service.get_by_id(organization_id, user_id=current_user.id,)

    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.",)

    return organization

@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
)

async def update_organization(
    organization_id: UUID,
    request: OrganizationUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[object, Depends(get_organization_service),],
):
    try:
        organization = await organization_service.update(
            organization_id=organization_id,
            user_id=current_user.id,
            **request.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),) from exc

    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.",)

    return organization

@router.delete(
    "/{organization_id}",
    response_model=dict,
)

async def delete_organization(
    organization_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[object, Depends(get_organization_service),],
):
    try:
        deleted = await organization_service.delete(
            organization_id=organization_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),) from exc

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.",)

    return {
        "success": True,
        "message": "Organization deleted successfully.",
    }

@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)

async def add_member(
    organization_id: UUID,
    request: OrganizationMemberRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[object, Depends(get_organization_service)],
):
    try:
        return await organization_service.add_member(
            organization_id=organization_id,
            actor_user_id=current_user.id,
            user_id=request.user_id,
            role=request.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),) from exc

@router.delete(
    "/{organization_id}/members/{user_id}",
    response_model=dict,
)

async def remove_member(
    organization_id: UUID,
    user_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    organization_service: Annotated[object, Depends(get_organization_service)],
):
    try:
        removed = await organization_service.remove_member(
            organization_id=organization_id,
            actor_user_id=current_user.id,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization member not found.")

    return {
        "success": True,
        "message": "Organization member removed.",
    }

__all__ = ["router"]