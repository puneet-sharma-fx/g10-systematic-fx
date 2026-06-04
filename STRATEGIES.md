# Strategies Index

A one-page index of every strategy tested in this repo, what was actually found, and where to look for the details. All Sharpes are **net of 5 pips round-trip cost** unless stated otherwise. Period 2010–2024 (or as constrained by data).

For full per-strategy details: [`strategies/README.md`](strategies/README.md). For the original extension plan: [`strategies/PLAN.md`](strategies/PLAN.md).

---

## ✅ Working strategies (net Sharpe > 1)

The core finding of the repo: **the change in 2Y rate differential predicts next-day FX**, generalises across G10, and survives as a portfolio.

| # | Strategy | Period | Net Sharpe | Ann. Ret | Max DD | Calmar |
|---|---|---|---|---|---|---|
| **12** | **Calibrated rate-diff portfolio** (core 4) | 2010-2024 | **2.73** | +25.5% | −22.0% | **1.16** |
| **1** | EURUSD: Δ(EU 2Y − US 2Y) → next-day EURUSD | 2010-2024 | **2.75** | +22.9% | −15.3% | 1.50 |
| **10** | Rate-diff portfolio (uncalibrated, 5% vol) | 2010-2024 | **2.70** | +13.6% | −13.2% | 1.03 |
| **6** | USDCAD rate-diff | 2010-2024 | **2.06** | +15.2% | −14.8% | 1.03 |
| **8** ⚠ | USDSEK rate-diff (cost-model caveat) | 2012-2024 | **2.13** | +21.4% | −15.7% | 1.36 |
| **2** | GBPUSD rate-diff | 2010-2024 | **1.50** | +13.1% | −25.8% | 0.51 |
| **5** ⚠ | USDJPY rate-diff (brutal −59% DD) | 2010-2024 | **1.44** | +12.8% | **−59.2%** | 0.22 |
| **3** | AUDUSD rate-diff | 2010-2024 | **1.22** | +12.8% | −23.0% | 0.56 |
| **14** ⚠ | Calibrated portfolio + 50-DMA trend filter | 2010-2024 | **1.59** | +12.4% | −17.5% | 0.70 |

## ⚠ Borderline (Sharpe 0–1)

| # | Strategy | Period | Net Sharpe | Notes |
|---|---|---|---|---|
| **4** | NZDUSD rate-diff | 2016-2024 | 0.92 | NZ data starts 2016, shorter sample |

## ❌ Failed / rejected / inconclusive

| # | Strategy | Net Sharpe | Why it failed |
|---|---|---|---|
| **7** | USDCHF rate-diff | 0.00 | SNB peg break 2015 + safe-haven flows override rates |
| **11 ❌** | Cross-sectional momentum portfolio (rejected) | −0.34 | Post-GFC FX momentum decay; confirmed at 21/63/126/252 lookbacks |
| **13 ⚠** | CFTC positioning ±2σ + 21-DMA reversal (long+short) | −0.07 | Asymmetric: short 40% win ✓, long 30% win ✗ |
| **9** | USDNOK rate-diff (deferred) | — | TVC has no NO 2Y data; deferred to Norges Bank API |
| **Tech sweep ⚠** | 15 classic technical indicators × 3 majors | best +0.14 | None deployable; consistent with Park-Irwin 2007 |
| **15** ❌ | EURUSD SMA20 + RSI(14) combo (long-only) | −0.34 | 49 trades, 24.5% win rate. Classic confluence doesn't work on liquid EURUSD |

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
