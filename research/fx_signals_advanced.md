# Advanced G10 FX Signals: Research Scoping Document

Signals beyond the basic carry / momentum / COT already in this repo. For each: construction, data sources, evidence quality, public-data feasibility, realistic net Sharpe, and implementation priority.

---

## 1. Vol-Normalised Carry

**Signal.** `VN_carry[pair,t] = (rate_base − rate_quote)[t] / RealVol[pair, t-30d:t]`

Divide the raw rate differential by the pair's trailing 30-day realised FX volatility. Cross-sectionally z-score across G10 pairs as usual.

**Why it works.** Low-vol periods inflate carry signals relative to the risk actually taken; high-vol periods deflate them. Vol-normalisation corrects for this — each unit of carry signal represents the same risk-adjusted carry regardless of the current vol regime. It also eliminates the characteristic left-tail skewness of raw carry: Dupuy (2021, JBF) finds skewness flips from −0.76 (raw carry) to +0.97 (vol-normalised).

**Evidence.**
- Dupuy (2021, Journal of Banking & Finance): vol-adjusted carry Sharpe = **1.07** vs **0.76** raw carry (G10, 1990–2020).
- Koijen, Moskowitz, Pedersen, Vrugt (2018, JFE): diversified cross-asset carry SR ≈ 1.2.
- Macrosynergy: "modest improvement on its own (+0.05–0.08), but material when combined with valuation adjustment."

**Data.** FRED for rates (already in repo); Yahoo Finance daily OHLC for realised vol (already fetched).

**Public-data feasibility.** ✅ Fully implementable — all data already in repo.

**Realistic net Sharpe.** 0.8–1.0 per pair (improvement of +0.1 to +0.3 over raw carry).

**Implementation.** Modify `_rate_diff_strategy.py`: add a `vol_normalise=True` flag. Divide `d_diff[t]` by 30-day rolling std of FX returns before taking sign. Or apply vol-normalisation at the portfolio level by scaling `w_i = signal_i / RealVol_i`.

**Priority.** 🔴 Highest — all data already available, one-line change to signal construction, well-documented improvement.

---

## 2. FX Volatility Risk Premium (VRP)

**Signal.** `VRP[pair,t] = IV[pair,t,1M] − RealVol[pair, t-1M:t]`

Long currencies where implied vol is high relative to realised vol (option sellers earn a premium); short where VRP is low or negative.

**Why it works.** Option sellers in FX are systematically compensated for bearing crash risk — implied vol embeds a premium above expected realised vol. Pairs with high VRP are expensive to hedge → mean-reverting toward realised vol → underlying tends to appreciate as hedging demand falls.

**Evidence.**
- Della Corte, Kozhan, Neuberger (2021, JFE): Cross-sectional VRP strategy Sharpe ≈ **0.5–0.7**. Low correlation with carry/momentum (≈0.10–0.15).
- Della Corte, Ramadorai, Sarno (2016, JFE): VRP directly predicts spot FX returns directionally, R² = 1–5% at 1-month horizon.

**Full vs approximated signal.**
- Full: Bloomberg 1M ATM implied vol surface — not free.
- Approximated: Use GARCH(1,1)-fitted vol as "implied" vol proxy. `VRP_approx = GARCH_sigma − RealVol`. Sharpe degrades from ~0.6 to ~0.3–0.4 but signal remains positive.

**Data.** Yahoo Finance daily OHLC for realised vol; FRED VIXCLS as a global vol-regime proxy.

**Public-data feasibility.** ⚠️ Partial — approximatable without options data with ~50% Sharpe degradation.

**Realistic net Sharpe.** 0.3–0.5 (approximated); 0.5–0.7 (full options data).

**Priority.** 🟡 Medium — worth implementing GARCH approximation; validate before committing to Bloomberg subscription.

---

## 3. Term Structure Signal (Yield Curve Slope Differential)

**Signal.** `TS[pair,t] = (Y10_base − Y2_base)[t] − (Y10_quote − Y2_quote)[t]`

The difference in yield curve steepness between base and quote country. A steeper base curve → stronger expected base-country growth and future rate hikes → base currency appreciation.

**Why it works.** The 2Y rate differential (current carry) captures the level of rate differentials; the slope differential captures the direction of expected future rates. They are partially orthogonal signals. Cao, Lavoie, Renne (2018): level + slope + curvature differentials explain up to 50% of in-sample 1-year currency return variation.

**Evidence.**
- Cao, Lavoie, Renne (2018): Nelson-Siegel slope differential dominant at 3–12 month horizons (strongest predictive window).
- Lustig, Verdelhan (2014, JFE): The term structure of carry trade risk premia — slope of the carry curve is itself tradeable.

**Best horizon.** 3–12 months. Add to portfolio as a monthly-rebalancing complement to the daily 2Y-diff signal.

