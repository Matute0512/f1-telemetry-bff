from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LapDTO:
    """Application representation of a lap."""

    lap_number: int
    driver_number: int
    lap_time: float
    date_start: datetime
