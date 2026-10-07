import asyncio

from f1_telemetry_bff.application.use_cases.select_head_to_head_laps import (
    SelectHeadToHeadLapsUseCase,
)
from f1_telemetry_bff.domain.entities import HeadToHeadTelemetry
from f1_telemetry_bff.domain.ports import TelemetryRepository


class GetHeadToHeadTelemetryUseCase:
    """Retrieve full telemetry for two selected laps of two drivers in a session."""

    def __init__(
        self,
        select_laps_use_case: SelectHeadToHeadLapsUseCase,
        telemetry_repository: TelemetryRepository,
    ) -> None:
        self._select_laps_use_case = select_laps_use_case
        self._telemetry_repository = telemetry_repository

    async def execute(
        self,
        session_key: int,
        driver_a_number: int,
        lap_a_number: int,
        driver_b_number: int,
        lap_b_number: int,
    ) -> HeadToHeadTelemetry:
        selection = await self._select_laps_use_case.execute(
            session_key=session_key,
            driver_a_number=driver_a_number,
            lap_a_number=lap_a_number,
            driver_b_number=driver_b_number,
            lap_b_number=lap_b_number,
        )

        telemetry_a, telemetry_b = await asyncio.gather(
            self._telemetry_repository.get_telemetry_for_lap(
                session_key=session_key,
                driver_number=driver_a_number,
                lap=selection.lap_a,
            ),
            self._telemetry_repository.get_telemetry_for_lap(
                session_key=session_key,
                driver_number=driver_b_number,
                lap=selection.lap_b,
            ),
        )

        return HeadToHeadTelemetry(
            session=selection.session,
            driver_a=selection.driver_a,
            lap_a=selection.lap_a,
            telemetry_a=telemetry_a,
            driver_b=selection.driver_b,
            lap_b=selection.lap_b,
            telemetry_b=telemetry_b,
        )
