from pydantic import BaseModel

from f1_telemetry_bff.presentation.api.schemas.lap import LapResponse
from f1_telemetry_bff.presentation.api.schemas.session import (
    DriverResponse,
    SessionInfoResponse,
)
from f1_telemetry_bff.presentation.api.schemas.telemetry import (
    TelemetryPointResponse,
)


class HeadToHeadSelectionResponse(BaseModel):
    session: SessionInfoResponse
    driver_a: DriverResponse
    driver_b: DriverResponse


class HeadToHeadLapSelectionResponse(BaseModel):
    session: SessionInfoResponse
    driver_a: DriverResponse
    lap_a: LapResponse
    driver_b: DriverResponse
    lap_b: LapResponse


class HeadToHeadTelemetryResponse(BaseModel):
    session: SessionInfoResponse
    driver_a: DriverResponse
    lap_a: LapResponse
    telemetry_a: list[TelemetryPointResponse]
    driver_b: DriverResponse
    lap_b: LapResponse
    telemetry_b: list[TelemetryPointResponse]


class ComparisonPointResponse(BaseModel):
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


class HeadToHeadComparisonSummaryResponse(BaseModel):
    total_distance: float
    total_time_delta: float


class HeadToHeadComparisonResponse(BaseModel):
    session: SessionInfoResponse
    driver_a: DriverResponse
    lap_a: LapResponse
    driver_b: DriverResponse
    lap_b: LapResponse
    summary: HeadToHeadComparisonSummaryResponse
    points: list[ComparisonPointResponse]
