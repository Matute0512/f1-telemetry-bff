from f1_telemetry_bff.application.dto import (
    DriverDTO,
    HeadToHeadSelectionDTO,
    SessionDTO,
)
from f1_telemetry_bff.presentation.api.schemas.mappers import (
    head_to_head_selection_dto_to_response,
)


def test_head_to_head_selection_dto_to_response_maps_all_fields() -> None:
    dto = HeadToHeadSelectionDTO(
        session=SessionDTO(
            session_key=9158,
            session_name="Practice 1",
            session_type="Practice",
            year=2023,
        ),
        driver_a=DriverDTO(
            driver_number=1,
            name="Max Verstappen",
            acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        ),
        driver_b=DriverDTO(
            driver_number=44,
            name="Lewis Hamilton",
            acronym="HAM",
            team_name="Mercedes",
            team_colour="00D2BE",
        ),
    )

    response = head_to_head_selection_dto_to_response(dto)

    assert response.session.session_key == 9158
    assert response.session.session_name == "Practice 1"
    assert response.driver_a.driver_number == 1
    assert response.driver_a.name == "Max Verstappen"
    assert response.driver_b.driver_number == 44
    assert response.driver_b.name == "Lewis Hamilton"


def test_head_to_head_lap_selection_dto_to_response_maps_all_fields() -> None:
    from f1_telemetry_bff.application.dto import (
        HeadToHeadLapSelectionDTO,
        LapDTO,
    )
    from f1_telemetry_bff.presentation.api.schemas.mappers import (
        head_to_head_lap_selection_dto_to_response,
    )

    dto = HeadToHeadLapSelectionDTO(
        session=SessionDTO(
            session_key=9158,
            session_name="Practice 1",
            session_type="Practice",
            year=2023,
        ),
        driver_a=DriverDTO(
            driver_number=1,
            name="Max Verstappen",
            acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        ),
        lap_a=LapDTO(
            lap_number=10,
            driver_number=1,
            lap_time=92.123,
            date_start="2023-09-15T10:00:00+00:00",
        ),
        driver_b=DriverDTO(
            driver_number=44,
            name="Lewis Hamilton",
            acronym="HAM",
            team_name="Mercedes",
            team_colour="00D2BE",
        ),
        lap_b=LapDTO(
            lap_number=12,
            driver_number=44,
            lap_time=91.876,
            date_start="2023-09-15T10:05:00+00:00",
        ),
    )

    response = head_to_head_lap_selection_dto_to_response(dto)

    assert response.session.session_key == 9158
    assert response.driver_a.driver_number == 1
    assert response.lap_a.lap_number == 10
    assert response.lap_a.lap_time == 92.123
    assert response.driver_b.driver_number == 44
    assert response.lap_b.lap_number == 12
    assert response.lap_b.lap_time == 91.876


def test_head_to_head_telemetry_dto_to_response_maps_all_fields() -> None:
    from datetime import UTC, datetime

    from f1_telemetry_bff.application.dto import (
        HeadToHeadTelemetryDTO,
        LapDTO,
        TelemetryPointDTO,
    )
    from f1_telemetry_bff.presentation.api.schemas.mappers import (
        head_to_head_telemetry_dto_to_response,
    )

    point_a = TelemetryPointDTO(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=0.0,
        speed=310.0,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )
    point_b = TelemetryPointDTO(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
        x=15.0,
        y=25.0,
        z=0.0,
        speed=305.0,
        throttle=95.0,
        brake=0.0,
        gear=7,
    )
    dto = HeadToHeadTelemetryDTO(
        session=SessionDTO(
            session_key=9158,
            session_name="Practice 1",
            session_type="Practice",
            year=2023,
        ),
        driver_a=DriverDTO(
            driver_number=1,
            name="Max Verstappen",
            acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        ),
        lap_a=LapDTO(
            lap_number=10,
            driver_number=1,
            lap_time=92.123,
            date_start="2023-09-15T10:00:00+00:00",
        ),
        telemetry_a=[point_a],
        driver_b=DriverDTO(
            driver_number=44,
            name="Lewis Hamilton",
            acronym="HAM",
            team_name="Mercedes",
            team_colour="00D2BE",
        ),
        lap_b=LapDTO(
            lap_number=12,
            driver_number=44,
            lap_time=91.876,
            date_start="2023-09-15T10:05:00+00:00",
        ),
        telemetry_b=[point_b],
    )

    response = head_to_head_telemetry_dto_to_response(dto)

    assert response.session.session_key == 9158
    assert response.driver_a.driver_number == 1
    assert response.lap_a.lap_number == 10
    assert len(response.telemetry_a) == 1
    assert response.telemetry_a[0].speed == 310.0
    assert response.driver_b.driver_number == 44
    assert response.lap_b.lap_number == 12
    assert len(response.telemetry_b) == 1
    assert response.telemetry_b[0].speed == 305.0