**Data.** All free on FRED: US (`DGS2`, `DGS10`), Germany/ECB, UK BoE, Japan, Canada, Australia, NZ, Switzerland, Sweden — all available as FRED series.

**Public-data feasibility.** ✅ Fully implementable on FRED.

**Realistic net Sharpe.** 0.4–0.6 standalone; higher as a diversifying complement to carry.

**Priority.** 🟡 Medium — easy data, new signal dimension, complements existing repo infrastructure.

---

## 4. Dollar Factor (DOL) Strategy

**Signal.** `DOL[t] = (1/9) × Σᵢ (return[pair_i,t])` — the equal-weighted average return of all 9 G10 pairs vs USD.

**Dollar carry trade**: Go long a basket of all non-USD currencies equally when US 2Y < G10-average 2Y (USD has below-average yield); go short when US 2Y > average (USD is the high-yielder).

**Why it works.** Lustig, Roussanov, Verdelhan (2011, RFS): DOL and HML_FX (cross-sectional carry) are the two orthogonal risk factors that explain all G10 carry portfolio returns. The dollar carry trade exploits the time-variation in the DOL factor.

**Evidence.**
- DOL factor Sharpe ≈ 0.4–0.6 (standalone time-series dollar carry).
- Orthogonal to HML_FX — provides diversification in a multi-factor portfolio.
- US industrial production growth predicts DOL with R² ≈ 25% at 1-year horizon.

**Practical construction for this repo.**
```python
g10_2y_avg = short_rates[["EUR","GBP","AUD","NZD","JPY","CAD","CHF","SEK","NOK"]].mean(axis=1)
dol_signal = np.sign(g10_2y_avg - short_rates["USD"])
# Scale to equal-weight position across all pairs, sign applied uniformly
```

**Data.** FRED short rates — all already in repo.

**Public-data feasibility.** ✅ Fully implementable — uses data already fetched.

**Realistic net Sharpe.** 0.4–0.6 standalone; valuable as an uncorrelated diversifier to pair-level strategies.

**Priority.** 🟡 Medium — trivial to implement on existing infrastructure.

---

## 5. Macro Factor Signals

### 5a. Taylor Rule Deviation

**Signal.** `TaylorDiff[pair,t] = (i*_base − i_base)[t] − (i*_quote − i_quote)[t]`

Where `i* = r* + π + 0.5(π − 2%) + 0.5 × output_gap`. If base rate is below Taylor-implied, CB will hike → base currency appreciates.

**Evidence.** Molodtsova & Papell (2009, JIE): Out-of-sample predictability for 11/12 G10 pairs at 1-month horizon — stronger than PPP or monetary models alone.

**Data.** FRED: CPI series by country (e.g., `CPALTT01USM661S`, equivalents for G10); IP for output gap proxy (`INDPRO` for US, OECD equivalents for others).

**Feasibility.** ✅ Publicly available, but requires real-time CPI and IP data (monthly frequency, 1–3 month lag).

**Realistic net Sharpe.** 0.3–0.5 standalone at monthly rebalance.

**Priority.** 🟢 Lower — slow signal (monthly data), existing carry signal captures much of the same variation.

### 5b. Cross-Asset (Oil → CAD, Equity → AUD)

**Signal.** Daily change in WTI crude → next-day USDCAD return (negative relationship: crude up → CAD strengthens → USDCAD falls).

**Evidence.** Ferraro, Rossi, Rogoff (2015): Oil daily changes statistically significant predictor of CAD at daily frequency; time-unstable post-2015.

**Data.** FRED `DCOILWTICO` (WTI crude, daily, free). Yahoo Finance `^GSPC` for S&P 500 → AUD/NZD signal.

**Feasibility.** ✅ Fully public.

**Realistic net Sharpe.** 0.2–0.4 standalone; best used as a signal component, not primary driver.

**Priority.** 🟢 Lower — time-unstable; worth including in a multi-signal composite but not standalone.

---

## 6. Carry Crash Indicators (Risk Filter)

**Purpose.** Not a directional signal — a risk filter that scales all carry/rate-diff positions down during crash conditions.

**Four indicators (all public-data):**

| Indicator | Source | Threshold | Action |
|---|---|---|---|
| VIX level | FRED `VIXCLS` | > 25: scale 50%; > 35: scale 0% | Applied to all positions |
| TED spread | FRED `TEDRATE` (hist); SOFR-OIS (current) | > 50bps: elevated; > 100bps: crisis | Scale down carry positions |
| COT crowding | CFTC (already fetched) | Net spec position > 1.5σ trailing 2Y | Reduce position on crowded side |
| Carry momentum | Trailing 20-day strategy return | 2+ consecutive negative weeks | Reduce leverage |

**Evidence.** Brunnermeier, Nagel, Pedersen (2009, NBER): these four are the empirically validated early-warning signals. Using VIX + TED reduces carry skewness from −2.5 to approximately −0.5.

