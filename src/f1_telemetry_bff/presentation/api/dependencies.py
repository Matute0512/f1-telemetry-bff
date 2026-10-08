from typing import Annotated

import httpx
from fastapi import Depends, Request

from f1_telemetry_bff.application.use_cases import (
    GetHeadToHeadComparisonUseCase,
    GetHeadToHeadTelemetryUseCase,
    GetLapTelemetryUseCase,
    GetSessionDetailsUseCase,
    GetSessionLapsUseCase,
    SelectHeadToHeadDriversUseCase,
    SelectHeadToHeadLapsUseCase,
)
from f1_telemetry_bff.domain.services.lap_comparison_service import (
    LapComparisonService,
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


def get_select_head_to_head_laps_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> SelectHeadToHeadLapsUseCase:
    openf1_client = OpenF1Client(client)
    session_repository = OpenF1SessionRepository(openf1_client)
    telemetry_repository = OpenF1TelemetryRepository(openf1_client)

    return SelectHeadToHeadLapsUseCase(
        session_repository=session_repository,
        telemetry_repository=telemetry_repository,
    )


def get_get_head_to_head_telemetry_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GetHeadToHeadTelemetryUseCase:
    openf1_client = OpenF1Client(client)
    session_repository = OpenF1SessionRepository(openf1_client)
    telemetry_repository = OpenF1TelemetryRepository(openf1_client)

    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repository,
        telemetry_repository=telemetry_repository,
    )

    return GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repository,
    )


def get_get_head_to_head_comparison_use_case(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GetHeadToHeadComparisonUseCase:
    openf1_client = OpenF1Client(client)
    session_repository = OpenF1SessionRepository(openf1_client)
    telemetry_repository = OpenF1TelemetryRepository(openf1_client)

    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repository,
        telemetry_repository=telemetry_repository,
    )
    comparison_service = LapComparisonService()

    return GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repository,
        comparison_service=comparison_service,
    )
