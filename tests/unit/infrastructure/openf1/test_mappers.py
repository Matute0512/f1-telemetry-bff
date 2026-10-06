from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.infrastructure.openf1.mappers import is_complete, map_lap
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Lap


def test_map_openf1_lap_to_domain_lap() -> None:
    date_start = datetime(2026, 10, 5, 15, 30, tzinfo=UTC)

    openf1_lap = OpenF1Lap(
        driver_number=1,
        lap_number=10,
        lap_duration=82.456,
        date_start=date_start,
    )

    lap = map_lap(openf1_lap)

    assert lap.driver_number == 1
    assert lap.lap_number == 10
    assert lap.lap_time == 82.456
    assert lap.date_start == date_start


def test_is_complete_returns_true_when_all_fields_present() -> None:
    lap = OpenF1Lap(
        driver_number=1,
        lap_number=10,
        lap_duration=82.456,
        date_start=datetime(2026, 10, 5, 15, 30, tzinfo=UTC),
    )

    assert is_complete(lap) is True


@pytest.mark.parametrize(
    ("lap_duration", "date_start"),
    [
        (None, datetime(2026, 10, 5, 15, 30, tzinfo=UTC)),
        (82.456, None),
        (None, None),
    ],
)
def test_is_complete_returns_false_when_fields_missing(
    lap_duration: float | None,
    date_start: datetime | None,
) -> None:
    lap = OpenF1Lap(
        driver_number=1,
        lap_number=1,
        lap_duration=lap_duration,
        date_start=date_start,
    )

    assert is_complete(lap) is False
