const API_BASE = "http://localhost:8000";

export interface Market {
  coin: string;
  mark_price: number;
  open_interest_usd: number;
  funding_rate: number;
  max_leverage: number;
  day_volume: number;
}

export interface Scenario {
  name: string;
  description: string;
  coin: string;
  price_drop_pct: number;
  duration_hours: number;
}

export interface CascadeRound {
  round_number: number;
  price_before: number;
  price_after: number;
  liquidation_volume_usd: number;
  positions_liquidated: number;
  book_absorption_pct: number;
  cumulative_bad_debt: number;
  stage: string;
}

export interface CascadeReport {
  coin: string;
  scenario_name: string;
  starting_price: number;
  final_price: number;
  price_drop_pct: number;
  total_liquidation_volume_usd: number;
  cascade_rounds: number;
  bad_debt_usd: number;
  backstop_triggered: boolean;
  adl_triggered: boolean;
  rounds: CascadeRound[];
  parameters_used: Record<string, number>;
  warnings: string[];
}

export async function fetchMarkets(): Promise<Market[]> {
  const resp = await fetch(`${API_BASE}/markets`);
  return resp.json();
}

export async function fetchScenarios(): Promise<Scenario[]> {
  const resp = await fetch(`${API_BASE}/scenarios`);
  return resp.json();
}

export async function runSimulation(params: {
  coin: string;
  scenario: string;
  custom_drop_pct?: number;
  custom_duration_hours?: number;
}): Promise<CascadeReport> {
  const resp = await fetch(`${API_BASE}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || "Simulation failed");
  }
  return resp.json();
}
