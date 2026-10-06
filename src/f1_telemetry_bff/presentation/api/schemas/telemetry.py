from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TelemetryPointResponse(BaseModel):
    """HTTP response representation of a telemetry point."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    x: float
    y: float
    z: float
    speed: float
    throttle: float
    brake: float
    gear: int


class LapTelemetryResponse(BaseModel):
    """HTTP response representation of a lap's telemetry."""

    model_config = ConfigDict(from_attributes=True)

    session_key: int
    driver_number: int
    lap_number: int
    telemetry_points: list[TelemetryPointResponse]
