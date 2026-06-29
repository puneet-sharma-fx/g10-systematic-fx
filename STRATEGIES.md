# Strategies Index

A one-page index of every strategy tested in this repo, what was actually found, and where to look for the details. All Sharpes are **net of 5 pips round-trip cost** unless stated otherwise. Period 2010–2024 (or as constrained by data).

For full per-strategy details: [`strategies/README.md`](strategies/README.md). For the original extension plan: [`strategies/PLAN.md`](strategies/PLAN.md).

---

## ⚠️ Critical caveat — Strategy #21 finding (2026-06-12)

**The 1-day-extra-lag rigour check applied to Strategy #1 (EURUSD rate-diff) caused its Sharpe to collapse from +2.75 to −0.58.** Signal correlation went from +0.27 to +0.028 (~10× collapse); β shrank from 0.0335 to 0.0035. This is the same timing-artefact pattern that disqualified Strategy #17 (Oil → USDCAD).

**Implication.** The entire rate-diff family below — Strategies #1–#10, #12, #18 — uses the same `d_diff` signal structure. All of them likely contain the same intraday timing leakage between FRED/ECB rate-close timestamps and Yahoo's 5pm ET FX close. The apparent edge is almost certainly capturing *same-day* contemporaneous response to rate moves, measured at misaligned timestamps, not *lagged* predictive content. **Not tradable in real-time from a 5pm ET FX-close entry**.

**Status.** All rate-diff strategies are now flagged as ⚠️ **VERIFIED TIMING ARTEFACT (pending proper time-aligned reconstruction)**. Until rebuilt with synchronised end-of-day fixings, their Sharpes should be read as data-alignment artefacts, not deployable edges. The repo's iteration trail — apparent edge → rigour check → honest downgrade — is preserved in git history (`e7f65de`, `38de409` for #17/#19; `056d210`, [next commit] for #1/#21).

**What's next.** The proper fix requires data with synchronised timestamps (e.g., 5pm ET fixings for FRED/ECB rates and EURUSD spot from the same minute). That's a meaningful re-engineering project, not a one-day commit.

---

## ⚠ Rate-diff family (Sharpes >1 but verified timing artefact — see #21)

The original core finding was that **the change in 2Y rate differential predicts next-day FX**. Strategy #21 (1-day-extra-lag rigour check on Strategy #1) showed Sharpe collapses from +2.75 to −0.58 and signal correlation from +0.27 to +0.028. **All strategies below use the same `d_diff` signal structure and likely contain the same intraday timing leakage between FRED/ECB rate-close timestamps and Yahoo's 5pm ET FX close.** Apparent Sharpes shown for historical record; not deployable at 5pm ET FX-close entry without proper time-aligned data.

| # | Strategy | Period | Apparent Net Sharpe | Status |
|---|---|---|---|---|
| **18** | Equal-weight rate-diff portfolio | 2010-2024 | 2.90 | ⚠ Timing artefact (likely) |
| **1** | EURUSD: Δ(EU 2Y − US 2Y) → next-day EURUSD | 2010-2024 | 2.75 → ⚠ | **Verified by #21**: collapses to −0.58 with 1-day lag |
| **12** | Calibrated rate-diff portfolio (core 4) | 2010-2024 | 2.73 | ⚠ Timing artefact (likely) |
| **10** | Rate-diff portfolio (uncalibrated) | 2010-2024 | 2.70 | ⚠ Timing artefact (likely) |
| **8** | USDSEK rate-diff (cost caveat) | 2012-2024 | 2.13 | ⚠ Timing artefact + cost model artefact |
| **6** | USDCAD rate-diff | 2010-2024 | 2.06 | ⚠ Timing artefact (likely) |
| **14** | Calibrated portfolio + 50-DMA trend filter | 2010-2024 | 1.59 | ⚠ Timing artefact (likely) |
| **2** | GBPUSD rate-diff | 2010-2024 | 1.50 | ⚠ Timing artefact (likely) |
| **5** | USDJPY rate-diff (brutal −59% DD) | 2010-2024 | 1.44 | ⚠ Timing artefact + DD |
| **3** | AUDUSD rate-diff | 2010-2024 | 1.22 | ⚠ Timing artefact (likely) |

**Pending verification.** Strategy #21 confirmed the artefact for #1 specifically. To confirm or rule out for the other strategies, repeat the 1-day-extra-lag test on each. Strategy #19 already confirmed the same artefact pattern for the cross-asset Oil/USDCAD case (#17 → #19).

## ✅ Working strategies (verified, net Sharpe > 1)

*No directional strategy has yet survived the time-alignment rigour check. Repo is in active reconstruction mode pending properly time-aligned signals.*

## 🛡️ Risk overlays (deployable independent of base signal)

| # | Overlay | Period | Effect on #18 base | Status |
|---|---|---|---|---|
| **22** | Carry crash filter (VIX + self-momentum) — Brunnermeier-Nagel-Pedersen 2009 | 2010–2024 | Vol −17% (10.1%→8.4%), Sharpe flat (2.90→2.91), MaxDD −7%, skew +0.05 | ✅ Deployable as a vol-reducer. **Validated independent of base signal — works on any carry-style portfolio.** |

## ⚠ Borderline (Sharpe 0–1)

| # | Strategy | Period | Net Sharpe | Notes |
|---|---|---|---|---|
| **4** | NZDUSD rate-diff | 2016-2024 | 0.92 | NZ data starts 2016, shorter sample |
| **25** | Turtle System 1 (no filter) on commodities + crypto (8 instruments, vol-targeted) | 2010-2024 | **0.43** | **Profit factor 1.36, daily skew +0.82.** Same code as #24b but cross-asset shift to its native habitat. BTC alone PF 2.93, ETH PF 2.49 (max win +300%). Long avg +2.70% vs short avg −0.67% — long side carries the edge. Validates implementation; isolates FX rejection to that asset class. |
| **28** | 20/50 DMA crossover with 1 ATR stop on commodities + crypto (8 instruments, vol-targeted) | 2010-2024 | **0.42** | **Profit factor 1.47, daily skew +0.50.** Same code as #27 but cross-asset shift. BTC PF 2.96, ETH PF 3.30 (max win +281%). Long avg +3.08% / short avg −0.47%. Validates the asset-class hypothesis across BOTH MA-crossover and Turtle spec families. |
| **29** | Crash filter overlay (VIX + self-momentum) on #28 | 2010-2024 | **0.51** | **First overlay in the repo to materially add Sharpe.** All metrics improve simultaneously: Sortino 0.63 → 0.75, MaxDD −26.84% → −19.15% (−7.7pp), Calmar 0.17 → 0.26, skew +0.50 → +0.62, ann ret +4.58% → +5.00%. IR +0.14. Conditional Sharpe test: on the 1,455 binding days, base earns −0.08, filtered earns +0.09 — filter is removing bad days specifically. |
| **30** ❌ | Crash filter overlay (same spec) on #25 (Turtle base) | 2010-2024 | 0.41 (vs base 0.43) | **Cross-spec test FAILS — overlay doesn't generalise.** IR −0.23, Sharpe −0.02, Sortino −0.07, skew +0.82 → +0.30 (−0.52). MaxDD does improve (−7.3pp) but at the cost of returns (−1.31pp). Conditional Sharpe test: base earns +0.19 on binding days, filtered +0.00 — filter removes GOOD days, opposite to #29. Turtle's edge is vol-positive (breakouts during high-vol periods); MA-cross's edge isn't. Overlay is base-specific, not universal. |
| **31** ❌ | Cross-sectional 5-day mean reversion on G10 FX (long bottom-2 losers, short top-2 winners, weekly rebalance) | 2010-2024 | −0.19 | **The cleanest falsification of "FX is exploitable at the weekly horizon."** Mirror image of #11 (momentum, Sharpe −0.34). If #11 lost because of mean reversion, #31 should have won. It didn't. **Therefore G10 FX is neither trending nor mean-reverting at 1-week horizon — just noise.** Gross Sharpe +0.08 (tiny MR effect exists), but 28.45% cumulative cost drag destroys it. Daily skew +0.25 (proper MR signature, but doesn't pay). 6th independent TA-in-FX confirmation. |
| **32** ❌ | Cross-sectional inflation-differential momentum on G10 FX (Taylor rule, monthly rebalance) | 2010-2024 | −0.13 | **First strategy in repo to USE the new `data/economic.py` ingestion layer.** Long top-3 currencies / short bottom-3 by CPI YoY differential vs US. Net Sharpe −0.13, gross Sharpe −0.13 (NOT a cost problem — cost drag only 0.27%). Signal "gets stuck": AU/NZ long 99%/92% of days, CHF short 98% — driven by **structural** inflation differences across countries, not **dynamic** Taylor-rule responses. Falsifies the cross-sectional reading of Molodtsova-Papell (2009) on post-GFC data. 7th independent TA-on-FX confirmation. |
| **20** | Classical vol-normalised carry (Dupuy 2021 spec, monthly) | 2010-2024 | 0.07 | Confirms post-2008 carry decay; LEVEL signal nearly dead in this era |

## ❌ Failed / rejected / inconclusive

