from __future__ import annotations
from uuid import UUID

class OrganizationManager:
    def __init__(
        self,
        organization_repository,
        user_repository,
        audit_logger=None,
    ):
        self.organization_repository = organization_repository
        self.user_repository = user_repository
        self.audit_logger = audit_logger

    async def get(self, organization_id: UUID,):
        return await self.organization_repository.get_by_id(organization_id)

    async def get_by_slug(self, slug: str,):
        return await self.organization_repository.get_by_slug(slug.strip().lower())

    async def get_for_user(self, user_id: UUID,):
        return await self.organization_repository.get_for_user(user_id)

    async def create(self, name: str, slug: str, owner_id: UUID, **extra,):
        normalized_slug = slug.strip().lower()
        existing = await self.organization_repository.get_by_slug(normalized_slug)

        if existing is not None:
            raise ValueError("Organization slug already exists.")

        organization = await self.organization_repository.create(
            name=name.strip(),
            slug=normalized_slug,
            owner_id=owner_id,
            **extra,
        )

        if self.audit_logger:
            await self.audit_logger.log(
                event_type="organization_created",
                user_id=owner_id,
                organization_id=organization.id,
            )

        return organization

    async def update(self, organization_id: UUID, **changes,):
        if not changes:
            raise ValueError("No organization changes supplied.")
        if "slug" in changes:
            changes["slug"] = changes["slug"].strip().lower()

        organization = await self.organization_repository.update(organization_id, **changes,)

        if organization is None:
            raise ValueError("Organization not found.")

        return organization

    async def delete(self, organization_id: UUID,) -> bool:
        organization = await self.organization_repository.get_by_id(organization_id)

        if organization is None:
            return False

        return await self.organization_repository.delete(organization_id)