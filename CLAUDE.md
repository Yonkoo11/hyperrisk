# Vibecoder Mode - Paste this into any project's CLAUDE.md

## Communication Rules
- Never say: branch, commit, merge, PR, push, pull, HEAD, diff, npm, deploy, lint, daemon, env var
- Instead say: version, save point, combine changes, publish, update, latest, changes, install, check code
- Never show raw terminal output. Summarize in one sentence.
- Never show error messages directly. Say what happened and what you're doing to fix it.
- When done, describe what changed by what the user would SEE in the app, not what files changed.

## Behavior Rules
- Auto-save after every completed task (git add specific files + commit). Never ask "should I commit?"
- If you need to create a version, just do it silently.
- If tests fail, fix them without explaining test frameworks.
- After each task: update ai/progress.md with a "What Changed (Plain English)" section.
- Keep all explanations to 1-3 sentences. If the user wants more detail, they'll ask.

---

# HyperRisk - Perp Parameter Stress Testing for Hyperliquid

## What This Is
Self-serve risk simulation for Hyperliquid perpetual futures markets. Users pick a market + crash scenario, get a liquidation cascade report showing bad debt, margin calls, and parameter recommendations.

## Phase 1 Gate (MUST PASS BEFORE ANY OTHER WORK)
Core Action: User picks a Hyperliquid perp market + historical crash scenario, gets a liquidation cascade simulation
Success Test: Replay a known liquidation event and produce a directionally accurate cascade report
NOT Phase 1: Web UI polish, real-time monitoring, parameter recommendations, multi-market sim, HIP-3 integration, landing page

## Build Order (ENFORCED)
1. Core action works (simulation engine produces output for one market + one scenario)
2. Data flows (real Hyperliquid API data, not mocks)
3. Product complete (all grant-demo features functional)
4. Visual polish LAST

## Tech Stack
- Backend: Python (FastAPI)
- Frontend: Svelte + Vite
- Data: Hyperliquid API (order book, trades with liquidation cause field, funding rates)

## Grant Context
- Program: Hyperliquid Builders Program (rolling, no deadline)
- Category: Analytics/Data
- Funding: $100K grant request
- Key angle: On-chain order book makes simulations uniquely accurate vs AMM-based DEXes

## Related
- Pacifica RiskLab (~/Projects/pacifica-risklab) shares the simulation concept for a different chain
- Degen Claw (~/Projects/degen-claw) is our trading agent on Hyperliquid
