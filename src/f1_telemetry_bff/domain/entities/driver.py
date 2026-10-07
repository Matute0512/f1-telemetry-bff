from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Driver:
    driver_number: int
    name: str
    acronym: str
    team: str = ""
    team_name: str | None = None
    team_colour: str | None = None

    def __post_init__(self) -> None:
        if not self.team and self.team_name:
            object.__setattr__(self, "team", self.team_name)
        elif self.team and not self.team_name:
            object.__setattr__(self, "team_name", self.team)
