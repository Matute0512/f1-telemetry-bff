from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Circuit:
    circuit_key: int
    name: str
    country: str
    location: str
