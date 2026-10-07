from typing import Annotated

import httpx
from fastapi import Depends, Request

from f1_telemetry_bff.application.use_cases import (
    GetLapTelemetryUseCase,
    GetSessionDetailsUseCase,
    GetSessionLapsUseCase,
    SelectHeadToHeadDriversUseCase,
)
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.repository import (
    OpenF1TelemetryRepository,
)
from f1_telemetry_bff.infrastructure.openf1.session_repository import (
    OpenF1SessionRepository,
)


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_get_session_laps_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GetSessionLapsUseCase:
    openf1_client = OpenF1Client(client)
    repository = OpenF1TelemetryRepository(openf1_client)

    return GetSessionLapsUseCase(repository)


def get_get_lap_telemetry_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GetLapTelemetryUseCase:
    openf1_client = OpenF1Client(client)
    repository = OpenF1TelemetryRepository(openf1_client)

    return GetLapTelemetryUseCase(repository)


def get_get_session_details_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GetSessionDetailsUseCase:
    openf1_client = OpenF1Client(client)
    repository = OpenF1SessionRepository(openf1_client)

    return GetSessionDetailsUseCase(repository)


def get_select_head_to_head_drivers_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> SelectHeadToHeadDriversUseCase:
    openf1_client = OpenF1Client(client)
    repository = OpenF1SessionRepository(openf1_client)

    return SelectHeadToHeadDriversUseCase(repository)
