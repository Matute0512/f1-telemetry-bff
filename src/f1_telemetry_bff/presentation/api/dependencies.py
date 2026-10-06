from typing import Annotated

import httpx
from fastapi import Depends, Request

from f1_telemetry_bff.application.use_cases.get_session_laps import (
    GetSessionLapsUseCase,
)
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.repository import (
    OpenF1TelemetryRepository,
)


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_get_session_laps_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GetSessionLapsUseCase:
    openf1_client = OpenF1Client(client)
    repository = OpenF1TelemetryRepository(openf1_client)

    return GetSessionLapsUseCase(repository)
