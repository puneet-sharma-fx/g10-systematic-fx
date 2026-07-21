# Quant FX Research Reference

Industry practices, signal taxonomy, benchmarking standards, and open research questions for systematic G10 FX strategy development. Built from primary academic literature and practitioner sources. Updated alongside strategy iteration.

---

## Signal Taxonomy

### ✅ Carry

**Construction.** `rate[base] − rate[quote]`, cross-sectionally z-scored, typically 20-day smoothed to reduce rate-fixing lag noise. Go long high-yield, short low-yield currencies.

**Theoretical basis.** Exploits the forward premium puzzle / UIP violation (Fama 1984). Lustig, Roussanov & Verdelhan (2011, *RFS*) decompose carry returns into a **dollar factor (DOL)** and a **HML_FX carry factor**. The premium is compensation for crash risk — carry loads heavily on global liquidity and equity volatility shocks.

**Typical Sharpe (pre-2008).** ~0.5–0.8 gross G10. DB Currency Carry Index: ~0.29 net long-run.

**Post-2008 deterioration.** Benchmark carry delivered Sharpe ~0.06 post-2008 vs ~0.76 pre-crisis (ScienceDirect 2021). Augmented/conditional carry improves to ~0.16.

**Key failure modes.** JPY/CHF carry shorts unwind violently in risk-off (2008, 2020, Aug-2024 BoJ pivot). ZIRP 2011–2016: G10 differentials compress to near-zero; signal loses discriminatory power. SNB peg removal Jan-2015: single-day CHF appreciation ~20%.

**Status in this repo.** Track 1 (strategy.py) uses FRED short rates. Per-signal Sharpe near zero on v1 — known gap, v2 improvement planned: vol-normalise carry as `rate_diff / σ_pair`.

---

### ✅ 2Y Rate-Differential Change (Track 2 core signal)

**Construction.** `d_diff[t] = Δ(base_2Y − quote_2Y)[t]`; `pos[t+1] = sign(d_diff[t])`. Held 1 day. This is *not* the level of the carry differential — it's the *daily change*.

**Theoretical basis.** Related to UIP but operating at a shorter frequency: when the rate differential moves in favour of the base currency today, the FX rate adjusts the next day. The regression `next-day FX return ~ β · Δ(2Y diff)` shows β = +0.03 to +0.04, R² = 1–7%, t-stats 6–17 across all 8 G10 pairs — statistically real everywhere.

**Typical net Sharpe found here.** 2.75 (EURUSD), 2.06 (USDCAD), 2.13 (USDSEK, caveat), 1.50 (GBPUSD), 1.44 (USDJPY), 1.22 (AUDUSD), 0.92 (NZDUSD), 0.00 (USDCHF).

**Key scrutiny area.** A daily net Sharpe of 2.75 is in "suspicious-high" territory by industry standards (> 2.0 daily is fund-quality, > 3.0 is overfit territory). Two open questions:
1. **Timestamp alignment**: ECB rate fixed at 14:15 Frankfurt; FRED at 15:00 Washington; Yahoo FX close at 16:00 New York. Is the signal genuinely predictive or contemporaneously correlated? **Test needed**: re-run strat_01 with `d_diff[t-1]` (1-day lag) and compare Sharpe.
2. **USDSEK cost artefact**: 5 pips RT at SEK spot ~10.5 ≈ 0.24 bps vs realistic 25–100 bps institutional spread. Net Sharpe 2.13 is likely inflated by ~30–50%.

---

### ❌ Cross-Sectional Momentum (Tested, Rejected)

**Construction.** Rank all pairs by past 21/63/126/252-day return. Long top-3, short bottom-3. Menkhoff et al. (2012, *JFE*) is the definitive reference — works on 40+ currency universe, decays badly below 20 pairs.

**Result here.** Sharpe −0.34 (strat_11). Consistent with literature: G10 has only 9 pairs, far too thin for cross-sectional sorting. All 4 lookback windows tested, all negative.

**Why it failed.** Post-2008 momentum decay documented academically (Quantpedia OOS: "slightly negative"). Also: 9 pairs is too small — the cross-section needs ~40+ currencies for the law of large numbers to apply.

---

### ❌ Classic Technical Analysis (Tested, Rejected)

**Coverage.** 15 indicators × 3 pairs (EURUSD, GBPUSD, USDJPY): RSI, MACD, Bollinger Bands, ATR breakout, Stochastic, SMA/EMA crossovers, etc.

**Result.** Best net Sharpe +0.14. Consistent with Park & Irwin (2007) meta-study: technical rules had positive returns pre-2000, no significant edge post-2000 in G10 spot.

---

### ⚠ CFTC COT Positioning (Partially Tested)

