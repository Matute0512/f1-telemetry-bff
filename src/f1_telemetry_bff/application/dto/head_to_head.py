from dataclasses import dataclass

from f1_telemetry_bff.application.dto.lap_to_dto import LapDTO
from f1_telemetry_bff.application.dto.session import DriverDTO, SessionDTO
from f1_telemetry_bff.application.dto.telemetry import TelemetryPointDTO


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


@dataclass(frozen=True, slots=True)
class HeadToHeadTelemetryDTO:
    session: SessionDTO
    driver_a: DriverDTO
    lap_a: LapDTO
    telemetry_a: list[TelemetryPointDTO]
    driver_b: DriverDTO
    lap_b: LapDTO
    telemetry_b: list[TelemetryPointDTO]
