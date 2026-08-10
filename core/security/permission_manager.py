from __future__ import annotations
from typing import Iterable

class PermissionManager:
    def has_permission(self, permissions: Iterable[str], required: str,) -> bool:
        permission_set = set(permissions)

        return (required in permission_set or "*" in permission_set)

    def require(self, permissions: Iterable[str], required: str,) -> None:
        if not self.has_permission(permissions, required):
            raise PermissionError(f"Missing permission: {required}")