from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.application.dto.telemetry import TelemetryPointDTO
from f1_telemetry_bff.presentation.api.schemas.mappers import (
    lap_telemetry_to_response,
    telemetry_point_dto_to_response,
)


@pytest.mark.unit
def test_telemetry_point_dto_to_response_maps_all_fields() -> None:
    timestamp = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    dto = TelemetryPointDTO(
        timestamp=timestamp,
        x=12.0,
        y=24.0,
        z=0.5,
        speed=305.0,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )

    response = telemetry_point_dto_to_response(dto)

    assert response.timestamp == timestamp
    assert response.x == 12.0
    assert response.y == 24.0
    assert response.z == 0.5
    assert response.speed == 305.0
    assert response.throttle == 100.0
    assert response.brake == 0.0
    assert response.gear == 8


@pytest.mark.unit
def test_lap_telemetry_to_response_maps_all_fields() -> None:
    timestamp = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    dto = TelemetryPointDTO(
        timestamp=timestamp,
        x=12.0,
        y=24.0,
        z=0.5,
        speed=305.0,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )

    response = lap_telemetry_to_response(
        session_key=9158,
        driver_number=1,
        lap_number=5,
        telemetry_dtos=[dto],
    )

    assert response.session_key == 9158
    assert response.driver_number == 1
    assert response.lap_number == 5
    assert len(response.telemetry_points) == 1
    assert response.telemetry_points[0].speed == 305.0
