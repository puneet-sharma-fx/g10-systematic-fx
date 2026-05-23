# Strategies

Numbered, self-contained single-purpose strategies. Each is a standalone module with its own data layer, position rule, and reproducible script.

## Summary table

All Strategies #1–#8 use the same rule: `pos[t+1] = sign(Δ(base 2Y − quote 2Y)[t])`, held 1 day, 5 pips round-trip cost.

| # | Pair | Period | Net Sharpe | Net Ann. Return | Max DD | Notes |
|---|---|---|---|---|---|---|
| 1 | EURUSD | 2010–2024 | **2.75** | +22.9% | −15.3% | Headline result |
| 2 | GBPUSD | 2010–2024 | 1.50 | +13.1% | −25.8% | |
| 3 | AUDUSD | 2010–2024 | 1.22 | +12.8% | −23.0% | |
| 4 | NZDUSD | 2016–2024 | 0.92 | +9.0% | −32.7% | Short history (NZ 2Y from 2016) |
| 5 | USDJPY | 2010–2024 | 1.44 | +12.8% | **−59.2%** | JPY fat-tails crush DD |
| 6 | USDCAD | 2010–2024 | **2.06** | +15.2% | −14.8% | Best risk-adjusted after #1 |
| 7 | USDCHF | 2010–2024 | **0.00** | −0.0% | −65.9% | Signal fails on CHF (SNB peg, safe-haven dynamics) |
| 8 | USDSEK | 2012–2024 | 2.13 ⚠️ | +21.4% | −15.7% | Cost-model artefact (spot ~10.5 makes 5-pip cost fractionally tiny) |
| 9 | USDNOK | — | — | — | — | Deferred: NO 2Y unavailable on TVC |

**Key observations.**
- 5 of 8 net Sharpes are >1.0; signal generalises broadly across G10 majors.
- CHF is the clear failure — signal has no edge there.
- JPY shows strong Sharpe with brutal drawdown; not deployable as-is.
- SEK number is inflated by the fixed-pip cost model interacting with high spot level.
- USDCAD is the second-most-credible result (low DD, deep market, fair cost assumption).

See [`PLAN.md`](PLAN.md) for the original plan and hypotheses being tested.

---

## Signal diagnostics across all 8 pairs

For each strategy we ran the underlying predictive regression:

```
next-day FX return   ~   α + β · Δ(base 2Y − quote 2Y)
```

![Regression panels for all 8 pairs](../reports/regressions_all_pairs.png)

| # | Pair | β | R² | t-stat | N | Strategy Sharpe (net) |
|---|---|---|---|---|---|---|
| 1 | EURUSD | +0.0325 | **7.03%** | +17.2 | 3,909 | 2.75 |
| 2 | GBPUSD | +0.0184 | 2.95% | +10.9 | 3,909 | 1.50 |
| 3 | AUDUSD | +0.0255 | 3.45% | +11.8 | 3,909 | 1.22 |
| 4 | NZDUSD | +0.0210 | 4.07% | +9.8 | 2,263 | 0.92 |
| 5 | USDJPY | +0.0350 | **7.27%** | +17.5 | 3,909 | 1.44 |
| 6 | USDCAD | +0.0298 | **6.35%** | +16.3 | 3,909 | 2.06 |
| 7 | USDCHF | +0.0101 | 0.99% | +6.3 | 3,909 | 0.00 |
| 8 | USDSEK | +0.0223 | 3.42% | +10.7 | 3,229 | 2.13 |

**Reads.**
- **All 8 βs are positive** — direction is UIP-consistent across the entire G10 universe.
- **All p-values are effectively zero** (t-stats from 6.3 to 17.5) — the signal is statistically real everywhere.
- **R² ranges 1.0% to 7.3%** — high for daily FX. Median 3.7%.
- **CHF outlier explained**: lowest β (0.0101) and lowest R² (0.99%) — the signal genuinely has little informational content for CHF, consistent with the strategy printing Sharpe 0.00.
- **EURUSD, USDJPY, USDCAD** are the strongest signals (R² > 6%). USDJPY's strong β does not survive into a strong Sharpe because of fat-tail drawdowns.
- **Signal IC and strategy Sharpe correlate but not 1:1** — execution path, drawdown sensitivity, and pair liquidity also matter.

Script: [`../notebooks/regression_all_pairs.py`](../notebooks/regression_all_pairs.py)

---

