from typing import Any

import pytest

from f1_telemetry_bff.domain.entities import SessionDetails
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.session_repository import (
    OpenF1SessionRepository,
)


class FakeSessionOpenF1Client(OpenF1Client):
    def __init__(
        self,
        sessions: list[dict[str, Any]] | None = None,
        drivers: list[dict[str, Any]] | None = None,
    ) -> None:  # type: ignore[override]
        self._sessions = sessions or []
        self._drivers = drivers or []
        self.sessions_call_params: dict[str, Any] | None = None
        self.drivers_call_params: dict[str, Any] | None = None

    async def get_sessions(
        self,
        session_key: int | None = None,
    ) -> list[dict[str, Any]]:
        self.sessions_call_params = {"session_key": session_key}
        return self._sessions

    async def get_drivers(
        self,
        session_key: int,
    ) -> list[dict[str, Any]]:
        self.drivers_call_params = {"session_key": session_key}
        return self._drivers


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_details_success() -> None:
    raw_sessions = [
        {
            "session_key": 9158,
            "session_name": "Practice 1",
            "session_type": "Practice",
            "year": 2023,
            "circuit_key": 61,
            "circuit_short_name": "Marina Bay",
            "country_name": "Singapore",
            "location": "Marina Bay",
        }
    ]
    raw_drivers = [
        {
            "session_key": 9158,
            "driver_number": 1,
            "full_name": "Max Verstappen",
            "name_acronym": "VER",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
        },
        {
            "session_key": 9158,
            "driver_number": 44,
            "full_name": "Lewis Hamilton",
            "name_acronym": "HAM",
            "team_name": "Mercedes",
            "team_colour": "00D2BE",
        },
    ]

    client = FakeSessionOpenF1Client(sessions=raw_sessions, drivers=raw_drivers)
    repo = OpenF1SessionRepository(client)

    result = await repo.get_session_details(session_key=9158)

    assert result is not None
    assert isinstance(result, SessionDetails)

    assert result.session.session_key == 9158
    assert result.session.session_name == "Practice 1"
    assert result.session.session_type == "Practice"
    assert result.session.year == 2023

    assert result.circuit.circuit_key == 61
    assert result.circuit.name == "Marina Bay"
    assert result.circuit.country == "Singapore"
    assert result.circuit.location == "Marina Bay"

    assert len(result.drivers) == 2
    assert result.drivers[0].driver_number == 1
    assert result.drivers[0].name == "Max Verstappen"
    assert result.drivers[0].acronym == "VER"
    assert result.drivers[0].team_name == "Red Bull Racing"
    assert result.drivers[0].team_colour == "3671C6"

    assert result.drivers[1].driver_number == 44
    assert result.drivers[1].name == "Lewis Hamilton"
    assert result.drivers[1].acronym == "HAM"
    assert result.drivers[1].team_name == "Mercedes"
    assert result.drivers[1].team_colour == "00D2BE"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_details_not_found() -> None:
    client = FakeSessionOpenF1Client(sessions=[], drivers=[])
    repo = OpenF1SessionRepository(client)

    result = await repo.get_session_details(session_key=9999)

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_details_deduplicates_drivers() -> None:
    raw_sessions = [
        {
            "session_key": 9158,
            "session_name": "Practice 1",
            "session_type": "Practice",
            "year": 2023,
            "circuit_key": 61,
            "circuit_short_name": "Marina Bay",
            "country_name": "Singapore",
            "location": "Marina Bay",
        }
    ]
    raw_drivers = [
        {
            "session_key": 9158,
            "driver_number": 1,
            "full_name": "Max Verstappen",
            "name_acronym": "VER",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
        },
        {
            "session_key": 9158,
            "driver_number": 1,
            "full_name": "Max Verstappen",
            "name_acronym": "VER",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
        },
    ]

    client = FakeSessionOpenF1Client(sessions=raw_sessions, drivers=raw_drivers)
    repo = OpenF1SessionRepository(client)

    result = await repo.get_session_details(session_key=9158)

    assert result is not None
    assert len(result.drivers) == 1
    assert result.drivers[0].driver_number == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_details_selects_requested_session() -> None:
    requested_session_key = 9158

    raw_sessions = [
        {
            "session_key": 1234,
            "session_name": "Practice 1",
            "session_type": "Practice",
            "year": 2023,
            "circuit_key": 10,
            "circuit_short_name": "Other",
            "country_name": "Other Country",
            "location": "Other Location",
        },
        {
            "session_key": requested_session_key,
            "session_name": "Race",
            "session_type": "Race",
            "year": 2023,
            "circuit_key": 61,
            "circuit_short_name": "Singapore",
            "country_name": "Singapore",
            "location": "Marina Bay",
        },
    ]

    client = FakeSessionOpenF1Client(
        sessions=raw_sessions,
        drivers=[],
    )
    repo = OpenF1SessionRepository(client)

    result = await repo.get_session_details(
        session_key=requested_session_key,
    )

    assert result is not None
    assert result.session.session_key == requested_session_key
    assert result.session.session_name == "Race"
    assert result.circuit.circuit_key == 61
    assert result.circuit.name == "Singapore"
