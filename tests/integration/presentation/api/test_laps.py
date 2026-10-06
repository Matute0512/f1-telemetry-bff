from collections.abc import Generator
from datetime import UTC, datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from f1_telemetry_bff.domain.entities import Lap
from f1_telemetry_bff.main import app
from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_session_laps_use_case,
)


class FakeGetSessionLapsUseCase:
    """Fake use case that records execution parameters and returns preconfigured laps."""

    def __init__(self, laps: list[Lap] | None = None) -> None:
        self.laps = laps or []
        self.executed = False
        self.received_session_key: int | None = None
        self.received_driver_number: int | None = None

    async def execute(self, session_key: int, driver_number: int) -> list[Lap]:
        self.executed = True
        self.received_session_key = session_key
        self.received_driver_number = driver_number
        return self.laps


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
def test_get_session_laps_success(client: TestClient) -> None:
    date_start_1 = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    date_start_2 = datetime(2026, 10, 5, 15, 31, 30, tzinfo=UTC)

    mocked_laps = [
        Lap(
            lap_number=1,
            driver_number=1,
            lap_time=82.456,
            date_start=date_start_1,
        ),
        Lap(
            lap_number=2,
            driver_number=1,
            lap_time=81.123,
            date_start=date_start_2,
        ),
    ]

    fake_use_case = FakeGetSessionLapsUseCase(laps=mocked_laps)
    app.dependency_overrides[get_get_session_laps_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/drivers/1/laps")

    assert response.status_code == 200
    assert fake_use_case.executed is True
    assert fake_use_case.received_session_key == 9158
    assert fake_use_case.received_driver_number == 1

    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 2

    assert payload[0]["lap_number"] == 1
    assert payload[0]["driver_number"] == 1
    assert payload[0]["lap_time"] == 82.456
    assert payload[0]["date_start"] == "2026-10-05T15:30:00Z"

    assert payload[1]["lap_number"] == 2
    assert payload[1]["driver_number"] == 1
    assert payload[1]["lap_time"] == 81.123
    assert payload[1]["date_start"] == "2026-10-05T15:31:30Z"


@pytest.mark.integration
def test_get_session_laps_invalid_session_key(client: TestClient) -> None:
    fake_use_case = FakeGetSessionLapsUseCase()
    app.dependency_overrides[get_get_session_laps_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/invalid_session/drivers/1/laps")

    assert response.status_code == 422
    assert fake_use_case.executed is False


@pytest.mark.integration
def test_get_session_laps_invalid_driver_number(client: TestClient) -> None:
    fake_use_case = FakeGetSessionLapsUseCase()
    app.dependency_overrides[get_get_session_laps_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/drivers/invalid_driver/laps")

    assert response.status_code == 422
    assert fake_use_case.executed is False


@pytest.mark.integration
def test_app_lifespan_initializes_shared_http_client(client: TestClient) -> None:
    assert hasattr(app.state, "http_client")
    assert isinstance(app.state.http_client, httpx.AsyncClient)
    assert app.state.http_client.is_closed is False
