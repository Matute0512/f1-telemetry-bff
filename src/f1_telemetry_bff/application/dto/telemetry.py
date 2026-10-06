from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TelemetryPointDTO:
    """Application representation of a telemetry point."""

    timestamp: datetime
    x: float
    y: float
    z: float
    speed: float
    throttle: float
    brake: float
    gear: int
