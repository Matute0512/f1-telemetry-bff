from datetime import UTC, datetime

import pytest

from f1_telemetry_bff.domain.entities import (
    Driver,
    Lap,
    Session,
    TelemetryPoint,
)
from f1_telemetry_bff.domain.services.lap_comparison_service import (
    COORDINATE_SCALE,
    GRID_STEP_METERS,
    InsufficientTelemetryDomainError,
    LapComparisonService,
)


def _make_session_and_drivers() -> tuple[Session, Driver, Driver, Lap, Lap]:
    session = Session(
        session_key=9158,
        session_name="Practice 1",
        session_type="Practice",
        year=2023,
    )
    driver_a = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    driver_b = Driver(
        driver_number=44,
        name="Lewis Hamilton",
        acronym="HAM",
        team_name="Mercedes",
        team_colour="00D2BE",
    )
    lap_a = Lap(
        lap_number=10,
        driver_number=1,
        lap_time=90.0,
        date_start=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
    )
    lap_b = Lap(
        lap_number=12,
        driver_number=44,
        lap_time=91.0,
        date_start=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
    )
    return session, driver_a, driver_b, lap_a, lap_b


def test_constants_defined() -> None:
    assert COORDINATE_SCALE == 10.0
    assert GRID_STEP_METERS == 10.0


def test_empty_telemetry_raises_insufficient_error() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()

    with pytest.raises(InsufficientTelemetryDomainError) as exc_info:
        service.compare_laps(
            session=session,
            driver_a=d_a,
            lap_a=lap_a,
            telemetry_a=[],
            driver_b=d_b,
            lap_b=lap_b,
            telemetry_b=[],
        )
    assert "At least 2 telemetry points are required" in str(exc_info.value)


def test_single_point_telemetry_raises_insufficient_error() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()
    p = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=3,
    )

    with pytest.raises(InsufficientTelemetryDomainError) as exc_info:
        service.compare_laps(
            session=session,
            driver_a=d_a,
            lap_a=lap_a,
            telemetry_a=[p],
            driver_b=d_b,
            lap_b=lap_b,
            telemetry_b=[p, p],
        )
    assert "At least 2 telemetry points are required" in str(exc_info.value)


def test_zero_cumulative_distance_raises_insufficient_error() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()
    p1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=30.0,
        speed=0.0,
        throttle=0.0,
        brake=100.0,
        gear=1,
    )
    p2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 1, tzinfo=UTC),
        x=10.0,
        y=20.0,
        z=30.0,
        speed=0.0,
        throttle=0.0,
        brake=100.0,
        gear=1,
    )

    with pytest.raises(InsufficientTelemetryDomainError) as exc_info:
        service.compare_laps(
            session=session,
            driver_a=d_a,
            lap_a=lap_a,
            telemetry_a=[p1, p2],
            driver_b=d_b,
            lap_b=lap_b,
            telemetry_b=[p1, p2],
        )
    assert "Total cumulative distance is zero" in str(exc_info.value)


def test_distance_calculation_with_scale_10_and_sorting() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()

    # Lap A: (0, 0, 0) -> (300, 400, 0)
    # Euclidean dx=300, dy=400, dz=0 => sqrt(90000 + 160000) = 500
    # Scaled / 10.0 => 50.0 meters.
    # Provide points out of chronological order to verify sorting
    p_a2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 2, tzinfo=UTC),
        x=300.0,
        y=400.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=5,
    )
    p_a1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=10.0,
        gear=4,
    )

    # Lap B: (0, 0, 0) -> (0, 600, 0) => 60.0 meters
    p_b1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=120.0,
        throttle=60.0,
        brake=5.0,
        gear=4,
    )
    p_b2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 2, tzinfo=UTC),
        x=0.0,
        y=600.0,
        z=0.0,
        speed=220.0,
        throttle=100.0,
        brake=0.0,
        gear=6,
    )

    result = service.compare_laps(
        session=session,
        driver_a=d_a,
        lap_a=lap_a,
        telemetry_a=[p_a2, p_a1],  # Unordered
        driver_b=d_b,
        lap_b=lap_b,
        telemetry_b=[p_b1, p_b2],
    )

    # Common distance should be min(50.0, 60.0) = 50.0
    assert result.total_distance == 50.0
    # Grid should be: 0, 10, 20, 30, 40, 50
    distances = [p.distance for p in result.points]
    assert distances == [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]


