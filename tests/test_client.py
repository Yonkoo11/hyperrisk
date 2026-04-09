"""Integration tests for Hyperliquid API client. Hits real API."""

import asyncio
import time

import pytest

from src.data.client import HyperliquidClient


@pytest.fixture
def client():
    c = HyperliquidClient()
    yield c
    asyncio.get_event_loop().run_until_complete(c.close())


@pytest.mark.asyncio
async def test_get_meta_returns_btc():
    client = HyperliquidClient()
    try:
        metas, contexts = await client.get_meta_and_contexts()
        coins = [m.coin for m in metas]
        assert "BTC" in coins
        btc_idx = coins.index("BTC")
        assert metas[btc_idx].max_leverage > 0
        assert contexts[btc_idx].mark_price > 0
        assert contexts[btc_idx].open_interest > 0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_get_l2_book_has_depth():
    client = HyperliquidClient()
    try:
        book = await client.get_l2_book("BTC")
        assert len(book.bids) >= 10
        assert len(book.asks) >= 10
        assert book.bids[0].price > 0
        assert book.bids[0].size > 0
        assert book.bid_depth_usd > 0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_get_candles_returns_data():
    client = HyperliquidClient()
    try:
        now = int(time.time() * 1000)
        day_ago = now - 86400 * 1000
        candles = await client.get_candles("BTC", "1h", day_ago, now)
        assert len(candles) >= 20
        assert candles[0].open > 0
        assert candles[0].volume >= 0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_get_funding_history():
    client = HyperliquidClient()
    try:
        now = int(time.time() * 1000)
        week_ago = now - 7 * 86400 * 1000
        records = await client.get_funding_history("BTC", week_ago, now)
        assert len(records) > 0
        assert isinstance(records[0].funding_rate, float)
        assert records[0].timestamp > 0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_rate_limiter_allows_burst():
    client = HyperliquidClient()
    try:
        # 5 rapid calls should all succeed without rate limit errors
        for _ in range(5):
            book = await client.get_l2_book("BTC")
            assert len(book.bids) > 0
    finally:
        await client.close()
