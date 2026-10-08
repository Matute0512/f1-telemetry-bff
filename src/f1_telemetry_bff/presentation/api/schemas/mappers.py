from f1_telemetry_bff.application.dto import (
    CircuitDTO,
    ComparisonPointDTO,
    DriverDTO,
    HeadToHeadComparisonDTO,
    HeadToHeadLapSelectionDTO,
    HeadToHeadSelectionDTO,
    HeadToHeadTelemetryDTO,
    LapDTO,
    SessionDetailsDTO,
    SessionDTO,
    TelemetryPointDTO,
)
from f1_telemetry_bff.presentation.api.schemas.head_to_head import (
    ComparisonPointResponse,
    HeadToHeadComparisonResponse,
    HeadToHeadComparisonSummaryResponse,
    HeadToHeadLapSelectionResponse,
    HeadToHeadSelectionResponse,
    HeadToHeadTelemetryResponse,
)
from f1_telemetry_bff.presentation.api.schemas.lap import LapResponse
from f1_telemetry_bff.presentation.api.schemas.session import (
    CircuitResponse,
    DriverResponse,
    SessionDetailsResponse,
    SessionInfoResponse,
)
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


def session_info_dto_to_response(session: SessionDTO) -> SessionInfoResponse:
    return SessionInfoResponse(
        session_key=session.session_key,
        session_name=session.session_name,
        session_type=session.session_type,
        year=session.year,
    )


def circuit_dto_to_response(circuit: CircuitDTO) -> CircuitResponse:
    return CircuitResponse(
        circuit_key=circuit.circuit_key,
        name=circuit.name,
        country=circuit.country,
        location=circuit.location,
    )


def driver_dto_to_response(driver: DriverDTO) -> DriverResponse:
    return DriverResponse(
        driver_number=driver.driver_number,
        name=driver.name,
        acronym=driver.acronym,
        team_name=driver.team_name,
        team_colour=driver.team_colour,
    )


def session_details_dto_to_response(
    details: SessionDetailsDTO,
) -> SessionDetailsResponse:
    return SessionDetailsResponse(
        session=session_info_dto_to_response(details.session),
        circuit=circuit_dto_to_response(details.circuit),
        drivers=[driver_dto_to_response(d) for d in details.drivers],
    )


def head_to_head_selection_dto_to_response(
    selection: HeadToHeadSelectionDTO,
) -> HeadToHeadSelectionResponse:
    return HeadToHeadSelectionResponse(
        session=session_info_dto_to_response(selection.session),
        driver_a=driver_dto_to_response(selection.driver_a),
        driver_b=driver_dto_to_response(selection.driver_b),
    )


def head_to_head_lap_selection_dto_to_response(
    selection: HeadToHeadLapSelectionDTO,
) -> HeadToHeadLapSelectionResponse:
    return HeadToHeadLapSelectionResponse(
        session=session_info_dto_to_response(selection.session),
        driver_a=driver_dto_to_response(selection.driver_a),
        lap_a=lap_dto_to_response(selection.lap_a),
        driver_b=driver_dto_to_response(selection.driver_b),
        lap_b=lap_dto_to_response(selection.lap_b),
    )


def head_to_head_telemetry_dto_to_response(
    dto: HeadToHeadTelemetryDTO,
) -> HeadToHeadTelemetryResponse:
    return HeadToHeadTelemetryResponse(
        session=session_info_dto_to_response(dto.session),
        driver_a=driver_dto_to_response(dto.driver_a),
        lap_a=lap_dto_to_response(dto.lap_a),
        telemetry_a=[telemetry_point_dto_to_response(p) for p in dto.telemetry_a],
        driver_b=driver_dto_to_response(dto.driver_b),
        lap_b=lap_dto_to_response(dto.lap_b),
        telemetry_b=[telemetry_point_dto_to_response(p) for p in dto.telemetry_b],
    )


def comparison_point_dto_to_response(
    dto: ComparisonPointDTO,
) -> ComparisonPointResponse:
    return ComparisonPointResponse(
        distance=dto.distance,
        elapsed_time_a=dto.elapsed_time_a,
        elapsed_time_b=dto.elapsed_time_b,
        time_delta=dto.time_delta,
        speed_a=dto.speed_a,
        speed_b=dto.speed_b,
        speed_delta=dto.speed_delta,
        throttle_a=dto.throttle_a,
        throttle_b=dto.throttle_b,
        throttle_delta=dto.throttle_delta,
        brake_a=dto.brake_a,
        brake_b=dto.brake_b,
        brake_delta=dto.brake_delta,
        gear_a=dto.gear_a,
        gear_b=dto.gear_b,
    )


def head_to_head_comparison_dto_to_response(
    dto: HeadToHeadComparisonDTO,
) -> HeadToHeadComparisonResponse:
    return HeadToHeadComparisonResponse(
        session=session_info_dto_to_response(dto.session),
        driver_a=driver_dto_to_response(dto.driver_a),
        lap_a=lap_dto_to_response(dto.lap_a),
        driver_b=driver_dto_to_response(dto.driver_b),
        lap_b=lap_dto_to_response(dto.lap_b),
        summary=HeadToHeadComparisonSummaryResponse(
            total_distance=dto.summary.total_distance,
            total_time_delta=dto.summary.total_time_delta,
        ),
        points=[comparison_point_dto_to_response(p) for p in dto.points],
    )
