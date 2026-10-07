import pytest

from f1_telemetry_bff.domain.entities import (
    Driver,
    HeadToHeadLapSelection,
    Lap,
    Session,
)


def test_head_to_head_lap_selection_creation() -> None:
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

    selection = HeadToHeadLapSelection(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        driver_b=driver_b,
        lap_b=lap_b,
    )

    assert selection.session == session
    assert selection.driver_a == driver_a
    assert selection.lap_a == lap_a
    assert selection.driver_b == driver_b
    assert selection.lap_b == lap_b


def test_head_to_head_lap_selection_is_immutable() -> None:
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

    selection = HeadToHeadLapSelection(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        driver_b=driver_b,
        lap_b=lap_b,
    )

    with pytest.raises(AttributeError):
        selection.lap_a = lap_b  # type: ignore[misc]
