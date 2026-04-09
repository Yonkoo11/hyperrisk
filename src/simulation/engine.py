"""Cascade simulation engine for Hyperliquid perpetual futures.

This is the core product. Models the 3-stage liquidation cascade:
1. Market liquidation: equity < maintenance margin, market orders to book
2. Backstop: equity < 2/3 maint margin, HLP vault absorbs
3. ADL: HLP exhausted, profitable traders forcibly closed

The engine uses a synthetic position distribution (we can't see real positions)
and real order book depth to simulate cascading liquidations during a crash.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.data.models import CascadeReport, CascadeRound, OrderBookSnapshot
from src.simulation.orderbook import OrderBookImpactModel
from src.simulation.positions import PositionDistConfig, PositionDistribution
from src.simulation.scenarios import CrashScenario, generate_price_path


@dataclass
class SimulationConfig:
    book_thinning_factor: float = 0.5
    max_rounds: int = 50
    max_sub_rounds: int = 3  # secondary liquidation rounds per price step
    large_position_threshold_usd: float = 100_000
    large_position_first_pct: float = 0.20  # 20% liquidated initially
    backstop_capacity_pct: float = 0.05  # HLP vault ~ 5% of OI
    position_count: int = 10_000
    price_steps: int = 50
    pareto_alpha: float = 1.5
    seed: int | None = 42


class CascadeSimulator:
    """Runs cascade simulation for a given market state and crash scenario."""

    def __init__(self, config: SimulationConfig | None = None):
        self.config = config or SimulationConfig()

    def run(
        self,
        scenario: CrashScenario,
        mark_price: float,
        total_oi_usd: float,
        max_leverage: int,
        funding_rate: float,
        book: OrderBookSnapshot,
    ) -> CascadeReport:
        cfg = self.config

        # Build models
        pos_config = PositionDistConfig(
            n_positions=cfg.position_count,
            pareto_alpha=cfg.pareto_alpha,
            seed=cfg.seed,
        )
        positions = PositionDistribution(
            total_oi_usd=total_oi_usd,
            mark_price=mark_price,
            max_leverage=max_leverage,
            funding_rate=funding_rate,
            config=pos_config,
        )
        book_model = OrderBookImpactModel(book, cfg.book_thinning_factor)

        # Generate price path
        price_path = generate_price_path(scenario, cfg.price_steps)

        # Run cascade
        rounds: list[CascadeRound] = []
        cumulative_bad_debt = 0.0
        total_liq_volume = 0.0
        backstop_remaining = total_oi_usd * cfg.backstop_capacity_pct
        backstop_triggered = False
        adl_triggered = False
        current_price = mark_price

        for step_idx, price_fraction in enumerate(price_path):
            if step_idx >= cfg.max_rounds:
                break

            new_price = mark_price * price_fraction

            # Skip if price hasn't changed meaningfully
            if abs(new_price - current_price) / current_price < 0.001:
                continue

            step_liq_volume = 0.0
            step_positions_liq = 0
            step_stage = "market"

            # Main liquidation check + sub-rounds for secondary cascade
            check_price = new_price
            for sub_round in range(cfg.max_sub_rounds + 1):
                at_risk = positions.get_positions_at_risk(check_price)

                if at_risk["count"] == 0:
                    break

                # Apply large position rule: >100K positions only 20% first round
                liq_volume = at_risk["total_volume_usd"]
                large_mask = at_risk["sizes_usd"] > cfg.large_position_threshold_usd
                if large_mask.any() and sub_round == 0:
                    large_vol = float(at_risk["sizes_usd"][large_mask].sum())
                    reduction = large_vol * (1.0 - cfg.large_position_first_pct)
                    liq_volume -= reduction

                # Net selling pressure (in a crash, longs dominate liquidations)
                net_sell = at_risk["long_volume_usd"] - at_risk["short_volume_usd"]

                # Market impact from liquidation volume
                if abs(net_sell) > 0:
                    impact = book_model.price_impact_for_volume(
                        abs(net_sell), "sell" if net_sell > 0 else "buy"
                    )
                else:
                    impact = 0.0

                # Calculate bad debt for this round
                # Simplified: bad debt occurs when positions are so underwater
                # that their remaining equity is negative after liquidation
                # Estimate: positions with > 20x leverage in a > 10% crash
                # generate ~2% of their notional as bad debt
                high_lev_mask = at_risk["leverages"] > 15
                if high_lev_mask.any():
                    high_lev_vol = float(at_risk["sizes_usd"][high_lev_mask].sum())
                    price_move = abs(check_price - mark_price) / mark_price
                    bad_debt_this_round = high_lev_vol * price_move * 0.1
                else:
                    bad_debt_this_round = 0.0

                # Determine stage
                if bad_debt_this_round > 0:
                    if backstop_remaining > 0:
                        absorbed = min(bad_debt_this_round, backstop_remaining)
                        backstop_remaining -= absorbed
                        bad_debt_this_round -= absorbed
                        step_stage = "backstop"
                        backstop_triggered = True
                    else:
                        step_stage = "adl"
                        adl_triggered = True

                cumulative_bad_debt += bad_debt_this_round
                step_liq_volume += liq_volume
                step_positions_liq += at_risk["count"]

                # Mark positions as liquidated
                positions.mark_liquidated(at_risk["indices"])

                # Secondary price impact (clamped to prevent runaway)
                impact = min(impact, 0.10)  # cap at 10% per sub-round
                if impact > 0.001 and sub_round < cfg.max_sub_rounds:
                    if net_sell > 0:
                        check_price *= (1.0 - impact)
                    else:
                        check_price *= (1.0 + impact)
                    # Floor: never below 1% of starting price
                    check_price = max(check_price, mark_price * 0.01)
                else:
                    break

            if step_liq_volume > 0:
                total_liq_volume += step_liq_volume
                book_depth = book.bid_depth_usd or 1.0
                absorption = min(1.0, book_depth * cfg.book_thinning_factor / step_liq_volume)

                rounds.append(CascadeRound(
                    round_number=len(rounds) + 1,
                    price_before=current_price,
                    price_after=check_price,
                    liquidation_volume_usd=step_liq_volume,
                    positions_liquidated=step_positions_liq,
                    book_absorption_pct=absorption,
                    cumulative_bad_debt=cumulative_bad_debt,
                    stage=step_stage,
                ))

            current_price = check_price

        # Compile report
        final_price = current_price
        actual_drop = (mark_price - final_price) / mark_price if mark_price > 0 else 0

        warnings = []
        if total_liq_volume == 0:
            warnings.append("No liquidations triggered. Drop may be too small for current leverage distribution.")
        if adl_triggered:
            warnings.append("ADL triggered: HLP vault exhausted. Profitable traders would be force-closed.")

        return CascadeReport(
            coin=scenario.coin,
            scenario_name=scenario.name,
            starting_price=mark_price,
            final_price=final_price,
            price_drop_pct=actual_drop,
            total_liquidation_volume_usd=total_liq_volume,
            cascade_rounds=len(rounds),
            bad_debt_usd=cumulative_bad_debt,
            backstop_triggered=backstop_triggered,
            adl_triggered=adl_triggered,
            rounds=rounds,
            parameters_used={
                "book_thinning_factor": cfg.book_thinning_factor,
                "position_count": cfg.position_count,
                "pareto_alpha": cfg.pareto_alpha,
                "backstop_capacity_pct": cfg.backstop_capacity_pct,
                "large_position_threshold_usd": cfg.large_position_threshold_usd,
            },
            warnings=warnings,
        )
