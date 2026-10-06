from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LapResponse(BaseModel):
    """HTTP response representation of a lap."""

    model_config = ConfigDict(from_attributes=True)

    lap_number: int
    driver_number: int
    lap_time: float
    date_start: datetime
