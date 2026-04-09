<script lang="ts">
  import { onMount } from "svelte";
  import type { CascadeReport } from "./api";
  import Chart from "chart.js/auto";

  export let report: CascadeReport | null = null;

  let priceCanvas: HTMLCanvasElement;
  let volumeCanvas: HTMLCanvasElement;
  let priceChart: Chart | null = null;
  let volumeChart: Chart | null = null;

  function fmt(n: number): string {
    if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(0)}K`;
    return `$${n.toFixed(0)}`;
  }

  function stageColor(stage: string): string {
    if (stage === "market") return "#4caf50";
    if (stage === "backstop") return "#ff9800";
    return "#f44336"; // adl
  }

  $: if (report && priceCanvas && volumeCanvas) {
    renderCharts();
  }

  function renderCharts() {
    if (!report || !report.rounds.length) return;

    const labels = report.rounds.map((r) => `R${r.round_number}`);

    // Price chart
    if (priceChart) priceChart.destroy();
    priceChart = new Chart(priceCanvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Price",
            data: report.rounds.map((r) => r.price_after),
            borderColor: "#7c5cff",
            backgroundColor: "rgba(124,92,255,0.1)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            title: { display: true, text: "Price ($)", color: "#888" },
            ticks: { color: "#888" },
            grid: { color: "#222" },
          },
          x: { ticks: { color: "#888" }, grid: { color: "#222" } },
        },
      },
    });

    // Volume chart
    if (volumeChart) volumeChart.destroy();
    volumeChart = new Chart(volumeCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Liquidation Volume",
            data: report.rounds.map((r) => r.liquidation_volume_usd),
            backgroundColor: report.rounds.map((r) => stageColor(r.stage)),
            borderRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            title: { display: true, text: "Volume ($)", color: "#888" },
            ticks: {
              color: "#888",
              callback: (v) => fmt(Number(v)),
            },
            grid: { color: "#222" },
          },
          x: { ticks: { color: "#888" }, grid: { color: "#222" } },
        },
      },
    });
  }
</script>

{#if report}
  <div class="results">
    <div class="summary-grid">
      <div class="stat">
        <span class="stat-label">Liquidation Volume</span>
        <span class="stat-value">{fmt(report.total_liquidation_volume_usd)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Cascade Rounds</span>
        <span class="stat-value">{report.cascade_rounds}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Price Drop</span>
        <span class="stat-value">{(report.price_drop_pct * 100).toFixed(1)}%</span>
      </div>
      <div class="stat">
        <span class="stat-label">Bad Debt</span>
        <span class="stat-value">{fmt(report.bad_debt_usd)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Final Price</span>
        <span class="stat-value">${report.final_price.toLocaleString()}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Backstop</span>
        <span class="stat-value" class:danger={report.backstop_triggered}>
          {report.backstop_triggered ? "TRIGGERED" : "Safe"}
        </span>
      </div>
    </div>

    {#if report.adl_triggered}
      <div class="alert">
        ADL TRIGGERED: Insurance fund exhausted. Profitable traders would be force-closed.
      </div>
    {/if}

    {#if report.warnings.length}
      {#each report.warnings as w}
        <div class="warning">{w}</div>
      {/each}
    {/if}

    <div class="charts">
      <div class="chart-box">
        <h3>Price Cascade</h3>
        <canvas bind:this={priceCanvas}></canvas>
      </div>
      <div class="chart-box">
        <h3>Liquidation Volume by Round</h3>
        <canvas bind:this={volumeCanvas}></canvas>
      </div>
    </div>

    <div class="legend">
      <span class="dot" style="background:#4caf50"></span> Market
      <span class="dot" style="background:#ff9800"></span> Backstop
      <span class="dot" style="background:#f44336"></span> ADL
    </div>
  </div>
{/if}

<style>
  .results {
    margin-top: 1.5rem;
  }
  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 0.8rem;
    margin-bottom: 1.5rem;
  }
  .stat {
    background: #1a1a2e;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 0.8rem;
  }
  .stat-label {
    display: block;
    font-size: 0.7rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.3rem;
  }
  .stat-value {
    font-size: 1.2rem;
    font-weight: 700;
    color: #e0e0e0;
  }
  .stat-value.danger {
    color: #ff9800;
  }
  .alert {
    background: rgba(244, 67, 54, 0.15);
    border: 1px solid #f44336;
    border-radius: 6px;
    padding: 0.8rem;
    color: #f44336;
    font-weight: 600;
    margin-bottom: 1rem;
    font-size: 0.85rem;
  }
  .warning {
    background: rgba(255, 152, 0, 0.1);
    border: 1px solid #ff9800;
    border-radius: 6px;
    padding: 0.6rem;
    color: #ff9800;
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
  }
  .charts {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  .chart-box {
    background: #1a1a2e;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 1rem;
  }
  .chart-box h3 {
    font-size: 0.8rem;
    color: #888;
    margin: 0 0 0.8rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .legend {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-top: 1rem;
    font-size: 0.75rem;
    color: #888;
  }
  .dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
</style>
