# Plan: Cross-G10 Extension of the Rate-Differential Signal

**Date**: May 2026
**Status**: Planning — implementation in progress (Strategies #2–#9)

---

## Why

Strategy #1 — `Δ(EU 2Y − US 2Y) → next-day EURUSD` — printed **Sharpe 2.75 net of 5 pips round-trip cost** over 2010–2024 (gross 3.45, hit rate 56%). Strong enough to ask the natural follow-up question:

> Does this generalise across G10, or is it an EURUSD-specific quirk?

This document is the plan to answer that.

---

## What

Apply the same structure as Strategy #1 to the 8 remaining G10 pairs. For each pair with base currency **X** and quote currency **Y**:

- **Signal**: `d_diff[t] = Δ(X_2Y − Y_2Y)` — the daily change in the 2-year rate differential on day *t*
- **Position**: `pos[t+1] = sign(d_diff[t])`, ±1 at full notional
- **Hold**: 1 trading day
- **Cost**: 5 pips round-trip (= 2.5 pips per unit of |Δpos|)
- **Period**: 2010-01-01 → 2024-12-31

| # | Pair | Signal | Status |
|---|---|---|---|
| 1 | EURUSD | Δ(EU 2Y − US 2Y) | ✅ Sharpe 2.75 net |
| 2 | GBPUSD | Δ(GB 2Y − US 2Y) | ✅ Sharpe 1.50 net |
| 3 | AUDUSD | Δ(AU 2Y − US 2Y) | ✅ Sharpe 1.22 net |
| 4 | NZDUSD | Δ(NZ 2Y − US 2Y) | ✅ Sharpe 0.92 net (gross 1.96) |
| 5 | USDJPY | Δ(US 2Y − JP 2Y) | ✅ Sharpe 1.44 net (−59% DD) |
| 6 | USDCAD | Δ(US 2Y − CA 2Y) | ✅ Sharpe 2.06 net |
| 7 | USDCHF | Δ(US 2Y − CH 2Y) | ✅ Sharpe 0.00 net — signal fails on CHF |
| 8 | USDSEK | Δ(US 2Y − SE 2Y) | ✅ Sharpe 2.13 net (⚠️ 5-pip cost optimistic at SEK spot ~10.5) |
| 9 | USDNOK | Δ(US 2Y − NO 2Y) | ⚠️ Deferred — NO 2Y unavailable on TradingView (only NO10Y available). To revisit with Norges Bank API or accept tenor mismatch. |
| **10** | **Portfolio** | Vol-targeted G10 rate-diff portfolio (EUR, GBP, AUD, CAD) | ✅ Sharpe 2.70 net (−13% DD, Calmar 1.03) |
| 11 ❌ | Momentum portfolio | Cross-sectional 21-day momentum, weekly, top-2/bottom-2 | Rejected — Sharpe −0.34. FX momentum decay post-GFC; documented in [`strategies/rejected/`](rejected/) |
| **12** | **Calibrated portfolio** | Strategy #10 with ex-ante rolling-vol leverage scalar (avg 2.19×) | ✅ Sharpe 2.73 net, hits 10% vol target, Calmar 1.16 |
| 13 ⚠️ | CFTC positioning extreme (long+short) | ±2σ positioning + 21-DMA reversal trigger, both sides | ⚠️ Sharpe −0.07, 30 trades. Asymmetric: short side 40% win ✓, long side 30% win ✗ — crowded shorts (esp. USDJPY long during carry-trade era) don't unwind, they continue. |
| Tech ⚠️ | 15 classic indicators × 3 majors | RSI, MACD, Bollinger, Donchian, Ichimoku, SMA Cross, etc. — canonical defaults | None deployable. Best: TRIX on USDJPY +0.14. 41 of 45 net Sharpes negative. Consistent with Park-Irwin 2007. See [`technical/`](technical/) |

---

## Outcomes we're trying to distinguish

- **Generalises across G10** → real cross-currency signal worth deploying systematically.
- **Works for some pairs but not others** → tells us which FX markets the rate-path signal actually drives (likely majors > commodity > smaller crosses).
- **Only EURUSD holds up** → the headline result was probably a timing-alignment or pair-specific quirk; back to the drawing board.

---

## Output for each strategy

- One numbered, standalone strategy module: `strategies/strat_0N_<base>_<quote>_2y_diff.py`
- Equity curve PNG in `reports/`
- Result row in the comparison table in [`strategies/README.md`](README.md)

---

## Caveats inherited from Strategy #1

- **Timing-alignment risk** — Yahoo's FX close timestamp may not align with rate fixings, inflating apparent edge.
- **Sub-period stability** untested across regimes (ZIRP era 2010–2016 vs post-ZIRP 2022+).
- **Realisable cost varies by pair liquidity** — 5 pips is fair for EURUSD but tight for USDNOK. May need pair-specific cost assumptions later.
- **Position sizing is full ±1**, no vol-targeting yet. Production deployment would need vol scaling and capacity testing.
