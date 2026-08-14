from __future__ import annotations
from uuid import UUID

class RoleManager:
    ROLES = {
        "owner",
        "admin",
        "member",
    }
    ROLE_HIERARCHY = {
        "member": 1,
        "admin": 2,
        "owner": 3,
    }

    def __init__(self, organization_repository, user_repository, audit_logger=None):
        self.organization_repository = organization_repository
        self.user_repository = user_repository
        self.audit_logger = audit_logger

    def validate_role(self, role: str) -> str:
        role = role.strip().lower()

        if role not in self.ROLES:
            raise ValueError(f"Invalid role: {role}")

        return role

    def can_manage_role(self, actor_role: str, target_role: str,) -> bool:
        actor_role = self.validate_role(actor_role)
        target_role = self.validate_role(target_role)

        return (
            self.ROLE_HIERARCHY[actor_role]
            > self.ROLE_HIERARCHY[target_role]
        )

    async def assign_role(self, actor_id: UUID, target_user_id: UUID, organization_id: UUID, role: str,) -> None:
        role = self.validate_role(role)

        organization = await self.organization_repository.get_by_id(organization_id)

        if organization is None:
            raise ValueError("Organization not found.")

        target_user = await self.user_repository.get_by_id(target_user_id)

        if target_user is None:
            raise ValueError("Target user not found.")
        if self.audit_logger:
            await self.audit_logger.log(
                event_type="role_assigned",
                user_id=actor_id,
                target_user_id=target_user_id,
                organization_id=organization_id,
                role=role,
            )