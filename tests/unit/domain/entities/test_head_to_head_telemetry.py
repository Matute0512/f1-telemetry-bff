from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.domain.entities import (
    Driver,
    HeadToHeadTelemetry,
    Lap,
    Session,
    TelemetryPoint,
)


def _make_telemetry_point(speed: float) -> TelemetryPoint:
    return TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=0.0,
        speed=speed,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )


def test_head_to_head_telemetry_creation() -> None:
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
        date_start="2023-09-15T10:00:00+00:00",
    )
    lap_b = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.876,
        date_start="2023-09-15T10:05:00+00:00",
    )
    telemetry_a = [_make_telemetry_point(310.0)]
    telemetry_b = [_make_telemetry_point(305.0)]

    h2h_telemetry = HeadToHeadTelemetry(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        telemetry_a=telemetry_a,
        driver_b=driver_b,
        lap_b=lap_b,
        telemetry_b=telemetry_b,
    )

    assert h2h_telemetry.session == session
    assert h2h_telemetry.driver_a == driver_a
    assert h2h_telemetry.lap_a == lap_a
    assert h2h_telemetry.telemetry_a == telemetry_a
    assert h2h_telemetry.driver_b == driver_b
    assert h2h_telemetry.lap_b == lap_b
    assert h2h_telemetry.telemetry_b == telemetry_b


def test_head_to_head_telemetry_is_immutable() -> None:
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
        date_start="2023-09-15T10:00:00+00:00",
    )
    lap_b = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.876,
        date_start="2023-09-15T10:05:00+00:00",
    )

    h2h_telemetry = HeadToHeadTelemetry(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        telemetry_a=[],
        driver_b=driver_b,
        lap_b=lap_b,
        telemetry_b=[],
    )

    with pytest.raises(AttributeError):
        h2h_telemetry.driver_a = driver_b  # type: ignore[misc]

