from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    InsufficientTelemetryDataError,
    LapNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.application.use_cases import (
    GetHeadToHeadComparisonUseCase,
    SelectHeadToHeadLapsUseCase,
)
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    HeadToHeadComparison,
    Lap,
    Session,
    SessionDetails,
    TelemetryPoint,
)
from f1_telemetry_bff.domain.ports import SessionRepository, TelemetryRepository
from f1_telemetry_bff.domain.services.lap_comparison_service import (
    LapComparisonService,
)


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
        date_start=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
    )
    lap_b = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.876,
        date_start=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
    )
    return lap_a, lap_b


def _make_points(speed: float) -> list[TelemetryPoint]:
    return [
        TelemetryPoint(
            timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
            x=0.0,
            y=0.0,
            z=0.0,
            speed=speed,
            throttle=100.0,
            brake=0.0,
            gear=7,
        ),
        TelemetryPoint(
            timestamp=datetime(2023, 9, 15, 10, 0, 2, tzinfo=UTC),
            x=200.0,
            y=0.0,
            z=0.0,
            speed=speed + 20.0,
            throttle=100.0,
            brake=0.0,
            gear=8,
        ),
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_success() -> None:
    details, driver_1, driver_44 = _make_session_and_drivers()
    lap_a, lap_b = _make_laps()
    points_a = _make_points(280.0)
    points_b = _make_points(275.0)

    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(
        laps_by_driver={1: [lap_a], 44: [lap_b]},
        telemetry_by_lap={(1, 10): points_a, (44, 12): points_b},
    )
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    comparison_service = LapComparisonService()
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
        comparison_service=comparison_service,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert isinstance(result, HeadToHeadComparison)
    assert result.session == details.session
    assert result.driver_a == driver_1
    assert result.lap_a == lap_a
    assert result.driver_b == driver_44
    assert result.lap_b == lap_b
    assert result.total_distance == 20.0
    assert len(result.points) == 3
    assert len(telemetry_repo.received_lap_telemetry_calls) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_empty_telemetry_raises_error() -> None:
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
    comparison_service = LapComparisonService()
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
        comparison_service=comparison_service,
    )

    with pytest.raises(InsufficientTelemetryDataError):
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=44,
            lap_b_number=12,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_concurrent_gathering() -> None:
    details, _, _ = _make_session_and_drivers()
    lap_a, lap_b = _make_laps()
    points_a = _make_points(280.0)
    points_b = _make_points(275.0)

    select_laps_mock = AsyncMock()
    from f1_telemetry_bff.domain.entities import HeadToHeadLapSelection

    select_laps_mock.execute.return_value = HeadToHeadLapSelection(
        session=details.session,
        driver_a=details.drivers[0],
        lap_a=lap_a,
        driver_b=details.drivers[1],
        lap_b=lap_b,
    )

    telemetry_repo_mock = AsyncMock(spec=TelemetryRepository)
    telemetry_repo_mock.get_telemetry_for_lap.side_effect = [points_a, points_b]

    comparison_service = LapComparisonService()
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_mock,
        telemetry_repository=telemetry_repo_mock,
        comparison_service=comparison_service,
    )

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        lap_a_number=10,
        driver_b_number=44,
        lap_b_number=12,
    )

    assert result.total_distance == 20.0
    assert telemetry_repo_mock.get_telemetry_for_lap.call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_same_driver_raises_error() -> None:
    session_repo = FakeSessionRepository()
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
        comparison_service=LapComparisonService(),
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_session_not_found_raises_error() -> None:
    session_repo = FakeSessionRepository(details=None)
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
        comparison_service=LapComparisonService(),
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_driver_not_found_raises_error() -> None:
    details, _, _ = _make_session_and_drivers()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository()
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
        comparison_service=LapComparisonService(),
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_head_to_head_comparison_lap_not_found_raises_error() -> None:
    details, _, _ = _make_session_and_drivers()
    lap_a, _ = _make_laps()
    session_repo = FakeSessionRepository(details=details)
    telemetry_repo = FakeTelemetryRepository(laps_by_driver={1: [lap_a], 44: []})
    select_laps_use_case = SelectHeadToHeadLapsUseCase(
        session_repository=session_repo,
        telemetry_repository=telemetry_repo,
    )
    use_case = GetHeadToHeadComparisonUseCase(
        select_laps_use_case=select_laps_use_case,
        telemetry_repository=telemetry_repo,
        comparison_service=LapComparisonService(),
    )

    with pytest.raises(LapNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            lap_a_number=10,
            driver_b_number=44,
            lap_b_number=99,
        )

    assert exc_info.value.driver_number == 44
    assert exc_info.value.lap_number == 99
