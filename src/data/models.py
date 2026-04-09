"""Pydantic models for HyperRisk data and simulation results."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Market Data ---


class MarketMeta(BaseModel):
    coin: str
    max_leverage: int
    sz_decimals: int = 4

    @property
    def initial_margin_at_max(self) -> float:
        return 1.0 / self.max_leverage

    @property
    def maint_margin_at_max(self) -> float:
        return self.initial_margin_at_max / 2.0

    def maint_margin_for_leverage(self, leverage: float) -> float:
        """Maintenance margin rate for a given leverage. Linear interpolation."""
        initial = 1.0 / leverage
        return initial / 2.0


class AssetContext(BaseModel):
    coin: str
    mark_price: float
    mid_price: float | None = None
    oracle_price: float | None = None
    funding_rate: float  # hourly rate as decimal
    open_interest: float  # in coins
    day_volume: float  # USD notional
    prev_day_price: float | None = None

    @property
    def open_interest_usd(self) -> float:
        return self.open_interest * self.mark_price


class OrderBookLevel(BaseModel):
    price: float
    size: float  # in coins
    num_orders: int = 0

    @property
    def notional(self) -> float:
        return self.price * self.size


class OrderBookSnapshot(BaseModel):
    coin: str
    timestamp: int = 0
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)

    @property
    def bid_depth_usd(self) -> float:
        return sum(level.notional for level in self.bids)

    @property
    def ask_depth_usd(self) -> float:
        return sum(level.notional for level in self.asks)

    @property
    def mid_price(self) -> float | None:
        if self.bids and self.asks:
            return (self.bids[0].price + self.asks[0].price) / 2.0
        return None


class Candle(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class FundingRecord(BaseModel):
    coin: str
    funding_rate: float
    timestamp: int


# --- Simulation ---


class SimulationRequest(BaseModel):
    coin: str = "BTC"
    scenario: str = "btc_30pct_2h"
    custom_drop_pct: float | None = None
    custom_duration_hours: float | None = None
    config_overrides: dict | None = None


class CascadeRound(BaseModel):
    round_number: int
    price_before: float
    price_after: float
    liquidation_volume_usd: float
    positions_liquidated: int
    book_absorption_pct: float
    cumulative_bad_debt: float
    stage: str  # "market", "backstop", "adl"


class CascadeReport(BaseModel):
    coin: str
    scenario_name: str
    starting_price: float
    final_price: float
    price_drop_pct: float
    total_liquidation_volume_usd: float
    cascade_rounds: int
    bad_debt_usd: float
    backstop_triggered: bool
    adl_triggered: bool
    peak_funding_rate: float | None = None
    rounds: list[CascadeRound] = Field(default_factory=list)
    parameters_used: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
