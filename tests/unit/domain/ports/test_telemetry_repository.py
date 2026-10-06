import pytest

from f1_telemetry_bff.domain.ports import TelemetryRepository


def test_telemetry_repository_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        TelemetryRepository()
