from datetime import UTC, datetime

from f1_telemetry_bff.domain.entities.lap import Lap, TelemetryPoint


def test_lap_creation() -> None:
    timestamp = datetime(2026, 10, 5, 15, 30, tzinfo=UTC)

    point = TelemetryPoint(
        timestamp=timestamp,
        x=10.0,
        y=20.0,
        z=0.0,
        speed=300.0,
    )

    lap = Lap(
        lap_number=10,
        driver_number=1,
        lap_time=82.456,
        date_start=timestamp,
        telemetry_points=(point,),
    )

    assert lap.lap_number == 10
    assert lap.driver_number == 1
    assert lap.lap_time == 82.456
    assert len(lap.telemetry_points) == 1
    assert lap.telemetry_points[0] == point
