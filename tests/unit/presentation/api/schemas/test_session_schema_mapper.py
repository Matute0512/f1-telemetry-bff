import pytest

from f1_telemetry_bff.application.dto import (
    CircuitDTO,
    DriverDTO,
    SessionDetailsDTO,
    SessionDTO,
)
from f1_telemetry_bff.presentation.api.schemas.mappers import (
    circuit_dto_to_response,
    driver_dto_to_response,
    session_details_dto_to_response,
    session_info_dto_to_response,
)


@pytest.mark.unit
def test_session_info_dto_to_response_maps_all_fields() -> None:
    dto = SessionDTO(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )

    response = session_info_dto_to_response(dto)

    assert response.session_key == 9158
    assert response.session_name == "Practice 1"
    assert response.session_type == "Practice"
    assert response.year == 2023


@pytest.mark.unit
def test_circuit_dto_to_response_maps_all_fields() -> None:
    dto = CircuitDTO(
        circuit_key=61,
        name="Marina Bay Street Circuit",
        country="Singapore",
        location="Marina Bay",
    )

    response = circuit_dto_to_response(dto)

    assert response.circuit_key == 61
    assert response.name == "Marina Bay Street Circuit"
    assert response.country == "Singapore"
    assert response.location == "Marina Bay"


@pytest.mark.unit
def test_driver_dto_to_response_maps_all_fields() -> None:
    dto = DriverDTO(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )

    response = driver_dto_to_response(dto)

    assert response.driver_number == 1
    assert response.name == "Max Verstappen"
    assert response.acronym == "VER"
    assert response.team_name == "Red Bull Racing"
    assert response.team_colour == "3671C6"


@pytest.mark.unit
def test_session_details_dto_to_response_maps_all_fields() -> None:
    session_dto = SessionDTO(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    circuit_dto = CircuitDTO(
        circuit_key=61,
        name="Marina Bay Street Circuit",
        country="Singapore",
        location="Marina Bay",
    )
    driver_dto = DriverDTO(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    details_dto = SessionDetailsDTO(
        session=session_dto,
        circuit=circuit_dto,
        drivers=[driver_dto],
    )

    response = session_details_dto_to_response(details_dto)

    assert response.session.session_key == 9158
    assert response.circuit.circuit_key == 61
    assert len(response.drivers) == 1
    assert response.drivers[0].driver_number == 1
