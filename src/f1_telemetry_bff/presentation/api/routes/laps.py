from typing import Annotated

from fastapi import APIRouter, Depends

from f1_telemetry_bff.application.dto.mappers import (
    lap_to_dto,
    telemetry_point_to_dto,
)
from f1_telemetry_bff.application.use_cases import (
    GetLapTelemetryUseCase,
    GetSessionLapsUseCase,
)
from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_lap_telemetry_use_case,
    get_get_session_laps_use_case,
)
from f1_telemetry_bff.presentation.api.schemas import (
    LapResponse,
    LapTelemetryResponse,
)
from f1_telemetry_bff.presentation.api.schemas.mappers import (
    lap_dto_to_response,
    lap_telemetry_to_response,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Laps"],
)


@router.get(
    "/sessions/{session_key}/drivers/{driver_number}/laps",
    response_model=list[LapResponse],
)
async def get_session_laps(
    session_key: int,
    driver_number: int,
    use_case: Annotated[
        GetSessionLapsUseCase,
        Depends(get_get_session_laps_use_case),
    ],
) -> list[LapResponse]:
    laps = await use_case.execute(
        session_key=session_key,
        driver_number=driver_number,
    )

    lap_dtos = [lap_to_dto(lap) for lap in laps]

    return [lap_dto_to_response(lap) for lap in lap_dtos]


@router.get(
    "/sessions/{session_key}/drivers/{driver_number}/laps/{lap_number}/telemetry",
    response_model=LapTelemetryResponse,
)
async def get_lap_telemetry(
    session_key: int,
    driver_number: int,
    lap_number: int,
    use_case: Annotated[
        GetLapTelemetryUseCase,
        Depends(get_get_lap_telemetry_use_case),
    ],
) -> LapTelemetryResponse:
    telemetry_points = await use_case.execute(
        session_key=session_key,
        driver_number=driver_number,
        lap_number=lap_number,
    )

    point_dtos = [telemetry_point_to_dto(point) for point in telemetry_points]

    return lap_telemetry_to_response(
        session_key=session_key,
        driver_number=driver_number,
        lap_number=lap_number,
        telemetry_dtos=point_dtos,
    )
