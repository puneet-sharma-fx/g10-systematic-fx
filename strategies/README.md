# Strategies

Numbered, self-contained single-purpose strategies. Each is a standalone module with its own data layer, position rule, and reproducible script.

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
