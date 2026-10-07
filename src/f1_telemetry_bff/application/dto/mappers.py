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
