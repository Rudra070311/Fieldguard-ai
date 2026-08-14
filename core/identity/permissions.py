from __future__ import annotations
from uuid import UUID

class PermissionManager:
    def __init__(self, user_repository, organization_repository):
        self.user_repository = user_repository
        self.organization_repository = organization_repository

    async def has_permission(self, user_id: UUID, permission: str, organization_id: UUID | None = None ) -> bool:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            return False
        if getattr(user, "suspended", False):
            return False

        permissions = self._get_user_permissions(user)

        if permission in permissions:
            return True
        if organization_id is not None:
            return await self._organization_permission(
                user,
                organization_id,
                permission,
            )

        return False

    async def _organization_permission(self, user, organization_id: UUID, permission: str,) -> bool:
        organizations = await self.organization_repository.get_for_user(user.id)
        organization = next(
            (
                item
                for item in organizations
                if item.id == organization_id
            ),
            None,
        )

        if organization is None:
            return False

        role = getattr(organization, "role", None)

        return permission in self.permissions_for_role(role)

    def permissions_for_role(self, role: str | None,) -> set[str]:
        role_permissions = {
            "owner": {
                "users.read",
                "users.write",
                "users.delete",
                "organizations.read",
                "organizations.write",
                "organizations.delete",
                "profile.read",
                "profile.write",
            },
            "admin": {
                "users.read",
                "users.write",
                "organizations.read",
                "organizations.write",
                "profile.read",
                "profile.write",
            },
            "member": {
                "users.read",
                "organizations.read",
                "profile.read",
                "profile.write",
            },
        }

        return role_permissions.get(role or "", set())

    def _get_user_permissions(self, user) -> set[str]:
        explicit = getattr(user, "permissions", None)

        if explicit is None:
            return set()
        if isinstance(explicit, dict):
            return {
                key
                for key, enabled in explicit.items()
                if enabled
            }
        if isinstance(explicit, (list, tuple, set)):
            return set(explicit)

        return set()