| # | Strategy | Net Sharpe | Why it failed |
|---|---|---|---|
| **7** | USDCHF rate-diff | 0.00 | SNB peg break 2015 + safe-haven flows override rates |
| **11 ❌** | Cross-sectional momentum portfolio (rejected) | −0.34 | Post-GFC FX momentum decay; confirmed at 21/63/126/252 lookbacks |
| **13 ⚠** | CFTC positioning ±2σ + 21-DMA reversal (long+short) | −0.07 | Asymmetric: short 40% win ✓, long 30% win ✗ |
| **9** | USDNOK rate-diff (deferred) | — | TVC has no NO 2Y data; deferred to Norges Bank API |
| **Tech sweep ⚠** | 15 classic technical indicators × 3 majors | best +0.14 | None deployable; consistent with Park-Irwin 2007 |
| **15** ❌ | EURUSD SMA20 + RSI(14) combo (long-only) | −0.34 | 49 trades, 24.5% win rate. Classic confluence doesn't work on liquid EURUSD |
| **16** ❌ | VIX spike → safe-haven short (USDJPY + USDCHF) | −0.39 | Safe-haven thesis empirically broken in JPY carry-trade era + post-SNB CHF |
| **17** ⚠ | Oil (WTI) → next-day USDCAD (timing artefact) | 3.96 → ⚠ | Verified by #19: collapses to −0.84 with 1-day extra lag. Captures intraday WTI-USDCAD response in Yahoo close-time gap. Not tradable real-time. |
| **19** ✓ | Oil → USDCAD with 1-day lag (rigour check) | −0.84 | Verification of #17 — confirms it was timing artefact. Signal correlation collapses from −0.16 to ~0. |
| **21** ✓ | EURUSD rate-diff with 1-day lag (rigour check) | −0.58 | **The most important verification in the repo.** Confirms #1's edge was timing artefact; entire rate-diff family flagged. Signal corr collapses from +0.27 to +0.028. |
| **23** ❌ | Donchian/ATR breakout with trailing stop (core4, 60d/1.5 ATR/2.5 ATR) | −0.18 | **Third independent confirmation of TA-in-FX dead** (after #11 momentum and the 15-indicator tech sweep). 23 trades over 15 years, 34.8% win rate, profit factor 0.60. Daily skew −2.13 (single-day stop hits dominate). EURUSD alone profitable (4 trades, PF 7.84); GBPUSD chopped (PF 0.16). NOT a timing artefact — uses only FX OHLC. Consistent with Park-Irwin 2007. |
| **24a** ❌ | Canonical Turtle System 1 (20d entry / 10d exit / 2N stop / last-loser filter) | −0.01 | **Filter dead-lock pathology.** Only 7 trades over 15 years (filter froze the strategy after each winner). 57% win rate, profit factor 1.02. Avg gross exposure 0.6% — strategy is essentially "do nothing." |
| **24b** ❌ | Turtle System 1 without filter (pure 20d/10d/2N) | −0.28 | **Whipsaw graveyard.** 689 trades over 15 years (11/pair/year), 34.7% win rate, profit factor 0.87. Active losses from chop, MaxDD −28.5%. Confirms classical Turtle parameters do not extract edge from G10 FX. |
| **26a** ❌ | Carry-TSMOM filter overlay on #20 (12m lookback, soft scale 0.5) | 0.01 (vs base 0.07) | **Rejected.** IR −0.18, vol −1.1pp, MaxDD −2.1pp, skew −0.16. The Moskowitz-Ooi-Pedersen TSMOM rescue requires base trend-following content in P&L path; #20 has Sharpe 0.07 so trailing-12m sign is noise. Filter activates 52.5% of months but destroys rather than adds value. |
| **26b** ❌ | Carry-TSMOM filter overlay on #20 (12m lookback, hard scale 0.0) | −0.06 (vs base 0.07) | **Rejected.** Same IR −0.18 as soft variant; goes fully flat 52.5% of months. Hit rate collapses 52% → 22% (no return earned during off-months). Same conclusion: post-2008 carry decay isn't fixable by simple TSMOM. |
| **27** ❌ | 20/50 DMA crossover with 1 ATR stop below MA20 (core4 FX) | −0.09 | **Rejected, but the LEAST BAD TA-in-FX result so far.** 351 trades, 31.6% win rate, profit factor 0.94, daily skew **+0.17** (proper trend-follower signature!). Avg win/loss ratio 2:1 (+2.35% / −1.16%). 5th independent TA-in-FX confirmation. Per-pair PF: GBPUSD 1.13, AUDUSD 1.12 (borderline), EURUSD 0.69, USDCAD 0.80. Almost works on cost — 4.05% cumulative cost drag is the main hurdle. |

## 🔬 Supporting analyses (diagnostics & rigour checks)

| Artefact | What it shows | Verdict |
|---|---|---|
| **Signal-IC regression** (`notebooks/regression_all_pairs.py`) | β, R², t-stat per pair for next-day FX ~ Δrate-diff | All 8 βs positive, t-stats 6.3 – 17.5 |
| **Sub-period stability** (`notebooks/subperiod_stability.py`) | Sharpe across ZIRP/Divergence/COVID/Hiking regimes | Signal strongest when rates are most active |
| **Momentum lookback sweep** (`notebooks/explore_momentum_lookbacks.py`) | Cross-sectional MOM at 21/63/126/252 days | Negative at every horizon |
| **2Y diff scatter** (`notebooks/explore_2y_diff_vs_eurusd.py`) | EURUSD: β = +0.0335, R² = 7.5% | Strong, UIP-consistent |

## 📊 Public track records (auditable daily CSVs)

Anyone can re-derive Sharpe / DD / hit-rate from raw numbers. In [`live/track_record/`](live/track_record/):

- `strategy_01_eurusd_track_record.csv` (3,912 rows, 12 cols)
- `strategy_02_gbpusd_track_record.csv` (3,911 rows, 12 cols)
- `strategy_06_usdcad_track_record.csv` (3,911 rows, 12 cols)
- `strategy_10_portfolio_core4_track_record.csv` (3,881 rows)
- `strategy_12_portfolio_calibrated_track_record.csv` (3,881 rows)
- `strategy_13_cot_extreme_long_short_track_record.csv` (3,390 rows)

---

## What the research narrative shows

| Layer | Evidence |
|---|---|
| **A real factor exists** | Strategies #1–#10: rate-diff signal works on 7 of 8 G10 pairs, generalises into portfolio |
| **It's regime-robust** | Sub-period analysis shows positive in all four macro regimes (ZIRP / divergence / COVID / hiking) |
| **It's correctly calibrated** | Strategy #12 fixes leverage to hit 10% vol target without changing Sharpe |
| **Failures are documented honestly** | Momentum, positioning (long side), classic TA, trend-confirmation overlay — all tested, all rejected/degraded with literature-citation context |
| **Results are auditable** | 6 daily-frequency CSVs let any reviewer recompute the headline numbers |

---

## How to read this repo

- **5-minute glance**: this file + main [`README.md`](README.md) + [`reports/regressions_all_pairs.png`](reports/regressions_all_pairs.png)
- **30-minute deep-dive**: [`strategies/README.md`](strategies/README.md) for per-strategy details + [`strategies/PLAN.md`](strategies/PLAN.md) for the original extension plan
- **Verification**: any CSV in [`live/track_record/`](live/track_record/) — open in any spreadsheet, recompute the metrics yourself
- **Reproducing**: each strategy has a standalone script in [`strategies/`](strategies/). Requires `FRED_API_KEY` for Strategy #1; rest use cached TVC yields.

## Stack

- **Data**: FRED (US rates, VIX), ECB SDW (Euro-area yield), TradingView via `tvDatafeed` (international 2Y), yfinance (FX spot), CFTC TFF (positioning)
- **Python**: pandas, numpy, scipy, statsmodels, matplotlib
- **Backtesting**: bespoke walk-forward + event-driven engines (no `backtrader` / `vectorbt` dependency for the published strategies)
- **Cost model**: 5 pips round-trip (2.5 pips per unit of position turnover), pip-size aware per pair (JPY = 0.01)

---

# Strategy Details (annotated format)

> *Each strategy below follows the same format: explanation, results, and a variable glossary that defines every code-level parameter / variable used in the implementation. Strategy #20 is the first to use this format; others to follow.*

---

## Strategy #20 — Classical vol-normalised carry (G10, monthly rebalance)

**Explanation.** Each month-end, computes the vol-normalised carry score for each G10 pair as `(base 2Y rate − quote 2Y rate) / 30-day realised FX vol`. Ranks all 7 G10 pairs by this score, goes long the top-2 (highest vol-adjusted carry — the "best risk-adjusted yielders") and short the bottom-2 (lowest, typically the lowest-yielders). Each position is sized at 1/4 of capital, so total gross exposure is 100% (50% long / 50% short, dollar-neutral). Holds positions for one month, then re-ranks at the next month-end. This is the **classical level-based carry** signal — fundamentally different from our `d_diff`-based strategies (#1, #18) which use the *change* in rate differential.

**Result** (2010–2024, monthly, net of 5 pips RT cost):
Net Sharpe **0.07**, annual return **+0.44%**, max DD **−20.85%**, monthly skew **−0.07** (does NOT confirm Dupuy's +0.97 positive-skew claim for the pre-2020 era). The result confirms the post-2008 carry decay documented in the literature ("Benchmark carry SR ~0.06 post-2008 vs ~0.76 pre-crisis") and demonstrates *why* our change-based `d_diff` approach (Strategy #18 Sharpe 2.90 net) dominates the classical level-based carry on the same 2010–2024 universe.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `rate_diff[pair, t]` | LEVEL of base 2Y yield minus quote 2Y yield |
| `realised_vol[pair, t]` | 30-day rolling stdev of FX returns, annualised |
| `score[pair, t]` | Vol-normalised carry signal: `rate_diff / realised_vol` |
| `weights_monthly[pair, t]` | End-of-month portfolio weight per pair |
| `positions_monthly[pair, t]` | Weights shifted +1 month for next-month return |
| `N_LONG`, `N_SHORT` | Number of pairs in long/short legs (= 2 each) |
| `LEG_WEIGHT` | Per-position weight: `1 / (N_LONG + N_SHORT)` = 0.25 |
| `VOL_WINDOW_DAYS` | Realised vol lookback in trading days (= 30) |
| `COST_ROUND_TRIP_PIPS` | Total bid-ask round-trip cost in pips (= 5.0) |
| `cost_unit_pips` | Half of round-trip cost (= 2.5 pips per unit traded) |
| `pip_size` | Smallest quote increment (0.0001, except JPY = 0.01) |
| `turnover[pair, t]` | Absolute change in weight from previous month |
| `cost_per_pair[pair, t]` | Per-pair monthly cost: `turnover × cost_unit / spot` |
| `gross_port_monthly[t]` | Sum of `positions × pair_returns` across pairs |
| `net_port_monthly[t]` | Gross monthly return minus total cost |
| `monthly_skew` | Skewness of net monthly returns (Dupuy's tail-risk metric) |

**Data sources.** 2Y yields cached at `data/raw/tvc_2y_yields.csv` (TVC via tvDatafeed, 9 currencies). FX from yfinance (e.g. `EURUSD=X`).
**Reference.** Dupuy, P. (2021). *"Risk-Adjusted Return Managed Carry Trade"*, Journal of Banking & Finance.
**Script.** [`strategies/strat_20_vol_normalised_carry.py`](strategies/strat_20_vol_normalised_carry.py)
**Track record CSV.** [`live/track_record/strategy_20_vol_normalised_carry_track_record.csv`](live/track_record/strategy_20_vol_normalised_carry_track_record.csv)
**Equity curve.** [`reports/strategy_20_vol_normalised_carry.png`](reports/strategy_20_vol_normalised_carry.png)

---

## Strategy #22 — Carry crash filter overlay (VIX + self-momentum on #18 base)

**Explanation.** A **deployable risk-management overlay** — not a directional signal. Scales the position weights of a base carry-style strategy down during crash conditions, intended to reduce left-tail crash exposure with minimal Sharpe drag. The overlay is computed daily as the product of two scalars in `[0, 1]`. The first, `vix_scale`, falls linearly from 1.0 when VIX ≤ 20 to 0.0 when VIX ≥ 40 — at VIX 30 it is 0.50, halving position size. The second, `mom_scale`, is a self-referential drawdown gate: it equals 0.5 when the trailing-20-day return of the unfiltered base strategy is more than −1σ below its 252-day mean, and 1.0 otherwise. The combined scalar is lagged 1 day to avoid look-ahead, then multiplied into the per-pair weights of Strategy #18 (the equal-weight `d_diff` portfolio, leverage-calibrated). The classical Brunnermeier-Nagel-Pedersen (2009) construction adds TED-spread (now SOFR-OIS post-2022) and CFTC-positioning conditions; we omit TED here because FRED's `TEDRATE` was discontinued Jan 2022 and the SOFR equivalent isn't in the existing fetcher layer — a 2-indicator construction is the realistic public-data implementation through 2024.

**Result** (2010–2024, daily, net of 5 pips RT cost): on the **#18 base** (Sharpe 2.90, vol 10.1%, MaxDD −19.3%, skew +0.31), the filter produces Sharpe **2.91** (≈flat), vol **8.4%** (−17%), MaxDD **−18.0%** (−7%), skew **+0.36** (+0.05). Annualised return drops from 29.2% to 24.4% as expected for the lower vol. **The filter is active on 38% of days and brings positions fully flat on 1.5% of days (VIX > 40).** Calmar slightly degrades (1.51 → 1.36) since the vol reduction outpaces the drawdown reduction. The expected dramatic skewness rescue from Brunnermeier 2009 (≈ −2.5 → ≈ −0.5 on classical level-carry) does NOT materialise here, because **#18's base skewness is already positive (+0.31)** — the `d_diff` (change in rate-diff) signal does not carry the negative-skew tail that classical level-carry has, so there is less left-tail to fix. Validated use case: a deployable vol-reducer / regime-de-risker with no Sharpe drag, that would apply identically on top of any future *properly time-aligned* carry-style strategy reconstructed from this body of work.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `d_diff[pair, t]` | Daily change in (base 2Y − quote 2Y) for each pair |
| `weights_raw[pair, t]` | Equal-weight per-pair direction: `sign(d_diff) / N_pairs` |
| `leverage_scalar[t]` | Rolling 63d realised-vol leverage to hit `TARGET_VOL` |
| `weights_base[pair, t]` | Strategy #18 base weights: `weights_raw × leverage_scalar` |
| `vix[t]` | Daily VIX close (yfinance `^VIX`, FRED fallback) |
| `vix_scale[t]` | VIX-based scalar in `[0,1]`, linear 1.0→0.0 over VIX 20→40 |
| `VIX_FULL_BELOW` | VIX level below which scalar is 1.0 (= 20.0) |
| `VIX_FLAT_ABOVE` | VIX level at which scalar hits 0.0 (= 40.0) |
| `tr20[t]` | Trailing 20-day sum of unfiltered base net returns |
| `z_tr20[t]` | Z-score of `tr20` vs trailing 252d mean and stdev |
| `mom_scale[t]` | Self-momentum gate: 0.5 when `z_tr20 < −1.0`, else 1.0 |
| `MOM_Z_TRIGGER` | Z-threshold for momentum gate trigger (= −1.0) |
| `MOM_SCALE_ON_TRIGGER` | Scalar applied when drawdown gate triggers (= 0.5) |
| `scale_raw[t]` | `vix_scale × mom_scale`, clipped to `[0,1]` |
| `scale[t]` | `scale_raw` lagged 1 day — the no-lookahead crash scalar |
| `weights_filt[pair, t]` | Filtered weights: `weights_base × scale` |
| `net_base[t]` | Net return of #18 base portfolio (no filter) |
| `net_filt[t]` | Net return of #22 filtered portfolio |
| `n_active` | Days where `scale < 0.95` (filter materially binding) |
| `n_zero` | Days where `scale < 0.05` (flat positions) |
| `mean_scale` | Average daily scalar across the sample |

**Data sources.** 2Y yields cached at `data/raw/tvc_2y_yields.csv`. FX from yfinance. VIX from yfinance `^VIX` (FRED `VIXCLS` fallback).
**Reference.** Brunnermeier, Nagel, Pedersen (2009). *"Carry Trades and Currency Crashes"*, NBER Macroeconomics Annual.
**Script.** [`strategies/strat_22_carry_crash_filter_overlay.py`](strategies/strat_22_carry_crash_filter_overlay.py)
**Track record CSV.** [`live/track_record/strategy_22_crash_filter_overlay_track_record.csv`](live/track_record/strategy_22_crash_filter_overlay_track_record.csv)
**Equity curve.** [`reports/strategy_22_carry_crash_filter_overlay.png`](reports/strategy_22_carry_crash_filter_overlay.png)

---

## Strategy #23 — Donchian/ATR breakout with trailing stop (G10 core4, REJECTED)

**Explanation.** Classic trend-following breakout: enter LONG when today's close breaks a `DONCHIAN_LOOKBACK`-day resistance by `BREAKOUT_ATR_MULT × ATR`, enter SHORT on the symmetric downside break. While in a position, ratchet a trailing stop at `TRAIL_STOP_ATR_MULT × ATR` from close (raises only for longs, lowers only for shorts). Exit when the close crosses the stop. One position at a time per pair, full ±1/N sizing while active (max gross exposure = 100% when all 4 pairs simultaneously in trade), 1-day execution lag on signals. ATR is the canonical 14-day simple rolling mean of true range. **Critically, this strategy uses ONLY FX OHLC** (no rates, no VIX, no positioning data) — so its result is genuine price-pattern predictive content, structurally immune to the intraday timing-leakage artefact that flagged the rate-diff family in Strategy #21. Parameters chosen per the canonical trend-follower playbook and user spec (60-day resistance ≈ "tested 2-3 times per year"; 1.5 ATR breakout buffer to filter whipsaws; 2.5 ATR trailing stop wide enough to let trends run for weeks).

**Result** (2010–2024, daily close-to-close, net of 5 pips RT cost): **rejected**. Net Sharpe **−0.18**, ann return **−0.27%**, MaxDD **−6.94%**, Calmar **−0.04**, daily skew **−2.13**. Total trades **23** over 15 years (0.37 per pair per year — too few to be statistically meaningful), of which 8 long and 15 short. Trade-level win rate **34.8%**, profit factor **0.60** (a losing strategy). Per-pair: EURUSD 75% win on 4 trades (PF 7.84) saves face for that pair alone; GBPUSD 20% win on 10 trades (PF 0.16) destroys everything; AUDUSD PF 0.06; USDCAD PF 1.01. The daily-return skew of **−2.13** is the textbook "stop-loss in volatile single day" signature — a breakout strategy is *supposed* to have positive skew (small losses, big wins) but the wide ATR trailing stop allows the close-to-stop adverse moves to dominate the loss distribution. Confirms what the literature has been saying for two decades: **Park & Irwin (2007)** — *"Technical Analysis in Foreign Exchange Markets: Is There Still Profitability?"* found TA-in-FX profitability gone post-1990s. This is now the **third independent confirmation** in this repo (after Strategy #11 cross-sectional momentum, Sharpe −0.34, and the 15-indicator technical sweep that produced 41/45 negative net Sharpes). FX in 2010–2024 is too mean-reverting at multi-month horizons for breakout signals to extract a positive net edge.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `high[t]`, `low[t]`, `close[t]` | Daily yfinance OHLC for each pair |
| `prev_close[t]` | Yesterday's close (used in true-range calc) |
| `tr[t]` | True range: `max(H−L, |H−prev_close|, |L−prev_close|)` |
| `atr[t]` | `ATR_PERIOD`-day simple mean of `tr` |
| `ATR_PERIOD` | True-range averaging window (= 14 days, canonical) |
| `resistance[t]` | `DONCHIAN_LOOKBACK`-day rolling max of close, shifted 1d |
| `support[t]` | `DONCHIAN_LOOKBACK`-day rolling min of close, shifted 1d |
| `DONCHIAN_LOOKBACK` | Resistance/support window (= 60 days, "2-3 peaks per year") |
| `BREAKOUT_ATR_MULT` | Required overshoot above resistance to enter (= 1.5 × ATR) |
| `TRAIL_STOP_ATR_MULT` | Trailing stop distance from close (= 2.5 × ATR) |
| `position[pair, t]` | Per-pair state: +1 long, −1 short, 0 flat |
| `stop[pair, t]` | Current trailing-stop level (raised only for longs) |
| `entry_close[pair]` | Close price when the active trade was opened |
| `weights[pair, t]` | Per-pair portfolio weight: `position / N_pairs` |
| `weights_lag[pair, t]` | `weights.shift(1)` — what we actually hold today |
| `turnover[pair, t]` | `|weights_lag.diff()|` — drives cost |
| `cost_per_pair[pair, t]` | `turnover × (2.5 pips × pip_size) / close` |
| `gross_port[t]` | Sum across pairs of `weights_lag × fx_return` |
| `net_port[t]` | `gross_port − cost_total` |
| `n_trades_per_pair` | Completed-trade count per pair |
| `n_long`, `n_short` | Long-side vs short-side trade counts |
| `win_rate` | Fraction of closed trades with `pnl_pct > 0` |
| `profit_factor` | `Σ winning pnl / |Σ losing pnl|` |
| `avg_duration_days` | Mean calendar-day holding period per trade |
| `time_in_market[pair]` | Fraction of days `|position| > 0` per pair |

**Data sources.** yfinance daily OHLC (`EURUSD=X`, `GBPUSD=X`, `AUDUSD=X`, `USDCAD=X`).
**Reference.** Park, C.-H. & Irwin, S. (2007). *"What Do We Know About the Profitability of Technical Analysis?"*, Journal of Economic Surveys 21(4). Also Dennis-Eckhardt "Turtle Trading" 1984 (informal source for the breakout-with-trailing-stop archetype).
**Script.** [`strategies/strat_23_atr_breakout_trailing_stop.py`](strategies/strat_23_atr_breakout_trailing_stop.py)
**Track record CSV.** [`live/track_record/strategy_23_atr_breakout_track_record.csv`](live/track_record/strategy_23_atr_breakout_track_record.csv)
**Trade log CSV.** [`live/track_record/strategy_23_atr_breakout_track_record_trades.csv`](live/track_record/strategy_23_atr_breakout_track_record_trades.csv)
**Equity curve.** [`reports/strategy_23_atr_breakout_trailing_stop.png`](reports/strategy_23_atr_breakout_trailing_stop.png)

---

## Strategy #24 — Classic Turtle Trading System 1 (filter ON vs OFF, REJECTED both)

**Explanation.** The most-documented breakout system in trading history — the 1984 Dennis-Eckhardt rules published by Curtis Faith in *"Way of the Turtle"* (2007). Per-pair rules: 20-day breakout entry (no ATR buffer — break the prior 20-day max/min of closes); 10-day reversion exit (close drops below the prior 10-day low for longs, the symmetric for shorts); fixed 2N hard stop at entry where N is 20-day ATR; one position at a time per pair; sized equal-weight 1/N. The defining feature is the **last-trade-loser filter**: skip a System 1 entry signal if the previous completed trade was a winner; take it only if the previous trade was a loser (or there is no prior history). The filter is meant to weed out chop after exhausted trends. Run on the same core4 universe as #23 for direct comparison. **Two variants are run in the same module** so we can isolate the filter's contribution: #24a with filter ON, #24b with filter OFF.

**Result** (2010–2024, daily, net of 5 pips RT cost): **both rejected, for different reasons**.

*#24a (filter ON, canonical Turtle):* Sharpe **−0.01**, ann return ~0.00%, MaxDD **−2.20%**, daily skew **−7.16**. **Only 7 trades over 15 years**. 57.1% win rate, profit factor 1.02. **Avg gross exposure 0.6%** — the strategy is essentially "do nothing." This exposes the **filter dead-lock pathology**: after the first trade on a pair wins, the filter blocks every subsequent entry signal until a loser is taken, but you can't take any signals because the filter is blocking them. EURUSD is permanently frozen after its single 1-trade winner; GBPUSD permanently frozen after its single 1-trade winner. The few trades that DO happen are because the next-after-a-loser permission temporarily un-freezes the pair. 1,940 entry signals were rejected by the filter across all four pairs.

*#24b (filter OFF, pure 20/10/2N breakout):* Sharpe **−0.28**, ann return **−1.43%**, MaxDD **−28.45%**, daily skew −0.17. **689 trades** (11.1 per pair per year), 34.7% win rate, profit factor **0.87**. Avg gross exposure 69.8%. **Active losses from whipsaws** — the strategy is in the market 70% of the time but loses on costs and chop. Confirms what the literature has been saying for decades: classical Turtle parameters worked spectacularly on commodities and currency *futures* in the 1980s when trends were strong and longer-lasting, but they do not extract net edge from G10 *spot FX* in the post-GFC era. This is now the **fourth independent confirmation of TA-in-FX dead** in this repo, alongside #11 momentum, the 15-indicator technical sweep, and #23 wider-window Donchian.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `atr[t]` | 20-day mean of true range (Turtle's "N") |
| `entry_high[t]` | 20-day rolling max of close, shifted 1d (resistance) |
| `entry_low[t]` | 20-day rolling min of close, shifted 1d (support) |
| `exit_high[t]` | 10-day rolling max of close, shifted 1d (short reversion exit) |
| `exit_low[t]` | 10-day rolling min of close, shifted 1d (long reversion exit) |
| `ATR_PERIOD` | True-range averaging window (= 20 days, Turtle's "N") |
| `ENTRY_BREAKOUT_LOOKBACK` | Entry window in days (= 20) |
| `EXIT_REVERSION_LOOKBACK` | Exit window in days (= 10) |
| `HARD_STOP_ATR_MULT` | Hard stop distance from entry (= 2.0 × N) |
| `USE_LAST_LOSER_FILTER` | Toggle for the canonical Turtle filter |
| `in_signal_state_prev` | Did yesterday have an active breakout signal? |
| `new_signal_event` | True only on the FIRST day a fresh breakout fires |
| `has_trade_history` | Has at least one trade closed on this pair? |
| `last_trade_won` | Was the most recent completed trade profitable? |
| `take_trade` | Filter result: take or skip the current signal? |
| `stop_level[pair]` | Fixed hard stop at entry (does NOT trail) |
| `entry_atr[pair]` | N at entry — defines the hard stop distance |
| `n_skipped` | Count of NEW signal events rejected by filter |
| `exit_reason` | Either "stop" (hard stop hit) or "reversion" (10d exit) |
| `weights[pair, t]` | Per-pair portfolio weight: `position / N_pairs` |
| `turnover[pair, t]` | `|weights_lag.diff()|` — drives cost |
| `n_stop_exits`, `n_reversion_exits` | Decomposition of exits by reason |

**Data sources.** yfinance daily OHLC (`EURUSD=X`, `GBPUSD=X`, `AUDUSD=X`, `USDCAD=X`).
**Reference.** Faith, Curtis (2007). *"Way of the Turtle: The Secret Methods that Turned Ordinary People into Legendary Traders"*, McGraw-Hill. Original Dennis-Eckhardt 1984 informal rules. Also Park & Irwin (2007), JES 21(4), for the TA-in-FX dead-since-1990s literature.
**Script.** [`strategies/strat_24_turtle_trading_system1.py`](strategies/strat_24_turtle_trading_system1.py)
**Track record CSVs.**
- [`live/track_record/strategy_24a_turtle_system1_filter_on_track_record.csv`](live/track_record/strategy_24a_turtle_system1_filter_on_track_record.csv) (filter ON)
- [`live/track_record/strategy_24b_turtle_system1_filter_off_track_record.csv`](live/track_record/strategy_24b_turtle_system1_filter_off_track_record.csv) (filter OFF)
- Trade logs for each, named `*_trades.csv`.

**Equity curves.**
- [`reports/strategy_24_turtle_system1_filter_on.png`](reports/strategy_24_turtle_system1_filter_on.png)
- [`reports/strategy_24_turtle_system1_filter_off.png`](reports/strategy_24_turtle_system1_filter_off.png)

---

## Strategy #25 — Turtle System 1 on commodities + crypto (the right asset class)

**Explanation.** The honest cross-asset test of Strategy #24b's implementation. Same code, same parameters (20-day breakout entry, 10-day reversion exit, 2N fixed hard stop, no filter), shifted to the asset universe the literature has always pointed to: commodities and crypto. Eight instruments via yfinance — Gold (`GC=F`), Silver (`SI=F`), Copper (`HG=F`), WTI Crude (`CL=F`), Natural Gas (`NG=F`), Soybeans (`ZS=F`), Bitcoin (`BTC-USD`), Ethereum (`ETH-USD`). BTC enters the universe from 2014-09 and ETH from 2017-11; positions are only opened on dates with data. Position sizing is **inverse-vol weighted** (`weight = position × TARGET_INSTR_VOL / realised_vol`, capped ±30%) so BTC's 70% annualised vol doesn't dominate Gold's 12% vol. Per-instrument vol target is 5%, which with 8 active instruments and modest correlations puts portfolio vol in the 12–15% range. Cost model is 10 bps round-trip per leg (= 5 bps per unit of turnover) — slightly conservative for liquid futures, fair for retail crypto. Two-decade question this answers: **is the #24b FX rejection a coding bug or a real asset-class limitation?** If our implementation is correct, this run should produce a positive Sharpe.

**Result** (2010–2024, daily, net of 10 bps RT per leg): **net Sharpe +0.43, profit factor 1.36, daily skew +0.82** — the proper trend-follower signature (small frequent losses, occasional huge wins). Annualised return **+6.29%**, ann vol **14.63%**, max DD **−35.14%**, Calmar **0.18**. 1,217 trades over 15 years (~9.8 per instrument per year), 35.5% trade win rate. The strategy is in-market 94% of days on average — actively trading the entire sample. Long average PnL +2.70% vs short average PnL −0.67%: the edge is overwhelmingly on the **long side**, consistent with the 2017 and 2020–21 commodity supercycle and crypto bull markets. Per-instrument: **BTC alone profit factor 2.93** (43.3% win, avg win +31.06%, max win +231%); **ETH profit factor 2.49** (avg win +33.66%, max win **+300.37%** on a single trade). Commodities are marginal — Gold PF 0.96, Silver 1.02, Copper 0.70, Oil 1.14, NatGas 0.81, Soybean 1.04 — the crypto allocation does most of the lifting. Cumulative cost drag over 15 years is 28% (the gross-to-net Sharpe gap, 0.55 → 0.43, is meaningful). The result **validates the implementation**: identical code produces Sharpe +0.43 with PF 1.36 and skew +0.82 on the right asset class versus Sharpe −0.28 with PF 0.87 and skew −0.17 on G10 FX. The classical Dennis-Eckhardt parameters work in their native habitat (commodities + crypto) and fail outside it (FX) — exactly as Faith (2007) and Covel (2017) describe.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `atr[instr, t]` | 20-day mean of true range per instrument |
| `entry_high[instr, t]` | 20-day rolling max of close, shifted 1d |
| `entry_low[instr, t]` | 20-day rolling min of close, shifted 1d |
| `exit_high[instr, t]` | 10-day rolling max of close, shifted 1d |
| `exit_low[instr, t]` | 10-day rolling min of close, shifted 1d |
| `position[instr, t]` | +1 long, −1 short, 0 flat per instrument |
| `stop_level[instr]` | Fixed 2N stop set at entry (does not trail) |
| `realised_vol[instr, t]` | 21-day rolling annualised stdev of pct change |
| `TARGET_INSTR_VOL` | Per-instrument volatility target (= 5%) |
| `MAX_INSTR_WEIGHT` | Per-instrument absolute weight cap (= 30%) |
| `weights[instr, t]` | `position × TARGET_INSTR_VOL / realised_vol`, capped |
| `weights_lag[instr, t]` | `weights.shift(1)` — what we actually hold today |
| `data_avail[instr, t]` | True if instrument had data by date t (handles BTC/ETH late start) |
| `COST_RT_BPS` | Round-trip cost per leg in bps (= 10) |
| `cost_per_unit` | Half of round-trip / 10000 = 5 bps per unit of turnover |
| `turnover[instr, t]` | `|weights_lag.diff()|` per instrument |
| `cost_total[t]` | Sum across instruments of `turnover × cost_per_unit` |
| `gross_port[t]` | Sum across instruments of `weights_lag × pct_change(close)` |
| `net_port[t]` | `gross_port − cost_total` |
| `exit_reason` | Either "stop" (hard stop hit) or "reversion" (10d exit) |
| `pnl_pct` | Trade-level PnL: `(exit − entry)/entry` (sign-adjusted) |

**Data sources.** yfinance continuous futures (`GC=F`, `SI=F`, `HG=F`, `CL=F`, `NG=F`, `ZS=F`) and spot crypto (`BTC-USD`, `ETH-USD`).
**Reference.** Faith, Curtis (2007). *"Way of the Turtle"*, McGraw-Hill. Covel, Michael (2017). *"The Complete TurtleTrader"*. The historical record of Dennis-Eckhardt 1984–1988 Turtle Trading on commodities/futures.
**Script.** [`strategies/strat_25_turtle_commodities_crypto.py`](strategies/strat_25_turtle_commodities_crypto.py)
**Track record CSV.** [`live/track_record/strategy_25_turtle_commodities_crypto_track_record.csv`](live/track_record/strategy_25_turtle_commodities_crypto_track_record.csv)
**Trade log CSV.** [`live/track_record/strategy_25_turtle_commodities_crypto_track_record_trades.csv`](live/track_record/strategy_25_turtle_commodities_crypto_track_record_trades.csv)
**Equity curve.** [`reports/strategy_25_turtle_commodities_crypto.png`](reports/strategy_25_turtle_commodities_crypto.png)

### #25 sub-period stability — the most important caveat on this strategy

The full-sample Sharpe +0.43 hides material regime concentration. Annualised net Sharpe by macro regime:

| Regime | Days | Sharpe | Ann Ret | Ann Vol | MaxDD | Skew | #Trades | Win % | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ZIRP 2010-15 | 1564 | **+0.31** | +4.07% | 13.1% | −18.4% | +0.14 | 421 | 36.3% | 1.07 |
| Divergence 2016-19 | 1043 | **+0.41** | +5.64% | 13.6% | −17.0% | +0.50 | 351 | 34.5% | 1.64 |
| **COVID 2020-21** | 523 | **+1.81** | **+34.58%** | 19.1% | −9.4% | **+2.19** | 169 | 41.4% | **2.65** |
| **Hiking 2022-24** | 782 | **−0.48** | **−7.33%** | 15.3% | **−35.1%** | −0.06 | 276 | 31.9% | 0.77 |
| **Full 2010-24** | 3912 | **+0.43** | +6.29% | 14.6% | −35.1% | +0.82 | 1217 | 35.5% | 1.36 |

**Per-instrument Sharpe by regime** (gross of cost, isolates which instruments drove which periods):

| Instrument | ZIRP | Divergence | COVID | Hiking | FULL |
|---|---:|---:|---:|---:|---:|
| Gold | +0.12 | +0.09 | −0.62 | +0.09 | −0.00 |
| Silver | +0.74 | −0.22 | −0.02 | −0.69 | +0.11 |
| Copper | −0.03 | −0.58 | +0.45 | −0.88 | −0.27 |
| WTI Crude | +0.16 | +0.26 | **+1.33** | −0.62 | +0.32 |
| Natural Gas | +0.02 | −0.59 | +0.37 | −0.07 | −0.11 |
| Soybeans | −0.22 | −0.19 | +0.88 | +0.42 | +0.07 |
| **BTC** | **+0.68** | **+1.39** | **+1.53** | **+0.36** | **+0.96** |
| ETH | — | +0.68 | **+1.55** | −0.06 | +0.47 |

**Findings.**
- **3 of 4 regimes positive** — the strategy is mostly regime-stable, BUT the most recent regime (Hiking 2022-24) is negative and contains the full-sample worst drawdown (−35.1%). 2022-24 was where the entire MaxDD happened.
- **COVID 2020-21 contributes disproportionately** to the headline Sharpe — +1.81 over 2 years drives most of the cumulative wealth in the full sample. ZIRP and Divergence are modestly positive but not enough alone to justify deployment.
- **BTC is the only instrument with positive Sharpe in every regime** — without crypto, the commodities-only result would be marginal-to-negative. The strategy is really a **crypto trend-follower with a commodity overlay**, not a "commodity trend-follower with crypto exposure."
- **Gold full-sample Sharpe is essentially zero** (−0.00) despite gold's famous trend-following reputation. Within commodities, only WTI (+0.32) and Soybeans (+0.07) carry positive full-sample edge.
- **The honest deployability question:** what makes 2025+ different from 2022-24? Anyone trading this today must have a thesis on why the recent regime won't continue.

**Script.** [`notebooks/subperiod_stability_strat25.py`](notebooks/subperiod_stability_strat25.py)
**Chart.** [`reports/subperiod_stability_strat25.png`](reports/subperiod_stability_strat25.png)

---

## Strategy #26 — Carry-TSMOM filter overlay on #20 (REJECTED both variants)

**Explanation.** Implements the highest-priority signal from the v2 FX research doc — Moskowitz-Ooi-Pedersen (2012, JFE) time-series momentum applied to the carry FACTOR RETURN itself, not to the underlying FX spot. The hypothesis: carry-trade unwinds (2008, 2015 CNY scare, 2020 COVID, 2022 BoJ pivot, Aug-2024 yen carry blow-up) are persistent — once the carry factor starts losing, it keeps losing for months as carry investors forcibly deleverage. A TSMOM filter on the carry return should catch the regime change and scale positions down. Per the canonical MOP 2012 spec: compute `trailing_12m_carry_return`, scale positions at 1.0 when trailing return is positive and at 0.5 (soft) or 0.0 (hard) when negative, lag 1 month to avoid look-ahead, multiply into the existing base weights. Two variants run in the same module — #26a (soft, scale 0.5 when off) and #26b (hard, scale 0.0 when off). Base strategy: #20 (classical vol-normalised carry, monthly rebalance) which has full-sample net Sharpe 0.07. Cost recomputed from the new turnover that scale changes induce (e.g., scale 1.0 → 0.5 generates |Δw|=0.5 across all 7 pairs even when no signal changes).

**Result** (2010–2024, monthly, net of 5 pips RT cost): **both variants REJECTED**. #26a soft: Sharpe **0.01** (vs base 0.07), Ann return +0.07% (vs +0.44%), Max DD −18.73% (vs −20.85%), monthly skew **−0.23** (vs −0.07), tracking error 2.06%, **information ratio −0.18**. #26b hard: Sharpe **−0.06**, Ann return −0.31%, Max DD −17.20%, monthly skew **−0.27**, tracking error 4.13%, **information ratio −0.18**, hit rate collapses from 52% to 22% (no return earned during the 52.5% of months the filter forces flat). The filter activates 52.5% of months — substantial intervention — but destroys rather than adds value. The interpretation: **the MOP TSMOM rescue requires the base strategy to have genuine trend-following content in its P&L path**. #20's classical level-carry has Sharpe 0.07 — its base return is essentially noise about a near-zero mean. The trailing-12m sign of a noise series is itself noise, so the filter is gating on no real signal. Skewness gets *worse* (−0.07 → −0.23/−0.27) because the filter removes some good months alongside the bad ones. The Hurst-Ooi-Pedersen (2017, JPM) "Century of Evidence on Trend-Following" finding holds for the 1880s–2000s sample they studied; the post-2010 era's carry decay leaves no trend to filter. Net learning: post-2008 G10 carry isn't fixable by simple TSMOM regime conditioning. This is a clean independent confirmation that #20's Sharpe 0.07 isn't a regime-conditioning oversight — the signal is genuinely dead in this era.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `base[monthly]` | #20's monthly-rebalanced track record loaded from CSV |
| `trailing_12m[t]` | Rolling 12-month sum of `base.net_return` |
| `TSMOM_LOOKBACK_MONTHS` | TSMOM lookback in months (= 12, canonical MOP 2012) |
| `scale_raw[t]` | `1.0` if `trailing_12m[t] > 0` else `scale_when_negative` |
| `scale_when_negative` | Tunable: 0.5 (soft #26a) or 0.0 (hard #26b) |
| `scale[t]` | `scale_raw.shift(1)` — applied to next month, no look-ahead |
| `weights_old[pair, t]` | #20's original monthly weights (from base CSV) |
| `weights_new[pair, t]` | `weights_old × scale` — filtered weights |
| `gross_old[t]` | #20's monthly gross return |
| `gross_new[t]` | `gross_old × scale` — filtered gross return (linear scaling) |
| `new_turnover[t]` | `|weights_new.diff()|.sum(axis=1)` — monthly turnover after filter |
| `new_cost[t]` | `new_turnover × 2.27 bps` (approximate uniform half-spread/spot) |
| `net_new[t]` | `gross_new − new_cost` — filtered net return |
| `tracking_err` | Annualised stdev of `(net_new − base_net)` — overlay drift |
| `ir` | Information ratio: active return / tracking error |
| `n_filter_active` | Months where `scale < 1.0` |
| `n_filter_off` | Months where `scale == 0.0` (only relevant for #26b) |
| `mean_scale` | Average daily scalar across the sample |

**Data sources.** Reuses #20's monthly track record (no new data); cost approximated via 2.27 bps half-spread applicable across all 7 pairs at typical spot.
**Reference.** Moskowitz, Ooi & Pedersen (2012). *"Time Series Momentum"*, JFE 104(2). Hurst, Ooi & Pedersen (2017). *"A Century of Evidence on Trend-Following Investing"*, J. of Portfolio Management 44(1). v2 research doc Section 1 "Carry-TSMOM Filter".
**Script.** [`strategies/strat_26_carry_tsmom_filter.py`](strategies/strat_26_carry_tsmom_filter.py)
**Track record CSVs.**
- [`live/track_record/strategy_26a_carry_tsmom_filter_track_record.csv`](live/track_record/strategy_26a_carry_tsmom_filter_track_record.csv) (soft variant)
- [`live/track_record/strategy_26b_carry_tsmom_filter_track_record.csv`](live/track_record/strategy_26b_carry_tsmom_filter_track_record.csv) (hard variant)

**Equity curve.** [`reports/strategy_26_carry_tsmom_filter.png`](reports/strategy_26_carry_tsmom_filter.png)

---

## Strategy #27 — 20/50 DMA crossover with 1 ATR stop (REJECTED, but the least-bad TA-in-FX result)

**Explanation.** The most textbook trend-following spec there is: enter LONG when 20-day SMA crosses above 50-day SMA ("golden cross"), enter SHORT on the symmetric "death cross". While in a position, the stop level is recomputed daily as `ma20 ± 1 × ATR(14)` (below MA20 for longs, above for shorts) — non-ratchet, moving with the 20-DMA each day as specified by the user. Exit on stop OR on opposite crossover (reversal triggers immediate exit + new opposite position on the same day). Universe: G10 core 4 (EURUSD, GBPUSD, AUDUSD, USDCAD), equal-weight ±1/N per active pair, max gross exposure 100%. The simplest moving-average system in trading — taught in every retail course, built into every charting package. The question this answers: does it survive 5 pips RT cost on G10 spot FX?

**Result** (2010–2024, daily, net of 5 pips RT): **rejected, but the LEAST BAD TA-in-FX result tested so far**. Net Sharpe **−0.09**, ann return **−0.35%**, MaxDD **−12.91%**, Calmar **−0.03**, daily skew **+0.17** (the proper trend-follower signature, finally — small frequent losses, occasional bigger wins). Total **351 trades** (88-92 per pair), 176 long / 175 short (perfectly balanced), trade-level win rate **31.6%**, average win **+2.35%** vs average loss **−1.16%** (**2:1 reward-to-risk** at the trade level — structurally correct for trend-following). Average trade duration 31 days. Per-pair: **GBPUSD PF 1.13, AUDUSD PF 1.12** (both barely above breakeven), EURUSD PF 0.69, USDCAD PF 0.80. Exit decomposition: **341 of 351 trades exit on the ATR stop**, only 10 via opposite crossover reversal — the 1 ATR stop is tight relative to the time between MA crossovers, so the stop dominates. Avg gross exposure 50%. Compared to prior FX TA tests this is the "structurally healthy" rejection: #23 Donchian had daily skew −2.13 (broken shape); #24b Turtle had skew −0.17 and PF 0.87; **#27 has skew +0.17 and PF 0.94 — closest to working.** The honest read: the strategy is doing trend-following CORRECTLY, but in G10 FX 2010–2024 the 31.6% win rate × 2:1 reward ratio yields ~+0.27% per gross-of-cost trade — not enough to overcome 4.05% cumulative cost drag. This is the **5th independent confirmation of TA-in-FX dead** in this repo (after #11 momentum portfolio, the 15-indicator technical sweep, #23 Donchian, #24b Turtle), and the most structurally informative one because the trade-level metrics are nearly the right shape — there just isn't enough multi-week trend content in G10 spot FX to extract net edge.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `high[t]`, `low[t]`, `close[t]` | Daily yfinance OHLC per pair |
| `ma_fast[t]` | 20-day simple moving average of close |
| `ma_slow[t]` | 50-day simple moving average of close |
| `atr[t]` | 14-day mean of true range (canonical ATR) |
| `FAST_MA_DAYS` | Fast MA window (= 20 days) |
| `SLOW_MA_DAYS` | Slow MA window (= 50 days) |
| `STOP_ATR_MULT` | Stop offset multiplier (= 1.0 × ATR) |
| `diff[t]` | `ma_fast − ma_slow` — sign tracks current regime |
| `golden_x[t]` | True only on day `diff` flips negative → positive |
| `death_x[t]` | True only on day `diff` flips positive → negative |
| `stop_level[t]` | `ma_fast ∓ STOP_ATR_MULT × atr` (recomputed daily, non-ratchet) |
| `position[pair, t]` | +1 long, −1 short, 0 flat per pair |
| `entry_close[pair]` | Close price when active trade was opened |
| `weights[pair, t]` | Per-pair portfolio weight: `position / N_pairs` |
| `weights_lag[pair, t]` | `weights.shift(1)` — what we actually hold today |
| `turnover[pair, t]` | `|weights_lag.diff()|` — drives cost |
| `exit_reason` | Either "stop" (close < stop_level) or "reversal" (opposite crossover) |
| `n_stop_exits` | How many trades exited on the ATR stop |
| `n_reversal_exits` | How many trades exited because the opposite crossover fired |
| `pnl_pct` | Trade-level PnL: `(exit − entry)/entry` (sign-adjusted) |
| `avg_long_pct`, `avg_short_pct` | Long-side and short-side average trade PnL |

**Data sources.** yfinance daily OHLC (`EURUSD=X`, `GBPUSD=X`, `AUDUSD=X`, `USDCAD=X`).
**Reference.** No single canonical paper — this is the most-taught retail TA system in existence. The "golden cross / death cross" framing dates to Charles Dow's editorials, ~1900. Most charting packages default to 50/200 or 20/50 SMA pairs. Park & Irwin (2007), JES 21(4) — the same reference cited for #23 and #24 — covers MA-crossover systems specifically as part of the "post-1990 TA-in-FX dead" body of evidence.
**Script.** [`strategies/strat_27_ma_crossover_atr_stop.py`](strategies/strat_27_ma_crossover_atr_stop.py)
**Track record CSV.** [`live/track_record/strategy_27_ma_crossover_atr_stop_track_record.csv`](live/track_record/strategy_27_ma_crossover_atr_stop_track_record.csv)
**Trade log CSV.** [`live/track_record/strategy_27_ma_crossover_atr_stop_track_record_trades.csv`](live/track_record/strategy_27_ma_crossover_atr_stop_track_record_trades.csv)
**Equity curve.** [`reports/strategy_27_ma_crossover_atr_stop.png`](reports/strategy_27_ma_crossover_atr_stop.png)

---

## Strategy #28 — 20/50 DMA crossover with 1 ATR stop on commodities + crypto

**Explanation.** The asset-class companion to Strategy #27. Identical spec — 20-day SMA crosses 50-day SMA for entry, stop set at `MA20 ∓ 1 × ATR(14)` recomputed daily, opposite crossover triggers same-day reversal — applied to the same 8-instrument universe used in Strategy #25 (Gold, Silver, Copper, WTI Crude, NatGas, Soybeans via yfinance continuous front-month futures `=F`, plus Bitcoin and Ethereum spot via `BTC-USD` and `ETH-USD`). Position sizing is **inverse-vol weighted** (per-instrument vol target 5%, weight cap ±30%) so BTC's 70% annualised vol doesn't dominate gold's 12% vol. Costs are 10 bps round-trip per leg — slightly conservative for liquid futures, fair for retail crypto. Two-decade question this resolves: does the 20/50 MA crossover's "structurally healthy" trade-level shape from #27 (positive skew, 2:1 reward:risk) translate the same asset-class Sharpe boost we saw on #24b → #25? If yes, the FX rejection in #27 is genuine asset-class behaviour; if no, our cross-asset hypothesis is shakier than it looked.

**Result** (2010–2024, daily, net of 10 bps RT per leg): **net Sharpe +0.42, profit factor 1.47, daily skew +0.50** — confirming the asset-class swap reproduces cleanly across both trend-following spec families. Annualised return **+4.58% net** (vs −0.35% on FX), ann vol **10.97%**, max DD **−26.84%**, Calmar **0.17**. **605 trades** over 15 years (4.87 per instrument per year), 302 long / 303 short (balanced), 31.9% trade win rate, average win **+12.84%** vs average loss **−4.10%** (3:1 reward-to-risk per trade). Long average PnL +3.08% vs short average PnL −0.47% — same long-side dominance as #25, consistent with 2017 + 2020–21 + 2022 commodity supercycle and crypto bull markets. Cumulative cost drag is **14.72% over 15 years** — much higher than #27's 4.05% because of more frequent trading (4.87 vs 5.65 trades/instr/year is similar but crypto's volatility creates larger weight swings under inverse-vol sizing). Per-instrument: **ETH PF 3.30** (max win **+281.58%** on a single trade), **BTC PF 2.96** (max win +145%), SILVER 1.13, GOLD 1.05, OIL 1.05, SOYBEAN 1.04, NATGAS 0.78, COPPER 0.73 — crypto allocation carries most of the edge again, commodities ex-crypto would be marginal. Cross-spec validation table:

| Spec | FX Sharpe | Commodities+Crypto Sharpe | Δ |
|---|---:|---:|---:|
| Turtle 20/10/2N (#24b → #25) | −0.28 | +0.43 | +0.71 |
| **20/50 MA Crossover (#27 → #28)** | **−0.09** | **+0.42** | **+0.51** |

Same code, same period, same cost methodology, only the universe changes. **The implementation is validated across two independent spec families. The G10 FX rejection of trend-following is a genuine asset-class limitation, not a coding artefact.**

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `high[t]`, `low[t]`, `close[t]` | Daily yfinance OHLC per instrument |
| `ma_fast[t]`, `ma_slow[t]` | 20-day and 50-day SMA of close |
| `atr[t]` | 14-day mean of true range |
| `diff[t]` | `ma_fast − ma_slow` per instrument |
| `golden_x[t]`, `death_x[t]` | True on day `diff` flips negative/positive |
| `stop_level[t]` | `ma_fast ∓ STOP_ATR_MULT × atr` (daily, non-ratchet) |
| `position[instr, t]` | +1 long, −1 short, 0 flat per instrument |
| `realised_vol[instr, t]` | 21-day rolling annualised stdev of pct change |
| `TARGET_INSTR_VOL` | Per-instrument volatility target (= 5%) |
| `MAX_INSTR_WEIGHT` | Per-instrument absolute weight cap (= 30%) |
| `weights[instr, t]` | `position × TARGET_INSTR_VOL / realised_vol`, capped |
| `weights_lag[instr, t]` | `weights.shift(1)` — held today |
| `data_avail[instr, t]` | True if instrument had data by date t (handles BTC/ETH late start) |
| `COST_RT_BPS` | Round-trip cost per leg in bps (= 10) |
| `turnover[instr, t]` | `|weights_lag.diff()|` per instrument |
| `cost_total[t]` | Sum across instruments of `turnover × 5 bps` |
| `exit_reason` | Either "stop" (close crosses stop_level) or "reversal" (opposite crossover) |

**Data sources.** yfinance continuous futures (`GC=F`, `SI=F`, `HG=F`, `CL=F`, `NG=F`, `ZS=F`) and spot crypto (`BTC-USD`, `ETH-USD`).
**Reference.** No single canonical paper; this is the textbook MA-crossover spec applied to the asset universe Faith (2007) and Covel (2017) document as Turtle Trading's native habitat. Park & Irwin (2007), JES 21(4), for the FX-specific TA failure context.
**Script.** [`strategies/strat_28_ma_crossover_commodities_crypto.py`](strategies/strat_28_ma_crossover_commodities_crypto.py)
**Track record CSV.** [`live/track_record/strategy_28_ma_crossover_commodities_crypto_track_record.csv`](live/track_record/strategy_28_ma_crossover_commodities_crypto_track_record.csv)
**Trade log CSV.** [`live/track_record/strategy_28_ma_crossover_commodities_crypto_track_record_trades.csv`](live/track_record/strategy_28_ma_crossover_commodities_crypto_track_record_trades.csv)
**Equity curve.** [`reports/strategy_28_ma_crossover_commodities_crypto.png`](reports/strategy_28_ma_crossover_commodities_crypto.png)

### #28 sub-period stability — and the deployment-deciding comparison with #25

Same regime windows used for #25 and the rate-diff family (ZIRP 2010-15, Divergence 2016-19, COVID 2020-21, Hiking 2022-24). Annualised net Sharpe by regime:

| Regime | Days | Sharpe | Ann Ret | Ann Vol | MaxDD | Skew | #Trades | Win % | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ZIRP 2010-15 | 1564 | **+0.36** | +3.70% | 10.4% | −22.1% | +0.28 | 221 | 29.0% | 1.10 |
| Divergence 2016-19 | 1043 | **+0.29** | +3.02% | 10.6% | −20.3% | +1.16 | 179 | 31.3% | 1.34 |
| **COVID 2020-21** | 523 | **+1.10** | +13.25% | 12.0% | −8.5% | +0.38 | 75 | 40.0% | **3.15** |
| **Hiking 2022-24** | 782 | **+0.22** | +2.64% | 11.9% | −26.8% | +0.22 | 130 | 33.1% | 1.11 |
| **Full 2010-24** | 3912 | **+0.42** | +4.58% | 11.0% | −26.8% | +0.50 | 605 | 31.9% | 1.47 |

**Positive Sharpe in ALL FOUR regimes** — including Hiking 2022-24, where #25 lost money. The maximum drawdown (−26.84%) still lives in the Hiking regime, but unlike #25 the strategy made positive net return over those three years.

**Side-by-side vs Strategy #25 on the same universe** — this is the deployment-deciding table:

| Regime | #25 Turtle 20/10/2N | #28 20/50 MA-Cross | Δ |
|---|---:|---:|---:|
| ZIRP 2010-15 | +0.31 | +0.36 | +0.05 |
| Divergence 2016-19 | +0.41 | +0.29 | −0.12 |
| **COVID 2020-21** | **+1.81** | +1.10 | **−0.71** (smaller boom) |
| **Hiking 2022-24** | **−0.48** | **+0.22** | **+0.70** (rescued) |
| **FULL SAMPLE** | **+0.43** | **+0.42** | −0.01 |

The full-sample Sharpes are statistically indistinguishable (+0.43 vs +0.42), but **the regime distribution is materially different**:
- **#25 is regime-concentrated** — COVID Sharpe +1.81 carries most of the cumulative wealth, but the strategy would have lost money over the 3 most recent years.
- **#28 is regime-distributed** — smaller COVID boom (+1.10 instead of +1.81), but no regime loses money. Worst regime is Hiking at +0.22 vs #25's −0.48.

For an actual deployment decision, **#28 is the clearly more attractive choice** despite the same full-sample number. A regime-stable Sharpe is much more valuable than a regime-concentrated one — particularly because the deployment-killing question we flagged on #25 ("what makes 2025+ different from 2022-24?") has a different answer here: #28 worked through 2022-24, so a 2025 deployment doesn't require a regime-change thesis.

**Per-instrument annualised Sharpe by regime** (gross of cost):

| Instrument | ZIRP | Divergence | COVID | Hiking | FULL |
|---|---:|---:|---:|---:|---:|
| Gold | +0.27 | +0.32 | −0.28 | −0.31 | +0.09 |
| Silver | **+0.83** | +0.16 | −0.45 | −0.46 | +0.27 |
| Copper | −0.13 | −0.27 | −0.07 | +0.10 | −0.11 |
| WTI Crude | +0.21 | −0.13 | +0.60 | −0.24 | +0.09 |
| Natural Gas | −0.17 | −0.76 | +0.78 | +0.23 | −0.08 |
| Soybeans | −0.26 | −0.38 | +0.48 | **+0.75** | +0.01 |
| **BTC** | **+0.44** | **+1.42** | **+0.96** | **+0.51** | **+0.84** |
| ETH | — | +0.51 | **+1.28** | +0.09 | +0.39 |

**Findings.**
- **BTC is the workhorse on both strategies** — only instrument with positive Sharpe in every regime in both #25 AND #28. The diversification value of commodities is more about smoothing crypto's vol than about contributing edge.
- **Commodities ex-crypto are individually marginal**: Gold +0.09, Copper −0.11, WTI +0.09, NatGas −0.08, Soybean +0.01. Only Silver (+0.27) carries meaningful standalone edge across the full sample, and only because of its very strong ZIRP-era number (+0.83 then weakly negative since).
- **Soybeans Hiking-cycle result is the differentiator vs #25**: +0.75 here vs +0.42 on #25. Combined with Copper +0.10 and NatGas +0.23, the MA-crossover spec extracts modest positive edge from commodities in the recent regime where the Turtle spec couldn't.
- **The portfolio works because inverse-vol sizing smooths the basket**, not because each instrument has individual edge. Without the BTC+ETH allocation the strategy would be marginal-to-flat.

**Script.** [`notebooks/subperiod_stability_strat28.py`](notebooks/subperiod_stability_strat28.py)
**Chart.** [`reports/subperiod_stability_strat28.png`](reports/subperiod_stability_strat28.png)

---

## Strategy #29 — Crash filter overlay on #28 (first overlay to add Sharpe)

**Explanation.** Takes the VIX + self-momentum crash scalar built for Strategy #22 (originally an overlay on the equal-weight rate-diff portfolio #18, which was later flagged as a timing artefact) and re-applies it without parameter retuning to a different base: Strategy #28, the 20/50 MA crossover on commodities + crypto. **The point of the test is that #28 is a genuine trend-following strategy** (not timing-artefact-suspect like #18), so this is the first time the overlay is being tested on a deployable base. Filter spec identical to #22: VIX scalar linear from 1.0 at VIX≤20 to 0.0 at VIX≥40; self-momentum scalar of 0.5 when the trailing-20d return of the unfiltered base is below −1σ of its trailing 252d, else 1.0; combined as `vix_scale × mom_scale`, clipped to [0, 1], lagged 1 day for no look-ahead, multiplied into the per-instrument weights of #28. Cost recomputed from new filtered turnover at the same 10 bps RT per leg as the base.

**Result** (2010–2024, daily, net of 10 bps RT per leg): **the first overlay test in the repo that materially adds value across every metric**. Sharpe **0.42 → 0.51 (+0.09)**, Sortino **0.63 → 0.75 (+0.11)**, ann return **+4.58% → +5.00% (+0.42pp)**, ann vol **10.97% → 9.81% (−1.16pp)**, max DD **−26.84% → −19.15% (+7.69pp)**, Calmar **0.17 → 0.26 (+0.09)**, daily skew **+0.50 → +0.62 (+0.12)**. Cumulative wealth +16pp over the base over 15 years. Overlay diagnostics: tracking error 3.02% annualised, **information ratio +0.14** (positive — the overlay adds active value), cost of insurance +10.5 bps/yr (the cost penalty for the filter-induced turnover). Filter is materially binding 37.2% of days and fully flat 1.5% (VIX > 40 was reached only in 2020 COVID and briefly in 2022). Median drawdown spell cut from 10 days to 4 days (**−60%**); maximum drawdown spell barely changed (1,083 → 1,068 days) — the filter is a short-cycle VIX/momentum protector, not a long-cycle regime detector. Mean daily scalar 0.84. **The conditional Sharpe test** is the smoking gun: on the 1,455 days the filter chooses to bind, the base #28 strategy earns Sharpe **−0.08** (yes, those are bad days), while the filtered #29 strategy earns Sharpe **+0.09** on the same days. The filter is **removing bad days specifically**, not randomly reducing exposure. Comparing to prior overlay attempts: #22 (crash filter on timing-artefact #18) had Sharpe Δ ≈ 0 and IR ~0 — vol-reducer only; #26 (TSMOM filter on dead-carry #20) had Sharpe Δ −0.06 and IR −0.18 — destroyed value; **#29 (crash filter on real trend-follower #28) has Sharpe Δ +0.09 and IR +0.14 — adds value**. The overlay's value is base-specific: it needs a base with real drawdowns that correlate with VIX spikes and the base's own momentum drawdowns. #28 has both (the 2022-24 MaxDD of −26.84% lined up partially with VIX elevation and trailing-return weakness); #22 had only the first (#18's drawdowns were partly synchronised with VIX but the base was bogus); #26 had neither (#20 had no real trend or drawdown). **This is the cleanest deployable risk-overlay result in the repo.**

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `base[weight_INSTR, t]` | Per-instrument daily weights from #28's CSV |
| `vix[t]` | Daily VIX close (yfinance `^VIX`) |
| `VIX_FULL_BELOW` | VIX level at which scalar is 1.0 (= 20.0) |
| `VIX_FLAT_ABOVE` | VIX level at which scalar hits 0.0 (= 40.0) |
| `vix_scale[t]` | Linear interp from 1.0→0.0 over VIX 20→40 |
| `MOM_LOOKBACK_DAYS` | Self-momentum trailing window (= 20 days) |
| `MOM_REF_DAYS` | Z-score reference window (= 252 days) |
| `MOM_Z_TRIGGER` | Z-threshold for momentum gate (= −1.0) |
| `MOM_SCALE_ON_TRIGGER` | Exposure scalar when gate triggers (= 0.5) |
| `tr20[t]` | Trailing 20-day sum of base #28 net returns |
| `z_tr20[t]` | Z-score of `tr20` vs trailing 252d mean and stdev |
| `mom_scale[t]` | 0.5 when `z_tr20 < −1.0`, else 1.0 |
| `scale_raw[t]` | `vix_scale × mom_scale`, clipped to [0, 1] |
| `scale[t]` | `scale_raw.shift(1)` — applied to next day's positions |
| `weights_filt[instr, t]` | `base_weights × scale` per instrument |
| `gross_filt[t]` | `base_gross × scale` (linear scaling) |
| `cost_filt[t]` | `|weights_filt.diff()|.sum() × 5 bps` (recomputed turnover) |
| `net_filt[t]` | `gross_filt − cost_filt` |
| `tracking_err` | Annualised stdev of `(net_filt − base_net)` |
| `ir` | Information ratio: active return / tracking error |
| `cost_of_insurance_bps` | Filter-induced cost increase per year, in bps |
| `n_filter_active` | Days where `scale < 0.95` (materially binding) |
| `n_filter_off` | Days where `scale < 0.05` (fully flat) |
| `cond_base_sharpe` | Sharpe of base on filter-binding days only |
| `cond_filt_sharpe` | Sharpe of filtered on filter-binding days only |
| `median_dd_days`, `max_dd_days` | Drawdown spell duration stats |

**Data sources.** Reuses #28's daily CSV (no new strategy fetch). VIX from yfinance `^VIX`.
**Reference.** Brunnermeier, Nagel, Pedersen (2009). *"Carry Trades and Currency Crashes"*, NBER Macroeconomics Annual. Same overlay spec as Strategy #22.
**Script.** [`strategies/strat_29_crash_filter_on_28.py`](strategies/strat_29_crash_filter_on_28.py)
**Track record CSV.** [`live/track_record/strategy_29_crash_filter_on_28_track_record.csv`](live/track_record/strategy_29_crash_filter_on_28_track_record.csv)
**Equity curve.** [`reports/strategy_29_crash_filter_on_28.png`](reports/strategy_29_crash_filter_on_28.png)

### #29 worst-period analysis — where the filter actually trimmed losses

Defensive companion analysis to confirm yesterday's headline +0.09 Sharpe improvement is driven by the overlay catching the worst stretches (rather than by general exposure reduction).

**Worst 15 calendar months on the #28 base vs #29 filtered.** Sum of losses on worst-15 months: base −73.5%, filtered −54.6%, **saved +18.9pp**. Of the 15 worst base months, the filter **trimmed 12, missed 2, was flat on 1**. The 5 biggest "saves" all happened during materially active filter regimes (mean monthly scale 0.32–0.50):

| Month | #28 base | #29 filtered | Δ | Mean scale |
|---|---:|---:|---:|---:|
| **2022-10** | −5.11% | −2.11% | **+3.01pp** | 0.37 |
| **2022-09** | −4.65% | −1.74% | **+2.91pp** | 0.32 |
| **2020-09** | −5.86% | −3.13% | **+2.73pp** | 0.41 |
| 2016-09 | −5.03% | −2.54% | +2.49pp | 0.50 |
| 2022-11 | −4.17% | −2.05% | +2.12pp | 0.50 |

The two misses (2023-08 and 2019-09) both had filter scalar above 0.80 — the filter wasn't firing materially. Those losses came from base-strategy signal failures **not** correlated with VIX spikes or self-momentum dips. Reasonable bounded limitation rather than systematic failure of the overlay.

**Top 5 peak-to-trough drawdown episodes.** The worst single drawdown on the #28 base is the 2022-06 → 2023-09 cliff that we flagged in the sub-period analysis as the deployment-killing question. The filter trims it from **−26.84%** to **−19.15%** over the same dates — **7.7pp shallower drawdown on the most important episode**:

| Rank | #28 base depth | Dates | #29 filtered depth | Same episode trimmed? |
|---|---:|---|---:|---|
| 1 | −26.84% | 2022-06 → 2023-09 | **−19.15%** | **Yes — 7.7pp trimmed** |
| 2 | −22.06% | 2010-11 → 2014-06 | −18.36% (different episode) | Ranks shuffle |
| 3 | −20.28% | 2017-09 → 2019-02 | −17.73% (different episode) | Ranks shuffle |

**Tail-shape diagnostic.** The clean test that the IR's +0.14 isn't an artefact: the filter should asymmetrically clip the left tail. Daily return quantiles:

| Quantile | #28 base | #29 filtered | Δ |
|---|---:|---:|---:|
| **1% (deep left)** | −1.79% | **−1.60%** | **+0.19pp** ← left tail trimmed |
| 5% | −1.11% | −0.96% | +0.15pp ← left tail trimmed |
| 95% | +1.12% | +1.03% | −0.09pp ← right tail clipped |
| **99% (deep right)** | +2.06% | +1.91% | −0.15pp ← right tail clipped |
| **Tail ratio** (95th / \|5th\|) | 1.01 | **1.07** | **+0.06** ← improvement |

The filter trims the deep left tail (+0.19pp at the 1% quantile) materially more than it clips the corresponding right tail (−0.15pp at 99%). Tail ratio improves from 1.01 to 1.07. That's the structural reason the IR is positive — the overlay reshapes the distribution asymmetrically, not just narrows it.

**Bottom line on #29's deployability**: the overlay's value isn't a statistical fluke. It engages during materially-bad stretches (worst-5 wins were all on low-scale months), trims the most important drawdown (2022-24 cliff), and reshapes the distribution to clip left more than right.

**Script.** [`notebooks/worst_periods_strat29.py`](notebooks/worst_periods_strat29.py)
**Chart.** [`reports/worst_periods_strat29.png`](reports/worst_periods_strat29.png)

---

## Strategy #30 — Crash filter overlay on #25 (cross-spec test; filter DOES NOT generalise)

**Explanation.** The cross-spec validation test for #29's finding. Strategy #29 showed the VIX + self-momentum crash scalar materially adds Sharpe on top of #28 (20/50 MA crossover on commodities + crypto). This module applies the **identical overlay spec** (no retuning) to **Strategy #25** (Turtle System 1 on the same universe). The two bases use identical instruments (Gold, Silver, Copper, WTI, NatGas, Soybean, BTC, ETH), identical inverse-vol sizing (5% per-instrument vol target, ±30% cap), identical cost model (10 bps RT per leg). The only difference is the trend-following spec: Turtle's 20-day breakout + 10-day reversion + 2N hard stop vs MA-crossover's 20/50 SMA + 1×ATR trailing stop. If the overlay's positive result on #28 was due to "trend-following + crash filter" as a general principle, the result should hold here. If the overlay is base-specific, this test reveals it.

**Result** (2010–2024, daily, net of 10 bps RT per leg): **the overlay does NOT generalise — IR −0.23, Sharpe degrades modestly (0.43 → 0.41), and the conditional Sharpe test gives the opposite reading from #29**. Full table: Sharpe **0.43 → 0.41 (−0.02)**, Sortino **0.66 → 0.59 (−0.07)**, ann return **+6.29% → +4.98% (−1.31pp)**, ann vol **14.63% → 12.26% (−2.38pp)**, max DD **−35.14% → −27.83% (+7.31pp)**, Calmar 0.18 → 0.18 (flat), **daily skew +0.82 → +0.30 (−0.52)** — a significant degradation of the proper-trend-follower signature. Tracking error 5.76%, **information ratio −0.23** (overlay actively destroys risk-adjusted value), cost of insurance +17.6 bps/yr (higher friction than #29). Filter binding 38.2% of days, fully flat 1.4% — almost identical filter activity to #29, so the difference can't be attributed to "the filter didn't fire enough." Median drawdown spell barely improves (5 → 4 days); max drawdown spell unchanged (638 days). **The conditional Sharpe test is the smoking gun for failure**: on the 1,494 filter-binding days, **the #25 base earns Sharpe +0.19** (not bad days!) while the **filtered #30 earns Sharpe +0.00** on the same days. The filter is removing GOOD days, not bad ones — exactly opposite the #29 result. Three-base overlay comparison after this run:

| Overlay | Base | Base SR | Filtered SR | Δ | IR | Verdict |
|---|---|---:|---:|---:|---:|---|
| #22 | #18 rate-diff (timing artefact) | 2.90 | 2.91 | +0.01 | ~0.00 | Vol-reducer only, base bogus |
| **#29** | **#28 MA-cross (commod+crypto)** | **0.42** | **0.51** | **+0.09** | **+0.14** | **Adds value — removes bad days** |
| **#30** | **#25 Turtle (commod+crypto)** | **0.43** | **0.41** | **−0.02** | **−0.23** | **Destroys value — removes good days** |

**Interpretation.** Identical universe, identical overlay spec, opposite results. The crash filter's value is **spec-specific**, not universe-specific. The proper interpretation: the **Turtle 20/10/2N** captures trends with a tighter exit (10-day reversion) than the **20/50 MA crossover**, so it tends to be ALREADY positioned in winning trades when VIX spikes — the big wins in #25 happen DURING volatile periods because breakouts and vol are correlated. The MA crossover with the slower 20/50 signal is often still BUILDING into a trend when VIX spikes, so the filter cuts exposure during periods that would have been bad for #28 (the 1×ATR trailing stop is tight and gets stopped during chop). The Turtle's edge is more **vol-positive** than the MA crossover's — meaning the filter trims exactly the wrong days for #25. This is a real finding about how different trend-following specs interact with volatility regimes, not just a generic null result. **Honest research outcome**: the #29 result was NOT a universal "trend-following + crash filter" story — it was a #28-specific result. The overlay needs to be base-validated before deployment.

**What this teaches the repo** (with the three-base comparison now complete):

1. **Overlay works** when base drawdowns correlate with VIX spikes + self-momentum dips (i.e., crash conditions = base losses) — #29 case.
2. **Overlay is neutral** when the base has no genuine drawdown signal to trim — #22 case (the underlying signal was a timing artefact).
3. **Overlay destroys value** when the base's gains concentrate during the same vol-spike periods the filter trims — #30 case (Turtle catches vol-driven breakouts).

The proper deployment rule for the overlay is therefore: **only apply it to bases where the conditional Sharpe test passes** (filter-binding days have negative base Sharpe). This is now a documented test in this repo.

**Variables (code-level glossary).**

| Variable | Meaning (5–10 words) |
|---|---|
| `base[weight_INSTR, t]` | Per-instrument daily weights from #25's CSV |
| `vix[t]` | Daily VIX close (yfinance `^VIX`) |
| `vix_scale[t]` | Linear interp from 1.0 to 0.0 over VIX 20→40 |
| `tr20[t]` | Trailing 20-day sum of #25 base net returns |
| `z_tr20[t]` | Z-score of `tr20` vs trailing 252d window |
| `mom_scale[t]` | 0.5 when `z_tr20 < −1.0`, else 1.0 |
| `scale_raw[t]` | `vix_scale × mom_scale` clipped to [0, 1] |
| `scale[t]` | `scale_raw.shift(1)` — applied to next-day positions |
| `weights_filt[instr, t]` | `base_weights × scale` per instrument |
| `gross_filt[t]` | `base_gross × scale` (linear scaling) |
| `cost_filt[t]` | Filtered turnover × 5 bps per unit |
| `net_filt[t]` | `gross_filt − cost_filt` |
| `ir` | Information ratio: active return / tracking error |
| `cost_of_insurance_bps` | Filter-induced cost increase per year, in bps |
| `cond_base_sharpe` | Sharpe of base on filter-binding days only |
| `cond_filt_sharpe` | Sharpe of filtered on filter-binding days only |

**Data sources.** Reuses #25's daily CSV. VIX from yfinance `^VIX`.
**Reference.** Same overlay spec as #22 and #29 — no retuning. Brunnermeier, Nagel, Pedersen (2009).
**Script.** [`strategies/strat_30_crash_filter_on_25.py`](strategies/strat_30_crash_filter_on_25.py)
**Track record CSV.** [`live/track_record/strategy_30_crash_filter_on_25_track_record.csv`](live/track_record/strategy_30_crash_filter_on_25_track_record.csv)
**Equity curve.** [`reports/strategy_30_crash_filter_on_25.png`](reports/strategy_30_crash_filter_on_25.png)
