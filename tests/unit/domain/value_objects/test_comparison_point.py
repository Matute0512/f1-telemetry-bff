import pytest

from f1_telemetry_bff.domain.value_objects import ComparisonPoint


def test_comparison_point_creation() -> None:
    point = ComparisonPoint(
        distance=10.0,
        elapsed_time_a=1.5,
        elapsed_time_b=1.4,
        time_delta=0.1,
        speed_a=250.0,
        speed_b=245.0,
        speed_delta=5.0,
        throttle_a=98.0,
        throttle_b=100.0,
        throttle_delta=-2.0,
        brake_a=0.0,
        brake_b=0.0,
        brake_delta=0.0,
        gear_a=6,
        gear_b=6,
    )

    assert point.distance == 10.0
    assert point.elapsed_time_a == 1.5
    assert point.elapsed_time_b == 1.4
    assert point.time_delta == 0.1
    assert point.speed_a == 250.0
    assert point.speed_b == 245.0
    assert point.speed_delta == 5.0
    assert point.throttle_a == 98.0
    assert point.throttle_b == 100.0
    assert point.throttle_delta == -2.0
    assert point.brake_a == 0.0
    assert point.brake_b == 0.0
    assert point.brake_delta == 0.0
    assert point.gear_a == 6
    assert point.gear_b == 6


def test_comparison_point_is_immutable() -> None:
    point = ComparisonPoint(
        distance=10.0,
        elapsed_time_a=1.5,
        elapsed_time_b=1.4,
        time_delta=0.1,
        speed_a=250.0,
        speed_b=245.0,
        speed_delta=5.0,
        throttle_a=98.0,
        throttle_b=100.0,
        throttle_delta=-2.0,
        brake_a=0.0,
        brake_b=0.0,
        brake_delta=0.0,
        gear_a=6,
        gear_b=6,
    )

    with pytest.raises(AttributeError):
        point.distance = 20.0  # type: ignore[misc]
