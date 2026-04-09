# HyperRisk - AI Memory

## Phase 1 Gate (MUST PASS BEFORE ANY OTHER WORK)
Core Action: User picks a Hyperliquid perp market + historical crash scenario, gets a liquidation cascade simulation showing bad debt accumulation
Success Test: Replay a known Hyperliquid liquidation event (e.g., large BTC/ETH dump) and produce a cascade report that's directionally accurate (order of magnitude correct on liquidation volume)
Min Tech: Python (FastAPI) + Hyperliquid API (order book snapshots, trade history with `cause` field for liquidations)
NOT Phase 1: Web UI, real-time monitoring, parameter recommendations, multi-market simulation, HIP-3 integrations, landing page, design polish
Status: [ ] NOT STARTED

## Hackathon / Grant Context
- **Program:** Hyperliquid Builders Program (rolling grants/investments, no deadline)
- **Category:** Analytics/Data
- **Funding ask:** $100K grant (6 months, milestone-based)
- **Evaluation:** Personal review, no rubric. They want "real, resilient infrastructure and tooling."
- **Application:** https://docs.google.com/forms/d/e/1FAIpQLScJ8ZueDUSQtQaiQ1-8-sgEiAoaAt-iqKAvN1o2kX5sbwlGvA/viewform

## Chosen Idea
**#5 from research base (Tier 1): DeFi Parameter Simulation adapted for Hyperliquid perps**
- Self-serve Gauntlet. What they charge $1.6M/year for, built for the Hyperliquid ecosystem.
- Platform-native advantage: Hyperliquid's fully on-chain order book (200K orders/sec) enables simulation with REAL depth data, not synthetic AMM curves.
- HIP-3 (builder-deployed perps) creates growing demand - more markets need parameter testing.

## Competitive Landscape
- **Gauntlet / Chaos Labs:** Enterprise-only, $500K-$2M/year. Won't serve small protocols.
- **ASXN Dashboard:** Real-time metrics, liquidations, risk. But no simulation/what-if analysis.
- **HyperTracker:** Wallet behavior tracking. Different product.
- **Flowscan:** Builder code analytics. Different product.
- **Gap:** Zero self-serve parameter simulation tools for Hyperliquid.

## Fatal Flaws to Watch
1. Hyperliquid team could build this internally (they have the data)
2. API may not expose all needed data (insurance fund levels, long/short ratio)
3. Order book depth snapshots may not be historically available
4. Accuracy depends on modeling assumptions about hidden liquidity

## Related Projects
- **Pacifica RiskLab** (~/Projects/pacifica-risklab) - Same core idea, different chain (Pacifica). Shares simulation engine concepts. Deadline Apr 16.
- **Degen Claw** (~/Projects/degen-claw) - Trading agent on Hyperliquid. Shows ecosystem commitment.

## Tech Stack
- Backend: Python (FastAPI)
- Frontend: Svelte + Vite
- Data: Hyperliquid API (REST + WebSocket), daily trade logs (LZ4 compressed)
- Key API endpoints: order book snapshots, trade history (has liquidation `cause` field), funding rate history

## Deliverables for Grant Application
- Working demo or prototype link
- GitHub repo
- Milestones + timeline document
- Budget breakdown
- 3-month and 6-month success metrics

## Decisions
- (none yet)
