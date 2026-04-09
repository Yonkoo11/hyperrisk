"""Order book impact model for liquidation cascade simulation.

Models how market orders (from liquidations) consume order book depth
and cause price impact. Includes a thinning factor to account for
market makers withdrawing during stress.
"""

from __future__ import annotations

from src.data.models import OrderBookSnapshot


class OrderBookImpactModel:
    """Simulates market impact on an order book snapshot."""

    def __init__(self, book: OrderBookSnapshot, thinning_factor: float = 0.5):
        """
        thinning_factor: 0.0-1.0, fraction of book depth REMAINING during stress.
            0.5 means 50% of liquidity remains (market makers pull half their orders).
            This is the most impactful tuning parameter for accuracy.
        """
        self.book = book
        self.thinning_factor = thinning_factor

    def simulate_market_sell(self, volume_usd: float) -> tuple[float, float]:
        """Simulate selling into bids. Returns (vwap, final_price).

        Walks down bid levels consuming liquidity. If volume exceeds total
        book depth, extrapolates with increasing slippage.
        """
        if volume_usd <= 0 or not self.book.bids:
            best_bid = self.book.bids[0].price if self.book.bids else 0
            return (best_bid, best_bid)

        remaining = volume_usd
        total_filled = 0.0
        total_cost = 0.0
        final_price = self.book.bids[0].price

        for level in self.book.bids:
            available_usd = level.notional * self.thinning_factor
            if available_usd <= 0:
                continue

            fill = min(remaining, available_usd)
            total_filled += fill
            total_cost += fill  # at this price level
            final_price = level.price
            remaining -= fill

            if remaining <= 0:
                break

        # If we exhausted the book, extrapolate with increasing slippage
        if remaining > 0 and final_price > 0:
            # Each additional $1M causes 0.5% further price drop
            extra_slippage_pct = (remaining / 1_000_000) * 0.005
            final_price *= (1.0 - extra_slippage_pct)
            final_price = max(final_price, 0.01)  # floor
            total_filled += remaining

        vwap = (total_cost / total_filled * final_price) if total_filled > 0 else final_price
        # Simplified VWAP: average of best bid and final price weighted by fill
        if self.book.bids:
            vwap = (self.book.bids[0].price + final_price) / 2.0

        return (vwap, final_price)

    def simulate_market_buy(self, volume_usd: float) -> tuple[float, float]:
        """Simulate buying into asks. Returns (vwap, final_price)."""
        if volume_usd <= 0 or not self.book.asks:
            best_ask = self.book.asks[0].price if self.book.asks else 0
            return (best_ask, best_ask)

        remaining = volume_usd
        final_price = self.book.asks[0].price

        for level in self.book.asks:
            available_usd = level.notional * self.thinning_factor
            if available_usd <= 0:
                continue

            fill = min(remaining, available_usd)
            final_price = level.price
            remaining -= fill

            if remaining <= 0:
                break

        if remaining > 0 and final_price > 0:
            extra_slippage_pct = (remaining / 1_000_000) * 0.005
            final_price *= (1.0 + extra_slippage_pct)

        if self.book.asks:
            vwap = (self.book.asks[0].price + final_price) / 2.0
        else:
            vwap = final_price

        return (vwap, final_price)

    def price_impact_for_volume(self, volume_usd: float, side: str) -> float:
        """Returns fractional price impact (0.0 to 1.0+) for a given volume.

        side: "sell" or "buy"
        """
        if volume_usd <= 0:
            return 0.0

        if side == "sell":
            if not self.book.bids:
                return 0.5  # assume 50% impact if no data
            start_price = self.book.bids[0].price
            _, final = self.simulate_market_sell(volume_usd)
            return abs(start_price - final) / start_price if start_price > 0 else 0.0
        else:
            if not self.book.asks:
                return 0.5
            start_price = self.book.asks[0].price
            _, final = self.simulate_market_buy(volume_usd)
            return abs(final - start_price) / start_price if start_price > 0 else 0.0
