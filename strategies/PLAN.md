# Plan: Cross-G10 Extension of the Rate-Differential Signal

**Date**: May 2026 (original plan)
**Status (2026-06-12)**: ⚠️ The entire rate-diff family was flagged as timing artefact by Strategy #21's verification of #1. The "extension" results below printed positive Sharpes but those Sharpes are likely data-alignment artefacts, not deployable edges. Repo is in active reconstruction mode pending properly time-aligned signals.

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
| **14** ⚠ | **Calibrated portfolio + trend filter** | Strategy #12 + per-pair 50-DMA trend confirmation; drop weight if signal disagrees with trend | Sharpe 1.59 (vs #12's 2.73). Filter blocked 49% of cells but **degraded** the signal — rate-diff *leads* trends so the confirmation filter removes the most profitable entries. |
| 15 ❌ | EURUSD SMA20 + RSI(14) combo (long-only) | Classic textbook confluence: 20-DMA cross + RSI cross above 30 + 21-DMA exit | Rejected — Sharpe −0.34, 24.5% win rate. Classic technical playbook empirically dead on liquid EURUSD. See [`strategies/rejected/`](rejected/). |
| 16 ❌ | VIX spike → safe-haven short (USDJPY+USDCHF) | VIX z > +1σ over 252d → short both pairs for 10d | Rejected — Sharpe −0.39, −54% max DD. Safe-haven thesis empirically broken in JPY carry-trade era (BoJ ZIRP+YCC dominated) and post-SNB-peg-break CHF. See [`strategies/rejected/`](rejected/). |
| 17 ⚠ | Oil (WTI) → next-day USDCAD | pos[t+1] = −sign(oil_return[t]) — first non-rate-based cross-asset signal | ⚠ **VERIFIED TIMING ARTEFACT (#19).** Sharpe collapsed from +3.96 to −0.84 with 1-day extra lag. Captures intraday WTI-to-USDCAD response in the 2.5h Yahoo timestamp gap. Not tradable real-time. |
| **18** | **Equal-weight portfolio (new headline)** | Same as #12 but `sign(d_diff) × (1/N)` sizing (no z-score, no inverse-vol) | ✅ Sharpe **2.90 net** (vs #12's 2.73). Calmar 1.51. **Z-score machinery adds noise** on 4-pair cross-section; direction is the signal, magnitude is noise. New preferred portfolio spec. |
| 19 ✓ | Oil → USDCAD with 1-day extra lag (verification of #17) | pos[t+1] = −sign(oil_return[t−1]) | ✅ Negative-result verification. Sharpe −0.84, signal corr collapses from −0.16 to ~0. Confirms #17 was timing artefact. |
| 20 ⚠ | Classical vol-normalised carry (Dupuy 2021 spec) | `(rate_base − rate_quote) / 30d realised vol` on LEVEL, monthly long top-2 / short bottom-2 | ⚠ Sharpe **0.07** net, skew −0.07. Confirms post-2008 carry decay (literature: 0.76 pre-crisis → 0.06 post-crisis). Vol-normalisation doesn't rescue LEVEL signal in this era. Direct contrast with our `d_diff` (change) approach (#18 SR 2.90). |
| **21** ✓ | **EURUSD rate-diff with 1-day extra lag (rigour check of #1)** | `pos[t+1] = sign(d_diff[t−1])` — uses yesterday's d_diff to predict tomorrow's EURUSD | ✅ **The most important verification in the repo.** Sharpe collapses from +2.75 to **−0.58**. Signal corr collapses from +0.27 to +0.028, β shrinks ~10×. **Confirms #1 was timing artefact; the entire rate-diff family is flagged.** |
| **22** 🛡️ | **Carry crash filter overlay (Brunnermeier-Nagel-Pedersen 2009)** | `scale[t] = vix_scale × mom_scale ∈ [0,1]`; `weights_filt = weights_#18 × scale.shift(1)` | ✅ Deployable **vol-reducer with no Sharpe drag**: Sharpe 2.90→2.91, vol 10.1%→8.4% (−17%), MaxDD −19.3%→−18.0% (−7%), skew +0.31→+0.36. Skew rescue muted because #18's `d_diff` base has positive skew (not the negative-skew tail Brunnermeier filter was designed for). Overlay is independent of base — re-applies to any future carry-style strategy. |
| 23 ❌ | Donchian/ATR breakout with trailing stop (core4 G10 FX) | 60-day resistance, +1.5 ATR breakout buffer, 2.5 ATR trailing stop, full ±1/N per active pair | ❌ **Rejected.** Sharpe **−0.18**, 23 trades / 15y, 34.8% win rate, profit factor 0.60, daily skew −2.13. Third independent confirmation of TA-in-FX dead (after #11 momentum, tech sweep). NOT timing artefact — uses only FX OHLC. Per-pair: EURUSD PF 7.84 (4 trades only), GBPUSD PF 0.16, AUDUSD PF 0.06, USDCAD PF 1.01. Consistent with Park-Irwin 2007. |
| 24a ❌ | Canonical Turtle System 1 with last-loser filter | 20-day entry / 10-day exit / 2N fixed stop / filter ON | ❌ **Rejected — filter dead-lock pathology.** Sharpe **−0.01**, 7 trades / 15y, avg gross exposure 0.6%. After first winner per pair, filter blocks all subsequent entries until a loser can be taken — but the filter blocks the loser too. Pair becomes permanently frozen. |
| 24b ❌ | Turtle System 1 without filter (pure 20/10/2N) | Same as #24a but filter OFF | ❌ **Rejected — whipsaw graveyard.** Sharpe **−0.28**, 689 trades / 15y (11/pair/year), 34.7% win rate, profit factor 0.87. MaxDD −28.5%. Confirms classical Turtle parameters do not extract edge from G10 spot FX in 2010–2024. Fourth independent confirmation of TA-in-FX dead. |
| **25** ✓ | **Turtle System 1 (no filter) on commodities + crypto** | Same code as #24b. 8 instruments: Gold, Silver, Copper, Oil, NatGas, Soy, BTC, ETH. Inverse-vol sizing (5% per-instr target, ±30% cap). 10 bps RT cost per leg. | ✅ **Sharpe +0.43, PF 1.36, daily skew +0.82** (proper trend-follower signature). 1,217 trades over 15y, 35.5% win rate. BTC PF 2.93, ETH PF 2.49 (max win +300%). Long avg +2.70% / short avg −0.67%. **Validates implementation; isolates FX rejection to asset class.** Crypto allocation carries most of the edge; commodities marginal. |
| 26a ❌ | Carry-TSMOM filter overlay on #20 (Moskowitz-Ooi-Pedersen 2012, soft) | `scale = 1.0` if trailing-12m carry > 0, else `0.5`; apply to #20's monthly weights | ❌ **Rejected.** Sharpe 0.07 → 0.01, IR −0.18. MOP TSMOM rescue requires base trend-following content in P&L path; #20's near-zero base Sharpe has no trend to filter. Filter activates 52.5% of months but destroys value. Skewness gets worse (−0.07 → −0.23). |
| 26b ❌ | Carry-TSMOM filter overlay on #20 (hard variant) | Same as #26a but `scale = 0.0` when trailing 12m < 0 | ❌ **Rejected.** Sharpe 0.07 → −0.06, IR −0.18. Goes fully flat 52.5% of sample. Hit rate collapses 52% → 22%. Confirms post-2008 carry decay is not fixable by simple TSMOM. |
| 27 ❌ | 20/50 DMA crossover with 1 ATR stop below MA20 (core4 FX) | Long on golden cross, short on death cross; stop = `ma20 ∓ 1×ATR(14)` recomputed daily; opposite crossover triggers reversal | ❌ **Rejected, but least-bad TA-in-FX so far.** Sharpe **−0.09**, 351 trades, PF 0.94, daily skew **+0.17** (proper trend-follower!). 2:1 reward:risk per trade. 341/351 exits on the ATR stop. Per-pair: GBPUSD 1.13, AUDUSD 1.12 (borderline), EURUSD 0.69, USDCAD 0.80. **5th independent TA-in-FX rejection.** Cost drag 4.05% over 15y is the main hurdle — gross Sharpe is also −0.02 so the signal itself doesn't have enough edge. |
| **28** ✓ | **20/50 DMA crossover with 1 ATR stop on commodities + crypto** | Same code as #27. 8 instruments: Gold, Silver, Copper, Oil, NatGas, Soy, BTC, ETH. Inverse-vol sizing (5% per-instr target, ±30% cap). 10 bps RT cost per leg. | ✅ **Sharpe +0.42, PF 1.47, daily skew +0.50.** 605 trades over 15y, 31.9% win rate, 3:1 trade-level reward:risk. BTC PF 2.96, ETH PF 3.30 (max win +281%). Long avg +3.08% / short avg −0.47%. **Validates asset-class hypothesis across BOTH spec families** (Turtle Δ +0.71, MA-cross Δ +0.51). |

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
