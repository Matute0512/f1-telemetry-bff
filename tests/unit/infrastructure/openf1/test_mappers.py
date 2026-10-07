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


def test_map_openf1_session_and_circuit() -> None:
    from f1_telemetry_bff.infrastructure.openf1.mappers import map_circuit, map_session
    from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Session

    openf1_session = OpenF1Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
        circuit_key=61,
        circuit_short_name="Marina Bay",
        country_name="Singapore",
        location="Marina Bay",
    )

    session = map_session(openf1_session)
    circuit = map_circuit(openf1_session)

    assert session.session_key == 9158
    assert session.session_name == "Practice 1"
    assert session.session_type == "Practice"
    assert session.year == 2023

    assert circuit.circuit_key == 61
    assert circuit.name == "Marina Bay"
    assert circuit.country == "Singapore"
    assert circuit.location == "Marina Bay"


def test_map_openf1_driver() -> None:
    from f1_telemetry_bff.infrastructure.openf1.mappers import map_driver
    from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Driver

    openf1_driver = OpenF1Driver(
        session_key=9158,
        driver_number=1,
        full_name="Max Verstappen",
        name_acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )

    driver = map_driver(openf1_driver)

    assert driver.driver_number == 1
    assert driver.name == "Max Verstappen"
    assert driver.acronym == "VER"
    assert driver.team_name == "Red Bull Racing"
    assert driver.team_colour == "3671C6"
