from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.application.use_cases.get_lap_telemetry import (
    GetLapTelemetryUseCase,
)
from f1_telemetry_bff.domain.entities import Lap, TelemetryPoint
from f1_telemetry_bff.domain.ports import TelemetryRepository


class FakeTelemetryRepository(TelemetryRepository):
    def __init__(self, points: list[TelemetryPoint] | None = None) -> None:
        self.points = points or []
        self.received_session_key: int | None = None
        self.received_driver_number: int | None = None
        self.received_lap_number: int | None = None

    async def get_laps(
        self,
        session_key: int,
        driver_number: int,
    ) -> list[Lap]:
        return []

    async def get_telemetry(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        self.received_session_key = session_key
        self.received_driver_number = driver_number
        self.received_lap_number = lap_number
        return self.points

    async def get_telemetry_for_lap(
        self,
        session_key: int,
        driver_number: int,
        lap: Lap,
    ) -> list[TelemetryPoint]:
        return []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_lap_telemetry() -> None:
    expected_point = TelemetryPoint(
        timestamp=datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=0.0,
        speed=310.0,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )
    repository = FakeTelemetryRepository(points=[expected_point])
    use_case = GetLapTelemetryUseCase(repository)

    result = await use_case.execute(
        session_key=9158,
        driver_number=1,
        lap_number=10,
    )

    assert repository.received_session_key == 9158
    assert repository.received_driver_number == 1
    assert repository.received_lap_number == 10
    assert len(result) == 1
    assert result[0] == expected_point
