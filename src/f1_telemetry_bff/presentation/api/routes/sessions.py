from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from f1_telemetry_bff.application.dto.mappers import session_details_to_dto
from f1_telemetry_bff.application.use_cases import GetSessionDetailsUseCase
from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_session_details_use_case,
)
from f1_telemetry_bff.presentation.api.schemas import SessionDetailsResponse
from f1_telemetry_bff.presentation.api.schemas.mappers import (
    session_details_dto_to_response,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Sessions"],
)


@router.get(
    "/sessions/{session_key}",
    response_model=SessionDetailsResponse,
)
async def get_session_details(
    session_key: int,
    use_case: Annotated[
        GetSessionDetailsUseCase,
        Depends(get_get_session_details_use_case),
    ],
) -> SessionDetailsResponse:
    session_details = await use_case.execute(session_key=session_key)
    if session_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with key {session_key} not found",
        )

    dto = session_details_to_dto(session_details)
    return session_details_dto_to_response(dto)
