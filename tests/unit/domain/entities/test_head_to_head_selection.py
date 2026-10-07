from f1_telemetry_bff.domain.entities import (
    Driver,
    HeadToHeadSelection,
    Session,
)


def test_head_to_head_selection_creation() -> None:
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

    assert selection.session == session
    assert selection.driver_a == driver_a
    assert selection.driver_b == driver_b

