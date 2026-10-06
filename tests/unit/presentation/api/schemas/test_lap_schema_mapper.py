from datetime import UTC, datetime

from f1_telemetry_bff.application.dto.lap_to_dto import LapDTO
from f1_telemetry_bff.presentation.api.schemas.mappers import lap_dto_to_response


def _make_dto(
    *,
    lap_number: int = 10,
    driver_number: int = 1,
    lap_time: float = 82.456,
    date_start: datetime = datetime(2026, 10, 5, 15, 30, tzinfo=UTC),
) -> LapDTO:
    return LapDTO(
        lap_number=lap_number,
        driver_number=driver_number,
        lap_time=lap_time,
        date_start=date_start,
    )


def test_lap_dto_to_response_maps_all_fields() -> None:
    dto = _make_dto()

    response = lap_dto_to_response(dto)

    assert response.lap_number == dto.lap_number
    assert response.driver_number == dto.driver_number
    assert response.lap_time == dto.lap_time
    assert response.date_start == dto.date_start


def test_lap_dto_to_response_preserves_driver_number() -> None:
    dto = _make_dto(driver_number=16)

    response = lap_dto_to_response(dto)

    assert response.driver_number == 16


def test_lap_dto_to_response_preserves_lap_time() -> None:
    dto = _make_dto(lap_time=75.001)

    response = lap_dto_to_response(dto)

    assert response.lap_time == 75.001
