# Institutional Quant Fund Practices: Advanced Research (v2)

Substantially expanded from v1. Adds AQR full paper canon with construction details, Two Sigma/D.E. Shaw/Man AHL/Winton deep dives, alternative data and its decay rate, institutional risk management frameworks (PCA, factor stripping, Millennium pod), signal combination evidence (HRP vs equal-weight, IC-weighted vs equal-weight), and full meta-research on factor survival.

*Last updated: June 2026*

---

## 1. AQR — Full Research Program and Signal Architecture

### 1.1 Alternative Risk Premia (ARP) vs. Traditional Factors

**Traditional factors** = long-only exposures to asset class returns (equity, bonds, credit); you earn a premium for bearing systematic risk.

**Alternative Risk Premia (ARP)** = long-short, zero-cost, market-neutral exposures to common risk factors; you earn a return without net beta to the underlying asset class. The six canonical ARP families that AQR harvests ("Understanding Alternative Risk Premia," Ing-Chea Ang, AQR 2018):

| Factor | Description |
|---|---|
| **Value** | Long cheap, short expensive (PPP/book-price/yield) |
| **Momentum** | Long recent outperformers, short recent underperformers (1–12M) |
| **Carry** | Long high-carry, short low-carry (yield differentials in FX/bonds, roll in commodities) |
| **Defensive/Low-Beta** | Long low-risk assets, short high-risk (BAB mechanism) |
| **Trend** | Time-series momentum, long assets in uptrend, short in downtrend |
| **Volatility** | Short implied vs. realised vol premium (VRP) |

All six: investable via liquid instruments (futures, FX forwards), low mutual correlation, scale-invariant.

### 1.2 AQR Style Premia — Specific Construction

From AQR Style Premia Alternative Fund filings and "Understanding Style Premia":

**Asset class risk weights (approximate):**
- Individual equities: 30%
- Equity index futures: 23%
- Fixed income futures: 23%
- Currencies: 24%

**Signal risk weights in the composite:**
- Value: ~32% | Momentum: ~28% | Defensive: ~15% | Trend: ~12% | Carry: ~10% | Volatility: ~3%

**Key implementation details:**
- All signals z-scored cross-sectionally within each asset class before combination
- Weighting in **volatility space** (risk-weight, not notional-weight)
- Positions sized inversely to realised volatility at instrument level
- Portfolio targets a fixed ex-ante volatility (e.g., 10% annualised)

**FX-specific signals (from "Value and Momentum Everywhere," AMP 2013, JF):**
- FX value = deviation from PPP (5-year moving average of CPI-adjusted spot rate)
- FX momentum = 12-month spot return (skipping last month)
- FX carry = forward discount (domestic minus foreign interest rate)

Key finding: Value and momentum are **negatively correlated** with each other both within and across asset classes — combination provides genuine diversification, not just averaging.

### 1.3 AQR Macro Momentum ("A Half Century of Macro Momentum," Jordan Brooks, AQR 2017)

Extends momentum beyond price to fundamental macroeconomic data. Four macroeconomic themes:
1. **Business Cycle** — change in real GDP growth forecasts
2. **International Trade** — spot FX rate vs. export-weighted basket
3. **Monetary Policy** — front-end yield curve slope changes
4. **Risk Sentiment** — equity market excess returns

Signal aggregation: **equal-weighted average of 1-month, 3-month, and 12-month** lookback periods across all themes.

**Evidence:** Gross Sharpe ~0.7, net ~0.5 (1970–2016). Negatively correlated with carry and equity risk premium during stress — genuine diversifier.

### 1.4 Ilmanen "Investing Amid Low Expected Returns" (2022) — Five Prescriptions

Key book for any systematic investor. Core premise: The 40-year tailwind from falling rates and expanding valuations is over. Expected returns on 60/40 portfolios may be 2–4% real vs. historical 5–6%.

Five prescriptions:
1. **Diversify across return sources** — traditional asset class premia alone are insufficient; style premia and illiquidity premia must be added
2. **Humble forecasting** — valuation-based return forecasting has weak short-run signal but strong long-run signal (5–10 year horizon); do not market-time factors
3. **Illiquidity premia are real but overstated** — private equity premia: 50–100 bps real, not 200–300 bps as often claimed; selection bias adjustment reduces the apparent premium significantly
4. **Style premia (ARP) diversify well in low-return environments** — near-zero equity beta means they provide returns uncorrelated to traditional portfolio drawdowns
5. **Patience and discipline beat tactical factor rotation** — factor timing signals exist but are weak; tactical overlays degrade Sharpe ratios more often than not

**Directly confirmed by this repo:** Strategy #14 (trend-confirmation overlay on strat_12) degraded Sharpe from 2.73 to 1.59 — consistent with Ilmanen's point 5.

### 1.5 BAB (Betting Against Beta) — Post-2015 Performance

**Original (Frazzini & Pedersen, JFE 2014):** U.S. BAB Sharpe ~0.75 from 1926–2009, roughly double the value factor Sharpe.

