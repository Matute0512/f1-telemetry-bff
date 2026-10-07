import math
from collections.abc import Sequence
from dataclasses import dataclass

from f1_telemetry_bff.domain.entities.driver import Driver
from f1_telemetry_bff.domain.entities.head_to_head_comparison import (
    HeadToHeadComparison,
)
from f1_telemetry_bff.domain.entities.lap import Lap
from f1_telemetry_bff.domain.entities.session import Session
from f1_telemetry_bff.domain.entities.telemetry_point import TelemetryPoint
from f1_telemetry_bff.domain.value_objects.comparison_point import ComparisonPoint

# Empirical coordinate scaling factor:
# OpenF1 spatial coordinates (x, y, z) are converted to meters using a scale factor
# of 10.0 (i.e. coordinates in decimeters), validated empirically by comparing
# cumulative coordinate distance against speed-time integrals and known circuit lengths
# across real telemetry laps (e.g. Sakhir, Silverstone).
COORDINATE_SCALE: float = 10.0

# Resolution for common distance resampling grid (in meters)
GRID_STEP_METERS: float = 10.0


@dataclass(frozen=True, slots=True)
class _DistancePoint:
    distance: float
    elapsed_time: float
    speed: float
    throttle: float
    brake: float
    gear: int


class InsufficientTelemetryDomainError(ValueError):
    """Domain error raised when telemetry is insufficient to perform distance comparison."""


def _compute_distance_points(
    points: Sequence[TelemetryPoint],
    lap: Lap,
) -> list[_DistancePoint]:
    """Sort points by timestamp, compute cumulative 3D distance in meters and elapsed time."""
    if len(points) < 2:
        raise InsufficientTelemetryDomainError(
            f"At least 2 telemetry points are required, got {len(points)}"
        )

    # Sort chronologically by timestamp
    sorted_points = sorted(points, key=lambda p: p.timestamp)

    origin_time = lap.date_start
    distance_points: list[_DistancePoint] = []
    cumulative_dist = 0.0

    # First point at cumulative distance 0.0
    p0 = sorted_points[0]
    t0 = (p0.timestamp - origin_time).total_seconds()
    distance_points.append(
        _DistancePoint(
            distance=0.0,
            elapsed_time=t0,
            speed=p0.speed,
            throttle=p0.throttle,
            brake=p0.brake,
            gear=p0.gear,
        )
    )

    prev_p = p0
    for p in sorted_points[1:]:
        dx = p.x - prev_p.x
        dy = p.y - prev_p.y
        dz = p.z - prev_p.z
        raw_dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        cumulative_dist += raw_dist / COORDINATE_SCALE
        t = (p.timestamp - origin_time).total_seconds()
        distance_points.append(
            _DistancePoint(
                distance=cumulative_dist,
                elapsed_time=t,
                speed=p.speed,
                throttle=p.throttle,
                brake=p.brake,
                gear=p.gear,
            )
        )
        prev_p = p

    if cumulative_dist <= 0.0:
        raise InsufficientTelemetryDomainError(
            "Total cumulative distance is zero; no vehicle movement detected"
        )

    return distance_points


def _generate_common_grid(common_distance: float, step: float = GRID_STEP_METERS) -> list[float]:
    """Generate distance grid [0.0, step, 2*step, ..., common_distance]."""
    grid: list[float] = []
    current = 0.0
    while current < common_distance - 1e-6:
        grid.append(round(current, 6))
        current += step

    grid.append(common_distance)
    return grid


