from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Driver:
    driver_number: int
    name: str
    acronym: str
    team: str
