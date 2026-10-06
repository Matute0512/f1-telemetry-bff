from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.application.use_cases.get_session_laps import (
    GetSessionLapsUseCase,
)
from f1_telemetry_bff.domain.entities import Lap, TelemetryPoint
from f1_telemetry_bff.domain.ports import TelemetryRepository


class FakeTelemetryRepository(TelemetryRepository):
    async def get_laps(
        self,
        session_key: int,
        driver_number: int,
    ) -> list[Lap]:
        return [
            Lap(
                lap_number=10,
                driver_number=driver_number,
                lap_time=82.456,
                date_start=datetime(2026, 10, 5, 15, 30, tzinfo=UTC),
            )
        ]

    async def get_telemetry(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ):
        return []

    async def get_telemetry_for_lap(
        self,
        session_key: int,
        driver_number: int,
        lap: Lap,
    ) -> list[TelemetryPoint]:
        return []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_session_laps() -> None:
    repository = FakeTelemetryRepository()
    use_case = GetSessionLapsUseCase(repository)

    laps = await use_case.execute(
        session_key=1234,
        driver_number=1,
    )

    assert len(laps) == 1
    assert laps[0].lap_number == 10
    assert laps[0].driver_number == 1
    assert laps[0].lap_time == 82.456
