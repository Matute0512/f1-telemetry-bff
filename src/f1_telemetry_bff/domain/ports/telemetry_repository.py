from abc import ABC, abstractmethod

from f1_telemetry_bff.domain.entities import Lap, TelemetryPoint


class TelemetryRepository(ABC):
    """Port for retrieving F1 telemetry data."""

    @abstractmethod
    async def get_laps(
        self,
        session_key: int,
        driver_number: int,
    ) -> list[Lap]:
        """Return all laps for a driver in a session."""
        raise NotImplementedError

    @abstractmethod
    async def get_telemetry(
        self,
        session_key: int,
        driver_number: int,
        lap_number: int,
    ) -> list[TelemetryPoint]:
        """Return telemetry points for a specific lap."""
        raise NotImplementedError

    @abstractmethod
    async def get_telemetry_for_lap(
        self,
        session_key: int,
        driver_number: int,
        lap: Lap,
    ) -> list[TelemetryPoint]:
        """Return telemetry points for a specific lap entity."""
        raise NotImplementedError
