from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import FastAPI, Request

from f1_telemetry_bff.presentation.api.dependencies import (
    get_get_lap_telemetry_use_case,
    get_get_session_laps_use_case,
    get_http_client,
)


@pytest.mark.unit
def test_get_http_client_returns_shared_client_from_app_state() -> None:
    test_app = FastAPI()
    shared_client = httpx.AsyncClient()
    test_app.state.http_client = shared_client

    scope = {
        "type": "http",
        "app": test_app,
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    request = Request(scope)

    result = get_http_client(request)

    assert result is shared_client
    assert result is test_app.state.http_client


@pytest.mark.unit
def test_get_http_client_does_not_create_new_client() -> None:
    test_app = FastAPI()
    shared_client = httpx.AsyncClient()
    test_app.state.http_client = shared_client

    scope = {
        "type": "http",
        "app": test_app,
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    request_1 = Request(scope)
    request_2 = Request(scope)

    client_1 = get_http_client(request_1)
    client_2 = get_http_client(request_2)

    assert client_1 is shared_client
    assert client_2 is shared_client
    assert client_1 is client_2


@pytest.mark.unit
def test_get_session_laps_use_case_receives_provided_client() -> None:
    mock_client = MagicMock(spec=httpx.AsyncClient)

    use_case = get_get_session_laps_use_case(client=mock_client)

    assert use_case is not None


@pytest.mark.unit
def test_get_lap_telemetry_use_case_receives_provided_client() -> None:
    mock_client = MagicMock(spec=httpx.AsyncClient)

    use_case = get_get_lap_telemetry_use_case(client=mock_client)

    assert use_case is not None
