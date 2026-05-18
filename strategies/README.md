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
