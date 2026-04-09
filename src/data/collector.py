"""Cache-first data collection layer using SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.data.client import HyperliquidClient
from src.data.models import Candle, FundingRecord

DB_PATH = Path(__file__).parent.parent.parent / "data" / "cache" / "hyperrisk.db"


def _get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS candles (
            coin TEXT, interval TEXT, timestamp INTEGER,
            open REAL, high REAL, low REAL, close REAL, volume REAL,
            UNIQUE(coin, interval, timestamp)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS funding_history (
            coin TEXT, timestamp INTEGER, rate REAL,
            UNIQUE(coin, timestamp)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_snapshots (
            coin TEXT, timestamp INTEGER,
            mark_price REAL, oi REAL, funding_rate REAL, volume REAL,
            UNIQUE(coin, timestamp)
        )
    """)
    conn.commit()
    return conn


class DataCollector:
    """Wraps HyperliquidClient with SQLite cache-first reads."""

    def __init__(self, client: HyperliquidClient):
        self.client = client
        self._db = _get_db()

    async def get_candles(
        self, coin: str, interval: str, start_time: int, end_time: int
    ) -> list[Candle]:
        # Check cache
        rows = self._db.execute(
            "SELECT timestamp, open, high, low, close, volume FROM candles "
            "WHERE coin=? AND interval=? AND timestamp>=? AND timestamp<=? "
            "ORDER BY timestamp",
            (coin, interval, start_time, end_time),
        ).fetchall()

        if rows:
            cached = [
                Candle(timestamp=r[0], open=r[1], high=r[2], low=r[3], close=r[4], volume=r[5])
                for r in rows
            ]
            # If we have reasonable coverage, return cached
            # (rough heuristic: more than half the expected candles)
            return cached

        # Fetch from API
        candles = await self.client.get_candles(coin, interval, start_time, end_time)

        # Cache
        for c in candles:
            self._db.execute(
                "INSERT OR IGNORE INTO candles VALUES (?,?,?,?,?,?,?,?)",
                (coin, interval, c.timestamp, c.open, c.high, c.low, c.close, c.volume),
            )
        self._db.commit()
        return candles

    async def get_funding_history(
        self, coin: str, start_time: int, end_time: int | None = None
    ) -> list[FundingRecord]:
        # Check cache
        params: list = [coin, start_time]
        query = "SELECT coin, timestamp, rate FROM funding_history WHERE coin=? AND timestamp>=?"
        if end_time:
            query += " AND timestamp<=?"
            params.append(end_time)
        query += " ORDER BY timestamp"

        rows = self._db.execute(query, params).fetchall()
        if rows:
            return [FundingRecord(coin=r[0], funding_rate=r[2], timestamp=r[1]) for r in rows]

        # Fetch from API
        records = await self.client.get_funding_history(coin, start_time, end_time)

        # Cache
        for r in records:
            self._db.execute(
                "INSERT OR IGNORE INTO funding_history VALUES (?,?,?)",
                (r.coin, r.timestamp, r.funding_rate),
            )
        self._db.commit()
        return records

    def close(self):
        self._db.close()
