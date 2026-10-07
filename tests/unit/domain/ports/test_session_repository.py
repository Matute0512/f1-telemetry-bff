import pytest

from f1_telemetry_bff.domain.ports import SessionRepository


def test_session_repository_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        SessionRepository()  # type: ignore[abstract]
