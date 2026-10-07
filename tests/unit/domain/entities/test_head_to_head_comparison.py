from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.domain.entities import (
    Driver,
    HeadToHeadComparison,
    Lap,
    Session,
)
from f1_telemetry_bff.domain.value_objects import ComparisonPoint


def _make_comparison_point(distance: float) -> ComparisonPoint:
    return ComparisonPoint(
        distance=distance,
        elapsed_time_a=10.0,
        elapsed_time_b=10.2,
        time_delta=-0.2,
        speed_a=300.0,
        speed_b=295.0,
        speed_delta=5.0,
        throttle_a=100.0,
        throttle_b=95.0,
        throttle_delta=5.0,
        brake_a=0.0,
        brake_b=0.0,
        brake_delta=0.0,
        gear_a=7,
        gear_b=7,
    )


def test_head_to_head_comparison_creation() -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    driver_a = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    driver_b = Driver(
        driver_number=44,
        name="Lewis Hamilton",
        acronym="HAM",
        team_name="Mercedes",
        team_colour="00D2BE",
    )
    lap_a = Lap(
        lap_number=10,
        driver_number=1,
        lap_time=92.123,
        date_start=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
    )
    lap_b = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.876,
        date_start=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
    )
    points = [_make_comparison_point(0.0), _make_comparison_point(10.0)]

    comparison = HeadToHeadComparison(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        driver_b=driver_b,
        lap_b=lap_b,
        total_distance=10.0,
        points=points,
    )

    assert comparison.session == session
    assert comparison.driver_a == driver_a
    assert comparison.lap_a == lap_a
    assert comparison.driver_b == driver_b
    assert comparison.lap_b == lap_b
    assert comparison.total_distance == 10.0
    assert comparison.points == points


def test_head_to_head_comparison_is_immutable() -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    driver_a = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    driver_b = Driver(
        driver_number=44,
        name="Lewis Hamilton",
        acronym="HAM",
        team_name="Mercedes",
        team_colour="00D2BE",
    )
    lap_a = Lap(
        lap_number=10,
        driver_number=1,
        lap_time=92.123,
        date_start=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
    )
    lap_b = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.876,
        date_start=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
    )

    comparison = HeadToHeadComparison(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        driver_b=driver_b,
        lap_b=lap_b,
        total_distance=10.0,
        points=[_make_comparison_point(0.0)],
    )

    with pytest.raises(AttributeError):
        comparison.total_distance = 20.0  # type: ignore[misc]