**Post-publication challenges:**
- Novy-Marx (2016, "Betting Against Betting Against Beta"): BAB performance heavily driven by non-standard equal-weighting that concentrates exposure in micro-cap stocks (bottom 1% of market cap receives $1.05 of investment per $1 notional)
- When replicated with value-weighting and NYSE breakpoints: factor substantially weaker
- Post-2012 live AQR BAB data: diminished Sharpe vs. historical backtest — consistent with ~50% McLean-Pontiff publication decay
- Significant drawdown 2019–2020: low-volatility stocks de-rated sharply in the COVID recovery

**Current status:** BAB retains value as a **component** in a diversified quality/defensive factor bundle (as in QMJ), not as a standalone strategy.

### 1.6 QMJ (Quality Minus Junk) — What Matters Most

**Paper:** Asness, Frazzini, Pedersen (RFS 2019). Free dataset: AQR data library.

**Four-pillar architecture:**

| Pillar | Weight | Key Variables |
|---|---|---|
| Profitability | 25% | Gross profit/assets, ROE, ROA, cash return on assets, gross margin, accruals (negative sign) |
| Growth | 25% | 5-year changes in profitability ratios |
| Safety | 25% | Low beta, low idiosyncratic vol, low leverage, low O-score, low Z-score, low earnings vol |
| Payout | 25% | Dividend/equity ratio (net issuance is negative signal) |

**Hierarchy of importance:**
1. **Gross profitability/assets** (Novy-Marx 2013) — single most powerful; uses gross profit before R&D/marketing write-downs; more robust than ROE/ROA
2. **Accruals** (Sloan 1996) — high accrual components to earnings predict lower future returns; cash earnings quality is the key metric
3. **Low-beta/safety** — contributes most to diversification benefit vs. momentum/value
4. **Growth** — weakest individually but adds diversification when combined

**"Quality margin puzzle":** High-quality stocks trade at a premium, but not large enough to eliminate their alpha — investors systematically overpay for junk relative to quality. Behavioral: preference for lottery-like, high-vol, speculative stocks.

---

## 2. Two Sigma — What Is Publicly Known

### 2.1 Organizational Facts
- Founded 2001 by David Siegel and John Overdeck (both ex-D.E. Shaw); ~$60B AUM
- Flagship funds: Spectrum (+10.9% in 2024), Absolute Return Enhanced (+14.3% in 2024)
- ~3,000+ employees including 1,500+ researchers and engineers

### 2.2 ML Signal Generation Architecture
- **Data infrastructure:** Invested in Crux Informatics (data cleaning/normalisation pipeline) — industrial-scale alternative data processing
- **Trade frequency:** 300M+ shares traded daily — requires short-horizon signals; most signals operate at 1–10 day holding periods
- **Signal types (confirmed via job postings and public research):** Satellite imagery, credit card flows, NLP on earnings calls and news, web scraping, job posting data, geolocation foot traffic
- **ML architectures used:** Gradient boosting, neural networks, reinforcement learning for execution optimisation; confirmed use of XGBoost-type and LSTM-type architectures
- **Open-source contribution:** Flint — time-series feature library for Spark; used by systematic funds for feature generation on large datasets

### 2.3 Key Insight About Two Sigma's Edge
Unlike AQR, Two Sigma's edge is **process and infrastructure**, not theory that can be published. Their alpha is in the data acquisition, cleaning, and ML pipeline. Their published research covers principles, not specific alpha methods.

---

## 3. D.E. Shaw — Hybrid Systematic-Fundamental

### 3.1 Facts and Structure
- Founded 1988 by David Shaw; ~$60B AUM; David Shaw now primarily in computational biochemistry
- Confirmed structure: "systematic strategies that follow quantitative, technical and computational techniques; discretionary strategies based on human and fundamental analysis; and hybrid strategies that combine both"
- Pedro Domingos (author of *The Master Algorithm*) joined as head of ML in 2018 — confirms serious ML build-out

### 3.2 What Is Inferrable About Signal Generation
- **Statistical arbitrage at multi-second frequencies** — D.E. Shaw was the pioneer in the 1990s
- **Market structure exploitation** — first to profit systematically from SEC order handling rules
- **Long-horizon equity factors** — fundamental data fed through systematic screens; pioneered "quantamental" before the term existed
- **Cross-sectional equity pricing** — multi-factor models combining accounting, price, and alternative data

**Bottom line:** DESCO essentially invented institutional quant equity trading. Their edge is 35 years of proprietary signal development compounded. Nothing actionable is published.

---

## 4. Man AHL / Man Group — Deep Dive

### 4.1 Strategy Architecture (as of 2024–2025)
- **AHL Diversified:** Pure trend/momentum across ~400 liquid futures and FX markets
- **AHL Dimension:** Multi-strategy combining momentum (2–3 month), FX/fixed income carry, and short-term technical/seasonality
- **AHL Evolution:** ML-augmented; trades interest rates in less-developed markets (Brazilian rates, Korean won, credit indices)
- **AHL Alpha:** Flagship ML-driven fund; target volatility managed systematically

### 4.2 Machine Learning Integration at Man AHL