def test_linear_interpolation_and_deltas() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()

    # Lap A: 0m (t=0s, spd=100, thr=50, brk=10, gear=4) -> 20m (t=2s, spd=200, thr=100, brk=0, gear=6)
    # (dx=200 raw => 20m)
    p_a1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=10.0,
        gear=4,
    )
    p_a2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 2, tzinfo=UTC),
        x=200.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=6,
    )

    # Lap B: 0m (t=0.5s, spd=80, thr=40, brk=20, gear=3) -> 20m (t=2.5s, spd=180, thr=80, brk=0, gear=5)
    # (date_start of lap_b is 10:05:00, p_b1 is at 10:05:00.500)
    p_b1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, 500000, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=80.0,
        throttle=40.0,
        brake=20.0,
        gear=3,
    )
    p_b2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 2, 500000, tzinfo=UTC),
        x=200.0,
        y=0.0,
        z=0.0,
        speed=180.0,
        throttle=80.0,
        brake=0.0,
        gear=5,
    )

    result = service.compare_laps(
        session=session,
        driver_a=d_a,
        lap_a=lap_a,
        telemetry_a=[p_a1, p_a2],
        driver_b=d_b,
        lap_b=lap_b,
        telemetry_b=[p_b1, p_b2],
    )

    assert len(result.points) == 3
    # Midpoint at distance 10.0 m (ratio = 0.5)
    mid = result.points[1]
    assert mid.distance == 10.0

    # A interpolated: t=1.0, spd=150.0, thr=75.0, brk=5.0
    assert mid.elapsed_time_a == pytest.approx(1.0)
    assert mid.speed_a == pytest.approx(150.0)
    assert mid.throttle_a == pytest.approx(75.0)
    assert mid.brake_a == pytest.approx(5.0)

    # B interpolated: t=1.5, spd=130.0, thr=60.0, brk=10.0
    assert mid.elapsed_time_b == pytest.approx(1.5)
    assert mid.speed_b == pytest.approx(130.0)
    assert mid.throttle_b == pytest.approx(60.0)
    assert mid.brake_b == pytest.approx(10.0)

    # Deltas: A - B
    assert mid.time_delta == pytest.approx(1.0 - 1.5)  # -0.5
    assert mid.speed_delta == pytest.approx(150.0 - 130.0)  # 20.0
    assert mid.throttle_delta == pytest.approx(75.0 - 60.0)  # 15.0
    assert mid.brake_delta == pytest.approx(5.0 - 10.0)  # -5.0


def test_gear_nearest_neighbor() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()

    # Lap A: p1 at 0m (gear 3), p2 at 30m (gear 5)
    # At d=10m, distance to p1 is 10, distance to p2 is 20 -> gear 3
    # At d=20m, distance to p1 is 20, distance to p2 is 10 -> gear 5
    p_a1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=3,
    )
    p_a2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 3, tzinfo=UTC),
        x=300.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=5,
    )

    p_b1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=4,
    )
    p_b2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 3, tzinfo=UTC),
        x=300.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=6,
    )

    result = service.compare_laps(
        session=session,
        driver_a=d_a,
        lap_a=lap_a,
        telemetry_a=[p_a1, p_a2],
        driver_b=d_b,
        lap_b=lap_b,
        telemetry_b=[p_b1, p_b2],
    )

    pt_10 = result.points[1]  # distance 10.0
    assert pt_10.gear_a == 3
    assert pt_10.gear_b == 4

    pt_20 = result.points[2]  # distance 20.0
    assert pt_20.gear_a == 5
    assert pt_20.gear_b == 6


def test_exact_endpoint_when_not_multiple_of_step() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()

    # Common distance: 25.4 meters (dx = 254 raw)
    p_a1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=3,
    )
    p_a2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 2, tzinfo=UTC),
        x=254.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=4,
    )

    p_b1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=3,
    )
    p_b2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 2, tzinfo=UTC),
        x=254.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=4,
    )

    result = service.compare_laps(
        session=session,
        driver_a=d_a,
        lap_a=lap_a,
        telemetry_a=[p_a1, p_a2],
        driver_b=d_b,
        lap_b=lap_b,
        telemetry_b=[p_b1, p_b2],
    )

    assert result.total_distance == pytest.approx(25.4)
    distances = [p.distance for p in result.points]
    assert distances == [0.0, 10.0, 20.0, pytest.approx(25.4)]


def test_duplicate_consecutive_distance_handled_gracefully() -> None:
    session, d_a, d_b, lap_a, lap_b = _make_session_and_drivers()
    service = LapComparisonService()

    # Lap A has 2 points at identical coordinates (dx=dy=dz=0)
    p_a1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=3,
    )
    p_a2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 1, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=110.0,
        throttle=60.0,
        brake=0.0,
        gear=3,
    )
    p_a3 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 0, 2, tzinfo=UTC),
        x=200.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=4,
    )

    p_b1 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 0, tzinfo=UTC),
        x=0.0,
        y=0.0,
        z=0.0,
        speed=100.0,
        throttle=50.0,
        brake=0.0,
        gear=3,
    )
    p_b2 = TelemetryPoint(
        timestamp=datetime(2023, 9, 15, 10, 5, 2, tzinfo=UTC),
        x=200.0,
        y=0.0,
        z=0.0,
        speed=200.0,
        throttle=100.0,
        brake=0.0,
        gear=4,
    )

    # Should not raise ZeroDivisionError and complete successfully
    result = service.compare_laps(
        session=session,
        driver_a=d_a,
        lap_a=lap_a,
        telemetry_a=[p_a1, p_a2, p_a3],
        driver_b=d_b,
        lap_b=lap_b,
        telemetry_b=[p_b1, p_b2],
    )
    assert len(result.points) == 3
    assert result.points[0].distance == 0.0
    assert result.points[1].distance == 10.0
    assert result.points[2].distance == 20.0
