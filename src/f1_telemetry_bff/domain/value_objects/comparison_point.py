from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComparisonPoint:
    """A single interpolated point on the common distance grid comparing two laps.

    Attributes:
        distance: Distance along the lap in meters.
        elapsed_time_a: Elapsed time from lap A start to this distance (seconds).
        elapsed_time_b: Elapsed time from lap B start to this distance (seconds).
        time_delta: Difference in elapsed time (elapsed_time_a - elapsed_time_b).
        speed_a: Speed of car A at this distance (km/h).
        speed_b: Speed of car B at this distance (km/h).
        speed_delta: Difference in speed (speed_a - speed_b).
        throttle_a: Throttle percentage of car A (0-100).
        throttle_b: Throttle percentage of car B (0-100).
        throttle_delta: Difference in throttle (throttle_a - throttle_b).
        brake_a: Brake application/percentage of car A.
        brake_b: Brake application/percentage of car B.
        brake_delta: Difference in brake (brake_a - brake_b).
        gear_a: Gear of car A (nearest sample).
        gear_b: Gear of car B (nearest sample).
    """

    distance: float

    elapsed_time_a: float
    elapsed_time_b: float
    time_delta: float

    speed_a: float
    speed_b: float
    speed_delta: float

    throttle_a: float
    throttle_b: float
    throttle_delta: float

    brake_a: float
    brake_b: float
    brake_delta: float

    gear_a: int
    gear_b: int
