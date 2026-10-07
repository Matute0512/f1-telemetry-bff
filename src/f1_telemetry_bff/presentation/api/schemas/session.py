from pydantic import BaseModel


class SessionInfoResponse(BaseModel):
    session_key: int
    session_name: str
    session_type: str
    year: int


class CircuitResponse(BaseModel):
    circuit_key: int
    name: str
    country: str
    location: str


class DriverResponse(BaseModel):
    driver_number: int
    name: str
    acronym: str
    team_name: str | None = None
    team_colour: str | None = None


class SessionDetailsResponse(BaseModel):
    session: SessionInfoResponse
    circuit: CircuitResponse
    drivers: list[DriverResponse]
