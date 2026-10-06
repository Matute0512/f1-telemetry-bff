from datetime import UTC, datetime, timedelta

import pytest

from f1_telemetry_bff.infrastructure.openf1.models import OpenF1CarData, OpenF1Location
from f1_telemetry_bff.infrastructure.openf1.synchronizer import (
    DEFAULT_MAX_TIME_DELTA,
    TelemetrySynchronizer,
)


def _make_location(
    date: datetime,
    *,
    driver_number: int = 1,
    x: float = 100.0,
    y: float = 200.0,
    z: float = 10.0,
) -> OpenF1Location:
    return OpenF1Location(
        date=date,
        driver_number=driver_number,
        x=x,
        y=y,
        z=z,
    )


def _make_car_data(
    date: datetime,
    *,
    driver_number: int = 1,
    speed: float = 300.0,
    throttle: float = 100.0,
    brake: float = 0.0,
    gear: int = 7,
) -> OpenF1CarData:
    return OpenF1CarData(
        date=date,
        driver_number=driver_number,
        speed=speed,
        throttle=throttle,
        brake=brake,
        gear=gear,
    )


@pytest.mark.unit
def test_case_1_synchronize_exact_timestamps() -> None:
    t0 = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    locations = [_make_location(t0, x=10.0, y=20.0, z=0.0)]
    car_data = [_make_car_data(t0, speed=320.0, throttle=98.0, brake=0.0, gear=8)]

    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize(locations, car_data)

    assert len(points) == 1
    point = points[0]
    assert point.timestamp == t0
    assert point.x == 10.0
    assert point.y == 20.0
    assert point.z == 0.0
    assert point.speed == 320.0
    assert point.throttle == 98.0
    assert point.brake == 0.0
    assert point.gear == 8


@pytest.mark.unit
def test_case_2_synchronize_close_timestamps() -> None:
    t_loc = datetime(2026, 10, 5, 15, 30, 0, 270000, tzinfo=UTC)
    t_car = datetime(2026, 10, 5, 15, 30, 0, 275000, tzinfo=UTC)  # 5 ms difference

    locations = [_make_location(t_loc, x=55.0)]
    car_data = [_make_car_data(t_car, speed=280.0)]

    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize(locations, car_data)

    assert len(points) == 1
    assert points[0].timestamp == t_loc
    assert points[0].x == 55.0
    assert points[0].speed == 280.0


@pytest.mark.unit
def test_case_3_synchronize_multiple_samples() -> None:
    base = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    locations = [
        _make_location(base + timedelta(milliseconds=0), x=1.0),
        _make_location(base + timedelta(milliseconds=270), x=2.0),
        _make_location(base + timedelta(milliseconds=540), x=3.0),
        _make_location(base + timedelta(milliseconds=810), x=4.0),
    ]
    car_data = [
        _make_car_data(base + timedelta(milliseconds=0), speed=200.0),
        _make_car_data(base + timedelta(milliseconds=275), speed=210.0),
        _make_car_data(base + timedelta(milliseconds=550), speed=220.0),
        _make_car_data(base + timedelta(milliseconds=825), speed=230.0),
    ]

    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize(locations, car_data)

    assert len(points) == 4
    assert [p.x for p in points] == [1.0, 2.0, 3.0, 4.0]
    assert [p.speed for p in points] == [200.0, 210.0, 220.0, 230.0]


@pytest.mark.unit
def test_case_4_rejects_samples_exceeding_tolerance() -> None:
    t_loc = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    t_car = datetime(2026, 10, 5, 15, 30, 0, 600000, tzinfo=UTC)  # 600 ms > 500 ms default

    locations = [_make_location(t_loc)]
    car_data = [_make_car_data(t_car)]

    synchronizer = TelemetrySynchronizer(max_time_delta=DEFAULT_MAX_TIME_DELTA)
    points = synchronizer.synchronize(locations, car_data)

    assert points == []


@pytest.mark.unit
def test_case_5_empty_streams_returns_empty_list() -> None:
    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize([], [])

    assert points == []


@pytest.mark.unit
def test_case_6_only_locations_returns_empty_list() -> None:
    t0 = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    locations = [_make_location(t0)]

    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize(locations, [])

    assert points == []


@pytest.mark.unit
def test_case_7_only_car_data_returns_empty_list() -> None:
    t0 = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    car_data = [_make_car_data(t0)]

    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize([], car_data)

    assert points == []


@pytest.mark.unit
def test_case_8_chooses_closest_of_multiple_candidates() -> None:
    t_loc = datetime(2026, 10, 5, 15, 30, 0, 300000, tzinfo=UTC)  # 300 ms

    # Candidate A: 250 ms (diff: 50 ms)
    car_a = _make_car_data(
        datetime(2026, 10, 5, 15, 30, 0, 250000, tzinfo=UTC),
        speed=250.0,
    )
    # Candidate B: 320 ms (diff: 20 ms -> closer!)
    car_b = _make_car_data(
        datetime(2026, 10, 5, 15, 30, 0, 320000, tzinfo=UTC),
        speed=320.0,
    )
    # Candidate C: 400 ms (diff: 100 ms)
    car_c = _make_car_data(
        datetime(2026, 10, 5, 15, 30, 0, 400000, tzinfo=UTC),
        speed=400.0,
    )

    locations = [_make_location(t_loc)]
    car_data = [car_a, car_b, car_c]

    synchronizer = TelemetrySynchronizer()
    points = synchronizer.synchronize(locations, car_data)

    assert len(points) == 1
    # Candidate B must be chosen as it has the lowest absolute difference (20 ms vs 50 ms)
    assert points[0].speed == 320.0
