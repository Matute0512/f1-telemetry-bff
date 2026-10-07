from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.domain.entities import (
    Driver,
    HeadToHeadLapSelection,
    HeadToHeadSelection,
    Lap,
    Session,
)
from f1_telemetry_bff.main import app
from f1_telemetry_bff.presentation.api.dependencies import (
    get_select_head_to_head_drivers_use_case,
    get_select_head_to_head_laps_use_case,
)


class FakeSelectHeadToHeadDriversUseCase:
    """Fake use case that records execution parameters and returns or raises preconfigured values."""

    def __init__(
        self,
        selection: HeadToHeadSelection | None = None,
        exception_to_raise: Exception | None = None,
    ) -> None:
        self.selection = selection
        self.exception_to_raise = exception_to_raise
        self.executed = False
        self.received_session_key: int | None = None
        self.received_driver_a: int | None = None
        self.received_driver_b: int | None = None

    async def execute(
        self,
        session_key: int,
        driver_a_number: int,
        driver_b_number: int,
    ) -> HeadToHeadSelection:
        self.executed = True
        self.received_session_key = session_key
        self.received_driver_a = driver_a_number
        self.received_driver_b = driver_b_number
        if self.exception_to_raise:
            raise self.exception_to_raise
        assert self.selection is not None
        return self.selection


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
def test_select_head_to_head_drivers_success(client: TestClient) -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    driver_1 = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    driver_44 = Driver(
        driver_number=44,
        name="Lewis Hamilton",
        acronym="HAM",
        team_name="Mercedes",
        team_colour="00D2BE",
    )
    selection = HeadToHeadSelection(
        session=session,
        driver_a=driver_1,
        driver_b=driver_44,
    )

    fake_use_case = FakeSelectHeadToHeadDriversUseCase(selection=selection)
    app.dependency_overrides[get_select_head_to_head_drivers_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/head-to-head?driver_a=1&driver_b=44")

    assert response.status_code == 200
    assert fake_use_case.executed is True
    assert fake_use_case.received_session_key == 9158
    assert fake_use_case.received_driver_a == 1
    assert fake_use_case.received_driver_b == 44

    payload = response.json()
    assert payload["session"] == {
        "session_key": 9158,
        "session_name": "Practice 1",
        "session_type": "Practice",
        "year": 2023,
    }
    assert payload["driver_a"] == {
        "driver_number": 1,
        "name": "Max Verstappen",
        "acronym": "VER",
        "team_name": "Red Bull Racing",
        "team_colour": "3671C6",
    }
    assert payload["driver_b"] == {
        "driver_number": 44,
        "name": "Lewis Hamilton",
        "acronym": "HAM",
        "team_name": "Mercedes",
        "team_colour": "00D2BE",
    }


@pytest.mark.integration
def test_select_head_to_head_drivers_same_driver_returns_400(
    client: TestClient,
) -> None:
    fake_use_case = FakeSelectHeadToHeadDriversUseCase(
        exception_to_raise=SameDriverSelectedError(driver_number=1)
    )
    app.dependency_overrides[get_select_head_to_head_drivers_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/head-to-head?driver_a=1&driver_b=1")

    assert response.status_code == 400
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Driver A and Driver B cannot be the same driver (1)"


@pytest.mark.integration
def test_select_head_to_head_drivers_session_not_found_returns_404(
    client: TestClient,
) -> None:
    fake_use_case = FakeSelectHeadToHeadDriversUseCase(
        exception_to_raise=SessionNotFoundError(session_key=9999)
    )
    app.dependency_overrides[get_select_head_to_head_drivers_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9999/head-to-head?driver_a=1&driver_b=44")

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Session with key 9999 not found"


@pytest.mark.integration
def test_select_head_to_head_drivers_driver_a_not_found_returns_404(
    client: TestClient,
) -> None:
    fake_use_case = FakeSelectHeadToHeadDriversUseCase(
        exception_to_raise=DriverNotFoundError(driver_number=99, session_key=9158)
    )
    app.dependency_overrides[get_select_head_to_head_drivers_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/head-to-head?driver_a=99&driver_b=44")

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Driver 99 not found in session 9158"


@pytest.mark.integration
def test_select_head_to_head_drivers_driver_b_not_found_returns_404(
    client: TestClient,
) -> None:
    fake_use_case = FakeSelectHeadToHeadDriversUseCase(
        exception_to_raise=DriverNotFoundError(driver_number=88, session_key=9158)
    )
    app.dependency_overrides[get_select_head_to_head_drivers_use_case] = lambda: fake_use_case

    response = client.get("/api/v1/sessions/9158/head-to-head?driver_a=1&driver_b=88")

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Driver 88 not found in session 9158"


@pytest.mark.integration
def test_select_head_to_head_drivers_missing_query_param_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/sessions/9158/head-to-head?driver_a=1")
    assert response.status_code == 422


@pytest.mark.integration
def test_select_head_to_head_drivers_invalid_query_param_type_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/sessions/9158/head-to-head?driver_a=abc&driver_b=44")
    assert response.status_code == 422


@pytest.mark.integration
def test_select_head_to_head_drivers_invalid_session_key_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/sessions/invalid_session/head-to-head?driver_a=1&driver_b=44")
    assert response.status_code == 422


class FakeSelectHeadToHeadLapsUseCase:
    """Fake use case for Head-to-Head lap selection."""

    def __init__(
        self,
        selection: HeadToHeadLapSelection | None = None,
        exception_to_raise: Exception | None = None,
    ) -> None:
        self.selection = selection
        self.exception_to_raise = exception_to_raise
        self.executed = False
        self.received_session_key: int | None = None
        self.received_driver_a: int | None = None
        self.received_lap_a: int | None = None
        self.received_driver_b: int | None = None
        self.received_lap_b: int | None = None

    async def execute(
        self,
        session_key: int,
        driver_a_number: int,
        lap_a_number: int,
        driver_b_number: int,
        lap_b_number: int,
    ) -> HeadToHeadLapSelection:
        self.executed = True
        self.received_session_key = session_key
        self.received_driver_a = driver_a_number
        self.received_lap_a = lap_a_number
        self.received_driver_b = driver_b_number
        self.received_lap_b = lap_b_number
        if self.exception_to_raise:
            raise self.exception_to_raise
        assert self.selection is not None
        return self.selection


@pytest.mark.integration
def test_select_head_to_head_laps_success(client: TestClient) -> None:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    driver_1 = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    driver_44 = Driver(
        driver_number=44,
        name="Lewis Hamilton",
        acronym="HAM",
        team_name="Mercedes",
        team_colour="00D2BE",
    )
    lap_10 = Lap(
        lap_number=10,
        driver_number=1,
        lap_time=92.123,
        date_start="2023-09-15T10:00:00+00:00",
    )
    lap_12 = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.876,
        date_start="2023-09-15T10:05:00+00:00",
    )
    selection = HeadToHeadLapSelection(
        session=session,
        driver_a=driver_1,
        lap_a=lap_10,
        driver_b=driver_44,
        lap_b=lap_12,
    )

    fake_use_case = FakeSelectHeadToHeadLapsUseCase(selection=selection)
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=10&driver_b=44&lap_b=12"
    )

    assert response.status_code == 200
    assert fake_use_case.executed is True
    assert fake_use_case.received_session_key == 9158
    assert fake_use_case.received_driver_a == 1
    assert fake_use_case.received_lap_a == 10
    assert fake_use_case.received_driver_b == 44
    assert fake_use_case.received_lap_b == 12

    payload = response.json()
    assert payload["session"] == {
        "session_key": 9158,
        "session_name": "Practice 1",
        "session_type": "Practice",
        "year": 2023,
    }
    assert payload["driver_a"] == {
        "driver_number": 1,
        "name": "Max Verstappen",
        "acronym": "VER",
        "team_name": "Red Bull Racing",
        "team_colour": "3671C6",
    }
    assert payload["lap_a"] == {
        "lap_number": 10,
        "driver_number": 1,
        "lap_time": 92.123,
        "date_start": "2023-09-15T10:00:00Z",
    }
    assert payload["driver_b"] == {
        "driver_number": 44,
        "name": "Lewis Hamilton",
        "acronym": "HAM",
        "team_name": "Mercedes",
        "team_colour": "00D2BE",
    }
    assert payload["lap_b"] == {
        "lap_number": 12,
        "driver_number": 44,
        "lap_time": 91.876,
        "date_start": "2023-09-15T10:05:00Z",
    }


@pytest.mark.integration
def test_select_head_to_head_laps_same_driver_returns_400(client: TestClient) -> None:
    fake_use_case = FakeSelectHeadToHeadLapsUseCase(
        exception_to_raise=SameDriverSelectedError(driver_number=1)
    )
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=10&driver_b=1&lap_b=12"
    )

    assert response.status_code == 400
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Driver A and Driver B cannot be the same driver (1)"


@pytest.mark.integration
def test_select_head_to_head_laps_session_not_found_returns_404(client: TestClient) -> None:
    fake_use_case = FakeSelectHeadToHeadLapsUseCase(
        exception_to_raise=SessionNotFoundError(session_key=9999)
    )
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9999/head-to-head/laps?driver_a=1&lap_a=10&driver_b=44&lap_b=12"
    )

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Session with key 9999 not found"