**Construction (strat_13).** Long when speculative net position crosses below −2σ of 52-week range (oversold, reversal). Short when crosses above +2σ (overcrowded, reversal). Trigger confirmed by 21-DMA breakdown.

**Result.** Combined Sharpe −0.07. **Asymmetry found**: short side win rate ~40%, long side ~30%. Short-only variant Sharpe +0.28 — borderline.

**Why weak.** CFTC data is 3-day lagged; Tuesday collection date. COT extremes can persist 6–12 months during sustained macro trends. Best use as a risk filter (reduce exposure when longs are crowded), not a timing signal.

**Coverage gaps.** SEK, NOK: no CME FX futures → no COT data. This is structural, no workaround on public data.

---

### 🔬 Trend-Following Overlay (Tested, Degrades Signal)

**Construction (strat_14).** Apply a 50-DMA trend filter on top of strat_12 (calibrated rate-diff portfolio): only take a signal if the pair's FX price is above/below its 50-day moving average.

**Result.** Sharpe degrades from 2.73 (strat_12) to 1.59 (strat_14). Consistent with industry finding: trend overlays on carry/rate-diff often reduce returns by filtering out signal in choppy regimes but missing genuine continuation.

---

### 🔲 Not Yet Tested

| Signal | Priority | Blocker | Notes |
|---|---|---|---|
| **Lagged signal test (strat_01 with d_diff[t-1])** | **HIGHEST** | None | Must-do rigour check to bound timestamp-alignment contribution to Sharpe 2.75 |
| **USDSEK at 10-pip RT cost** | High | None | Recalibrate strat_08 with 10-pip RT to get realistic net Sharpe |
| **Vol-normalised carry** (`rate_diff / σ_pair`) | High | None | Planned v2 improvement for Track 1 |
| **USDNOK (strat_09)** | Medium | NO 2Y data | Norges Bank API at norges-bank.no publishes daily 2Y yields; alternative to TVC |
| **Sub-period stability per strategy** | Medium | None | `notebooks/subperiod_stability.py` exists for portfolio level; per-pair breakdown needed |
| **Deflated Sharpe Ratio calculation** | Medium | None | Bailey–López de Prado (SSRN 2460551) — adjusts for number of trials tested (~27 variants in this repo) |
| **PPP / Value signal** | Low | Annual data only | OECD PPP tables; 3–5y mean reversion horizon; low priority for daily/weekly strategies |
| **Volatility risk premium signal** | Low | Options data | IV − realised vol requires Bloomberg/Refinitiv options surface; not on public data |
| **Order flow / positioning** | Low | Proprietary | Prime broker data; no public substitute |
| **Regime-conditional carry** (condition on VIX < 20) | Medium | None | Documented by Koijen et al. to add ~0.2 Sharpe to carry |
| **Dollar factor (DOL) exposure analysis** | Medium | None | Lustig-Roussanov-Verdelhan factor; strategies may have unintentional USD directionality |

---

## Portfolio Construction Standards

### Vol Targeting

**Industry standard.** `w_i = (σ_target / σ_i) × signal_i`. Common targets: 10–15% annualised for G10 FX book. EWMA volatility estimator (half-life 10–21 days) standard for daily rebalancing.

**Evidence.** Moreira & Muir (2017, *JF*): vol targeting improves equity Sharpe 35–50%. For **FX specifically**, Man Group (2020): Sharpe improvement is negligible, but **drawdown and Calmar improve materially**. Primary benefit for FX is tail risk management, not return enhancement.

**Status in this repo.** Implemented in strat_10 (5% vol target) and strat_12 (calibrated to hit 10% vol target). Strat_12 Sharpe 2.73, max DD −22.0%, Calmar 1.16.

### Cross-Sectional Ranking

Top-3/bottom-3 construction used in Track 1. Industry norm for 9-pair universe. Score-weighted (proportional to z-score) is an alternative but requires outlier truncation at ±2σ (AQR standard).

### Correlation Management (Not Yet Implemented)

G10 pairs cluster: commodity FX (AUD, CAD, NZD) vs safe havens (JPY, CHF) vs EUR-bloc (EUR, SEK, NOK). Running the same rate-diff signal on all three produces correlated longs in commodity FX and correlated shorts in safe havens. **Not yet addressed in this repo** — cluster-based exposure caps would be a portfolio-level improvement.

### Regime-Dependent Sizing (Partial)

Track 1 uses VIX step-function (full exposure below 25, 50% above 25, 0% above 35). Track 2 portfolio strategies have no regime filter. Adding a smooth VIX scalar to strat_12 is a natural next step.

---

## Backtesting Standards and Where This Repo Stands

