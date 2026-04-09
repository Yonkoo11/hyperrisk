"""Thin async HTTP client for Hyperliquid public API.

No SDK dependency. All endpoints are public (no auth needed).
Port of the pattern from ~/Projects/degen-claw/scripts/data.ts hlPost().
"""

from __future__ import annotations

import asyncio
import time

import httpx

from src.data.models import (
    AssetContext,
    Candle,
    FundingRecord,
    MarketMeta,
    OrderBookLevel,
    OrderBookSnapshot,
)

HL_API = "https://api.hyperliquid.xyz/info"

# Rate limiting: 1200 weight per minute
WEIGHT_LIMIT = 1200
WEIGHT_WINDOW = 60.0  # seconds


class RateLimiter:
    """Token-bucket rate limiter for Hyperliquid API."""

    def __init__(self, limit: int = WEIGHT_LIMIT, window: float = WEIGHT_WINDOW):
        self.limit = limit
        self.window = window
        self._timestamps: list[tuple[float, int]] = []  # (time, weight)

    def _prune(self):
        cutoff = time.monotonic() - self.window
        self._timestamps = [(t, w) for t, w in self._timestamps if t > cutoff]

    @property
    def current_weight(self) -> int:
        self._prune()
        return sum(w for _, w in self._timestamps)

    async def acquire(self, weight: int = 2):
        while True:
            self._prune()
            if self.current_weight + weight <= self.limit:
                self._timestamps.append((time.monotonic(), weight))
                return
            await asyncio.sleep(0.1)


class HyperliquidClient:
    """Async client for Hyperliquid public info endpoints."""

    def __init__(self):
        self._http = httpx.AsyncClient(timeout=30.0)
        self._limiter = RateLimiter()

    async def close(self):
        await self._http.aclose()

    async def _post(self, body: dict, weight: int = 2):
        await self._limiter.acquire(weight)
        resp = await self._http.post(HL_API, json=body)
        resp.raise_for_status()
        return resp.json()

    async def get_meta_and_contexts(self) -> tuple[list[MarketMeta], list[AssetContext]]:
        """Fetch all market metadata and current asset contexts."""
        raw = await self._post({"type": "metaAndAssetCtxs"}, weight=20)
        meta_raw = raw[0]["universe"]
        ctx_raw = raw[1]

        metas = []
        contexts = []
        for m, c in zip(meta_raw, ctx_raw):
            metas.append(MarketMeta(
                coin=m["name"],
                max_leverage=m["maxLeverage"],
                sz_decimals=m.get("szDecimals", 4),
            ))
            def _safe_float(val) -> float | None:
                if val is None:
                    return None
                try:
                    f = float(val)
                    return f if f != 0 else None
                except (ValueError, TypeError):
                    return None

            contexts.append(AssetContext(
                coin=m["name"],
                mark_price=float(c["markPx"]),
                mid_price=_safe_float(c.get("midPx")),
                oracle_price=_safe_float(c.get("oraclePx")),
                funding_rate=float(c["funding"]),
                open_interest=float(c["openInterest"]),
                day_volume=float(c["dayNtlVlm"]),
                prev_day_price=_safe_float(c.get("prevDayPx")),
            ))
        return metas, contexts

    async def get_l2_book(self, coin: str, n_sig_figs: int | None = None) -> OrderBookSnapshot:
        """Fetch L2 order book snapshot (up to 20 levels per side)."""
        body: dict = {"type": "l2Book", "coin": coin}
        if n_sig_figs:
            body["nSigFigs"] = n_sig_figs
        raw = await self._post(body)
        levels = raw["levels"]

        def parse_levels(side: list[dict]) -> list[OrderBookLevel]:
            return [
                OrderBookLevel(
                    price=float(lv["px"]),
                    size=float(lv["sz"]),
                    num_orders=int(lv["n"]),
                )
                for lv in side
            ]

        return OrderBookSnapshot(
            coin=coin,
            timestamp=int(time.time() * 1000),
            bids=parse_levels(levels[0]),
            asks=parse_levels(levels[1]),
        )

    async def get_candles(
        self, coin: str, interval: str, start_time: int, end_time: int
    ) -> list[Candle]:
        """Fetch OHLCV candles. Max 5000 per request.

        interval: "1m", "5m", "15m", "1h", "4h", "1d"
        start_time, end_time: milliseconds since epoch
        """
        raw = await self._post(
            {
                "type": "candleSnapshot",
                "req": {
                    "coin": coin,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                },
            },
            weight=10,
        )
        return [
            Candle(
                timestamp=int(c["t"]),
                open=float(c["o"]),
                high=float(c["h"]),
                low=float(c["l"]),
                close=float(c["c"]),
                volume=float(c["v"]),
            )
            for c in raw
        ]

    async def get_funding_history(
        self, coin: str, start_time: int, end_time: int | None = None
    ) -> list[FundingRecord]:
        """Fetch funding rate history. Max 500 per request, paginate by advancing start_time."""
        all_records: list[FundingRecord] = []
        current_start = start_time

        while True:
            body: dict = {
                "type": "fundingHistory",
                "coin": coin,
                "startTime": current_start,
            }
            if end_time:
                body["endTime"] = end_time
            raw = await self._post(body, weight=20)

            if not raw:
                break

            for r in raw:
                all_records.append(FundingRecord(
                    coin=r["coin"],
                    funding_rate=float(r["fundingRate"]),
                    timestamp=int(r["time"]),
                ))

            if len(raw) < 500:
                break
            # Advance past the last record's timestamp
            current_start = int(raw[-1]["time"]) + 1

        return all_records
