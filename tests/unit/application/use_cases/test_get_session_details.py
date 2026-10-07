import pytest

from f1_telemetry_bff.application.use_cases import GetSessionDetailsUseCase
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_details_executes_repository() -> None:
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
    expected_details = SessionDetails(
        session=session,
        circuit=circuit,
        drivers=[driver],
    )

    repo = FakeSessionRepository(details=expected_details)
    use_case = GetSessionDetailsUseCase(repo)

    result = await use_case.execute(session_key=9158)

    assert repo.received_session_key == 9158
    assert result == expected_details


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_details_returns_none_when_not_found() -> None:
    repo = FakeSessionRepository(details=None)
    use_case = GetSessionDetailsUseCase(repo)

    result = await use_case.execute(session_key=9999)

    assert repo.received_session_key == 9999
    assert result is None
