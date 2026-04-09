"""Pre-built and custom crash scenarios for cascade simulation."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class CrashScenario:
    name: str
    description: str
    coin: str
    price_drop_pct: float  # 0.30 = 30% drop
    duration_hours: float
    # Normalized price path: list of fractions of starting price (1.0 -> 0.7 for 30% drop)
    # If empty, engine generates linear or exponential descent
    price_path: list[float] = field(default_factory=list)
    date: str = ""  # YYYY-MM-DD for historical events


# Pre-built scenarios
SCENARIOS: dict[str, CrashScenario] = {
    "oct_2025_crash": CrashScenario(
        name="oct_2025_crash",
        description="October 2025 crypto crash. $19B OI erased, $2.1B ADL. 36h cascade.",
        coin="BTC",
        price_drop_pct=0.30,
        duration_hours=36,
        date="2025-10-10",
    ),
    "btc_30pct_2h": CrashScenario(
        name="btc_30pct_2h",
        description="Hypothetical BTC flash crash: 30% in 2 hours.",
        coin="BTC",
        price_drop_pct=0.30,
        duration_hours=2,
    ),
    "btc_15pct_1h": CrashScenario(
        name="btc_15pct_1h",
        description="Moderate BTC dip: 15% in 1 hour.",
        coin="BTC",
        price_drop_pct=0.15,
        duration_hours=1,
    ),
    "eth_40pct_4h": CrashScenario(
        name="eth_40pct_4h",
        description="Hypothetical ETH crash: 40% in 4 hours.",
        coin="ETH",
        price_drop_pct=0.40,
        duration_hours=4,
    ),
}


def get_scenario(name: str) -> CrashScenario | None:
    return SCENARIOS.get(name)


def list_scenarios() -> list[dict]:
    return [
        {
            "name": s.name,
            "description": s.description,
            "coin": s.coin,
            "price_drop_pct": s.price_drop_pct,
            "duration_hours": s.duration_hours,
        }
        for s in SCENARIOS.values()
    ]


def build_custom_scenario(
    coin: str, drop_pct: float, duration_hours: float
) -> CrashScenario:
    return CrashScenario(
        name="custom",
        description=f"Custom: {coin} drops {drop_pct*100:.0f}% in {duration_hours}h",
        coin=coin,
        price_drop_pct=drop_pct,
        duration_hours=duration_hours,
    )


def generate_price_path(
    scenario: CrashScenario, n_steps: int = 50
) -> list[float]:
    """Generate a normalized price path if one isn't provided.

    Returns list of fractions of starting price.
    Uses exponential decay (crashes accelerate, not linear).
    """
    if scenario.price_path:
        return scenario.price_path

    # Exponential descent: price = e^(-k*t) where k chosen to hit target
    target = 1.0 - scenario.price_drop_pct
    t = np.linspace(0, 1, n_steps)
    # solve: e^(-k) = target => k = -ln(target)
    k = -np.log(max(target, 0.01))
    path = np.exp(-k * t)
    return path.tolist()
