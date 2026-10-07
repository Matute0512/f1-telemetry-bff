from dataclasses import dataclass

from f1_telemetry_bff.application.dto.session import DriverDTO, SessionDTO


@dataclass(frozen=True, slots=True)
class HeadToHeadSelectionDTO:
    session: SessionDTO
    driver_a: DriverDTO
    driver_b: DriverDTO