@pytest.mark.integration
def test_select_head_to_head_laps_driver_a_not_found_returns_404(client: TestClient) -> None:
    fake_use_case = FakeSelectHeadToHeadLapsUseCase(
        exception_to_raise=DriverNotFoundError(driver_number=99, session_key=9158)
    )
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=99&lap_a=10&driver_b=44&lap_b=12"
    )

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Driver 99 not found in session 9158"


@pytest.mark.integration
def test_select_head_to_head_laps_driver_b_not_found_returns_404(client: TestClient) -> None:
    fake_use_case = FakeSelectHeadToHeadLapsUseCase(
        exception_to_raise=DriverNotFoundError(driver_number=88, session_key=9158)
    )
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=10&driver_b=88&lap_b=12"
    )

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert response.json()["detail"] == "Driver 88 not found in session 9158"


@pytest.mark.integration
def test_select_head_to_head_laps_lap_a_not_found_returns_404(client: TestClient) -> None:
    from f1_telemetry_bff.application.exceptions import LapNotFoundError

    fake_use_case = FakeSelectHeadToHeadLapsUseCase(
        exception_to_raise=LapNotFoundError(session_key=9158, driver_number=1, lap_number=99)
    )
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=99&driver_b=44&lap_b=12"
    )

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert (
        response.json()["detail"] == "Lap 99 not found or incomplete for driver 1 in session 9158"
    )


@pytest.mark.integration
def test_select_head_to_head_laps_lap_b_not_found_returns_404(client: TestClient) -> None:
    from f1_telemetry_bff.application.exceptions import LapNotFoundError

    fake_use_case = FakeSelectHeadToHeadLapsUseCase(
        exception_to_raise=LapNotFoundError(session_key=9158, driver_number=44, lap_number=99)
    )
    app.dependency_overrides[get_select_head_to_head_laps_use_case] = lambda: fake_use_case

    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=10&driver_b=44&lap_b=99"
    )

    assert response.status_code == 404
    assert fake_use_case.executed is True
    assert (
        response.json()["detail"] == "Lap 99 not found or incomplete for driver 44 in session 9158"
    )


@pytest.mark.integration
def test_select_head_to_head_laps_missing_query_param_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=10&driver_b=44")
    assert response.status_code == 422


@pytest.mark.integration
def test_select_head_to_head_laps_invalid_query_param_type_returns_422(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/sessions/9158/head-to-head/laps?driver_a=1&lap_a=abc&driver_b=44&lap_b=12"
    )
    assert response.status_code == 422
