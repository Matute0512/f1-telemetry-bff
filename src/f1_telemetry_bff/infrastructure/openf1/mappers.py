from f1_telemetry_bff.domain.entities import Lap
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Lap


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
