# HyperRisk

Liquidation cascade simulator for Hyperliquid perpetual futures.

Pick a market, pick a crash scenario, see what happens. How many positions get margin called, how deep the cascade goes, whether the insurance fund holds, and how much bad debt piles up.

## Why this exists

Every perp market needs risk parameter testing. Gauntlet charges $1.6M/year. With HIP-3 letting anyone deploy perp markets on Hyperliquid, the number of markets needing this will grow fast. HyperRisk is the self-serve alternative.

Hyperliquid's fully on-chain order book means simulations use real depth data instead of synthetic AMM curves.

## Quick start

**Backend:**
```bash
cd ~/Projects/hyperrisk
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.server:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, select a market, pick a scenario, click Run.

**CLI (no frontend needed):**
```bash
python -m src.cli BTC 0.30
```

## API

- `GET /health` - status check
- `GET /markets` - all Hyperliquid perp markets with OI, funding, leverage
- `GET /scenarios` - pre-built crash scenarios
- `POST /simulate` - run a cascade simulation

```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"coin":"BTC","scenario":"btc_30pct_2h"}'
```

## How it works

1. Fetches live market data from Hyperliquid (OI, funding rate, order book depth)
2. Generates 10,000 synthetic positions using Pareto distribution (matches empirical crypto position size distributions)
3. Applies the crash scenario as a price path
4. At each price step: checks which positions breach maintenance margin, calculates liquidation volume, models order book impact, checks for secondary liquidations
5. Models the 3-stage Hyperliquid liquidation pipeline: market orders -> backstop (HLP vault) -> ADL

Key tuning parameters:
- `book_thinning_factor` (default 0.5): how much liquidity remains during stress. Market makers pull orders.
- `pareto_alpha` (default 1.5): shape of position size distribution. Lower = more whales.
- `backstop_capacity_pct` (default 0.05): HLP vault capacity as fraction of total OI.

## Tests

```bash
pytest tests/ -v
```

17 tests covering API client, simulation math, and FastAPI endpoints.

## Project structure

```
src/
  data/
    client.py      - Hyperliquid API client (httpx, no SDK needed)
    models.py      - Pydantic data models
    collector.py   - SQLite cache layer
  simulation/
    engine.py      - Cascade loop (the core)
    positions.py   - Synthetic position distribution
    orderbook.py   - Order book impact model
    scenarios.py   - Pre-built + custom crash scenarios
  api/
    server.py      - FastAPI app
    routes.py      - API endpoints
  cli.py           - CLI runner
frontend/          - Svelte + Vite
```

## Limitations

- Position distribution is synthetic. We can't see real individual positions.
- Order book snapshot is current state, not historical. The `book_thinning_factor` compensates for this.
- No insurance fund data from API. Backstop capacity is estimated.
- Funding rate impact during cascade is not yet modeled.