From "The Rise of Machine Learning at Man AHL" (Man Group):
- First true ML models deployed **live in client portfolios from early 2014**
- Initial constraint: ML models were constructed to be **orthogonal to existing momentum signals** — verified statistical independence before production deployment
- **Oxford-Man Institute (OMI):** Joint research venture with Oxford University; 19+ ML researchers hired full-time since 2016
- Notable published work: "Network Momentum Across Asset Classes" (arXiv:2308.11294, 2023) — graph-theoretic approaches to cross-asset momentum spillovers
- Transfer learning application: Astronomy image classification methods (Galaxy Zoo) adapted to classify signal quality from broker recommendations

### 4.3 Man AHL's FX Signal Architecture
- **FX carry:** Forward discount (domestic minus foreign interest rate); standard long highest 3 yielding G10 currencies, short lowest 3
- **FX momentum:** 1-month, 3-month, and 12-month price returns combined with equal weights
- **FX trend:** Time-series EWMA crossover (fast vs. slow MA); multiple lookback periods blended
- **FX value:** Real exchange rate deviation from long-run PPP; slow-moving, used as tilts rather than active signals

**Man AHL's key insight on trend:** "Momentum is a relatively weak signal at a single market level, but we see it almost everywhere. In every asset class we've ever looked at, we see evidence of price trends being more than just Brownian motion."

### 4.4 Campbell & Company — Published Research
From CME Group white papers:
- Signal breakdown (flagship Managed Futures): ~95% inputs are price-derived/technical; fundamental inputs feed non-trend models (~20% of programme)
- Key improvement: integrating alternative data — satellite imagery for agricultural yield, social media sentiment for equity positioning, economic nowcasting for rates

---

## 5. Winton Group — Research-Oriented CTA

### 5.1 David Harding and Shift Away from Pure Trend
Winton is distinctive for explicit scientific methodology. ~$10B AUM at peak.

From public talks and Hedge Fund Journal:
- "We noticed a consistent decline in the performance of trend-following strategies since the 1970s" — Harding's own acknowledgment of decay
- R&D team of 100+ researchers (PhDs, mathematicians, statisticians, astrophysicists)
- Pivotal shift (Risk.net, ~2017): Harding stated Winton was moving away from pure trend following because they no longer believed it was the best available systematic strategy
- Now runs systematic macro, long-short equities, credit, and other strategies alongside trend

### 5.2 Published Work on Non-Linear Trend
From arXiv:2510.23150 "Revisiting the Structure of Trend Premia" (2025):
- A **persistence rule in weight allocation** (limiting abrupt reallocation driven by transient covariance shifts) materially improves performance stability vs. equal-weight approaches
- Directly applicable to FX momentum signals: slow reallocation between trend signals reduces excessive turnover and costs

**"Two Centuries of Trend Following"** (arXiv:1404.3274): Shows price trends statistically significant and economically large for 200 years — argues against the hypothesis that trend following only works in specific regulatory regimes.

**CTA performance persistence:** Some evidence of persistence over 1–2 year horizons; largely disappears at 3+ year horizons. Not a reliable selection criterion.

---

## 6. Signal Construction at Institutional Level

### 6.1 Look-Ahead Bias — Institutional Standards

| Data Type | Institutional Standard | Rationale |
|---|---|---|
| Price signals | Close-to-close; entry at next day open (1-day lag) | Prevents intraday timing bias |
| Fundamental data | 2-month lag after fiscal quarter end | Ensures SEC filing is in EDGAR |
| Volume signals | Previous day's VWAP only | Never use same-day VWAP |
| Index membership | Beginning-of-period only | Prevents index-rebalancing look-ahead |
| Point-in-time databases | Compustat PIT, Bloomberg PIT for earnings | As-reported, not as-restated |

**The "lag-one extra day" test (AQR Craftsmanship Alpha):** If a strategy's Sharpe materially degrades when you add an extra 1-day lag to all signals, the strategy likely has implicit look-ahead bias. A robust strategy should be **insensitive to 1-day additional lag**.

*Critical for this repo: The EURUSD timestamp alignment test (re-run strat_01 with d_diff[t-1] vs d_diff[t]) directly implements this institutional standard.*

### 6.2 Walk-Forward vs. Expanding Window — What Institutions Actually Use

| Estimation Target | Window Type | Rationale |
|---|---|---|
| Signal parameters (lookback period, hedge ratio) | **Expanding window** | Theory justifies the parameter; data confirms it; reducing estimation variance matters more than stationarity |
| Covariance matrix for portfolio construction | **Rolling window (1–3 years)** | Stationarity more important; structural breaks matter |
| Volatility (for position sizing) | **EWMA (21–63 day half-life)** | Responsiveness to current regime is primary concern |

**The worst outcome:** Optimising window length in-sample. This is treated as hyperparameter tuning and dramatically inflates backtest Sharpe.

### 6.3 Signal Stacking — How Many Signals Before Overfitting?

**Key paper:** Novy-Marx (2015, NBER WP 21329): "Backtesting Strategies Based on Multiple Signals."

