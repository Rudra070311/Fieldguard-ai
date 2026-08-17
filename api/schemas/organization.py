from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

class OrganizationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    org_name: str = Field(min_length=1, max_length=256,)
    slug: str = Field(min_length=1, max_length=128,)

    @field_validator("org_name")
    @classmethod
    def validate_org_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Organization name cannot be empty.")

        return value

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("Organization slug cannot be empty.")

        return value

class OrganizationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    org_name: Optional[str] = Field(default=None, min_length=1, max_length=256,)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=128,)

    @field_validator("org_name")
    @classmethod
    def validate_org_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Organization name cannot be empty.")

        return value

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().lower()
        if not value:
            raise ValueError("Organization slug cannot be empty.")

        return value

class OrganizationMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    role: Optional[str] = Field(default=None, max_length=64,)

    @field_validator("role")
    @classmethod
    def normalize_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().lower()
        if not value:
            return None

        return value

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True,)
    id: UUID
    org_name: str
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True,)
    user_id: UUID
    org_id: UUID
    role: Optional[str] = None
    created_at: datetime

class OrganizationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True,)
    id: UUID
    org_name: str
    slug: str

class OrganizationListResponse(BaseModel):
    organizations: list[OrganizationSummary]

__all__ = [
    "OrganizationCreateRequest",
    "OrganizationUpdateRequest",
    "OrganizationMemberRequest",
    "OrganizationResponse",
    "OrganizationMemberResponse",
    "OrganizationSummary",
    "OrganizationListResponse",
]