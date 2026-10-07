from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    Session,
    SessionDetails,
)


def test_session_creation() -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )

    assert session.session_key == 9158
    assert session.session_name == "Practice 1"
    assert session.session_type == "Practice"
    assert session.year == 2023


def test_session_details_creation() -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    circuit = Circuit(
        circuit_key=61,
        name="Marina Bay Street Circuit",
        country="Singapore",
        location="Marina Bay",
    )
    driver = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )

    details = SessionDetails(
        session=session,
        circuit=circuit,
        drivers=[driver],
    )

    assert details.session == session
    assert details.circuit == circuit
    assert details.drivers == [driver]