| Standard | Industry Norm | This Repo Status |
|---|---|---|
| Walk-forward | Expanding or rolling, 3y train / 6m test min | ✅ Track 1 implemented in engine.py |
| Look-ahead prevention | `_slice_data()` at train boundary | ✅ Track 1 only; Track 2 is a single-pass backtest |
| Cost model | Pair-specific, pip-based | ✅ Pip-aware; SEK caveat documented |
| Minimum OOS history | 10y daily (~2,500 days) for meaningful inference | ✅ Most strategies 2010–2024 |
| Deflated Sharpe Ratio | Required when testing multiple variants | ❌ Not yet calculated |
| Timestamp lag test | Standard sanity check for daily signal-to-return strategies | ❌ Not yet run for Track 2 |
| Parameter sensitivity | ±30% perturbation on key params | ❌ Not yet done |
| Sub-period breakdown | ZIRP / divergence / COVID / hiking | ✅ `reports/subperiod_stability.png` |
| Rejection documentation | Committed failed strategies | ✅ strategies/rejected/ folder |

---

## Performance Benchmarking Reference

### Sharpe Norms (Net of Costs, Daily FX Strategy)

| Band | Sharpe | Interpretation |
|---|---|---|
| Suspicious | > 3.0 | Likely overfit unless 10y+ OOS at this level |
| Excellent / fund-quality | 1.5–3.0 | CTA upper tier; requires live verification |
| Good / publishable | 0.8–1.5 | Academic top-tier for FX |
| Marginal | 0.3–0.8 | Research-grade; deploy only with size limits |
| Noise | < 0.3 | Discard |

Industry threshold for live deployment: **Sharpe > 2.0** (QuantStart). Some quant shops require > 3.0 at research stage, acknowledging live degradation.

### IC (Information Coefficient) Benchmarks

| IC | Interpretation |
|---|---|
| > 0.10 | Strong; rare in G10 public data |
| 0.05–0.10 | Useful; worth allocating to |
| 0.02–0.05 | Weak but usable with breadth |
| < 0.02 | Noise |

EURUSD rate-diff signal R² = 7.03% implies IC ≈ 0.026–0.08 depending on construction — upper end of "useful" for a daily FX signal.

### Calmar and Drawdown

- Calmar > 1.0: institutional minimum. > 2.0: elite.
- Max DD of 20–40% normal over 10y G10 histories including crises.
- USDJPY −59% max DD (strat_05): not deployable at full size without vol-targeting.

---

## Key Literature

| Paper | Relevance |
|---|---|
| Lustig, Roussanov, Verdelhan (2011) *RFS* | Carry factor structure; dollar factor |
| Menkhoff, Sarno, Schmeling, Schrimpf (2012) *JFE* | Cross-sectional FX momentum; why it needs 40+ currencies |
| Brunnermeier, Nagel, Pedersen (2009) *NBER MA Annual* | Carry crash risk; JPY/CHF safe-haven mechanics |
| Asness, Moskowitz, Pedersen (2013) *JF* | Value and momentum everywhere; FX value construction |
| Bailey, López de Prado (2014) SSRN 2460551 | Deflated Sharpe Ratio; multiple testing in backtests |
| Moreira, Muir (2017) *JF* | Volatility targeting; drawdown improvement evidence |
| Park, Irwin (2007) *JFQA* | Technical analysis in FX; no edge post-2000 |
| Della Corte, Kozhan, Neuberger (2016) *JFE* | Vol risk premium as FX predictor |
| Evans, Lyons (2002) *JPE* | Order flow and FX; 60%+ daily EUR/USD variation explained |
| AQR "Trends Everywhere" | Multi-asset trend-following; FX trend works best in diversified context |
| Man Group (2020) | Vol targeting in currencies: Sharpe unchanged, tail risk improved |

---

## Data Source Limitations Quick Reference

| Source | What It Provides | Key Limitation |
|---|---|---|
| FRED | US 2Y (`DGS2`), FRED short rates | US-centric; 3 PM Washington timestamp |
| ECB Data Portal | ECB policy rates, EUR-area yields | 14:15 Frankfurt fix (pre-US-open); not all G10 |
| TradingView (TVC via tvDatafeed) | 2Y yields for most G10 | Unofficial; no NOK 2Y; ToS restrictions on bulk download |
| yfinance | G10 FX daily close | 4 PM New York mid-price; no bid/ask; not NAV-grade |
| CFTC COT | Weekly speculative positioning | 3-day lag; no SEK/NOK; Tuesday collection date |
| OANDA/Dukascopy | Historical OHLCV with bid/ask | Retail pricing, not institutional |

---

*Last updated: June 2026. Strategies #1–#14 + technical sweep covered.*
