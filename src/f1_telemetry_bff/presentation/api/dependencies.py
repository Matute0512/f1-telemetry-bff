import httpx
from fastapi import Depends

from f1_telemetry_bff.application.use_cases.get_session_laps import (
    GetSessionLapsUseCase,
)
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.repository import (
    OpenF1TelemetryRepository,
)


async def get_http_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient() as client:
        yield client


def get_get_session_laps_use_case(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> GetSessionLapsUseCase:
    openf1_client = OpenF1Client(client)
    repository = OpenF1TelemetryRepository(openf1_client)

    return GetSessionLapsUseCase(repository)
