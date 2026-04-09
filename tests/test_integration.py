"""Integration tests for FastAPI endpoints."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.server import app
from src.data.client import HyperliquidClient


@pytest_asyncio.fixture
async def client():
    # Manually set up app state since lifespan doesn't run in test transport
    app.state.hl_client = HyperliquidClient()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    await app.state.hl_client.close()


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_markets_returns_btc(client):
    resp = await client.get("/markets")
    assert resp.status_code == 200
    coins = [m["coin"] for m in resp.json()]
    assert "BTC" in coins


@pytest.mark.asyncio
async def test_simulate_returns_report(client):
    resp = await client.post("/simulate", json={
        "coin": "BTC",
        "scenario": "btc_30pct_2h",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["coin"] == "BTC"
    assert data["cascade_rounds"] > 0
    assert data["total_liquidation_volume_usd"] > 0


@pytest.mark.asyncio
async def test_simulate_custom_scenario(client):
    resp = await client.post("/simulate", json={
        "coin": "ETH",
        "scenario": "custom",
        "custom_drop_pct": 0.15,
        "custom_duration_hours": 1,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["coin"] == "ETH"


@pytest.mark.asyncio
async def test_invalid_coin_returns_error(client):
    resp = await client.post("/simulate", json={
        "coin": "FAKECOIN",
        "scenario": "btc_30pct_2h",
    })
    assert resp.status_code == 404
