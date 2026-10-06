from f1_telemetry_bff.domain.entities import Lap, TelemetryPoint
from f1_telemetry_bff.domain.ports import TelemetryRepository
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.mappers import map_lap
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Lap


class OpenF1TelemetryRepository(TelemetryRepository):
    """OpenF1 implementation of the telemetry repository."""

    def __init__(self, client: OpenF1Client) -> None:
        self._client = client

    async def get_laps(
        self,
        session_key: int,
        driver_number: int,
    ) -> list[Lap]:
        response = await self._client.get(
            "laps",
            params={
                "session_key": session_key,
                "driver_number": driver_number,
            },
        )

        openf1_laps = [OpenF1Lap.model_validate(item) for item in response]

        return [map_lap(lap) for lap in openf1_laps]

    async def get_telemetry(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        raise NotImplementedError
