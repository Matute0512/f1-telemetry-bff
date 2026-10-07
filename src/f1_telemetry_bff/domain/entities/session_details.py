from dataclasses import dataclass

from f1_telemetry_bff.domain.entities.circuit import Circuit
from f1_telemetry_bff.domain.entities.driver import Driver
from f1_telemetry_bff.domain.entities.session import Session


@dataclass(frozen=True, slots=True)
class SessionDetails:
    session: Session
    circuit: Circuit
    drivers: list[Driver]
