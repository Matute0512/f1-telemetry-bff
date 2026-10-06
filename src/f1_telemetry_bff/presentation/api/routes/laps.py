from typing import Annotated

from fastapi import APIRouter, Depends

from f1_telemetry_bff.application.dto.mappers import lap_to_dto
from f1_telemetry_bff.application.use_cases.get_session_laps import (
    GetSessionLapsUseCase,
)
from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_session_laps_use_case,
)
from f1_telemetry_bff.presentation.api.schemas import LapResponse
from f1_telemetry_bff.presentation.api.schemas.mappers import lap_dto_to_response

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