def _interpolate_lap_at_grid(
    distance_points: list[_DistancePoint],
    grid: list[float],
) -> list[dict[str, float | int]]:
    """Sample/interpolate lap telemetry at each distance target in grid in O(N + K) time."""
    n = len(distance_points)
    i = 0
    sampled: list[dict[str, float | int]] = []

    for d in grid:
        # Advance index until distance_points[i+1].distance >= d or we are at the end
        while i < n - 2 and distance_points[i + 1].distance < d:
            i += 1

        p0 = distance_points[i]
        p1 = distance_points[i + 1]

        dist0 = p0.distance
        dist1 = p1.distance
        span = dist1 - dist0

        if span > 1e-9:
            # Avoid extrapolating beyond [dist0, dist1] if floating point precision causes d slightly out of bounds
            clamped_d = max(dist0, min(d, dist1))
            ratio = (clamped_d - dist0) / span
            elapsed_time = p0.elapsed_time + (p1.elapsed_time - p0.elapsed_time) * ratio
            speed = p0.speed + (p1.speed - p0.speed) * ratio
            throttle = p0.throttle + (p1.throttle - p0.throttle) * ratio
            brake = p0.brake + (p1.brake - p0.brake) * ratio
        else:
            # Duplicate/identical distance points: take p0
            elapsed_time = p0.elapsed_time
            speed = p0.speed
            throttle = p0.throttle
            brake = p0.brake

        # Nearest neighbor for discrete gear
        dist_diff_0 = abs(d - dist0)
        dist_diff_1 = abs(d - dist1)
        gear = p0.gear if dist_diff_0 <= dist_diff_1 else p1.gear

        sampled.append(
            {
                "distance": d,
                "elapsed_time": elapsed_time,
                "speed": speed,
                "throttle": throttle,
                "brake": brake,
                "gear": gear,
            }
        )

    return sampled


class LapComparisonService:
    """Domain service that aligns and compares telemetry from two laps along a common distance grid."""

    def compare_laps(
        self,
        session: Session,
        driver_a: Driver,
        lap_a: Lap,
        telemetry_a: Sequence[TelemetryPoint],
        driver_b: Driver,
        lap_b: Lap,
        telemetry_b: Sequence[TelemetryPoint],
    ) -> HeadToHeadComparison:
        points_a = _compute_distance_points(telemetry_a, lap_a)
        points_b = _compute_distance_points(telemetry_b, lap_b)

        total_distance_a = points_a[-1].distance
        total_distance_b = points_b[-1].distance
        common_distance = min(total_distance_a, total_distance_b)

        if common_distance <= 0.0:
            raise InsufficientTelemetryDomainError("Common distance between both laps is zero")

        grid = _generate_common_grid(common_distance, step=GRID_STEP_METERS)

        sampled_a = _interpolate_lap_at_grid(points_a, grid)
        sampled_b = _interpolate_lap_at_grid(points_b, grid)

        comparison_points: list[ComparisonPoint] = []
        for sa, sb in zip(sampled_a, sampled_b, strict=True):
            d = float(sa["distance"])

            et_a = float(sa["elapsed_time"])
            et_b = float(sb["elapsed_time"])
            time_delta = et_a - et_b

            spd_a = float(sa["speed"])
            spd_b = float(sb["speed"])
            speed_delta = spd_a - spd_b

            thr_a = float(sa["throttle"])
            thr_b = float(sb["throttle"])
            throttle_delta = thr_a - thr_b

            brk_a = float(sa["brake"])
            brk_b = float(sb["brake"])
            brake_delta = brk_a - brk_b

            gear_a = int(sa["gear"])
            gear_b = int(sb["gear"])

            comparison_points.append(
                ComparisonPoint(
                    distance=d,
                    elapsed_time_a=et_a,
                    elapsed_time_b=et_b,
                    time_delta=time_delta,
                    speed_a=spd_a,
                    speed_b=spd_b,
                    speed_delta=speed_delta,
                    throttle_a=thr_a,
                    throttle_b=thr_b,
                    throttle_delta=throttle_delta,
                    brake_a=brk_a,
                    brake_b=brk_b,
                    brake_delta=brake_delta,
                    gear_a=gear_a,
                    gear_b=gear_b,
                )
            )

        return HeadToHeadComparison(
            session=session,
            driver_a=driver_a,
            lap_a=lap_a,
            driver_b=driver_b,
            lap_b=lap_b,
            total_distance=common_distance,
            points=comparison_points,
        )
