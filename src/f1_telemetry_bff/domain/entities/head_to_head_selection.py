from dataclasses import dataclass

from f1_telemetry_bff.domain.entities.driver import Driver
from f1_telemetry_bff.domain.entities.session import Session


@dataclass(frozen=True, slots=True)
class HeadToHeadSelection:
    session: Session
    driver_a: Driver
    driver_b: Driver
