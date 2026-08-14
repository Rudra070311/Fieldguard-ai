from __future__ import annotations
from uuid import UUID

class ProfileManager:
    def __init__(self, user_repository, audit_logger=None,):
        self.user_repository = user_repository
        self.audit_logger = audit_logger

    async def get(self, user_id: UUID,):
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        return user

    async def update(self, user_id: UUID, **profile_data,):
        if not profile_data:
            raise ValueError("No profile changes supplied.")

        protected_fields = {
            "id",
            "password_hash",
            "pin_hash",
            "is_admin",
            "permissions",
            "created_at",
            "updated_at",
        }

        invalid = protected_fields.intersection(profile_data)

        if invalid:
            raise ValueError(
                f"Protected fields cannot be changed here: "
                f"{', '.join(sorted(invalid))}"
            )

        user = await self.user_repository.update(user_id, **profile_data,)

        if user is None:
            raise ValueError("User not found.")

        if self.audit_logger:
            await self.audit_logger.log(
                event_type="profile_updated",
                user_id=user_id,
            )

        return user

    async def delete(self, user_id: UUID,) -> bool:
        return await self.user_repository.delete(user_id)