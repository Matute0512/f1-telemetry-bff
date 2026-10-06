from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.infrastructure.openf1.mappers import map_lap
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


def test_map_lap_rejects_missing_duration() -> None:
    lap = OpenF1Lap(
        driver_number=1,
        lap_number=10,
        lap_duration=None,
        date_start=None,
    )

    with pytest.raises(ValueError):
        map_lap(lap)
