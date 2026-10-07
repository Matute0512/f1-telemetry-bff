from dataclasses import dataclass

from f1_telemetry_bff.domain.entities.driver import Driver
from f1_telemetry_bff.domain.entities.lap import Lap
from f1_telemetry_bff.domain.entities.session import Session
from f1_telemetry_bff.domain.value_objects.comparison_point import ComparisonPoint


@dataclass(frozen=True, slots=True)
class HeadToHeadComparison:
    session: Session
    driver_a: Driver
    lap_a: Lap
    driver_b: Driver
    lap_b: Lap
    total_distance: float
    points: list[ComparisonPoint]