**Critical finding:** When signing each signal to predict positive returns, combining the best k signals out of n candidates produces bias almost as large as selecting the single best of n^k candidates. "Highly significant" backtested performance is easy to generate from purely random signals through selection.

**Institutional rules:**
- Each signal must have **prior theoretical motivation before data is touched** (pre-registration logic)
- t-statistic cutoff: Harvey, Liu, Zhu (2016) recommend **t > 3.0** for signals in a universe of 316+ previously tested factors; for 50 candidates, threshold ~2.5
- IC with existing composite: New signal IC with existing alpha should ideally be < 0.3
- **Rule of thumb:** Adding more than 8–12 signals with similar information sources rarely improves IR materially; marginal IR falls roughly as √(number of independent signals)

### 6.4 Correlation Management Across Signals

Standard institutional practice:
1. **Cross-signal correlation matrix** — monitor rolling 6-month IC correlations; flag pairs exceeding 0.6 (signals becoming redundant)
2. **Factor attribution after combination** — ensure combined alpha does not inadvertently load on a single known factor
3. **PCA on the signal matrix** — first principal component should explain < 30–40% of total signal variance in a well-diversified signal set

### 6.5 ISTA / Information Stability — Definition

The concept of **information stability** in signal research (used in WorldQuant-style systematic equity frameworks):
- Tests whether a signal's IC is **stable across subperiods, regions, and market regimes**
- Operational metric: compute rolling 6-month IC series; compute **ICIR = mean(IC) / std(IC)**
- Threshold: ICIR > 0.5 = stable signal; ICIR < 0.3 = potentially overfitted or regime-dependent
- A signal with mean IC > 0.03 but ICIR < 0.3 is not deployable without additional analysis

**Why ICIR matters for weighting:** The Grinold-Kahn fundamental law defines IR ≈ IC × √BR (breadth of bets). Maximising IR requires not just high mean IC but high IC consistency (ICIR). This is the institutional justification for equal-weighting signals when IC is similar but IC volatility differs.

---

## 7. Alternative Data — What Works and What Has Decayed

### 7.1 Satellite Data

| Use Case | Signal | Alpha Status |
|---|---|---|
| Retail same-store sales | Parking lot vehicle counting | ~18% better earnings estimates vs. analyst consensus; commoditised by 2019-2020 |
| Crude oil storage | Radar satellite inventory levels | Predicts EIA inventory report; now sold to 50+ funds |
| Agricultural yields | Multispectral NDVI from Sentinel-2 | Replaces USDA NASS estimates; still alpha at cutting edge |
| Commodity flows | AIS ship tracking | Marine Traffic free tier available; oil/LNG/grain positioning |

**Free public proxies:**
- NASA EarthData: MODIS and Landsat for NDVI; ~4-day frequency
- Sentinel-2 (ESA): 10m resolution, 5-day revisit; free
- Marine Traffic free tier: AIS ship positions

**Alpha decay:** Satellite signals for earnings (parking lots) had high alpha 2013–2018; by 2019, data vendors selling same datasets to 50+ funds simultaneously. Current alpha half-life from signal discovery to commoditisation: ~12–24 months once available from a commercial vendor.

### 7.2 Web Scraping Signals — What Is Extractable

| Signal | Evidence | Status |
|---|---|---|
| Job postings → revenue growth | Headcount trends predict revenue 2–3 quarters ahead; positive and significant | Still alpha; gaining adoption |
| Amazon product pricing → inventory | Price cuts = inventory buildup (bearish); available from CamelCamelCamel / Keepa | Semi-competitive |
| App store rankings | Abnormal downloads predict positive stock returns (HKU study, 326 public firms) | Commoditised via Bloomberg |
| Social media sentiment | Predicts 1–5 day price moves for retail-oriented stocks | Decays within 1 day for widely-covered stocks |
| Glassdoor employee satisfaction | Predicts future company performance and stock returns (Edmans et al.) | Moderately alpha; underused |

### 7.3 Credit Card Data — What It Predicts

**Providers:** Bloomberg Second Measure, Earnest Research, Affinity Solutions (YODLEE), Facteus.

**Evidence (ACM Sigmetrics 2019):** Model using anonymised weekly credit card transactions + 3-month earnings reports outperformed combined analyst consensus on 57% of quarterly earnings predictions for 30+ companies. Consumer spending predicts future earnings surprises **up to three quarters ahead**.

**Alpha decay:** Strong alpha 2015–2018. By 2020, every major hedge fund had a credit card data subscription. Current edge concentrated in **novel processing** (regional breakdowns, cohort segmentation, channel mix shifts), not raw spending signals.

### 7.4 Alternative Data Alpha Decay vs. Traditional Signals

