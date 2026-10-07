from f1_telemetry_bff.application.dto.head_to_head import (
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
    HeadToHeadLapSelection,
    HeadToHeadSelection,
    HeadToHeadTelemetry,
    Lap,
    Session,
    SessionDetails,
    TelemetryPoint,
)


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
