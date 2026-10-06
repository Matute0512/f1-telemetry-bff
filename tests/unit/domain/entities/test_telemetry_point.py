from datetime import UTC, datetime

from f1_telemetry_bff.domain.entities.telemetry_point import TelemetryPoint


def test_telemetry_point_creation() -> None:
    timestamp = datetime(2026, 10, 5, 15, 30, tzinfo=UTC)

    point = TelemetryPoint(
        timestamp=timestamp,
        x=10.5,
        y=20.5,
        z=0.0,
        speed=315.0,
        throttle=100.0,
        brake=0.0,
        gear=8,
    )

    assert point.timestamp == timestamp
    assert point.x == 10.5
    assert point.y == 20.5
    assert point.z == 0.0
    assert point.speed == 315.0
    assert point.throttle == 100.0
    assert point.brake == 0.0
    assert point.gear == 8