| Signal Type | Estimated Alpha Half-Life | Notes |
|---|---|---|
| Price momentum (12M) | 20–30 years post-publication; still positive | Academic arbitrage is slow; implementation difficult |
| Value (B/P, E/P) | 10–20 years; arguably decayed post-2007 | Very crowded by 2015 |
| Satellite imagery (parking lots) | ~3–5 years (peaked 2015–2020) | Fully commoditised; now sold by 50+ vendors |
| Credit card data | ~5–7 years (peaked 2013–2020) | Widely available; edge now in processing |
| App downloads (raw counts) | ~2–3 years | Bloomberg Terminal distribution killed signal |
| Web-scraped job postings | Currently 1–4 years | Still gaining adoption |
| Novel satellite (radar, multispectral) | Currently strong | Requires bespoke data agreements |

**Key paper on decay:** McLean & Pontiff (2016, JF): anomaly returns decline 26% out-of-sample before publication and 58% post-publication. Alternative data signals follow an **accelerated version** — more capital chases the signal faster.

---

## 8. Risk Management Frameworks at Institutional Level

### 8.1 Millennium Pod Structure — Technical Details

**Structure (from public sources):**
- 330+ autonomous pods as of late 2025; each pod is an independent P&L centre
- Central Risk Management monitors all pods in real-time across: rolling Sharpe (30-day, 90-day, inception), drawdown from peak capital, factor exposure overlaps across pods

**Capital Allocation Hard Rules:**
- 5% drawdown from allocated capital → **50% capital reduction**
- 7.5% drawdown → **full pod termination**
- These are hard stops, enforced centrally, non-negotiable

**Cross-pod factor risk:** The central risk team runs a cross-pod factor risk model (Barra-type applied to the aggregate firm). If 30 pods independently load on momentum, the firm has inadvertent momentum concentration risk. Risk team monitors and reduces allocation to pods contributing to concentration.

**Known problem with hard stops:** Forced liquidation at the drawdown trough — exactly when market impact is worst and signals may be most attractive. March 2020 COVID deleveraging: multi-manager funds enforcing hard stops underperformed those with softer drawdown controls because mass exits happened just before the April-May recovery.

### 8.2 PCA-Based vs. Barra/Axioma Factor Risk Models

| Model Type | When Used | Advantages | Disadvantages |
|---|---|---|---|
| Barra (fundamental) | Regulatory reporting, client communication | Interpretable; stable; auditable | May miss short-term co-movements |
| Axioma (hybrid) | Live portfolio optimisation | Offers both fundamental and statistical models in same API; robust regression | More complex; harder to explain |
| Internal PCA (statistical) | Detecting emerging hidden factor clusters | Data-driven; captures current dynamics | Unstable across windows; uninterpretable |

**Institutional practice:** Barra for reporting; Axioma or proprietary for live optimisation; internal PCA **alongside** commercial models to catch short-term co-movements not in any fundamental model.

**Hierarchical PCA** (López de Prado, arXiv:1910.02310): Apply PCA at multiple levels of asset clustering, improving stability of factor estimates. Best used when assets have clear hierarchical structure (sectors > industries > stocks).

### 8.3 Factor Exposure Stripping — Technical Implementation

**What it is:** Removing unwanted factor tilts from a signal/portfolio so only the intended exposure remains.

**Step-by-step:**
```python
# For each time period t:
# Step 1: Regress raw signal on nuisance factors
from sklearn.linear_model import LinearRegression

X = df[['sector_dummy', 'log_mktcap', 'momentum_12m', 'beta']].values
y = df['raw_signal'].values

model = LinearRegression().fit(X, y)
residual = y - model.predict(X)  # stripped signal

# Step 2: Cross-sectionally z-score the residual
from scipy import stats
stripped_signal = stats.zscore(residual)

# Step 3: Verify — run factor attribution on stripped signal
# Any remaining loadings should be < 0.05 in absolute terms
```

**When to use:**
- When testing a new signal: strip known factors first to determine if there is **genuine incremental information** beyond existing signals
- This is how AQR distinguishes "new alpha" from "repackaged factor exposure"
- Long-short: can fully neutralise exposures via the short leg; more effective than long-only

### 8.4 Stop-Loss vs. Drawdown Control — What Evidence Shows

**Position-level stop-losses:**
- Reduce left-tail risk but also reduce realised alpha — you exit at the worst time if the signal has mean reversion
- Works best for momentum strategies (cut losers = consistent with signal)
- Hurts most for value strategies (you exit at maximum fundamental value after a price decline — exactly when you should hold or add)

**Portfolio-level drawdown control (Macrosynergy research):**
- MinMax drawdown control achieves significantly higher annualised returns than risk-parity for the same worst-case drawdown constraint
- Mechanism: reduce overall leverage when rolling drawdown exceeds threshold; do not cut individual positions
- Allows position-level drawdowns to be weathered as long as portfolio-level drawdown is managed

**Institutional consensus:**
- Hard stops: use at position level for non-systematic positions (protect against model failure)
- Drawdown control: use at portfolio level as a volatility-targeting overlay (scale leverage inversely to realised vol)
- Avoid combining both rigidly — creates procyclical liquidation at worst times

### 8.5 Kelly Criterion — Institutional Practice

