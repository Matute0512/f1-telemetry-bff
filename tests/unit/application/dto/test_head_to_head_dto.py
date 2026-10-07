from f1_telemetry_bff.application.dto.mappers import (
    head_to_head_selection_to_dto,
)
from f1_telemetry_bff.domain.entities import (
    Driver,
    HeadToHeadSelection,
    Session,
)


def test_head_to_head_selection_to_dto_maps_all_fields() -> None:
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
    selection = HeadToHeadSelection(
        session=session,
        driver_a=driver_a,
        driver_b=driver_b,
    )

    dto = head_to_head_selection_to_dto(selection)

    assert dto.session.session_key == 9158
    assert dto.session.session_name == "Practice 1"
    assert dto.driver_a.driver_number == 1
    assert dto.driver_a.name == "Max Verstappen"
    assert dto.driver_b.driver_number == 44
    assert dto.driver_b.name == "Lewis Hamilton"


def test_head_to_head_lap_selection_to_dto_maps_all_fields() -> None:
    from f1_telemetry_bff.application.dto.mappers import (
        head_to_head_lap_selection_to_dto,
    )
    from f1_telemetry_bff.domain.entities import (
        HeadToHeadLapSelection,
        Lap,
    )

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

    dto = head_to_head_lap_selection_to_dto(selection)

    assert dto.session.session_key == 9158
    assert dto.driver_a.driver_number == 1
    assert dto.lap_a.lap_number == 10
    assert dto.lap_a.lap_time == 92.123
    assert dto.driver_b.driver_number == 44
    assert dto.lap_b.lap_number == 12
    assert dto.lap_b.lap_time == 91.876


def test_head_to_head_telemetry_to_dto_maps_all_fields() -> None:
    from datetime import UTC, datetime

    from f1_telemetry_bff.application.dto.mappers import (
        head_to_head_telemetry_to_dto,
    )
    from f1_telemetry_bff.domain.entities import (
        HeadToHeadTelemetry,
        Lap,
        TelemetryPoint,
    )

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
    point_a = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=0.0,
        speed=310.0,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )
    point_b = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
        x=15.0,
        y=25.0,
        z=0.0,
        speed=305.0,
        throttle=95.0,
        brake=0.0,
        gear=7,
    )
    h2h_telemetry = HeadToHeadTelemetry(
        session=session,
        driver_a=driver_a,
        lap_a=lap_a,
        telemetry_a=[point_a],
        driver_b=driver_b,
        lap_b=lap_b,
        telemetry_b=[point_b],
    )

    dto = head_to_head_telemetry_to_dto(h2h_telemetry)

    assert dto.session.session_key == 9158
    assert dto.driver_a.driver_number == 1
    assert dto.lap_a.lap_number == 10
    assert len(dto.telemetry_a) == 1
    assert dto.telemetry_a[0].speed == 310.0
    assert dto.driver_b.driver_number == 44
    assert dto.lap_b.lap_number == 12
    assert len(dto.telemetry_b) == 1
    assert dto.telemetry_b[0].speed == 305.0
