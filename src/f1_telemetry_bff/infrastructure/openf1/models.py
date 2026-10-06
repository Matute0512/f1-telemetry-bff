from datetime import datetime

from pydantic import BaseModel


class OpenF1Lap(BaseModel):
    """OpenF1 representation of a lap."""

    driver_number: int
    lap_number: int
    lap_duration: float | None
    date_start: datetime | None
