from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from f1_telemetry_bff.domain.entities import Lap, TelemetryPoint
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Lap
from f1_telemetry_bff.infrastructure.openf1.repository import (
    OpenF1TelemetryRepository,
)


class FakeOpenF1Client(OpenF1Client):
    def __init__(
        self,
        laps: list[dict[str, Any]] | None = None,
        locations: list[dict[str, Any]] | None = None,
        car_data: list[dict[str, Any]] | None = None,
    ) -> None:  # type: ignore[override]
        self._laps = laps or []
        self._locations = locations or []
        self._car_data = car_data or []
        self.location_call_params: dict[str, Any] | None = None
        self.car_data_call_params: dict[str, Any] | None = None

    async def get(
        self, resource: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return self._laps

    async def get_location(
        self,
        session_key: int,
        driver_number: int,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        self.location_call_params = {
            "session_key": session_key,
            "driver_number": driver_number,
            "date_start": date_start,
            "date_end": date_end,
        }
        return self._locations

    async def get_car_data(
        self,
        session_key: int,
        driver_number: int,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        self.car_data_call_params = {
            "session_key": session_key,
            "driver_number": driver_number,
            "date_start": date_start,
            "date_end": date_end,
        }
        return self._car_data


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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_telemetry_for_lap_calculates_time_interval_and_synchronizes() -> None:
    t_start = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    lap = Lap(
        lap_number=5,
        driver_number=1,
        lap_time=80.0,
        date_start=t_start,
    )
    expected_end = t_start + timedelta(seconds=80.0)

    raw_locations = [
        {
            "date": t_start.isoformat(),
            "driver_number": 1,
            "x": 10.0,
            "y": 20.0,
            "z": 1.0,
        }
    ]
    raw_car_data = [
        {
            "date": t_start.isoformat(),
            "driver_number": 1,
            "speed": 310.0,
            "throttle": 100.0,
            "brake": 0.0,
            "gear": 8,
        }
    ]

    fake_client = FakeOpenF1Client(locations=raw_locations, car_data=raw_car_data)
    repository = OpenF1TelemetryRepository(fake_client)

    points = await repository.get_telemetry_for_lap(
        session_key=9158,
        driver_number=1,
        lap=lap,
    )

    assert fake_client.location_call_params == {
        "session_key": 9158,
        "driver_number": 1,
        "date_start": t_start,
        "date_end": expected_end,
    }
    assert fake_client.car_data_call_params == {
        "session_key": 9158,
        "driver_number": 1,
        "date_start": t_start,
        "date_end": expected_end,
    }

    assert len(points) == 1
    assert isinstance(points[0], TelemetryPoint)
    assert points[0].timestamp == t_start
    assert points[0].x == 10.0
    assert points[0].y == 20.0
    assert points[0].z == 1.0
    assert points[0].speed == 310.0
    assert points[0].throttle == 100.0
    assert points[0].brake == 0.0
    assert points[0].gear == 8


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_telemetry_by_lap_number_finds_lap_and_returns_telemetry() -> None:
    t_start = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    raw_laps = [
        _make_openf1_lap(lap_number=10, lap_duration=85.0, date_start=t_start),
    ]
    raw_locations = [
        {
            "date": t_start.isoformat(),
            "driver_number": 1,
            "x": 5.0,
            "y": 15.0,
            "z": 0.5,
        }
    ]
    raw_car_data = [
        {
            "date": t_start.isoformat(),
            "driver_number": 1,
            "speed": 290.0,
            "throttle": 90.0,
            "brake": 0.0,
            "gear": 7,
        }
    ]

    fake_client = FakeOpenF1Client(
        laps=raw_laps,
        locations=raw_locations,
        car_data=raw_car_data,
    )
    repository = OpenF1TelemetryRepository(fake_client)

    points = await repository.get_telemetry(
        session_key=9158,
        driver_number=1,
        lap_number=10,
    )

    assert len(points) == 1
    assert points[0].speed == 290.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_telemetry_by_lap_number_returns_empty_when_lap_not_found() -> None:
    raw_laps = [
        _make_openf1_lap(lap_number=10, lap_duration=85.0),
    ]
    fake_client = FakeOpenF1Client(laps=raw_laps)
    repository = OpenF1TelemetryRepository(fake_client)

    points = await repository.get_telemetry(
        session_key=9158,
        driver_number=1,
        lap_number=99,
    )

    assert points == []
