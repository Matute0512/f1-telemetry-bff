from unittest.mock import AsyncMock

import pytest

from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    LapNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.application.use_cases import (
    SelectHeadToHeadLapsUseCase,
)
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    HeadToHeadLapSelection,
    Lap,
    Session,
    SessionDetails,
    TelemetryPoint,
)
from f1_telemetry_bff.domain.ports import SessionRepository, TelemetryRepository


class FakeSessionRepository(SessionRepository):
    def __init__(self, details: SessionDetails | None = None) -> None:
        self.details = details
        self.received_session_key: int | None = None

    async def get_session_details(self, session_key: int) -> SessionDetails | None:
        self.received_session_key = session_key
        return self.details


class FakeTelemetryRepository(TelemetryRepository):
    def __init__(self, laps_by_driver: dict[int, list[Lap]] | None = None) -> None:
        self.laps_by_driver = laps_by_driver or {}
        self.received_calls: list[tuple[int, int]] = []

    async def get_laps(self, session_key: int, driver_number: int) -> list[Lap]:
        self.received_calls.append((session_key, driver_number))
        return self.laps_by_driver.get(driver_number, [])

    async def get_telemetry(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        return []

    async def get_telemetry_for_lap(
        self,
        session_key: int,
        driver_number: int,
        lap: Lap,
    ) -> list[TelemetryPoint]:
        return []


def _make_session_details() -> tuple[SessionDetails, Driver, Driver]:
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
    details = SessionDetails(
        session=session,
        circuit=circuit,
        drivers=[driver_1, driver_44],
    )
    return details, driver_1, driver_44


def _make_laps() -> tuple[Lap, Lap]:
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
    return lap_a, lap_b


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_success() -> None:
    details, driver_1, driver_44 = _make_session_details()
    lap_a, lap_b = _make_laps()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={
            1: [lap_a],
            44: [lap_b],
        }
    )
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert isinstance(result, HeadToHeadLapSelection)
    assert result.session == details.session
    assert result.driver_a == driver_1
    assert result.lap_a == lap_a
    assert result.driver_b == driver_44
    assert result.lap_b == lap_b
    assert session_repo.received_session_key == 9158
    assert (9158, 1) in telemetry_repo.received_calls
    assert (9158, 44) in telemetry_repo.received_calls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_same_lap_number_different_drivers_success() -> None:
    details, _, _ = _make_session_details()
    lap_a = Lap(
        lap_number=10,
        driver_number=1,
        lap_time=92.123,
        date_start="2023-09-15T10:00:00+00:00",
    )
    lap_b = Lap(
        lap_number=10,
        driver_number=44,
        lap_time=91.876,
        date_start="2023-09-15T10:05:00+00:00",
    )
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={
            1: [lap_a],
            44: [lap_b],
        }
    )
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=10,
    )

    assert result.lap_a.lap_number == 10
    assert result.lap_b.lap_number == 10
    assert result.lap_a.driver_number == 1
    assert result.lap_b.driver_number == 44


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_same_driver_raises_error() -> None:
    details, _, _ = _make_session_details()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository()
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    with pytest.raises(SameDriverSelectedError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=1,
            lap_b_number=12,
        )

    assert exc_info.value.driver_number == 1
    assert len(telemetry_repo.received_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_session_not_found_raises_error() -> None:
    session_repo = FakeSessionRepository(details=None)
    telemetry_repo = FakeTelemetryRepository()
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    with pytest.raises(SessionNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9999,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=44,
            lap_b_number=12,
        )

    assert exc_info.value.session_key == 9999
    assert len(telemetry_repo.received_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_driver_a_not_found_raises_error() -> None:
    details, _, _ = _make_session_details()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository()
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    with pytest.raises(DriverNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=99,
            lap_a_number=10,
            driver_b_number=44,
            lap_b_number=12,
        )

    assert exc_info.value.driver_number == 99
    assert exc_info.value.session_key == 9158
    assert len(telemetry_repo.received_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_driver_b_not_found_raises_error() -> None:
    details, _, _ = _make_session_details()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository()
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    with pytest.raises(DriverNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=99,
            lap_b_number=12,
        )

    assert exc_info.value.driver_number == 99
    assert exc_info.value.session_key == 9158
    assert len(telemetry_repo.received_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_lap_a_not_found_raises_error() -> None:
    details, _, _ = _make_session_details()
    _, lap_b = _make_laps()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={
            1: [],
            44: [lap_b],
        }
    )
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    with pytest.raises(LapNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=44,
            lap_b_number=12,
        )

    assert exc_info.value.session_key == 9158
    assert exc_info.value.driver_number == 1
    assert exc_info.value.lap_number == 10


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_lap_b_not_found_raises_error() -> None:
    details, _, _ = _make_session_details()
    lap_a, _ = _make_laps()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={
            1: [lap_a],
            44: [],
        }
    )
    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )

    with pytest.raises(LapNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=44,
            lap_b_number=12,
        )

    assert exc_info.value.session_key == 9158
    assert exc_info.value.driver_number == 44
    assert exc_info.value.lap_number == 12


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_laps_runs_gather_concurrently() -> None:
    details, _, _ = _make_session_details()
    lap_a, lap_b = _make_laps()
    session_repo = FakeSessionRepository(details=details)

    mock_telemetry_repo = AsyncMock(spec=TelemetryRepository)
    mock_telemetry_repo.get_laps.side_effect = [
        [lap_a],
        [lap_b],
    ]

    use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=mock_telemetry_repo,
    )

    await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert mock_telemetry_repo.get_laps.await_count == 2
    mock_telemetry_repo.get_laps.assert_any_await(session_key=9158, driver_number=1)
    mock_telemetry_repo.get_laps.assert_any_await(session_key=9158, driver_number=44)