**Feasibility.** ✅ All public data. FRED VIXCLS and TEDRATE (or SOFR spread as post-2022 equivalent) are straightforward.

**Priority.** 🔴 High as an overlay on existing strategies — reduces tail risk with minimal Sharpe drag.

---

## 7. Risk Reversal / Skew Signal

**Signal.** 25-delta put-call IV spread as a sentiment/directional signal. `RR25 > 0` implies upside demand higher → base currency appreciation expected.

**Evidence.** Mueller, Stathopoulos, Vedolin (2017, JFE): RR25 cross-sectional dispersion contains a priced risk factor.

**Data availability.** ❌ Bloomberg/Refinitiv only. No free public source. Partially substituted by CFTC COT data (correlation ≈ 0.4–0.6 with RR25).

**Feasibility.** ❌ Not implementable without paid data terminal.

**Priority.** 🔵 Deferred — revisit when Bloomberg access is available.

---

## 8. Multi-Factor FX Composite (AQR Framework)

**AQR's documented G10 FX factor triplet (from Asness, Moskowitz, Pedersen 2013, JF):**
1. **Carry**: forward discount (rate differential)
2. **Momentum**: 12-1 month trailing return
3. **Value**: 5-year real exchange rate deviation from PPP

**Combination**: Equal-weight cross-sectional z-scores, long top-3, short bottom-3 G10 pairs.

**Evidence.** Carry alone SR 0.84; Momentum alone SR 0.95; Value alone SR 0.41; Combined SR **0.96** with significantly improved tail risk (carry-momentum correlation ≈ +0.05, carry-value ≈ −0.30, momentum-value ≈ −0.15).

**Key insight for this repo.** The negative value-momentum correlation is structural: value bets on mean reversion; momentum bets on continuation. Combining them reduces drawdowns without reducing expected returns. Your existing 2Y-diff rate signal is the carry component — adding momentum (12-1M return) and PPP-value would complete the AQR triplet at low marginal data cost.

**Data.** 
- PPP: OECD annual PPP tables (free); CPI from FRED for rolling real rate adjustment.
- Momentum: Yahoo Finance daily FX closes (already fetched).

**Feasibility.** ✅ All public.

**Priority.** 🟡 Medium-high — completing the triplet is a well-documented step with strong academic backing.

---

## Signal Priority Ranking

| Rank | Signal | Evidence | Feasibility | Effort | Expected SR |
|---|---|---|---|---|---|
| 1 | **Vol-normalised carry** | Strong | Public ✅ | Low | 0.8–1.0 |
| 2 | **Carry crash filter** (VIX+TED+COT) | Strong | Public ✅ | Low | Overlay only |
| 3 | **AQR triplet completion** (add 12-1M momentum + PPP value) | Strong | Public ✅ | Medium | 0.8–1.2 composite |
| 4 | **Term structure slope diff** | Moderate-strong | Public ✅ | Low | 0.4–0.6 |
| 5 | **Dollar factor (DOL)** | Strong | Public ✅ | Very low | 0.4–0.6 |
| 6 | **Cross-asset (oil→CAD, S&P→AUD)** | Moderate | Public ✅ | Low | 0.2–0.4 |
| 7 | **Taylor rule deviation** | Moderate-strong | Public ✅ | Medium | 0.3–0.5 |
| 8 | **VRP (GARCH approximation)** | Moderate | Public (approx) ⚠️ | Medium | 0.3–0.4 |
| 9 | **1-day lagged signal test** (rigour check, not new signal) | N/A | Already in repo ✅ | Very low | — |
| 10 | **Risk reversal / RR25** | Moderate | Bloomberg only ❌ | High | 0.3–0.5 |

---

## Key Papers

| Paper | Journal/Year | Key Signal |
|---|---|---|
| Asness, Moskowitz, Pedersen — "Value and Momentum Everywhere" | JF 2013 | Carry + momentum + value triplet for G10 FX |
| Koijen, Moskowitz, Pedersen, Vrugt — "Carry" | JFE 2018 | Unified carry across asset classes |
| Dupuy — "Risk-Adjusted Return Managed Carry Trade" | JBF 2021 | Vol-normalised carry |
| Della Corte, Kozhan, Neuberger | JFE 2021 | FX VRP cross-section |
| Brunnermeier, Nagel, Pedersen — "Carry Trades and Currency Crashes" | NBER 2009 | Crash indicators |
| Lustig, Roussanov, Verdelhan — "Common Risk Factors in Currency Markets" | RFS 2011 | DOL and HML_FX factors |
| Molodtsova, Papell | JIE 2009 | Taylor rule FX predictability |
| Ferraro, Rossi, Rogoff | CREI 2015 | Oil → CAD daily predictability |

*Last updated: June 2026*
