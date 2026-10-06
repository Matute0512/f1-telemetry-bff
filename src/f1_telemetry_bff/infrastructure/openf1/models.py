from datetime import datetime

from pydantic import BaseModel


class OpenF1Lap(BaseModel):
    """OpenF1 representation of a lap."""

    driver_number: int
    lap_number: int
    lap_duration: float | None
    date_start: datetime | None


class OpenF1Location(BaseModel):
    """OpenF1 representation of a location sample."""

    date: datetime
    driver_number: int
    x: float
    y: float
    z: float


class OpenF1CarData(BaseModel):
    """OpenF1 representation of a car telemetry sample."""

    date: datetime
    driver_number: int
    speed: float
    throttle: float
    brake: float
    gear: int
