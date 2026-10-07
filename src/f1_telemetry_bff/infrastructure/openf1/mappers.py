from f1_telemetry_bff.domain.entities import Circuit, Driver, Lap, Session
from f1_telemetry_bff.infrastructure.openf1.models import (
    OpenF1Driver,
    OpenF1Lap,
    OpenF1Session,
)


def map_lap(lap: OpenF1Lap) -> Lap:
    """Map a complete OpenF1 lap into a domain Lap."""
    return Lap(
        lap_number=lap.lap_number,
        driver_number=lap.driver_number,
        lap_time=lap.lap_duration,  # type: ignore[arg-type]
        date_start=lap.date_start,  # type: ignore[arg-type]
    )


def is_complete(lap: OpenF1Lap) -> bool:
    """Return True if the lap has all required timing data."""
    return lap.lap_duration is not None and lap.date_start is not None


def map_session(session: OpenF1Session) -> Session:
    """Map an OpenF1 session into a domain Session."""
    return Session(
        session_key=session.session_key,
        session_name=session.session_name,
        session_type=session.session_type,
        year=session.year,
    )


def map_circuit(session: OpenF1Session) -> Circuit:
    """Map circuit information from an OpenF1 session into a domain Circuit."""
    return Circuit(
        circuit_key=session.circuit_key,
        name=session.circuit_short_name or "",
        country=session.country_name or "",
        location=session.location or "",
    )


def map_driver(driver: OpenF1Driver) -> Driver:
    """Map an OpenF1 driver into a domain Driver."""
    name = driver.full_name or driver.broadcast_name or ""
    acronym = driver.name_acronym or ""
    return Driver(
        driver_number=driver.driver_number,
        name=name,
        acronym=acronym,
        team_name=driver.team_name,
        team_colour=driver.team_colour,
    )
