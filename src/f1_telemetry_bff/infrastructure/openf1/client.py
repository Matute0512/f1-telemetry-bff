from typing import Any

import httpx

from f1_telemetry_bff.config.settings import get_settings


class OpenF1Client:
    """HTTP client for the OpenF1 API."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._base_url = get_settings().openf1_base_url

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Perform a GET request against OpenF1."""
        response = await self._client.get(
            f"{self._base_url}/{endpoint}",
            params=params,
        )

        response.raise_for_status()

        return response.json()
