import pytest

from f1_telemetry_bff.domain.ports import Cache


def test_cache_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Cache()
