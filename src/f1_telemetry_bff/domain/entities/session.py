from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Session:
    session_key: int
    session_name: str
    session_type: str
    year: int
