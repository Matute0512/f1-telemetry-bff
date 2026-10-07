from f1_telemetry_bff.application.dto.mappers import (
    circuit_to_dto,
    driver_to_dto,
    session_details_to_dto,
    session_to_dto,
)
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    Session,
    SessionDetails,
)


def test_session_to_dto_maps_all_fields() -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )

    dto = session_to_dto(session)

    assert dto.session_key == 9158
    assert dto.session_name == "Practice 1"
    assert dto.session_type == "Practice"
    assert dto.year == 2023


def test_circuit_to_dto_maps_all_fields() -> None:
    circuit = Circuit(
        circuit_key=61,
        name="Marina Bay Street Circuit",
        country="Singapore",
        location="Marina Bay",
    )

    dto = circuit_to_dto(circuit)

    assert dto.circuit_key == 61
    assert dto.name == "Marina Bay Street Circuit"
    assert dto.country == "Singapore"
    assert dto.location == "Marina Bay"


def test_driver_to_dto_maps_all_fields() -> None:
    driver = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )

    dto = driver_to_dto(driver)

    assert dto.driver_number == 1
    assert dto.name == "Max Verstappen"
    assert dto.acronym == "VER"
    assert dto.team_name == "Red Bull Racing"
    assert dto.team_colour == "3671C6"


def test_session_details_to_dto_maps_nested_structure() -> None:
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

    dto = session_details_to_dto(details)

    assert dto.session.session_key == 9158
    assert dto.circuit.circuit_key == 61
    assert len(dto.drivers) == 1
    assert dto.drivers[0].driver_number == 1
