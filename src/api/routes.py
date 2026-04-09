"""API routes for HyperRisk."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from src.data.models import CascadeReport, SimulationRequest
from src.simulation.engine import CascadeSimulator, SimulationConfig
from src.simulation.scenarios import (
    build_custom_scenario,
    get_scenario,
    list_scenarios,
)

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@router.get("/markets")
async def markets(request: Request):
    client = request.app.state.hl_client
    metas, contexts = await client.get_meta_and_contexts()

    result = []
    for m, c in zip(metas, contexts):
        if c.open_interest <= 0:
            continue
        result.append({
            "coin": m.coin,
            "mark_price": c.mark_price,
            "open_interest_usd": c.open_interest_usd,
            "funding_rate": c.funding_rate,
            "max_leverage": m.max_leverage,
            "day_volume": c.day_volume,
        })

    # Sort by OI descending
    result.sort(key=lambda x: x["open_interest_usd"], reverse=True)
    return result


@router.get("/scenarios")
async def scenarios_list():
    return list_scenarios()


@router.post("/simulate", response_model=CascadeReport)
async def simulate(req: SimulationRequest, request: Request):
    client = request.app.state.hl_client

    # Fetch market data
    metas, contexts = await client.get_meta_and_contexts()

    coin_idx = None
    for i, m in enumerate(metas):
        if m.coin == req.coin.upper():
            coin_idx = i
            break

    if coin_idx is None:
        raise HTTPException(status_code=404, detail=f"Market {req.coin} not found")

    meta = metas[coin_idx]
    ctx = contexts[coin_idx]

    # Fetch order book
    book = await client.get_l2_book(req.coin.upper())

    # Build scenario
    if req.scenario == "custom":
        if not req.custom_drop_pct:
            raise HTTPException(status_code=400, detail="custom_drop_pct required for custom scenario")
        scenario = build_custom_scenario(
            req.coin.upper(),
            req.custom_drop_pct,
            req.custom_duration_hours or 2.0,
        )
    else:
        scenario = get_scenario(req.scenario)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario {req.scenario} not found")
        # Override coin if specified differently
        scenario.coin = req.coin.upper()
        if req.custom_drop_pct:
            scenario.price_drop_pct = req.custom_drop_pct

    # Build config with any overrides
    config_kwargs = {}
    if req.config_overrides:
        for key in ["book_thinning_factor", "position_count", "backstop_capacity_pct", "pareto_alpha"]:
            if key in req.config_overrides:
                config_kwargs[key] = req.config_overrides[key]

    config = SimulationConfig(**config_kwargs)
    simulator = CascadeSimulator(config)

    report = simulator.run(
        scenario=scenario,
        mark_price=ctx.mark_price,
        total_oi_usd=ctx.open_interest_usd,
        max_leverage=meta.max_leverage,
        funding_rate=ctx.funding_rate,
        book=book,
    )

    return report
