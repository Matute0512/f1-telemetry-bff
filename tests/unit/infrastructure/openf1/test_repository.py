from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.domain.entities import Lap
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Lap
from f1_telemetry_bff.infrastructure.openf1.repository import (
    OpenF1TelemetryRepository,
)


class FakeOpenF1Client(OpenF1Client):
    def __init__(self, laps: list[dict]) -> None:  # type: ignore[override]
        self._laps = laps

    async def get(self, resource: str, params: dict) -> list[dict]:
        return self._laps


def _make_openf1_lap(
    *,
    lap_number: int = 1,
    driver_number: int = 1,
    lap_duration: float | None = 82.456,
    date_start: datetime | None = datetime(2026, 10, 5, 15, 30, tzinfo=UTC),
) -> dict:
    lap = OpenF1Lap(
        lap_number=lap_number,
        driver_number=driver_number,
        lap_duration=lap_duration,
        date_start=date_start,
    )
    return lap.model_dump()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_laps_returns_complete_laps() -> None:
    raw = [_make_openf1_lap(lap_number=2), _make_openf1_lap(lap_number=3)]
    repository = OpenF1TelemetryRepository(FakeOpenF1Client(raw))

    laps = await repository.get_laps(session_key=9158, driver_number=1)

    assert len(laps) == 2
    assert laps[0].lap_number == 2
    assert laps[1].lap_number == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_laps_filters_laps_with_missing_duration() -> None:
    raw = [
        _make_openf1_lap(lap_number=1, lap_duration=None),
        _make_openf1_lap(lap_number=2, lap_duration=82.456),
    ]
    repository = OpenF1TelemetryRepository(FakeOpenF1Client(raw))

    laps = await repository.get_laps(session_key=9158, driver_number=1)

    assert len(laps) == 1
    assert laps[0].lap_number == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_laps_filters_laps_with_missing_date_start() -> None:
    raw = [
        _make_openf1_lap(lap_number=1, date_start=None),
        _make_openf1_lap(lap_number=2),
    ]
    repository = OpenF1TelemetryRepository(FakeOpenF1Client(raw))

    laps = await repository.get_laps(session_key=9158, driver_number=1)

    assert len(laps) == 1
    assert laps[0].lap_number == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_laps_returns_empty_list_when_all_laps_incomplete() -> None:
    raw = [
        _make_openf1_lap(lap_number=1, lap_duration=None, date_start=None),
    ]
    repository = OpenF1TelemetryRepository(FakeOpenF1Client(raw))

    laps = await repository.get_laps(session_key=9158, driver_number=1)

    assert laps == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_laps_filters_incomplete_laps_and_returns_domain_entities() -> None:
    date_start_2 = datetime(2026, 10, 5, 15, 31, 0, tzinfo=UTC)
    date_start_4 = datetime(2026, 10, 5, 15, 33, 0, tzinfo=UTC)

    raw = [
        _make_openf1_lap(lap_number=1, lap_duration=None, date_start=date_start_2),
        _make_openf1_lap(lap_number=2, lap_duration=82.100, date_start=date_start_2),
        _make_openf1_lap(lap_number=3, lap_duration=81.500, date_start=None),
        _make_openf1_lap(lap_number=4, lap_duration=80.900, date_start=date_start_4),
    ]
    repository = OpenF1TelemetryRepository(FakeOpenF1Client(raw))

    laps = await repository.get_laps(session_key=9158, driver_number=1)

    assert len(laps) == 2
    assert all(isinstance(lap, Lap) for lap in laps)

    lap_1, lap_2 = laps
    assert lap_1.lap_number == 2
    assert lap_1.driver_number == 1
    assert lap_1.lap_time == 82.100
    assert lap_1.date_start == date_start_2

    assert lap_2.lap_number == 4
    assert lap_2.driver_number == 1
    assert lap_2.lap_time == 80.900
    assert lap_2.date_start == date_start_4
