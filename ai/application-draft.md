# Hyperliquid Builders Program Application

---

**Project Name:**
HyperRisk

**Team lead name and contact (Telegram + email):**
[FILL IN]

**Are you a solo builder or a team?**
Solo

**Team size and brief bio (relevant experience, past projects):**
Solo builder. I've been actively building on Hyperliquid since early 2026. I run a live trading agent (QuantDoctor) in the Degen Claw competition so I know the Hyperliquid API, order book mechanics, and liquidation dynamics from the trading side. I'm also building a perp parameter simulator for another protocol (Pacifica), which gives me a head start on the core simulation math. Before Hyperliquid I built an x402 reliability oracle that won the PayTech hackathon, and a cross-chain privacy bridge with 27 passing tests on devnet. I ship fast using AI-assisted development which means I can move at team-of-3 speed as a solo builder.

**Team Links (GitHub, Twitter/X, website if any):**
GitHub: github.com/yonkoo11

**What are you building? Go into detail.**
HyperRisk is a self-serve parameter stress testing tool for Hyperliquid perpetual futures.

You pick a market (BTC-PERP), choose a crash scenario ("ETH drops 40% in 2 hours"), and the tool simulates the full liquidation cascade. How many positions get margin called, how deep the cascade goes, what the funding rate spike looks like, whether the insurance fund holds, and how much bad debt accumulates.

Today only Gauntlet and Chaos Labs do this kind of analysis. They charge $500K to $2M per year. No protocol under $50M TVL can afford that. With HIP-3 letting anyone deploy perp markets on Hyperliquid, the number of markets needing risk parameter testing is about to grow fast and none of those deployers can afford Gauntlet.

Hyperliquid is the best chain to build this on because the order book is fully on-chain. On AMM-based DEXes you have to guess at liquidity depth using mathematical curves. On Hyperliquid I have real bids and asks at every price level. That means cascade simulation uses actual order book depth instead of synthetic estimates. The accuracy gap is significant.

The tool also uses the liquidation cause field in Hyperliquid's trade history API for validation. I can replay real liquidation events and compare simulated cascades against what actually happened. Thats the feedback loop that makes the model trustworthy over time.

**What category does this fall under?**
Analytics/Data

**Current Stage?**
Idea (architecture designed, core simulation logic prototyped for a different perp protocol. Hyperliquid-specific data intergration not started yet.)

**Demo link or repo if available:**
github.com/Yonkoo11/hyperrisk

**What's your differentiation vs. existing solutions?**
There is no self-serve perp parameter simulation tool. Not for Hyperliquid, not for anyone. Gauntlet does custom engagements at $1.6M/year. Chaos Labs builds risk oracles for specific protocols (Jupiter, GMX). ASXN's dashboard shows real-time Hyperliquid data but cant answer "what happens if BTC drops 30% in one hour." Academic work exists (theres a solid agent-based model paper on arXiv from Jan 2025) but nobody turned it into a useable product.

HyperRisk's edge is Hyperliquid's on-chain order book. Every other chain forces you to model liquidity mathematically. Here I use actual depth. Thats a structural advantage that only exists on Hyperliquid.

**Are you seeking a grant or investment?**
Grant

**How much are you requesting?**
Up to $100,000

**How will funds be used? (brief budget breakdown)**
$60K for 6 months of full development time. $15K for infrastructure (compute for simulations, data storage for historical order book snapshots, API costs). $15K for independent review of the simulation methodology and accuracy validation. $10K buffer for unexpected costs like data gaps that need alternative sourcing or additional compute for backtesting.

**What milestones will you deliver, and on what timeline?**
Month 1-2: Core simulation engine running against real Hyperliquid data. Ingest order book snapshots and trade history. Replay at least one known liquidation cascade and publish accuracy benchmarks. Public demo availble.

Month 3-4: Web interface where anyone can run simulations. Historical replay validation across 5+ events. Accuracy benchmarks published openly. Basic parameter reccomendation engine ("at this depth, your maintenance margin should be X to avoid cascade risk").

Month 5-6: HIP-3 integration. When someone deploys a new perp market they can plug in their proposed parameters and see how they hold up under stress. API endpoint so other builders (dashboards, risk tools, frontends) can pull simulation data. Documenation and open-source release.

**Have you received other grants or investments?**
Won the x402 PayTech hackathon (Faktory, an AI treasury agent). Multiple hackathon builds across Hyperliquid, Starknet, Stellar, and Pacifica. No institutional funding to date.

**Are you building full-time or part-time on this?**
Part-time currently, transitioning to more hours as the grant milestones ramp up. I'm realistic about this: the first two months are data ingestion and core engine work which fits a part-time schedule well. Months 3-6 require more sustained effort as the product matures.

**Will the project be open or closed source?**
Open-source

**How does this make the Hyperliquid ecosystem more resilient or valuable?**
HIP-3 is one of Hyperliquid's biggest growth vectors. Anyone being able to deploy a perp market is powerful but it also means someone will deploy a market with bad parameters. One ugly cascade event on a poorly parameterized HIP-3 market hurts the whole ecosystems reputation. HyperRisk makes HIP-3 safer by letting deployers stress test their parameters before going live. Its the safety net that makes permissionless market creation actually work.

Beyond HIP-3 the tool benefits existing markets too. Validators, large traders, and the Hyperliquid team itself can use it to model tail risk scenarios and evaluate parameter change proposals with data instead of intuition. Better risk managment across the board means fewer blowups which means more institutional confidence which means more volume.

**What does success look like in 3 months? 6 months?**
3 months: Working simulation engine that accurately replays at least 3 major Hyperliquid liquidation events within 20% of actual cascade volume. At least 5 builders or deployers using it for parameter testing. Public accuracy benchmarks that anyone can verify.

6 months: Full web tool with historical replay, parameter recommendation engine, and a public API. 20+ regular users. At least one HIP-3 deployer used HyperRisk to set their initial parameters before going live. The simulation methodology has been reviewed by atleast one independent risk researcher.

**Anything else you want us to know?**
I'm already deep in the Hyperliquid ecosystem. I run a live trading agent in Degen Claw so I'm not someone who just showed up for grant money. I've seen the order book from the trading side, watched liquidation cascades happen in real time, and know where the data gaps are. That domain knowledge matters more than just writing simulation code.

I'm also building something similar for Pacifica's hackathon right now which means the core simulation math will be battle-tested on a different protocol before I even start the Hyperliquid-specific work. The Hyperliquid version will be better because of the on-chain order book advantage but the underlying cascade modeling will already be validated.

**How did you hear about this program?**
Twitter/X