**What institutions actually do:**
- **Renaissance Technologies:** Princeton-Newport documented using Kelly-based sizing; 19.1% annualised over 29 years partly attributed to Kelly-optimal sizing
- **Most institutional quant funds:** Use **fractional Kelly (typically 25–50% of full Kelly)** because:
  1. Parameter uncertainty — true Sharpe is estimated with noise; full Kelly on a noisy estimate leads to severe overbetting
  2. Leverage constraints — margin and regulatory leverage caps
  3. Drawdown limits — full Kelly drawdowns can exceed 50% during normal bad runs

**Half-Kelly:** Reduces worst-case drawdown by ~half while reducing terminal wealth by only ~8% (theoretical result) — the standard practitioner heuristic.

**In practice:** Quant funds rarely label their sizing as "Kelly." They use **volatility targeting** (e.g., "we target 10% portfolio volatility"), which achieves similar outcomes. The Kelly-equivalent formula is identical to the Grinold-Kahn position sizing formula: `size = IC × signal / volatility`.

---

## 9. Signal Combination — Going Deeper

### 9.1 IC-Weighted vs. Equal-Weight — Current Evidence

**In favour of IC-weighting (FactSet study):** Produces higher cumulative returns (~26.67 vs. 23.72 in one study) with minimal additional turnover (+1.4%). But requires stable IC estimates.

**In favour of equal-weight (AQR Craftsmanship Alpha, Israel/Jiang/Ross 2017, JPM):** In a high-signal-count regime, equal-weighting is more robust to IC estimation error. IC-weighting adds value only when signal IC is genuinely stable and well-estimated.

**Decision rule:**
- ICIR > 0.5 over 3+ years → IC-weighted or IR-proportional weighting
- ICIR < 0.5 → equal-weight (more robust to estimation error)
- N signals > 10 → equal-weight default (estimation error dominates)

**For this repo (N = 4–8 signals):** IC-weighting is potentially worthwhile once signals have 3+ years of OOS IC data. During initial testing, equal-weight is the correct default.

### 9.2 Hierarchical Risk Parity (HRP) — Does It Beat Equal Weight?

**Origin:** López de Prado (2016), "Building Diversified Portfolios that Outperform Out-of-Sample" (SSRN 2708678).

**Evidence:**
- HRP delivers **lower out-of-sample variance** than mean-variance (CLA) in Monte Carlo experiments, even though MVO's stated objective is minimum variance — a striking result
- Advantage largest when **asset return correlations have meaningful cluster structure**
- Validated in Munich Re research; outperforms ERC and equal-weight when N > 15 and clear clusters exist

**Limitation for small N:** With only 9 G10 pairs and 3–4 signal types, the hierarchical clustering may be unstable. The advantage of HRP over equal-weight is statistically significant only when N > 15 and cluster structure is clear.

**Recommendation for this repo:** Equal-weight with volatility normalisation is the appropriate default at current scale. HRP becomes relevant when signal count exceeds 10–12.

### 9.3 Ledoit-Wolf Shrinkage vs. Black-Litterman

These are **complementary, not alternatives:**

**Ledoit-Wolf (LW):** Addresses the covariance matrix estimation problem. Shrinks the sample covariance toward a target (e.g., constant correlation model). Used to improve the **covariance input** before any portfolio optimisation. Available in scikit-learn; standard at all institutional desks.

**Black-Litterman (BL):** Addresses the expected return estimation problem. "Views" (signal outputs) are blended with equilibrium expected returns with weights determined by confidence in the views. Applied to signal combination: treat each signal's predicted return as a "view" in BL, with confidence parameter proportional to signal's ICIR.

**Standard institutional combination:** LW shrinkage for the covariance matrix (always) + BL framework for expected returns (when priors and signals both exist). This combination is the current institutional standard for systematic multi-signal portfolios.

### 9.4 Alpha Decay and Signal Staleness — How to Incorporate

**Measuring decay:**
```python
# Compute IC at multiple forward horizons
for horizon in [1, 5, 10, 21, 63]:  # trading days
    ic_at_horizon = signal.corr(returns.shift(-horizon))

# Fit exponential decay
# IC(t) = IC(0) × exp(-λt)
# Half-life = ln(2) / λ
```

**Turnover-adjusted IR (Grinold 1994, updated Zhang et al. 2021 arXiv:2105.10306):**
```
IR_adj = IC × √BR / (1 + 2 × TC × λ)
```
Where TC = per-trade transaction cost, λ = decay rate. This penalises fast-decaying signals when transaction costs are non-trivial.

**For G10 FX (low TC):** Signals with half-lives of 3–10 days are implementable. For illiquid EM FX, only signals with half-life > 21 days are cost-effective.

**Integrated signals:** Combining signal_t and signal_{t-5} reduces whipsawing and transaction costs, often improving net-of-cost IR despite lower per-period predictive power.

---

## 10. Meta-Research on Quant Factor Survival

### 10.1 Harvey, Liu, Zhu (2016, RFS) — The Multiple Testing Problem

**Paper:** "…and the Cross-Section of Expected Returns" (RFS 29(1): 5–68, 2016; NBER WP 20592)

**Dataset:** 316 factors documented in academic literature as of 2015

