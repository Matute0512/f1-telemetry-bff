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


@dataclass(frozen=True, slots=True)
class ComparisonPointDTO:
    distance: float
    elapsed_time_a: float
    elapsed_time_b: float
    time_delta: float
    speed_a: float
    speed_b: float
    speed_delta: float
    throttle_a: float
    throttle_b: float
    throttle_delta: float
    brake_a: float
    brake_b: float
    brake_delta: float
    gear_a: int
    gear_b: int


@dataclass(frozen=True, slots=True)
class HeadToHeadComparisonSummaryDTO:
    total_distance: float
    total_time_delta: float


@dataclass(frozen=True, slots=True)
class HeadToHeadComparisonDTO:
    session: SessionDTO
    driver_a: DriverDTO
    lap_a: LapDTO
    driver_b: DriverDTO
    lap_b: LapDTO
    summary: HeadToHeadComparisonSummaryDTO
    points: list[ComparisonPointDTO]
