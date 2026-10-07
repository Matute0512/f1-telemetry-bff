from dataclasses import dataclass

from f1_telemetry_bff.domain.entities.driver import Driver
from f1_telemetry_bff.domain.entities.lap import Lap
from f1_telemetry_bff.domain.entities.session import Session
from f1_telemetry_bff.domain.entities.telemetry_point import TelemetryPoint


@dataclass(frozen=True, slots=True)
class HeadToHeadTelemetry:
    session: Session
    driver_a: Driver
    lap_a: Lap
    telemetry_a: list[TelemetryPoint]
    driver_b: Driver
    lap_b: Lap
    telemetry_b: list[TelemetryPoint]