**Key finding:** Adjusting for multiple testing, the appropriate t-statistic hurdle for a **new factor published today** is **t > 3.0** (vs. standard 1.96). Using t > 3.0: only 9 out of 313 return-correlated variables survive.

**Factors surviving t > 3.0 hurdle:**
- Market beta | Size (SMB) | Value (HML) | Momentum | Short-term reversal | Long-term reversal | Illiquidity (Amihud) | Gross profitability/assets | CMA (investment)

**For G10 FX:** Carry, momentum, and value are the three FX premia that survive multi-testing scrutiny. Any additional FX signal needs **t > 3.0** to be taken seriously at institutional level.

### 10.2 McLean & Pontiff (2016, JF) — Factor Decay After Publication

**Paper:** "Does Academic Research Destroy Stock Return Predictability?" (JF 71(1), 2016)

**Findings across 97 published predictors:**
- Returns **26% lower out-of-sample** but before publication (data mining/statistical overfitting)
- Returns **58% lower post-publication** (investor learning and trading the factor away)
- Half of out-of-sample decay is data mining; half is arbitrage

**What does NOT decay (or decays slowly):**
- High implementation cost anomalies (micro-cap, illiquid instruments) — barriers to arbitrage preserve alpha
- Anomalies requiring patience (value, long-term reversal) — psychological barriers to arbitrage
- Anomalies based on genuine systematic risk

**For FX:** Carry, momentum, and value have all been published for 20+ years. Pre-publication IC is the "true" signal; post-publication return is what's available to entrants. The post-2008 carry crash of 2015 and Aug-2024 BoJ pivot suggest that while carry persists, its left-tail risk is real and the risk-adjusted alpha may be lower than historical estimates.

### 10.3 Hou, Xue, Zhang (2020, RFS) — Replication Crisis

**Paper:** "Replicating Anomalies" (RFS 33: 2019–2133, 2020; NBER WP 23394)

**Method:** 452 anomalies tested with NYSE breakpoints and value-weighted returns (eliminating the small-cap problem inflating many anomaly returns)

**Failure rates (t < 1.96):**

| Category | Failure Rate |
|---|---|
| Trading frictions | **96%** — near-complete failure |
| Valuation | ~65% |
| Financing | ~60% |
| Investment | ~55% |
| Profitability | ~38% |
| Intangibles | ~34% |
| **Overall** | **65%** |

**What survives:**
- Momentum — robust across implementations
- Gross profitability — most reliable anomaly category
- Investment/CMA — survives when properly implemented
- Intangibles (R&D, organisational capital, brand value) — ~26 significant anomalies in this category

**Key methodological point for FX:** Many "trading frictions" anomalies are micro-cap phenomena that disappear under proper implementation. FX markets are deep and liquid — the equivalent concern is about realistic transaction cost assumptions in backtest (the USDSEK caveat in this repo is exactly this issue).

### 10.4 Detzel, Novy-Marx, Velikov (2023, JF) — Transaction Cost Reality

**Paper:** "Model Comparison with Transaction Costs" (JF 78: 1743–1775, 2023)

**Key finding:** Ignoring transaction costs, q-factor model and Barillas-Shanken 6-factor model appear superior to Fama-French. Accounting for transaction costs: **Fama-French five-factor model** has significantly higher squared Sharpe ratio — high-turnover factors lose their apparent advantage.

**Buy-hold spread technique (Novy-Marx & Velikov, RFS 2016):**
Most effective cost mitigation: use **asymmetric thresholds** for entering vs. maintaining positions.
```
Entry threshold: signal must exceed entry threshold (e.g., top quintile)
Hold threshold: maintain position as long as signal > hold threshold (e.g., top two quintiles)
```
This reduces turnover dramatically while retaining most of the alpha. Anomalies with turnover < 50%/month generate significant net spreads; those with > 50%/month rarely survive costs.

**For G10 FX:** FX transaction costs (~1–2 bps for G10 majors) are low relative to equity micro-caps. This means FX strategies can tolerate higher signal turnover before costs kill alpha. A momentum signal with 30-day half-life is implementable in FX but would be economically marginal in small-cap equities.

---

## Summary: Actionable Synthesis for This Repo

### Signal Architecture Hierarchy (ranked by robustness)

| Rank | Signal | Academic Robustness | Net Sharpe (FX) | Post-Publication Decay Risk |
|---|---|---|---|---|
| 1 | 2Y rate-diff change (our core signal) | Theoretically grounded; OOS ≈ 2.75 | HIGH | Unknown — novel daily-frequency variant |
| 2 | Carry (level of rate differential) | Harvey et al.: t > 3.0 survivor | 0.5–0.8 | Hutchinson et al.: significant decay post-2010 |
| 3 | Momentum (12-1M) | Harvey et al.: t > 3.0 survivor | 0.3–0.6 | Moderate decay; weaker post-GFC |
| 4 | Value (PPP deviation) | Harvey et al.: t > 3.0 survivor | 0.2–0.4 | Slowest decay; 5–10 year horizon |
| 5 | Macro momentum (GDP/trade/policy trend) | AQR validated 50 years | 0.5 net | Limited (requires non-trivial construction) |
| 6 | Trend (EWMA crossover) | Two-century evidence | 0.3–0.5 | Moderate; Winton documents decay |

