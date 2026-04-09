"""Synthetic position distribution model for cascade simulation.

Since individual Hyperliquid positions are not visible via API, we model
aggregate position distribution using observable data (OI, funding rate,
max leverage) and empirically-validated assumptions about crypto markets.

Key assumptions documented inline. All can be overridden via config.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PositionDistConfig:
    """Tunable parameters for position generation."""

    n_positions: int = 10_000
    pareto_alpha: float = 1.5  # shape param for position size distribution
    min_position_usd: float = 100.0
    max_position_pct_of_oi: float = 0.05  # largest position as fraction of OI
    entry_spread_pct: float = 0.05  # std dev of entry prices around mark price
    seed: int | None = 42  # for reproducibility

    # Leverage bucket distribution (must sum to 1.0)
    leverage_buckets: list[tuple[float, float, float]] | None = None
    # Default: (min_lev, max_lev, weight)
    # [(1, 3, 0.25), (3, 5, 0.20), (5, 10, 0.25), (10, 20, 0.20), (20, 50, 0.10)]


DEFAULT_LEV_BUCKETS = [
    (1.0, 3.0, 0.25),
    (3.0, 5.0, 0.20),
    (5.0, 10.0, 0.25),
    (10.0, 20.0, 0.20),
    (20.0, 50.0, 0.10),
]


class PositionDistribution:
    """Generates and queries synthetic positions for a single market."""

    def __init__(
        self,
        total_oi_usd: float,
        mark_price: float,
        max_leverage: int,
        funding_rate: float,  # hourly, positive = longs pay
        config: PositionDistConfig | None = None,
    ):
        self.total_oi_usd = total_oi_usd
        self.mark_price = mark_price
        self.max_leverage = max_leverage
        self.funding_rate = funding_rate
        self.config = config or PositionDistConfig()

        self._rng = np.random.default_rng(self.config.seed)
        self._generate()

    def _generate(self):
        n = self.config.n_positions
        cfg = self.config

        # 1. Position sizes (Pareto distribution, normalized to match OI)
        raw_sizes = (self._rng.pareto(cfg.pareto_alpha, n) + 1) * cfg.min_position_usd
        max_size = self.total_oi_usd * cfg.max_position_pct_of_oi
        raw_sizes = np.clip(raw_sizes, cfg.min_position_usd, max_size)
        # Normalize so sum matches total OI
        self.sizes_usd = raw_sizes * (self.total_oi_usd / raw_sizes.sum())

        # 2. Long/short assignment from funding rate
        # Positive funding = more longs than shorts
        long_pct = 0.5 + np.clip(self.funding_rate * 1000, -0.2, 0.2)
        self.is_long = self._rng.random(n) < long_pct

        # 3. Leverage assignment by bucket
        buckets = cfg.leverage_buckets or DEFAULT_LEV_BUCKETS
        bucket_weights = np.array([b[2] for b in buckets])
        bucket_weights /= bucket_weights.sum()
        bucket_indices = self._rng.choice(len(buckets), size=n, p=bucket_weights)

        self.leverages = np.zeros(n)
        for i, (lo, hi, _) in enumerate(buckets):
            mask = bucket_indices == i
            hi_clamped = min(hi, float(self.max_leverage))
            lo_clamped = min(lo, hi_clamped)
            self.leverages[mask] = self._rng.uniform(lo_clamped, hi_clamped, mask.sum())

        # 4. Entry prices (normal around mark, scaled by spread)
        spread = self.mark_price * cfg.entry_spread_pct
        self.entry_prices = self._rng.normal(self.mark_price, spread, n)
        self.entry_prices = np.clip(self.entry_prices, self.mark_price * 0.5, self.mark_price * 1.5)

        # 5. Compute liquidation prices
        self.liq_prices = self._compute_liq_prices()

        # Track which positions have been liquidated
        self.liquidated = np.zeros(n, dtype=bool)

    def _compute_liq_prices(self) -> np.ndarray:
        """Compute liquidation price for each position.

        For longs: liq_price = entry * (1 - maint_margin / leverage)
        For shorts: liq_price = entry * (1 + maint_margin / leverage)
        where maint_margin = 1 / (2 * leverage)
        """
        n = self.config.n_positions
        maint_rates = 1.0 / (2.0 * self.leverages)  # maintenance margin rate

        liq_prices = np.zeros(n)

        # Longs liquidated when price drops
        long_mask = self.is_long
        liq_prices[long_mask] = self.entry_prices[long_mask] * (
            1.0 - maint_rates[long_mask]
        )

        # Shorts liquidated when price rises
        short_mask = ~self.is_long
        liq_prices[short_mask] = self.entry_prices[short_mask] * (
            1.0 + maint_rates[short_mask]
        )

        return liq_prices

    def get_positions_at_risk(self, new_price: float) -> dict:
        """Find positions that would be liquidated at a given price.

        Returns dict with arrays of: indices, sizes_usd, is_long, leverages
        for positions that breach their liquidation price and haven't been
        liquidated already.
        """
        not_yet_liq = ~self.liquidated

        # Longs liquidated when price drops below liq_price
        long_at_risk = (
            self.is_long
            & not_yet_liq
            & (new_price <= self.liq_prices)
        )

        # Shorts liquidated when price rises above liq_price
        short_at_risk = (
            ~self.is_long
            & not_yet_liq
            & (new_price >= self.liq_prices)
        )

        at_risk = long_at_risk | short_at_risk

        return {
            "indices": np.where(at_risk)[0],
            "sizes_usd": self.sizes_usd[at_risk],
            "is_long": self.is_long[at_risk],
            "leverages": self.leverages[at_risk],
            "count": int(at_risk.sum()),
            "total_volume_usd": float(self.sizes_usd[at_risk].sum()),
            "long_volume_usd": float(self.sizes_usd[long_at_risk].sum()),
            "short_volume_usd": float(self.sizes_usd[short_at_risk].sum()),
        }

    def mark_liquidated(self, indices: np.ndarray):
        """Mark positions as liquidated so they're excluded from future rounds."""
        self.liquidated[indices] = True

    @property
    def remaining_oi_usd(self) -> float:
        return float(self.sizes_usd[~self.liquidated].sum())
