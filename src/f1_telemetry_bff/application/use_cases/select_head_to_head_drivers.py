from f1_telemetry_bff.application.exceptions import (
    DriverNotFoundError,
    SameDriverSelectedError,
    SessionNotFoundError,
)
from f1_telemetry_bff.domain.entities import HeadToHeadSelection
from f1_telemetry_bff.domain.ports import SessionRepository


class SelectHeadToHeadDriversUseCase:
    """Select and validate two drivers participating in a session for head-to-head comparison."""

    def __init__(self, session_repository: SessionRepository) -> None:
        self._session_repository = session_repository

    async def execute(
        self,
        session_key: int,
        driver_a_number: int,
        driver_b_number: int,
    ) -> HeadToHeadSelection:
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

        return HeadToHeadSelection(
            session=session_details.session,
            driver_a=driver_a,
            driver_b=driver_b,
        )

