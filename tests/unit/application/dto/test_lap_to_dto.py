from datetime import UTC, datetime

from f1_telemetry_bff.application.dto.mappers import lap_to_dto
from f1_telemetry_bff.domain.entities import Lap


def _make_lap(
    *,
    lap_number: int = 10,
    driver_number: int = 1,
    lap_time: float = 82.456,
    date_start: datetime = datetime(2026, 10, 5, 15, 30, tzinfo=UTC),
) -> Lap:
    return Lap(
        lap_number=lap_number,
        driver_number=driver_number,
        lap_time=lap_time,
        date_start=date_start,
    )


def test_lap_to_dto_maps_all_fields() -> None:
    lap = _make_lap()

    dto = lap_to_dto(lap)

    assert dto.lap_number == lap.lap_number
    assert dto.driver_number == lap.driver_number
    assert dto.lap_time == lap.lap_time
    assert dto.date_start == lap.date_start


def test_lap_to_dto_preserves_driver_number() -> None:
    lap = _make_lap(driver_number=44)

    dto = lap_to_dto(lap)

    assert dto.driver_number == 44


def test_lap_to_dto_preserves_lap_time() -> None:
    lap = _make_lap(lap_time=91.123)

    dto = lap_to_dto(lap)

    assert dto.lap_time == 91.123
