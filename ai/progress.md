# HyperRisk - Progress

## Session: 2026-04-09

### What Changed (Plain English)
Built the entire HyperRisk prototype from scratch in one session:
- The app connects to Hyperliquid's live data (prices, open interest, order book depth)
- You pick a market (like BTC) and a crash scenario (like "30% drop in 2 hours")
- It simulates what would happen: how many traders get liquidated, how deep the cascade goes, whether the insurance fund holds
- Results show up with charts in a web interface
- 17 tests all passing

### What's Done
- [x] Session 1: Data layer (API client, models, caching, 5 tests)
- [x] Session 2: Simulation engine (positions, order book, scenarios, cascade loop, CLI)
- [x] Session 3: FastAPI server (/simulate, /markets, /scenarios, 5 integration tests)
- [x] Session 4: Svelte frontend (market picker, scenario cards, results with charts)
- [x] README with setup instructions

### What's Next
- Push to GitHub
- October 2025 validation (replay real crash, document accuracy)
- Submit grant application with working demo link
- Tune parameters against real events

### Current State
- Backend: fully functional, 17/17 tests pass
- Frontend: builds clean, all components wired
- CLI: `python -m src.cli BTC 0.30` produces cascade report
- Sample output: BTC 30% crash -> 9 rounds, $842M liquidation volume, backstop triggered
