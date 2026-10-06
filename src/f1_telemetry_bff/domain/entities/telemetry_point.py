from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TelemetryPoint:
    timestamp: datetime
    x: float
    y: float
    z: float
    speed: float
