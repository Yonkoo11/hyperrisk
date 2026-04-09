"""Unit tests for cascade simulation engine."""

import numpy as np
import pytest

from src.data.models import OrderBookLevel, OrderBookSnapshot
from src.simulation.engine import CascadeSimulator, SimulationConfig
from src.simulation.orderbook import OrderBookImpactModel
from src.simulation.positions import PositionDistConfig, PositionDistribution
from src.simulation.scenarios import build_custom_scenario, generate_price_path


# --- Position Distribution Tests ---


def test_maint_margin_at_max_leverage():
    """40x leverage should give ~1.25% maintenance margin."""
    from src.data.models import MarketMeta
    meta = MarketMeta(coin="BTC", max_leverage=40)
    assert abs(meta.maint_margin_at_max - 0.0125) < 0.001


def test_maint_margin_at_low_leverage():
    """3x leverage should give ~16.7% maintenance margin."""
    from src.data.models import MarketMeta
    meta = MarketMeta(coin="BTC", max_leverage=40)
    maint = meta.maint_margin_for_leverage(3.0)
    assert abs(maint - 0.1667) < 0.01


def test_position_distribution_sums_to_oi():
    """Total notional of generated positions should match OI within 1%."""
    dist = PositionDistribution(
        total_oi_usd=5_000_000_000,
        mark_price=80_000,
        max_leverage=40,
        funding_rate=0.0001,
    )
    total = float(dist.sizes_usd.sum())
    assert abs(total - 5_000_000_000) / 5_000_000_000 < 0.01


def test_more_liquidations_at_larger_drop():
    """30% crash should trigger more liquidations than 10% crash."""
    dist = PositionDistribution(
        total_oi_usd=5_000_000_000,
        mark_price=80_000,
        max_leverage=40,
        funding_rate=0.0001,
    )

    small_drop = dist.get_positions_at_risk(80_000 * 0.90)
    # Reset liquidated state
    dist.liquidated[:] = False
    large_drop = dist.get_positions_at_risk(80_000 * 0.70)

    assert large_drop["total_volume_usd"] > small_drop["total_volume_usd"]


# --- Order Book Impact Tests ---


def _make_book(mid_price: float = 80_000, depth_per_level: float = 100) -> OrderBookSnapshot:
    """Create a synthetic order book for testing."""
    bids = [
        OrderBookLevel(price=mid_price - i * 10, size=depth_per_level / (mid_price - i * 10), num_orders=5)
        for i in range(20)
    ]
    asks = [
        OrderBookLevel(price=mid_price + i * 10, size=depth_per_level / (mid_price + i * 10), num_orders=5)
        for i in range(20)
    ]
    return OrderBookSnapshot(coin="BTC", bids=bids, asks=asks)


def test_larger_sell_has_more_impact():
    """$100M sell should have more impact than $10M sell."""
    book = _make_book(depth_per_level=500_000)
    model = OrderBookImpactModel(book, thinning_factor=0.5)

    impact_10m = model.price_impact_for_volume(10_000_000, "sell")
    impact_100m = model.price_impact_for_volume(100_000_000, "sell")

    assert impact_100m > impact_10m
    assert impact_10m > 0
    assert impact_100m < 1.0  # shouldn't be more than 100%


# --- Cascade Engine Tests ---


def test_cascade_produces_rounds():
    """30% crash on $5B OI should produce cascade rounds."""
    book = _make_book(depth_per_level=1_000_000)
    scenario = build_custom_scenario("BTC", 0.30, 2)
    config = SimulationConfig(position_count=5000, seed=42)
    sim = CascadeSimulator(config)

    report = sim.run(
        scenario=scenario,
        mark_price=80_000,
        total_oi_usd=5_000_000_000,
        max_leverage=40,
        funding_rate=0.0001,
        book=book,
    )

    assert report.cascade_rounds > 0
    assert report.total_liquidation_volume_usd > 0
    assert report.final_price < 80_000


def test_backstop_triggers_on_extreme_crash():
    """50% crash should trigger backstop or ADL."""
    book = _make_book(depth_per_level=500_000)
    scenario = build_custom_scenario("BTC", 0.50, 1)
    config = SimulationConfig(
        position_count=5000,
        seed=42,
        backstop_capacity_pct=0.01,  # tiny backstop to trigger ADL
    )
    sim = CascadeSimulator(config)

    report = sim.run(
        scenario=scenario,
        mark_price=80_000,
        total_oi_usd=5_000_000_000,
        max_leverage=40,
        funding_rate=0.0001,
        book=book,
    )

    assert report.backstop_triggered or report.adl_triggered
