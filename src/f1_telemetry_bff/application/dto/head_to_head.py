from dataclasses import dataclass

from f1_telemetry_bff.application.dto.lap_to_dto import LapDTO
from f1_telemetry_bff.application.dto.session import DriverDTO, SessionDTO


@dataclass(frozen=True, slots=True)
class HeadToHeadSelectionDTO:
    session: SessionDTO
    driver_a: DriverDTO
    driver_b: DriverDTO


@dataclass(frozen=True, slots=True)
class HeadToHeadLapSelectionDTO:
    session: SessionDTO
    driver_a: DriverDTO
    lap_a: LapDTO
    driver_b: DriverDTO
    lap_b: LapDTO
