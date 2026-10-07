from f1_telemetry_bff.application.dto.head_to_head import (
    ComparisonPointDTO,
    HeadToHeadComparisonDTO,
    HeadToHeadComparisonSummaryDTO,
    HeadToHeadLapSelectionDTO,
    HeadToHeadSelectionDTO,
    HeadToHeadTelemetryDTO,
)
from f1_telemetry_bff.application.dto.lap_to_dto import LapDTO
from f1_telemetry_bff.application.dto.session import (
    CircuitDTO,
    DriverDTO,
    SessionDetailsDTO,
    SessionDTO,
)
from f1_telemetry_bff.application.dto.telemetry import TelemetryPointDTO
from f1_telemetry_bff.domain.entities import (
    Circuit,
    Driver,
    HeadToHeadComparison,
    HeadToHeadLapSelection,
    HeadToHeadSelection,
    HeadToHeadTelemetry,
    Lap,
    Session,
    SessionDetails,
    TelemetryPoint,
)
from f1_telemetry_bff.domain.value_objects.comparison_point import ComparisonPoint


def lap_to_dto(lap: Lap) -> LapDTO:
    return LapDTO(
        lap_number=lap.lap_number,
        driver_number=lap.driver_number,
        lap_time=lap.lap_time,
        date_start=lap.date_start,
    )


def telemetry_point_to_dto(point: TelemetryPoint) -> TelemetryPointDTO:
    return TelemetryPointDTO(
        timestamp=point.timestamp,
        x=point.x,
        y=point.y,
        z=point.z,
        speed=point.speed,
        throttle=point.throttle,
        brake=point.brake,
        gear=point.gear,
    )


def session_to_dto(session: Session) -> SessionDTO:
    return SessionDTO(
        session_key=session.session_key,
        session_name=session.session_name,
        session_type=session.session_type,
        year=session.year,
    )


def circuit_to_dto(circuit: Circuit) -> CircuitDTO:
    return CircuitDTO(
        circuit_key=circuit.circuit_key,
        name=circuit.name,
        country=circuit.country,
        location=circuit.location,
    )


def driver_to_dto(driver: Driver) -> DriverDTO:
    return DriverDTO(
        driver_number=driver.driver_number,
        name=driver.name,
        acronym=driver.acronym,
        team_name=driver.team_name,
        team_colour=driver.team_colour,
    )


def session_details_to_dto(details: SessionDetails) -> SessionDetailsDTO:
    return SessionDetailsDTO(
        session=session_to_dto(details.session),
        circuit=circuit_to_dto(details.circuit),
        drivers=[driver_to_dto(d) for d in details.drivers],
    )


def head_to_head_selection_to_dto(
    selection: HeadToHeadSelection,
) -> HeadToHeadSelectionDTO:
    return HeadToHeadSelectionDTO(
        session=session_to_dto(selection.session),
        driver_a=driver_to_dto(selection.driver_a),
        driver_b=driver_to_dto(selection.driver_b),
    )


def head_to_head_lap_selection_to_dto(
    selection: HeadToHeadLapSelection,
) -> HeadToHeadLapSelectionDTO:
    return HeadToHeadLapSelectionDTO(
        session=session_to_dto(selection.session),
        driver_a=driver_to_dto(selection.driver_a),
        lap_a=lap_to_dto(selection.lap_a),
        driver_b=driver_to_dto(selection.driver_b),
        lap_b=lap_to_dto(selection.lap_b),
    )


def head_to_head_telemetry_to_dto(
    h2h: HeadToHeadTelemetry,
) -> HeadToHeadTelemetryDTO:
    return HeadToHeadTelemetryDTO(
        session=session_to_dto(h2h.session),
        driver_a=driver_to_dto(h2h.driver_a),
        lap_a=lap_to_dto(h2h.lap_a),
        telemetry_a=[telemetry_point_to_dto(p) for p in h2h.telemetry_a],
        driver_b=driver_to_dto(h2h.driver_b),
        lap_b=lap_to_dto(h2h.lap_b),
        telemetry_b=[telemetry_point_to_dto(p) for p in h2h.telemetry_b],
    )


def comparison_point_to_dto(point: ComparisonPoint) -> ComparisonPointDTO:
    return ComparisonPointDTO(
        distance=point.distance,
        elapsed_time_a=point.elapsed_time_a,
        elapsed_time_b=point.elapsed_time_b,
        time_delta=point.time_delta,
        speed_a=point.speed_a,
        speed_b=point.speed_b,
        speed_delta=point.speed_delta,
        throttle_a=point.throttle_a,
        throttle_b=point.throttle_b,
        throttle_delta=point.throttle_delta,
        brake_a=point.brake_a,
        brake_b=point.brake_b,
        brake_delta=point.brake_delta,
        gear_a=point.gear_a,
        gear_b=point.gear_b,
    )


def head_to_head_comparison_to_dto(
    comparison: HeadToHeadComparison,
) -> HeadToHeadComparisonDTO:
    total_time_delta = comparison.points[-1].time_delta if comparison.points else 0.0
    return HeadToHeadComparisonDTO(
        session=session_to_dto(comparison.session),
        driver_a=driver_to_dto(comparison.driver_a),
        lap_a=lap_to_dto(comparison.lap_a),
        driver_b=driver_to_dto(comparison.driver_b),
        lap_b=lap_to_dto(comparison.lap_b),
        summary=HeadToHeadComparisonSummaryDTO(
            total_distance=comparison.total_distance,
            total_time_delta=total_time_delta,
        ),
        points=[comparison_point_to_dto(p) for p in comparison.points],
    )
