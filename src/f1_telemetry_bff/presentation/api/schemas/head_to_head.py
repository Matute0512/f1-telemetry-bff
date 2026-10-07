from pydantic import BaseModel

from f1_telemetry_bff.presentation.api.schemas.session import (
    DriverResponse,
    SessionInfoResponse,
)


class HeadToHeadSelectionResponse(BaseModel):
    session: SessionInfoResponse
    driver_a: DriverResponse
    driver_b: DriverResponse
