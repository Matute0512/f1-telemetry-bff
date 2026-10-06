from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from f1_telemetry_bff.domain.entities import TelemetryPoint
from f1_telemetry_bff.main import app
from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_lap_telemetry_use_case,
)


class FakeGetLapTelemetryUseCase:
    """Fake use case that records execution parameters and returns preconfigured telemetry points."""

    def __init__(self, points: list[TelemetryPoint] | None = None) -> None:
        self.points = points or []
        self.executed = False
        self.received_session_key: int | None = None
        self.received_driver_number: int | None = None
        self.received_lap_number: int | None = None

    async def execute(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        self.executed = True
        self.received_session_key = session_key
        self.received_driver_number = driver_number
        self.received_lap_number = lap_number
        return self.points


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
def test_get_lap_telemetry_success(client: TestClient) -> None:
    t1 = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    t2 = datetime(2026, 10, 5, 15, 30, 0, 250000, tzinfo=UTC)

    mocked_points = [
        TelemetryPoint(
            timestamp=t1,
            x=10.0,
            y=20.0,
            z=1.0,
            speed=310.0,
            throttle=100.0,
            brake=0.0,
            gear=8,
        ),
        TelemetryPoint(
            timestamp=t2,
            x=15.0,
            y=25.0,
            z=1.2,
            speed=312.5,
            throttle=98.0,
            brake=0.0,
            gear=8,
        ),
    ]

    fake_use_case = FakeGetLapTelemetryUseCase(points=mocked_points)
    app.dependency_overrides[get_get_lap_telemetry_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/drivers/1/laps/10/telemetry")

    assert response.status_code == 200
    assert fake_use_case.executed is True
    assert fake_use_case.received_session_key == 9158
    assert fake_use_case.received_driver_number == 1
    assert fake_use_case.received_lap_number == 10

    payload = response.json()
    assert payload["session_key"] == 9158
    assert payload["driver_number"] == 1
    assert payload["lap_number"] == 10

    points = payload["telemetry_points"]
    assert isinstance(points, list)
    assert len(points) == 2

    assert points[0]["timestamp"] == "2026-10-05T15:30:00Z"
    assert points[0]["x"] == 10.0
    assert points[0]["y"] == 20.0
    assert points[0]["z"] == 1.0
    assert points[0]["speed"] == 310.0
    assert points[0]["throttle"] == 100.0
    assert points[0]["brake"] == 0.0
    assert points[0]["gear"] == 8

    assert points[1]["timestamp"] == "2026-10-05T15:30:00.250000Z"
    assert points[1]["x"] == 15.0
    assert points[1]["y"] == 25.0
    assert points[1]["z"] == 1.2
    assert points[1]["speed"] == 312.5
    assert points[1]["throttle"] == 98.0
    assert points[1]["brake"] == 0.0
    assert points[1]["gear"] == 8


@pytest.mark.integration
def test_get_lap_telemetry_empty_points(client: TestClient) -> None:
    fake_use_case = FakeGetLapTelemetryUseCase(points=[])
    app.dependency_overrides[get_get_lap_telemetry_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/drivers/1/laps/10/telemetry")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_key"] == 9158
    assert payload["driver_number"] == 1
    assert payload["lap_number"] == 10
    assert payload["telemetry_points"] == []


@pytest.mark.integration
def test_get_lap_telemetry_invalid_session_key(client: TestClient) -> None:
    fake_use_case = FakeGetLapTelemetryUseCase()
    app.dependency_overrides[get_get_lap_telemetry_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/invalid_session/drivers/1/laps/10/telemetry")

    assert response.status_code == 422
    assert fake_use_case.executed is False


@pytest.mark.integration
def test_get_lap_telemetry_invalid_driver_number(client: TestClient) -> None:
    fake_use_case = FakeGetLapTelemetryUseCase()
    app.dependency_overrides[get_get_lap_telemetry_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/drivers/invalid_driver/laps/10/telemetry")

    assert response.status_code == 422
    assert fake_use_case.executed is False


@pytest.mark.integration
def test_get_lap_telemetry_invalid_lap_number(client: TestClient) -> None:
    fake_use_case = FakeGetLapTelemetryUseCase()
    app.dependency_overrides[get_get_lap_telemetry_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/drivers/1/laps/invalid_lap/telemetry")

    assert response.status_code == 422
    assert fake_use_case.executed is False
