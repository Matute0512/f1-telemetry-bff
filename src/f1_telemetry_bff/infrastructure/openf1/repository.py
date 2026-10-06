from datetime import timedelta

from f1_telemetry_bff.domain.entities import Lap, TelemetryPoint
from f1_telemetry_bff.domain.ports import TelemetryRepository
from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client
from f1_telemetry_bff.infrastructure.openf1.mappers import is_complete, map_lap
from f1_telemetry_bff.infrastructure.openf1.models import (
    OpenF1CarData,
    OpenF1Lap,
    OpenF1Location,
)
from f1_telemetry_bff.infrastructure.openf1.synchronizer import (
    TelemetrySynchronizer,
)


class OpenF1TelemetryRepository(TelemetryRepository):
    """OpenF1 implementation of the telemetry repository."""

    def __init__(
        self,
        client: OpenF1Client,
        synchronizer: TelemetrySynchronizer | None = None,
    ) -> None:
        self._client = client
        self._synchronizer = synchronizer or TelemetrySynchronizer()

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

        return [map_lap(lap) for lap in openf1_laps if is_complete(lap)]

    async def get_telemetry_for_lap(
        self,
        session_key: int,
        driver_number: int,
        lap: Lap,
    ) -> list[TelemetryPoint]:
        start = lap.date_start
        end = lap.date_start + timedelta(seconds=lap.lap_time)

        raw_locations = await self._client.get_location(
            session_key=session_key,
            driver_number=driver_number,
            date_start=start,
            date_end=end,
        )
        raw_car_data = await self._client.get_car_data(
            session_key=session_key,
            driver_number=driver_number,
            date_start=start,
            date_end=end,
        )

        locations = [OpenF1Location.model_validate(item) for item in raw_locations]
        car_data = [OpenF1CarData.model_validate(item) for item in raw_car_data]

        return self._synchronizer.synchronize(locations, car_data)

    async def get_telemetry(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        laps = await self.get_laps(
            session_key=session_key,
            driver_number=driver_number,
        )
        lap = next((item for item in laps if item.lap_number == lap_number), None)
        if lap is None:
            return []

        return await self.get_telemetry_for_lap(
            session_key=session_key,
            driver_number=driver_number,
            lap=lap,
        )
