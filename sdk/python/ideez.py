from __future__ import annotations
from typing import Any, Optional
from uuid import UUID
import httpx

class IDeezError(Exception):
    pass

class IDeezClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.ideez.dev",
        timeout: float = 15.0,
    ):
        if not api_key:
            raise ValueError("api_key is required")

        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def health(self) -> dict[str, Any]:
        response = await self.client.get("/health")
        return self._handle(response)

    async def create_session(self, user_id: UUID | str, **kwargs: Any) -> dict[str, Any]:
        payload = {
            "user_id": str(user_id),
            **kwargs,
        }

        response = await self.client.post(
            "/api/v1/sessions",
            json=payload,
        )

        return self._handle(response)

    async def verify_pin(self, pin: str) -> dict[str, Any]:
        response = await self.client.post(
            "/api/v1/pin/verify",
            json={"pin": pin},
        )

        return self._handle(response)

    async def revoke_session(self, session_id: UUID | str) -> dict[str, Any]:
        response = await self.client.post(f"/api/v1/sessions/{session_id}/revoke",)

        return self._handle(response)

    async def __aenter__(self) -> "IDeezClient":
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        await self.close()

    @staticmethod
    def _handle(response: httpx.Response) -> dict[str, Any]:
        if response.is_success:
            return response.json()

        try:
            detail = response.json()
        except ValueError:
            detail = response.text

        raise IDeezError(f"iDeez API error {response.status_code}: {detail}")

__all__ = [
    "IDeezClient",
    "IDeezError",
]