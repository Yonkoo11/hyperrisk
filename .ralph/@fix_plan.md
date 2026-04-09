# Fix Plan - HyperRisk

## Tasks

- [ ] Task 1: Explore Hyperliquid API and document available endpoints
  - Acceptance: Written summary of endpoints for order book, trade history (with liquidation cause), funding rates, and any historical data availability
  - Files: ai/api-notes.md

- [ ] Task 2: Build data ingestion module for Hyperliquid trade history
  - Acceptance: Script fetches last 7 days of trades for BTC-PERP, parses liquidation events, stores in local SQLite
  - Files: src/data/ingest.py, src/data/models.py

- [ ] Task 3: Build order book snapshot collector
  - Acceptance: Script captures current order book depth for a given market, stores snapshots at configurable intervals
  - Files: src/data/orderbook.py

- [ ] Task 4: Build basic liquidation cascade simulator
  - Acceptance: Given a price drop %, current positions (from API), and order book depth, outputs estimated liquidation volume and cascade depth
  - Files: src/simulation/cascade.py

- [ ] Task 5: Create historical crash replay module
  - Acceptance: Feed in a date range, replay price action, compare simulated liquidations vs actual liquidations (from trade history cause field). Output: "simulated X liquidations, actual Y, accuracy Z%"
  - Files: src/simulation/replay.py

- [ ] Task 6: Build FastAPI endpoint for Phase 1 core action
  - Acceptance: POST /simulate with market + scenario params, returns JSON with cascade report
  - Files: src/api/main.py, src/api/routes.py

- [ ] Task 7: Validate against known event
  - Acceptance: Pick a real Hyperliquid liquidation cascade, replay it, document accuracy
  - Files: tests/test_replay_accuracy.py, ai/validation-results.md

## Completed
(builder fills this in)
