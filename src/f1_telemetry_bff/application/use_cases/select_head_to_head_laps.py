import asyncio

from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    LapNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.domain.entities import HeadToHeadLapSelection
from f1_telemetry_bff.domain.ports import SessionRepository, TelemetryRepository


class SelectHeadToHeadLapsUseCase:
    """Select and validate two independent laps for head-to-head comparison."""

    def __init__(
        self,
        session_repository: SessionRepository,
        telemetry_repository: TelemetryRepository,
    ) -> None:
        self._session_repository = session_repository
        self._telemetry_repository = telemetry_repository

    async def execute(
        self,
        session_key: int,
        driver_a_number: int,
        lap_a_number: int,
        driver_b_number: int,
        lap_b_number: int,
    ) -> HeadToHeadLapSelection:
        if driver_a_number == driver_b_number:
            raise SameDriverSelectedError(driver_number=driver_a_number)

        session_details = await self._session_repository.get_session_details(
            session_key=session_key
        )
        if session_details is None:
            raise SessionNotFoundError(session_key=session_key)

        driver_a = next(
            (d for d in session_details.drivers if d.driver_number == driver_a_number),
            None,
        )
        if driver_a is None:
            raise DriverNotFoundError(
                driver_number=driver_a_number,
                session_key=session_key,
            )

        driver_b = next(
            (d for d in session_details.drivers if d.driver_number == driver_b_number),
            None,
        )
        if driver_b is None:
            raise DriverNotFoundError(
                driver_number=driver_b_number,
                session_key=session_key,
            )

        laps_a, laps_b = await asyncio.gather(
            self._telemetry_repository.get_laps(
                session_key=session_key,
                driver_number=driver_a_number,
            ),
            self._telemetry_repository.get_laps(
                session_key=session_key,
                driver_number=driver_b_number,
            ),
        )

        lap_a = next(
            (lap for lap in laps_a if lap.lap_number == lap_a_number),
            None,
        )
        if lap_a is None:
            raise LapNotFoundError(
                session_key=session_key,
                driver_number=driver_a_number,
                lap_number=lap_a_number,
            )

        lap_b = next(
            (lap for lap in laps_b if lap.lap_number == lap_b_number),
            None,
        )
        if lap_b is None:
            raise LapNotFoundError(
                session_key=session_key,
                driver_number=driver_b_number,
                lap_number=lap_b_number,
            )

        return HeadToHeadLapSelection(
            session=session_details.session,
            driver_a=driver_a,
            lap_a=lap_a,
            driver_b=driver_b,
            lap_b=lap_b,
        )

