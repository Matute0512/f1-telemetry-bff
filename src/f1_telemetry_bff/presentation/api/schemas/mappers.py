from f1_telemetry_bff.application.dto import (
    CircuitDTO,
    DriverDTO,
    HeadToHeadSelectionDTO,
    LapDTO,
    SessionDetailsDTO,
    SessionDTO,
    TelemetryPointDTO,
)
from f1_telemetry_bff.presentation.api.schemas.head_to_head import (
    HeadToHeadSelectionResponse,
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
