<script lang="ts">
  import MarketPicker from "./lib/MarketPicker.svelte";
  import ScenarioSelector from "./lib/ScenarioSelector.svelte";
  import CascadeResults from "./lib/CascadeResults.svelte";
  import { runSimulation, type CascadeReport } from "./lib/api";

  let selectedCoin = "BTC";
  let scenario = "btc_30pct_2h";
  let customDrop = 30;
  let customHours = 2;
  let report: CascadeReport | null = null;
  let loading = false;
  let error = "";

  async function handleRun() {
    loading = true;
    error = "";
    report = null;

    try {
      const params: any = {
        coin: selectedCoin,
        scenario,
      };
      if (scenario === "custom") {
        params.custom_drop_pct = customDrop / 100;
        params.custom_duration_hours = customHours;
      }
      report = await runSimulation(params);
    } catch (e: any) {
      error = e.message || "Simulation failed";
    }
    loading = false;
  }
</script>

<main>
  <header>
    <h1>HyperRisk</h1>
    <p class="subtitle">Liquidation cascade simulator for Hyperliquid perps</p>
  </header>

  <div class="layout">
    <aside>
      <MarketPicker bind:selected={selectedCoin} />
      <ScenarioSelector
        bind:scenario
        bind:customDrop
        bind:customHours
      />
      <button class="run-btn" on:click={handleRun} disabled={loading}>
        {loading ? "Simulating..." : "Run Simulation"}
      </button>
    </aside>

    <section class="main-area">
      {#if error}
        <div class="error">{error}</div>
      {/if}

      {#if loading}
        <div class="spinner-container">
          <div class="spinner"></div>
          <p>Running cascade simulation...</p>
        </div>
      {/if}

      <CascadeResults {report} />

      {#if !report && !loading && !error}
        <div class="empty">
          <p>Select a market and scenario, then click <strong>Run Simulation</strong>.</p>
          <p class="hint">
            The simulator models liquidation cascades using real Hyperliquid order book
            depth and a synthetic position distribution based on current open interest.
          </p>
        </div>
      {/if}
    </section>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    background: #0f0f1a;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }
  header {
    text-align: center;
    margin-bottom: 2rem;
  }
  h1 {
    font-size: 2rem;
    margin: 0;
    background: linear-gradient(135deg, #7c5cff, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .subtitle {
    color: #888;
    margin: 0.3rem 0 0;
    font-size: 0.9rem;
  }
  .layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 2rem;
    align-items: start;
  }
  aside {
    position: sticky;
    top: 1rem;
  }
  .run-btn {
    width: 100%;
    padding: 0.8rem;
    background: linear-gradient(135deg, #7c5cff, #5a3fcc);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  .run-btn:hover:not(:disabled) {
    opacity: 0.9;
  }
  .run-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .error {
    background: rgba(244, 67, 54, 0.15);
    border: 1px solid #f44336;
    border-radius: 6px;
    padding: 0.8rem;
    color: #f44336;
    margin-bottom: 1rem;
  }
  .spinner-container {
    text-align: center;
    padding: 3rem 0;
    color: #888;
  }
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #333;
    border-top-color: #7c5cff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1rem;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .empty {
    text-align: center;
    padding: 4rem 2rem;
    color: #666;
  }
  .empty p {
    margin: 0.5rem 0;
  }
  .hint {
    font-size: 0.85rem;
    max-width: 500px;
    margin: 0.8rem auto 0;
  }
  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
    }
    aside {
      position: static;
    }
  }
</style>
