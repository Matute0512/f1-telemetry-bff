from f1_telemetry_bff.application.dto import LapDTO, TelemetryPointDTO
from f1_telemetry_bff.presentation.api.schemas.lap import LapResponse
from f1_telemetry_bff.presentation.api.schemas.telemetry import (
    LapTelemetryResponse,
    TelemetryPointResponse,
)


def lap_dto_to_response(lap: LapDTO) -> LapResponse:
    return LapResponse(
        lap_number=lap.lap_number,
        driver_number=lap.driver_number,
        lap_time=lap.lap_time,
        date_start=lap.date_start,
    )


def telemetry_point_dto_to_response(
    point: TelemetryPointDTO,
) -> TelemetryPointResponse:
    return TelemetryPointResponse(
        timestamp=point.timestamp,
        x=point.x,
        y=point.y,
        z=point.z,
        speed=point.speed,
        throttle=point.throttle,
        brake=point.brake,
        gear=point.gear,
    )


def lap_telemetry_to_response(
    session_key: int,
    driver_number: int,
    lap_number: int,
    telemetry_dtos: list[TelemetryPointDTO],
) -> LapTelemetryResponse:
    return LapTelemetryResponse(
        session_key=session_key,
        driver_number=driver_number,
        lap_number=lap_number,
        telemetry_points=[telemetry_point_dto_to_response(point) for point in telemetry_dtos],
    )
