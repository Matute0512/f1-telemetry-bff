from f1_telemetry_bff.domain.entities import TelemetryPoint
from f1_telemetry_bff.domain.ports import TelemetryRepository


class GetLapTelemetryUseCase:
    """Retrieve telemetry points for a specific lap in a session."""

    def __init__(self, telemetry_repository: TelemetryRepository) -> None:
        self._telemetry_repository = telemetry_repository

    async def execute(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        return await self._telemetry_repository.get_telemetry(
            session_key=session_key,
            driver_number=driver_number,
            lap_number=lap_number,
        )
