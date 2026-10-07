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
