from datetime import UTC, datetime
from typing import Any

import httpx
import pytest

from f1_telemetry_bff.infrastructure.openf1.client import OpenF1Client


def _make_mock_client(
    handler: Any,
) -> tuple[OpenF1Client, httpx.AsyncClient]:
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    client = OpenF1Client(http_client)
    return client, http_client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_location_sends_correct_endpoint_and_params() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "date": "2026-10-05T15:30:00Z",
                    "driver_number": 1,
                    "x": 10.0,
                    "y": 20.0,
                    "z": 0.0,
                }
            ],
        )

    client, http_client = _make_mock_client(handler)
    date_start = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    date_end = datetime(2026, 10, 5, 15, 31, 20, tzinfo=UTC)

    async with http_client:
        result = await client.get_location(
            session_key=9158,
            driver_number=1,
            date_start=date_start,
            date_end=date_end,
        )

    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req.url.path.endswith("/location")
    assert req.url.params["session_key"] == "9158"
    assert req.url.params["driver_number"] == "1"
    assert req.url.params["date>="] == date_start.isoformat()
    assert req.url.params["date<="] == date_end.isoformat()
    assert len(result) == 1
    assert result[0]["x"] == 10.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_location_without_dates() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json=[])

    client, http_client = _make_mock_client(handler)

    async with http_client:
        result = await client.get_location(session_key=9158, driver_number=1)

    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req.url.path.endswith("/location")
    assert req.url.params["session_key"] == "9158"
    assert req.url.params["driver_number"] == "1"
    assert "date>=" not in req.url.params
    assert "date<=" not in req.url.params
    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_car_data_sends_correct_endpoint_and_params() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "date": "2026-10-05T15:30:00Z",
                    "driver_number": 1,
                    "speed": 315.0,
                    "throttle": 100.0,
                    "brake": 0.0,
                    "gear": 8,
                }
            ],
        )

    client, http_client = _make_mock_client(handler)
    date_start = datetime(2026, 10, 5, 15, 30, 0, tzinfo=UTC)
    date_end = datetime(2026, 10, 5, 15, 31, 20, tzinfo=UTC)

    async with http_client:
        result = await client.get_car_data(
            session_key=9158,
            driver_number=1,
            date_start=date_start,
            date_end=date_end,
        )

    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req.url.path.endswith("/car_data")
    assert req.url.params["session_key"] == "9158"
    assert req.url.params["driver_number"] == "1"
    assert req.url.params["date>="] == date_start.isoformat()
    assert req.url.params["date<="] == date_end.isoformat()
    assert len(result) == 1
    assert result[0]["speed"] == 315.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_car_data_without_dates() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json=[])

    client, http_client = _make_mock_client(handler)

    async with http_client:
        result = await client.get_car_data(session_key=9158, driver_number=1)

    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req.url.path.endswith("/car_data")
    assert req.url.params["session_key"] == "9158"
    assert req.url.params["driver_number"] == "1"
    assert "date>=" not in req.url.params
    assert "date<=" not in req.url.params
    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_raises_http_status_error_on_server_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Server Error")

    client, http_client = _make_mock_client(handler)

    async with http_client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get("location")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_sessions_with_and_without_session_key() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json=[{"session_key": 9158, "session_name": "Practice 1"}])

    client, http_client = _make_mock_client(handler)

    async with http_client:
        res1 = await client.get_sessions(session_key=9158)
        res2 = await client.get_sessions()

    assert len(captured_requests) == 2
    assert captured_requests[0].url.path.endswith("/sessions")
    assert captured_requests[0].url.params["session_key"] == "9158"
    assert "session_key" not in captured_requests[1].url.params
    assert res1 == [{"session_key": 9158, "session_name": "Practice 1"}]
    assert res2 == [{"session_key": 9158, "session_name": "Practice 1"}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drivers_sends_session_key() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json=[{"driver_number": 1, "session_key": 9158}])

    client, http_client = _make_mock_client(handler)

    async with http_client:
        res = await client.get_drivers(session_key=9158)

    assert len(captured_requests) == 1
    assert captured_requests[0].url.path.endswith("/drivers")
    assert captured_requests[0].url.params["session_key"] == "9158"
    assert res == [{"driver_number": 1, "session_key": 9158}]
