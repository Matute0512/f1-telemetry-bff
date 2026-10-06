import bisect
from datetime import timedelta

from f1_telemetry_bff.domain.entities import TelemetryPoint
from f1_telemetry_bff.infrastructure.openf1.models import OpenF1CarData, OpenF1Location

# OpenF1 typically samples location and car_data at roughly 3.5 - 4 Hz (~250-300 ms between samples).
# A maximum tolerance of 500 ms (0.5 s) allows matching adjacent samples while avoiding
# associating mismatched or stale telemetry readings.
DEFAULT_MAX_TIME_DELTA = timedelta(milliseconds=500)


class TelemetrySynchronizer:
    """Synchronizes location and car telemetry streams by closest timestamp matching."""

    def __init__(self, max_time_delta: timedelta = DEFAULT_MAX_TIME_DELTA) -> None:
        self._max_time_delta = max_time_delta

    def synchronize(
        self,
        locations: list[OpenF1Location],
        car_data: list[OpenF1CarData],
    ) -> list[TelemetryPoint]:
        """Align location and car data samples into unified domain TelemetryPoint objects.

        For each location sample, finds the car_data sample with the closest timestamp.
        If the closest sample is within max_time_delta, produces a TelemetryPoint.
        Otherwise, discards the location sample without creating fabricated data.
        """
        if not locations or not car_data:
            return []

        # Ensure both streams are sorted by timestamp
        sorted_locations = sorted(locations, key=lambda loc: loc.date)
        sorted_car_data = sorted(car_data, key=lambda car: car.date)

        car_dates = [car.date for car in sorted_car_data]
        n_car = len(sorted_car_data)

        points: list[TelemetryPoint] = []

        for loc in sorted_locations:
            loc_date = loc.date
            idx = bisect.bisect_left(car_dates, loc_date)

            best_car: OpenF1CarData | None = None
            best_diff: timedelta | None = None

            # Check candidate at idx - 1
            if idx > 0:
                candidate = sorted_car_data[idx - 1]
                diff = abs(loc_date - candidate.date)
                best_car = candidate
                best_diff = diff

            # Check candidate at idx
            if idx < n_car:
                candidate = sorted_car_data[idx]
                diff = abs(loc_date - candidate.date)
                if best_diff is None or diff < best_diff:
                    best_car = candidate
                    best_diff = diff

            if best_car is not None and best_diff is not None and best_diff <= self._max_time_delta:
                points.append(
                    TelemetryPoint(
                        timestamp=loc.date,
                        x=loc.x,
                        y=loc.y,
                        z=loc.z,
                        speed=best_car.speed,
                        throttle=best_car.throttle,
                        brake=best_car.brake,
                        gear=best_car.gear,
                    )
                )

        return points
