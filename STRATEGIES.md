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

*Currently no strategies survive the time-alignment rigour check above. Repo is in active reconstruction mode pending properly time-aligned signals.*

## ⚠ Borderline (Sharpe 0–1)

| # | Strategy | Period | Net Sharpe | Notes |
|---|---|---|---|---|
| **4** | NZDUSD rate-diff | 2016-2024 | 0.92 | NZ data starts 2016, shorter sample |
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
