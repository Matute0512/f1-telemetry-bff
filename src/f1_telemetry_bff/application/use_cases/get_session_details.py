from f1_telemetry_bff.domain.entities import SessionDetails
from f1_telemetry_bff.domain.ports import SessionRepository


class GetSessionDetailsUseCase:
    """Retrieve session details including circuit and drivers."""

    def __init__(self, session_repository: SessionRepository) -> None:
        self._session_repository = session_repository

    async def execute(self, session_key: int) -> SessionDetails | None:
        return await self._session_repository.get_session_details(
            session_key=session_key,
        )
