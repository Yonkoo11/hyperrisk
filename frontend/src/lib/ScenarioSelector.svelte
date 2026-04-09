<script lang="ts">
  export let scenario: string = "btc_30pct_2h";
  export let customDrop: number = 30;
  export let customHours: number = 2;

  const presets = [
    { name: "btc_30pct_2h", label: "Flash Crash", desc: "30% in 2 hours" },
    { name: "btc_15pct_1h", label: "Moderate Dip", desc: "15% in 1 hour" },
    { name: "eth_40pct_4h", label: "ETH Crash", desc: "40% in 4 hours" },
    { name: "oct_2025_crash", label: "Oct 2025", desc: "Historical cascade" },
    { name: "custom", label: "Custom", desc: "Your parameters" },
  ];
</script>

<div class="scenarios">
  <label>Scenario</label>
  <div class="cards">
    {#each presets as p}
      <button
        class="card"
        class:active={scenario === p.name}
        on:click={() => (scenario = p.name)}
      >
        <span class="card-label">{p.label}</span>
        <span class="card-desc">{p.desc}</span>
      </button>
    {/each}
  </div>

  {#if scenario === "custom"}
    <div class="custom-controls">
      <div class="slider-group">
        <label for="drop">Drop: {customDrop}%</label>
        <input id="drop" type="range" min="5" max="80" step="5" bind:value={customDrop} />
      </div>
      <div class="slider-group">
        <label for="hours">Duration: {customHours}h</label>
        <input id="hours" type="range" min="0.5" max="48" step="0.5" bind:value={customHours} />
      </div>
    </div>
  {/if}
</div>

<style>
  .scenarios {
    margin-bottom: 1.5rem;
  }
  label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.4rem;
    color: #e0e0e0;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.5rem;
  }
  .card {
    padding: 0.6rem;
    background: #1a1a2e;
    border: 1px solid #333;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    color: #ccc;
    transition: border-color 0.15s, background 0.15s;
  }
  .card:hover {
    border-color: #556;
  }
  .card.active {
    border-color: #7c5cff;
    background: #1e1e3a;
  }
  .card-label {
    display: block;
    font-weight: 600;
    font-size: 0.85rem;
    color: #e0e0e0;
  }
  .card-desc {
    display: block;
    font-size: 0.75rem;
    color: #888;
    margin-top: 0.2rem;
  }
  .custom-controls {
    margin-top: 0.8rem;
    display: flex;
    gap: 1.5rem;
  }
  .slider-group {
    flex: 1;
  }
  .slider-group label {
    font-size: 0.8rem;
    color: #aaa;
    font-weight: 400;
    text-transform: none;
    letter-spacing: 0;
  }
  input[type="range"] {
    width: 100%;
    accent-color: #7c5cff;
  }
</style>
