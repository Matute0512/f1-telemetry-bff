import asyncio

from f1_telemetry_bff.domain.entities import Driver, SessionDetails
from f1_telemetry_bff.domain.ports import SessionRepository
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.mappers import (
    map_circuit,
    map_driver,
    map_session,
)
from f1_telemetry_bff.infrastructure.openf1.models import (
    OpenF1Driver,
    OpenF1Session,
)


class OpenF1SessionRepository(SessionRepository):
    """OpenF1 implementation of the session repository."""

    def __init__(self, client: OpenF1Client) -> None:
        self._client = client

    async def get_session_details(self, session_key: int) -> SessionDetails | None:
        raw_sessions, raw_drivers = await asyncio.gather(
            self._client.get_sessions(session_key=session_key),
            self._client.get_drivers(session_key=session_key),
        )

        if not raw_sessions:
            return None

        openf1_session = next(
            (
                OpenF1Session.model_validate(item)
                for item in raw_sessions
                if item.get("session_key") == session_key
            ),
            None,
        )

        if openf1_session is None:
            return None

        session = map_session(openf1_session)
        circuit = map_circuit(openf1_session)

        openf1_drivers = [OpenF1Driver.model_validate(item) for item in raw_drivers]
        seen_drivers: set[int] = set()
        drivers: list[Driver] = []

        for item in openf1_drivers:
            if item.driver_number not in seen_drivers:
                seen_drivers.add(item.driver_number)
                drivers.append(map_driver(item))

        return SessionDetails(
            session=session,
            circuit=circuit,
            drivers=drivers,
        )