## Strategy #1 — Δ(EU 2Y − US 2Y) → next-day EURUSD

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (EU_2Y − US_2Y)[t] − (EU_2Y − US_2Y)[t−1]`. Long EURUSD when the rate differential moved in EU's favour today, short when it moved against. Held 1 trading day.

**Exploration regression** (see [`../notebooks/explore_2y_diff_vs_eurusd.py`](../notebooks/explore_2y_diff_vs_eurusd.py)):

```
β = +0.0335     R² = 7.5%     t = +17.8     N = 3,910
```

**Transaction cost.** 5 pips total round-trip, charged as 2.5 pips per unit of |Δposition|.

**Result** (2010–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long EURUSD |
|---|---|---|---|
| Annualised Return | **+22.90%** | +28.71% | −1.73% |
| Annualised Vol | 8.34% | 8.32% | 8.52% |
| **Sharpe** | **2.75** | 3.45 | −0.20 |
| Max Drawdown | −15.29% | −13.03% | −35.35% |
| Hit Rate | 56.12% | 58.14% | 49.40% |
| Cumulative (15y) | +3,206% | +8,037% | −27.69% |

![Strategy #1 equity curve](../reports/strategy_01_eu_us_2y_diff_eurusd.png)

**Data sources.**
- US 2Y — FRED `DGS2` (daily)
- EU 2Y — ECB SDW `YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y` (daily, Euro-area AAA benchmark ≈ Bund 2Y curve)
- EURUSD — yfinance `EURUSD=X` (daily close)

**Caveats worth flagging before extrapolating.**
- A Sharpe of 2.75 is high enough that the result deserves skepticism on timing alignment — Yahoo's FX close timestamp may not align with FRED / ECB rate fixings, and some part of the "next-day" return may capture same-news response measured at a different timestamp.
- Strategy flips position 55% of days. Cumulative cost drag ≈ 6%/year.
- Sub-period stability not yet verified (ZIRP-era 2010–2016 vs post-ZIRP 2022+).
- Position sizing is full ±1 with no vol-targeting; production deployment would require vol scaling and capacity testing.

**Script.** [`strat_01_eu_us_2y_diff_eurusd.py`](strat_01_eu_us_2y_diff_eurusd.py)

---

## Strategy #2 — Δ(GB 2Y − US 2Y) → next-day GBPUSD

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (GB_2Y − US_2Y)[t] − (GB_2Y − US_2Y)[t−1]`. Long GBPUSD when the rate differential moved in GB's favour today.

