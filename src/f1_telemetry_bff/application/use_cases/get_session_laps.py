from f1_telemetry_bff.domain.entities import Lap
from f1_telemetry_bff.domain.ports import TelemetryRepository


class GetSessionLapsUseCase:
    """Retrieve all laps for a driver in a session."""

    def __init__(self, telemetry_repository: TelemetryRepository) -> None:
        self._telemetry_repository = telemetry_repository

    async def execute(
        self,
        session_key: int,
        driver_number: int,
    ) -> list[Lap]:
        return await self._telemetry_repository.get_laps(
            session_key=session_key,
            driver_number=driver_number,
        )
