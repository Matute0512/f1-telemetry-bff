from f1_telemetry_bff.application.dto.lap_to_dto import LapDTO
from f1_telemetry_bff.domain.entities import Lap


def lap_to_dto(lap: Lap) -> LapDTO:
    return LapDTO(
        lap_number=lap.lap_number,
        driver_number=lap.driver_number,
        lap_time=lap.lap_time,
        date_start=lap.date_start,
    )
