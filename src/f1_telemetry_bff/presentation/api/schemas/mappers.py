from f1_telemetry_bff.application.dto import LapDTO
from f1_telemetry_bff.presentation.api.schemas.lap import LapResponse


def lap_dto_to_response(lap: LapDTO) -> LapResponse:
    return LapResponse(
        lap_number=lap.lap_number,
        driver_number=lap.driver_number,
        lap_time=lap.lap_time,
        date_start=lap.date_start,
    )
