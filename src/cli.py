"""CLI runner: python -m src.cli BTC 0.30"""

from __future__ import annotations

import asyncio
import json
import sys

from src.data.client import HyperliquidClient
from src.simulation.engine import CascadeSimulator
from src.simulation.scenarios import build_custom_scenario, get_scenario


async def main():
    if len(sys.argv) < 3:
        print("Usage: python -m src.cli <COIN> <DROP_PCT> [SCENARIO_NAME]")
        print("  Example: python -m src.cli BTC 0.30")
        print("  Example: python -m src.cli BTC 0.30 oct_2025_crash")
        sys.exit(1)

    coin = sys.argv[1].upper()
    drop_pct = float(sys.argv[2])
    scenario_name = sys.argv[3] if len(sys.argv) > 3 else None

    client = HyperliquidClient()
    try:
        # Fetch live market data
        metas, contexts = await client.get_meta_and_contexts()

        # Find the coin
        coin_idx = None
        for i, m in enumerate(metas):
            if m.coin == coin:
                coin_idx = i
                break

        if coin_idx is None:
            print(f"Error: {coin} not found. Available: {', '.join(m.coin for m in metas[:10])}...")
            sys.exit(1)

        meta = metas[coin_idx]
        ctx = contexts[coin_idx]

        # Get order book
        book = await client.get_l2_book(coin)

        # Build scenario
        if scenario_name:
            scenario = get_scenario(scenario_name)
            if not scenario:
                print(f"Error: scenario '{scenario_name}' not found")
                sys.exit(1)
            scenario.coin = coin
            scenario.price_drop_pct = drop_pct
        else:
            scenario = build_custom_scenario(coin, drop_pct, duration_hours=2)

        # Run simulation
        simulator = CascadeSimulator()
        report = simulator.run(
            scenario=scenario,
            mark_price=ctx.mark_price,
            total_oi_usd=ctx.open_interest_usd,
            max_leverage=meta.max_leverage,
            funding_rate=ctx.funding_rate,
            book=book,
        )

        print(json.dumps(report.model_dump(), indent=2))

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
