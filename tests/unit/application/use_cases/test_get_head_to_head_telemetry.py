from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    LapNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.application.use_cases import (
    GetHeadToHeadTelemetryUseCase,
    SelectHeadToHeadLapsUseCase,
)
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    HeadToHeadLapSelection,
    HeadToHeadTelemetry,
    Lap,
    Session,
    SessionDetails,
    TelemetryPoint,
)
from f1_telemetry_bff.domain.ports import SessionRepository, TelemetryRepository


class FakeSessionRepository(SessionRepository):
    def __init__(self, details: SessionDetails | None = None) -> None:
        self.details = details

    async def get_session_details(self, session_key: int) -> SessionDetails | None:
        return self.details


class FakeTelemetryRepository(TelemetryRepository):
    def __init__(
        self,
        laps_by_driver: dict[int, list[Lap]] | None = None,
        telemetry_by_lap: dict[tuple[int, int], list[TelemetryPoint]] | None = None,
    ) -> None:
        self.laps_by_driver = laps_by_driver or {}
        self.telemetry_by_lap = telemetry_by_lap or {}
        self.received_lap_telemetry_calls: list[tuple[int, int, Lap]] = []

    async def get_laps(self, session_key: int, driver_number: int) -> list[Lap]:
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
        self.received_lap_telemetry_calls.append((session_key, driver_number, lap))
        return self.telemetry_by_lap.get((driver_number, lap.lap_number), [])


def _make_session_and_drivers() -> tuple[SessionDetails, Driver, Driver]:
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


def _make_point(speed: float) -> TelemetryPoint:
    return TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=0.0,
        speed=speed,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_success() -> None:
    details, driver_1, driver_44 = _make_session_and_drivers()
    lap_a, lap_b = _make_laps()
    point_a = _make_point(315.0)
    point_b = _make_point(308.0)

    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={1: [lap_a], 44: [lap_b]},
        telemetry_by_lap={(1, 10): [point_a], (44, 12): [point_b]},
    )
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert isinstance(result, HeadToHeadTelemetry)
    assert result.session == details.session
    assert result.driver_a == driver_1
    assert result.lap_a == lap_a
    assert result.telemetry_a == [point_a]
    assert result.driver_b == driver_44
    assert result.lap_b == lap_b
    assert result.telemetry_b == [point_b]
    assert len(telemetry_repo.received_lap_telemetry_calls) == 2
    assert (9158, 1, lap_a) in telemetry_repo.received_lap_telemetry_calls
    assert (9158, 44, lap_b) in telemetry_repo.received_lap_telemetry_calls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_empty_telemetry_preserved() -> None:
    details, _, _ = _make_session_and_drivers()
    lap_a, lap_b = _make_laps()

    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={1: [lap_a], 44: [lap_b]},
        telemetry_by_lap={(1, 10): [], (44, 12): []},
    )
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert result.telemetry_a == []
    assert result.telemetry_b == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_same_driver_raises_error() -> None:
    session_repo = FakeSessionRepository()
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
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
    assert len(telemetry_repo.received_lap_telemetry_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_session_not_found_raises_error() -> None:
    session_repo = FakeSessionRepository(details=None)
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
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
    assert len(telemetry_repo.received_lap_telemetry_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_driver_a_not_found_raises_error() -> None:
    details, _, _ = _make_session_and_drivers()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
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
    assert len(telemetry_repo.received_lap_telemetry_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_driver_b_not_found_raises_error() -> None:
    details, _, _ = _make_session_and_drivers()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
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
    assert len(telemetry_repo.received_lap_telemetry_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_lap_a_not_found_raises_error() -> None:
    details, _, _ = _make_session_and_drivers()
    _, lap_b = _make_laps()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={1: [], 44: [lap_b]},
    )
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
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

    assert exc_info.value.driver_number == 1
    assert exc_info.value.lap_number == 10
    assert len(telemetry_repo.received_lap_telemetry_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_lap_b_not_found_raises_error() -> None:
    details, _, _ = _make_session_and_drivers()
    lap_a, _ = _make_laps()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={1: [lap_a], 44: []},
    )
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=select_laps_use_case,
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

    assert exc_info.value.driver_number == 44
    assert exc_info.value.lap_number == 12
    assert len(telemetry_repo.received_lap_telemetry_calls) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_telemetry_runs_gather_concurrently() -> None:
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
    lap_a, lap_b = _make_laps()
    selection = HeadToHeadLapSelection(
        session=session,
        driver_a=driver_1,
        lap_a=lap_a,
        driver_b=driver_44,
        lap_b=lap_b,
    )

    mock_select_laps_use_case = AsyncMock(spec=SelectHeadToHeadLapsUseCase)
    mock_select_laps_use_case.execute.return_value = selection

    mock_telemetry_repo = AsyncMock(spec=TelemetryRepository)
    mock_telemetry_repo.get_telemetry_for_lap.side_effect = [
        [_make_point(300.0)],
        [_make_point(310.0)],
    ]

    use_case = GetHeadToHeadTelemetryUseCase(
        select_laps_use_case=mock_select_laps_use_case,
        telemetry_repository=mock_telemetry_repo,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert mock_telemetry_repo.get_telemetry_for_lap.await_count == 2
    mock_telemetry_repo.get_telemetry_for_lap.assert_any_await(
        session_key=9158,
        driver_number=1,
        lap=lap_a,
    )
    mock_telemetry_repo.get_telemetry_for_lap.assert_any_await(
        session_key=9158,
        driver_number=44,
        lap=lap_b,
    )
    assert len(result.telemetry_a) == 1
    assert len(result.telemetry_b) == 1