**Result** (2010–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long GBPUSD |
|---|---|---|---|
| Annualised Return | **+13.14%** | +18.14% | −1.20% |
| Annualised Vol | 8.74% | 8.73% | 8.83% |
| **Sharpe** | **1.50** | 2.08 | −0.14 |
| Max Drawdown | −25.76% | −21.13% | −37.49% |
| Hit Rate | 52.95% | 54.82% | 49.25% |
| Cumulative (15y) | +624% | +1,473% | −21.94% |

![Strategy #2 equity curve](../reports/strategy_02_gb_us_2y_diff_gbpusd.png)

**Data sources.** US 2Y: TradingView `TVC:US02Y`. GB 2Y: TradingView `TVC:GB02Y` (both via `tvDatafeed`). GBPUSD: yfinance `GBPUSD=X`.

**Script.** [`strat_02_gb_us_2y_diff_gbpusd.py`](strat_02_gb_us_2y_diff_gbpusd.py)

---

## Strategy #3 — Δ(AU 2Y − US 2Y) → next-day AUDUSD

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (AU_2Y − US_2Y)[t] − (AU_2Y − US_2Y)[t−1]`. Long AUDUSD when the rate differential moved in AU's favour today.

**Result** (2010–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long AUDUSD |
|---|---|---|---|
| Annualised Return | **+12.75%** | +21.15% | −1.91% |
| Annualised Vol | 10.45% | 10.44% | 10.56% |
| **Sharpe** | **1.22** | 2.03 | −0.18 |
| Max Drawdown | −23.03% | −19.96% | −47.96% |
| Hit Rate | 52.60% | 55.00% | 50.27% |
| Cumulative (15y) | +564% | +2,344% | −31.78% |

![Strategy #3 equity curve](../reports/strategy_03_au_us_2y_diff_audusd.png)

**Data sources.** US 2Y: TradingView `TVC:US02Y`. AU 2Y: TradingView `TVC:AU02Y` (both via `tvDatafeed`). AUDUSD: yfinance `AUDUSD=X`.

**Script.** [`strat_03_au_us_2y_diff_audusd.py`](strat_03_au_us_2y_diff_audusd.py)

---

## Strategy #4 — Δ(NZ 2Y − US 2Y) → next-day NZDUSD

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (NZ_2Y − US_2Y)[t] − (NZ_2Y − US_2Y)[t−1]`. Long NZDUSD when the rate differential moved in NZ's favour today.

**Note.** NZ 2Y data on TradingView only goes back to 2016-04-27, so this backtest covers ~8.5 years instead of the full 15 years of #1–#3.

**Result** (2016–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long NZDUSD |
|---|---|---|---|
| Annualised Return | +9.04% | +19.30% | −1.71% |
| Annualised Vol | 9.88% | 9.85% | 9.99% |
| **Sharpe** | **0.92** | 1.96 | −0.17 |
| Max Drawdown | −32.72% | −25.31% | −25.96% |
| Hit Rate | 49.93% | 52.89% | 50.15% |
| Cumulative | +116% | +442% | −18.0% |

![Strategy #4 equity curve](../reports/strategy_04_nz_us_2y_diff_nzdusd.png)

**Read.** First strategy to drop below Sharpe 1 net. Gross Sharpe 1.96 confirms the signal still has meaningful predictive content for NZDUSD; the 92% cumulative cost drag is what kills it. 5 pips round-trip may be optimistic for NZDUSD (less liquid than EUR/GBP majors).

**Data sources.** US 2Y: TradingView `TVC:US02Y`. NZ 2Y: TradingView `TVC:NZ02Y` (both via `tvDatafeed`). NZDUSD: yfinance `NZDUSD=X`.

**Script.** [`strat_04_nz_us_2y_diff_nzdusd.py`](strat_04_nz_us_2y_diff_nzdusd.py)

---

## Strategy #5 — Δ(US 2Y − JP 2Y) → next-day USDJPY

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (US_2Y − JP_2Y)[t] − (US_2Y − JP_2Y)[t−1]`. Long USDJPY when the rate differential moved in US's favour today.

**Result** (2010–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long USDJPY |
|---|---|---|---|
| Annualised Return | +12.81% | +18.99% | +3.87% |
| Annualised Vol | 8.92% | 8.91% | 9.19% |
| **Sharpe** | **1.44** | 2.13 | 0.42 |
| **Max Drawdown** | **−59.21%** | −34.51% | −20.48% |
| Hit Rate | 50.88% | 53.34% | 52.03% |
| Cumulative (15y) | +586% | +1,690% | +70.7% |

![Strategy #5 equity curve](../reports/strategy_05_us_jp_2y_diff_usdjpy.png)

**Read.** Strong Sharpe but worst max drawdown of any pair so far at −59%. JPY pairs are prone to fat-tail rate-policy shocks (2016 BoJ NIRP, 2022 BoJ defence, 2024 carry unwind) that compound through the daily-flip rule. Calmar ratio is poor; sizing would need to be smaller in production to keep DD reasonable.

**Data sources.** US 2Y: TradingView `TVC:US02Y`. JP 2Y: TradingView `TVC:JP02Y` (both via `tvDatafeed`). USDJPY: yfinance `USDJPY=X`.

**Script.** [`strat_05_us_jp_2y_diff_usdjpy.py`](strat_05_us_jp_2y_diff_usdjpy.py)

---

## Strategy #6 — Δ(US 2Y − CA 2Y) → next-day USDCAD

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (US_2Y − CA_2Y)[t] − (US_2Y − CA_2Y)[t−1]`. Long USDCAD when the rate differential moved in US's favour today.

**Result** (2010–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long USDCAD |
|---|---|---|---|
| Annualised Return | +15.19% | +20.89% | +2.38% |
| Annualised Vol | 7.39% | 7.37% | 7.58% |
| **Sharpe** | **2.06** | 2.83 | 0.31 |
| Max Drawdown | −14.82% | −12.33% | −17.42% |
| Hit Rate | 53.16% | 55.79% | 50.65% |
| Cumulative (15y) | +911% | +2,349% | +38.4% |

![Strategy #6 equity curve](../reports/strategy_06_us_ca_2y_diff_usdcad.png)

**Read.** Strongest result so far after EURUSD. Makes economic sense: Canada-US is the most rate-correlated G10 pair (deep cross-border trade, synchronised central-bank cycles), and USDCAD is the third-most-liquid G10 spot, so 5 pips is a realistic cost.

**Data sources.** US 2Y: TradingView `TVC:US02Y`. CA 2Y: TradingView `TVC:CA02Y` (both via `tvDatafeed`). USDCAD: yfinance `USDCAD=X`.

**Script.** [`strat_06_us_ca_2y_diff_usdcad.py`](strat_06_us_ca_2y_diff_usdcad.py)

---

## Strategy #7 — Δ(US 2Y − CH 2Y) → next-day USDCHF

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (US_2Y − CH_2Y)[t] − (US_2Y − CH_2Y)[t−1]`. Long USDCHF when the rate differential moved in US's favour today.

**Result** (2010–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long USDCHF |
|---|---|---|---|
| Annualised Return | −0.00% | +7.54% | −0.36% |
| Annualised Vol | 9.76% | 9.75% | 9.82% |
| **Sharpe** | **0.00** | 0.77 | −0.04 |
| **Max Drawdown** | **−65.90%** | −33.56% | −37.83% |
| Hit Rate | 48.79% | 51.32% | 51.37% |
| Cumulative (15y) | −7.3% | +199% | −12.4% |

![Strategy #7 equity curve](../reports/strategy_07_us_ch_2y_diff_usdchf.png)

**Read.** First strategy that doesn't work. Even gross Sharpe (0.77) is the weakest among the seven so far — the rate-diff signal has the least predictive power for USDCHF. Two structural reasons: (1) the SNB EUR/CHF floor removal of 15 Jan 2015 caused a one-day CHF appreciation of ~20%, which would have crushed any positioning at that moment regardless of rate signal; (2) CHF is a textbook safe-haven currency that often moves on global risk sentiment rather than rate differentials, especially during the post-GFC era of negative Swiss rates.

**Data sources.** US 2Y: TradingView `TVC:US02Y`. CH 2Y: TradingView `TVC:CH02Y` (both via `tvDatafeed`). USDCHF: yfinance `USDCHF=X`.

**Script.** [`strat_07_us_ch_2y_diff_usdchf.py`](strat_07_us_ch_2y_diff_usdchf.py)

---

## Strategy #8 — Δ(US 2Y − SE 2Y) → next-day USDSEK

**Signal.** `pos[t+1] = sign(d_diff[t])` where `d_diff[t] = (US_2Y − SE_2Y)[t] − (US_2Y − SE_2Y)[t−1]`. Long USDSEK when the rate differential moved in US's favour today.

**Note.** SE 2Y data on TradingView starts 2012-08-14, so this backtest covers ~12 years.

**Result** (2012–2024, daily):

| Metric | **Net (after 5 pips RT)** | Gross | Passive long USDSEK |
|---|---|---|---|
| Annualised Return | **+21.35%** | +22.12% | +4.42% |
| Annualised Vol | 10.00% | 10.00% | 10.16% |
| **Sharpe** | **2.13** | 2.21 | 0.44 |
| Max Drawdown | −15.67% | −14.93% | −21.90% |
| Hit Rate | 54.38% | 54.50% | 51.10% |
| Cumulative | +1,347% | +1,497% | +65.0% |

![Strategy #8 equity curve](../reports/strategy_08_us_se_2y_diff_usdsek.png)

**Important read on the cost model.** Net Sharpe is 2.13, but the cumulative cost drag is only 9.9% — much lower than the ~90% for EURUSD over a similar window. The reason is structural: USDSEK trades around 10.5 spot, so the same "5 pips" round-trip cost is fractionally **10× smaller** than for EURUSD at spot 1.10 (≈0.24 bps vs ≈2.27 bps per unit traded). In real markets, USDSEK spreads are *wider* in absolute pip terms than EURUSD's (USDSEK is less liquid), so the 5-pip assumption is **optimistic for SEK**. A realistic 10-pip RT cost would meaningfully degrade the net Sharpe. Treat the headline number with that caveat.

**Data sources.** US 2Y: TradingView `TVC:US02Y`. SE 2Y: TradingView `TVC:SE02Y` (both via `tvDatafeed`). USDSEK: yfinance `USDSEK=X`.

**Script.** [`strat_08_us_se_2y_diff_usdsek.py`](strat_08_us_se_2y_diff_usdsek.py)
