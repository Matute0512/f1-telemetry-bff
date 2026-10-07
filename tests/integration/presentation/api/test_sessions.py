from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    Session,
    SessionDetails,
)
from f1_telemetry_bff.main import app
from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_session_details_use_case,
)


class FakeGetSessionDetailsUseCase:
    """Fake use case that records execution parameters and returns preconfigured session details."""

    def __init__(self, details: SessionDetails | None = None) -> None:
        self.details = details
        self.executed = False
        self.received_session_key: int | None = None

    async def execute(self, session_key: int) -> SessionDetails | None:
        self.executed = True
        self.received_session_key = session_key
        return self.details


@pytest.fixture(autouse=True)
def clean_dependency_overrides() -> Generator[None, None, None]:
    """Ensure dependency overrides are always cleared after each test."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient instance for presentation integration tests."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.integration
def test_get_session_details_success(client: TestClient) -> None:
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

    fake_use_case = FakeGetSessionDetailsUseCase(details=details)
    app.dependency_overrides[get_get_session_details_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158")

    assert response.status_code == 200
    assert fake_use_case.executed is True
    assert fake_use_case.received_session_key == 9158

    payload = response.json()
    assert payload["session"] == {
        "session_key": 9158,
        "session_name": "Practice 1",
        "session_type": "Practice",
        "year": 2023,
    }
    assert payload["circuit"] == {
        "circuit_key": 61,
        "name": "Marina Bay Street Circuit",
        "country": "Singapore",
        "location": "Marina Bay",
    }
    assert payload["drivers"] == [
        {
            "driver_number": 1,
            "name": "Max Verstappen",
            "acronym": "VER",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
        }
    ]


@pytest.mark.integration
def test_get_session_details_not_found(client: TestClient) -> None:
    fake_use_case = FakeGetSessionDetailsUseCase(details=None)
    app.dependency_overrides[get_get_session_details_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9999")

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert fake_use_case.received_session_key == 9999
    assert response.json() == {"detail": "Session with key 9999 not found"}


@pytest.mark.integration
def test_get_session_details_invalid_session_key(client: TestClient) -> None:
    fake_use_case = FakeGetSessionDetailsUseCase()
    app.dependency_overrides[get_get_session_details_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/invalid_session")

    assert response.status_code == 422
    assert fake_use_case.executed is False
