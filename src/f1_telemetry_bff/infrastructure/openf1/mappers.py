from f1_telemetry_bff.domain.entities import Lap
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1Lap


def map_lap(lap: OpenF1Lap) -> Lap:
    """Map an OpenF1 lap into a domain Lap."""
    if lap.lap_duration is None:
        raise ValueError(
            f"Lap duration is missing for lap {lap.lap_number} of driver {lap.driver_number}"
        )

    if lap.date_start is None:
        raise ValueError(
            f"Lap start date is missing for lap {lap.lap_number} of driver {lap.driver_number}"
        )

    return Lap(
        lap_number=lap.lap_number,
        driver_number=lap.driver_number,
        lap_time=lap.lap_duration,
        date_start=lap.date_start,
    )
