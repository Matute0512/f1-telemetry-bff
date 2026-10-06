from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.application.dto.mappers import telemetry_point_to_dto
from f1_telemetry_bff.domain.entities import TelemetryPoint


@pytest.mark.unit
def test_telemetry_point_to_dto_maps_all_fields() -> None:
    timestamp = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    point = TelemetryPoint(
        timestamp=timestamp,
        x=15.5,
        y=25.5,
        z=1.0,
        speed=320.0,
        throttle=95.0,
        brake=0.0,
        gear=7,
    )

    dto = telemetry_point_to_dto(point)

    assert dto.timestamp == timestamp
    assert dto.x == 15.5
    assert dto.y == 25.5
    assert dto.z == 1.0
    assert dto.speed == 320.0
    assert dto.throttle == 95.0
    assert dto.brake == 0.0
    assert dto.gear == 7
