<script lang="ts">
  import { onMount } from "svelte";
  import { fetchMarkets, type Market } from "./api";

  export let selected: string = "BTC";
  let markets: Market[] = [];
  let loading = true;

  onMount(async () => {
    try {
      markets = await fetchMarkets();
    } catch (e) {
      console.error("Failed to load markets", e);
    }
    loading = false;
  });

  function fmt(n: number): string {
    if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(0)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(0)}K`;
    return `$${n.toFixed(0)}`;
  }
</script>

<div class="picker">
  <label for="market">Market</label>
  {#if loading}
    <p class="loading">Loading markets...</p>
  {:else}
    <select id="market" bind:value={selected}>
      {#each markets as m}
        <option value={m.coin}>
          {m.coin} — {fmt(m.open_interest_usd)} OI — {m.max_leverage}x
        </option>
      {/each}
    </select>
    {#each markets.filter(m => m.coin === selected) as m}
      <div class="meta">
        <span>Price: ${m.mark_price.toLocaleString()}</span>
        <span>OI: {fmt(m.open_interest_usd)}</span>
        <span>Funding: {(m.funding_rate * 100).toFixed(4)}%/h</span>
        <span>24h Vol: {fmt(m.day_volume)}</span>
      </div>
    {/each}
  {/if}
</div>

<style>
  .picker {
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
  select {
    width: 100%;
    padding: 0.6rem 0.8rem;
    background: #1a1a2e;
    color: #e0e0e0;
    border: 1px solid #333;
    border-radius: 6px;
    font-size: 0.95rem;
  }
  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-top: 0.6rem;
    font-size: 0.8rem;
    color: #888;
  }
  .loading {
    color: #666;
    font-size: 0.85rem;
  }
</style>
