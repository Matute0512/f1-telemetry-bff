import httpx
import pytest
from fastapi import FastAPI

from f1_telemetry_bff.main import lifespan


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lifespan_creates_http_client() -> None:
    test_app = FastAPI()

    async with lifespan(test_app):
        assert hasattr(test_app.state, "http_client")
        assert isinstance(test_app.state.http_client, httpx.AsyncClient)
        assert test_app.state.http_client.is_closed is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lifespan_closes_http_client() -> None:
    test_app = FastAPI()

    async with lifespan(test_app):
        client = test_app.state.http_client
        assert client.is_closed is False

    assert client.is_closed is True
