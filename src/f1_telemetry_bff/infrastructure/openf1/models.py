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


class OpenF1Session(BaseModel):
    """OpenF1 representation of a session."""

    session_key: int
    session_name: str
    session_type: str
    year: int
    circuit_key: int
    circuit_short_name: str | None = None
    country_name: str | None = None
    location: str | None = None


class OpenF1Driver(BaseModel):
    """OpenF1 representation of a driver."""

    session_key: int | None = None
    driver_number: int
    full_name: str | None = None
    broadcast_name: str | None = None
    name_acronym: str | None = None
    team_name: str | None = None
    team_colour: str | None = None
