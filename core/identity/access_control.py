from __future__ import annotations
from uuid import UUID
from database.repositories.user_repo import UserRepository
from database.repositories.organization_repo import OrganizationRepository

class AccessControl:
    def __init__(
        self,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
        permission_manager,
    ):
        self.user_repository = user_repository
        self.organization_repository = organization_repository
        self.permission_manager = permission_manager

    async def can_access_user(self, actor_id: UUID, target_user_id: UUID,) -> bool:
        if actor_id == target_user_id:
            return True

        return await self.permission_manager.has_permission(
            actor_id,
            "users.read",
        )

    async def can_modify_user(self, actor_id: UUID, target_user_id: UUID,) -> bool:
        if actor_id == target_user_id:
            return await self.permission_manager.has_permission(
                actor_id,
                "profile.write",
            )

        return await self.permission_manager.has_permission(
            actor_id,
            "users.write",
        )

    async def can_access_organization(self, actor_id: UUID, organization_id: UUID,) -> bool:
        return await self.permission_manager.has_permission(
            actor_id,
            "organizations.read",
            organization_id=organization_id,
        )

    async def can_modify_organization(self, actor_id: UUID, organization_id: UUID,) -> bool:
        return await self.permission_manager.has_permission(
            actor_id,
            "organizations.write",
            organization_id=organization_id,
        )

    async def require_permission(self, actor_id: UUID, permission: str, organization_id: UUID | None = None,) -> None:
        allowed = await self.permission_manager.has_permission(
            actor_id,
            permission,
            organization_id=organization_id,
        )

        if not allowed:
            raise PermissionError(f"Permission denied: {permission}")