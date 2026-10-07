from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SessionDTO:
    session_key: int
    session_name: str
    session_type: str
    year: int


@dataclass(frozen=True, slots=True)
class CircuitDTO:
    circuit_key: int
    name: str
    country: str
    location: str


@dataclass(frozen=True, slots=True)
class DriverDTO:
    driver_number: int
    name: str
    acronym: str
    team_name: str | None = None
    team_colour: str | None = None


@dataclass(frozen=True, slots=True)
class SessionDetailsDTO:
    session: SessionDTO
    circuit: CircuitDTO
    drivers: list[DriverDTO]
