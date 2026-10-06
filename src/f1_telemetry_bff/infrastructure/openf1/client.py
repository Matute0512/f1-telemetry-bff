from datetime import datetime
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

    async def get_location(
        self,
        session_key: int,
        driver_number: int,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve location samples for a driver in a session."""
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        if date_start is not None:
            params["date>="] = date_start.isoformat()
        if date_end is not None:
            params["date<="] = date_end.isoformat()

        return await self.get("location", params=params)

    async def get_car_data(
        self,
        session_key: int,
        driver_number: int,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve car telemetry samples for a driver in a session."""
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        if date_start is not None:
            params["date>="] = date_start.isoformat()
        if date_end is not None:
            params["date<="] = date_end.isoformat()

        return await self.get("car_data", params=params)
