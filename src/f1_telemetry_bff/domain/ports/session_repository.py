from abc import ABC, abstractmethod

from f1_telemetry_bff.domain.entities import SessionDetails


class SessionRepository(ABC):
    """Port for retrieving F1 session data."""

    @abstractmethod
    async def get_session_details(self, session_key: int) -> SessionDetails | None:
        """Return session details including session info, circuit, and drivers."""
        raise NotImplementedError
