import pytest

from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.application.use_cases import (
    SelectHeadToHeadDriversUseCase,
)
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    HeadToHeadSelection,
    Session,
    SessionDetails,
)
from f1_telemetry_bff.domain.ports import SessionRepository


class FakeSessionRepository(SessionRepository):
    def __init__(self, details: SessionDetails | None = None) -> None:
        self.details = details
        self.received_session_key: int | None = None

    async def get_session_details(self, session_key: int) -> SessionDetails | None:
        self.received_session_key = session_key
        return self.details


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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_drivers_success() -> None:
    details, driver_1, driver_44 = _make_session_details()
    repo = FakeSessionRepository(details=details)
    use_case = SelectHeadToHeadDriversUseCase(repo)

    result = await use_case.execute(
        session_key=9158,
        driver_a_number=1,
        driver_b_number=44,
    )

    assert isinstance(result, HeadToHeadSelection)
    assert result.session == details.session
    assert result.driver_a == driver_1
    assert result.driver_b == driver_44
    assert repo.received_session_key == 9158


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_drivers_same_driver_raises_error() -> None:
    details, _, _ = _make_session_details()
    repo = FakeSessionRepository(details=details)
    use_case = SelectHeadToHeadDriversUseCase(repo)

    with pytest.raises(SameDriverSelectedError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            driver_b_number=1,
        )

    assert exc_info.value.driver_number == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_drivers_session_not_found_raises_error() -> None:
    repo = FakeSessionRepository(details=None)
    use_case = SelectHeadToHeadDriversUseCase(repo)

    with pytest.raises(SessionNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9999,
            driver_a_number=1,
            driver_b_number=44,
        )

    assert exc_info.value.session_key == 9999


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_drivers_driver_a_not_found_raises_error() -> None:
    details, _, _ = _make_session_details()
    repo = FakeSessionRepository(details=details)
    use_case = SelectHeadToHeadDriversUseCase(repo)

    with pytest.raises(DriverNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=99,
            driver_b_number=44,
        )

    assert exc_info.value.driver_number == 99
    assert exc_info.value.session_key == 9158


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_head_to_head_drivers_driver_b_not_found_raises_error() -> None:
    details, _, _ = _make_session_details()
    repo = FakeSessionRepository(details=details)
    use_case = SelectHeadToHeadDriversUseCase(repo)

    with pytest.raises(DriverNotFoundError) as exc_info:
        await use_case.execute(
            session_key=9158,
            driver_a_number=1,
            driver_b_number=99,
        )

    assert exc_info.value.driver_number == 99
    assert exc_info.value.session_key == 9158

