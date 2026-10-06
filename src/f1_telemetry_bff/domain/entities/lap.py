from dataclasses import dataclass, field
from datetime import datetime

from f1_telemetry_bff.domain.entities.telemetry_point import TelemetryPoint


@dataclass(frozen=True, slots=True)
class Lap:
    lap_number: int
    driver_number: int
    lap_time: float
    date_start: datetime
    telemetry_points: tuple[TelemetryPoint, ...] = field(default_factory=tuple)