### Construction Checklist for Each New Signal

- [ ] Point-in-time data; 1-day lag on all price signals
- [ ] Strip market beta and sector (at minimum) before testing
- [ ] Require t > 3.0 for adding to live portfolio (Harvey, Liu, Zhu standard)
- [ ] Test IC stability (ICIR > 0.5) before IC-weighting
- [ ] Compute IC decay curve (1/5/10/21/63 day horizons)
- [ ] Run "lag-one extra day" test — Sharpe should not materially degrade
- [ ] Apply buy-hold spread (asymmetric thresholds) to reduce turnover
- [ ] Back-of-envelope: does net alpha exceed transaction costs at target turnover?

### Signal Combination Rules (Institutional Standard)

- Covariance estimation: **Ledoit-Wolf shrinkage** (always)
- Signal weighting: **equal-weight** when signals < 10; IC-weighted when ICIR > 0.5 over 3+ years; HRP when N > 15 and cluster structure exists
- Portfolio volatility: **target fixed annualised vol** (10%); scale all positions inversely to realised vol (EWMA 21–63 day)
- Kelly fraction: **25–50% of theoretical maximum**; implemented as vol-targeting with leverage cap

### Risk Management Rules

- Factor exposure strip: neutralise sector, size, and momentum from any new signal
- Cross-signal correlation: flag pairs with rolling IC correlation > 0.6
- Drawdown control: **portfolio-level vol scaling** preferred over hard position stops for systematic strategies
- PCA on residuals: run monthly to detect emerging hidden factor clusters not in the Barra model
- Multi-manager pod lesson: do not set hard position stops that trigger forced liquidation at trough drawdown

---

## Key Papers — Full Reference Table

| Paper | Year | Key Finding | Applicability to This Repo |
|---|---|---|---|
| Harvey, Liu, Zhu — "…and the Cross-Section of Expected Returns" | RFS 2016 | 316 factors; t > 3.0 required; only 9 survive | Raise bar for claiming any new signal is real |
| McLean, Pontiff — "Does Academic Research Destroy Stock Return Predictability?" | JF 2016 | 97 anomalies; 58% decay post-publication | Calibrate expectations on carry/momentum going forward |
| Hou, Xue, Zhang — "Replicating Anomalies" | RFS 2020 | 65% failure rate; 96% in trading frictions | USDSEK cost caveat is exactly the trading frictions problem |
| Detzel, Novy-Marx, Velikov — "Model Comparison with Transaction Costs" | JF 2023 | High-turnover factors don't survive costs; buy-hold spread effective | Apply asymmetric thresholds to carry positions |
| Novy-Marx — "Backtesting Strategies Based on Multiple Signals" | NBER WP 2015 | Multi-signal combination dramatically amplifies overfitting | Pre-register signals before looking at data |
| Asness, Moskowitz, Pedersen — "Value and Momentum Everywhere" | JF 2013 | V&M in 8 asset classes; negatively correlated | Core AQR triplet for G10 FX; carry+momentum+PPP |
| Frazzini, Pedersen — "Betting Against Beta" | JFE 2014 | Low-beta outperformance; construction bias noted post-publication | Use as quality sub-component, not standalone |
| Asness, Frazzini, Pedersen — "Quality Minus Junk" | RFS 2019 | Gross profitability + safety most important sub-components | India equities quality screen construction |
| Israel, Jiang, Ross — "Craftsmanship Alpha" | JPM 2017 | Implementation details matter; signal weighting + risk control add alpha | Every step in this repo's pipeline |
| López de Prado — "Building Diversified Portfolios (HRP)" | SSRN 2016 | HRP has lower OOS variance than MVO despite MVO's min-var objective | Useful when N > 15 signals |
| Man AHL — "The Rise of Machine Learning" | Man Group 2018 | ML must be verified orthogonal to existing signals before deployment | Any ML signal addition to this repo |
| Brooks — "A Half Century of Macro Momentum" | AQR 2017 | Macro momentum in FX/equity/rates/bonds; 4 macroeconomic themes; SR ~0.5 net | Business cycle differential signal (OECD CLI) |
| Ilmanen — "Investing Amid Low Expected Returns" | Book 2022 | Factor timing overlays hurt Sharpe; style premia diversify well | Confirmed by our Strategy #14 result |

---

*v2 adds: AQR full paper canon with specific signal weights and construction details, Two Sigma/D.E. Shaw/Man AHL/Winton deep dives with specific methodology, alternative data with decay rates, institutional risk management (PCA, factor stripping, Millennium pod mechanics), signal combination evidence (HRP, LW, BL), full meta-research on factor survival with Hou-Xue-Zhang and Detzel-Novy-Marx-Velikov results. The single most important new finding: the "lag-one extra day" test from AQR directly applies to the unresolved EURUSD timestamp alignment question.*
