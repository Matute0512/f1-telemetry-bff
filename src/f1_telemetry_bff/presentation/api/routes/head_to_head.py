from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from f1_telemetry_bff.application.dto.mappers import (
    head_to_head_lap_selection_to_dto,
    head_to_head_selection_to_dto,
)
from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    LapNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.application.use_cases import (
    SelectHeadToHeadDriversUseCase,
    SelectHeadToHeadLapsUseCase,
)
from f1_telemetry_bff.presentation.api.dependencies import (
    get_select_head_to_head_drivers_use_case,
    get_select_head_to_head_laps_use_case,
)
from f1_telemetry_bff.presentation.api.schemas import (
    HeadToHeadLapSelectionResponse,
    HeadToHeadSelectionResponse,
)
from f1_telemetry_bff.presentation.api.schemas.mappers import (
    head_to_head_lap_selection_dto_to_response,
    head_to_head_selection_dto_to_response,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Head to Head"],
)


@router.get(
    "/sessions/{session_key}/head-to-head",
    response_model=HeadToHeadSelectionResponse,
)
async def select_head_to_head_drivers(
    session_key: int,
    driver_a: Annotated[
        int,
        Query(
            description="Driver number for driver A",
            alias="driver_a",
        ),
    ],
    driver_b: Annotated[
        int,
        Query(
            description="Driver number for driver B",
            alias="driver_b",
        ),
    ],
    use_case: Annotated[
        SelectHeadToHeadDriversUseCase,
        Depends(get_select_head_to_head_drivers_use_case),
    ],
) -> HeadToHeadSelectionResponse:
    try:
        selection = await use_case.execute(
            session_key=session_key,
            driver_a_number=driver_a,
            driver_b_number=driver_b,
        )
    except SessionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except DriverNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except SameDriverSelectedError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    dto = head_to_head_selection_to_dto(selection)
    return head_to_head_selection_dto_to_response(dto)


@router.get(
    "/sessions/{session_key}/head-to-head/laps",
    response_model=HeadToHeadLapSelectionResponse,
)
async def select_head_to_head_laps(
    session_key: int,
    driver_a: Annotated[
        int,
        Query(
            description="Driver number for driver A",
            alias="driver_a",
        ),
    ],
    lap_a: Annotated[
        int,
        Query(
            description="Lap number for driver A",
            alias="lap_a",
        ),
    ],
    driver_b: Annotated[
        int,
        Query(
            description="Driver number for driver B",
            alias="driver_b",
        ),
    ],
    lap_b: Annotated[
        int,
        Query(
            description="Lap number for driver B",
            alias="lap_b",
        ),
    ],
    use_case: Annotated[
        SelectHeadToHeadLapsUseCase,
        Depends(get_select_head_to_head_laps_use_case),
    ],
) -> HeadToHeadLapSelectionResponse:
    try:
        selection = await use_case.execute(
            session_key=session_key,
            driver_a_number=driver_a,
            lap_a_number=lap_a,
            driver_b_number=driver_b,
            lap_b_number=lap_b,
        )
    except SessionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except DriverNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except SameDriverSelectedError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except LapNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err

    dto = head_to_head_lap_selection_to_dto(selection)
    return head_to_head_lap_selection_dto_to_response(dto)
