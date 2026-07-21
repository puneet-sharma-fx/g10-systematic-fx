# India Equities: Advanced Quant Research (v2)

Substantially expanded from v1. Adds SEBI regulatory data signals, institutional-grade data source map, factor anomaly evidence (including replication failures), IPO/options market signals, transaction cost breakdown, and actionable strategy tiers.

*Last updated: June 2026*

---

## What's New vs v1

| Area | v1 Coverage | v2 Status |
|---|---|---|
| Low-vol (BAB) | ✅ Basic | ✅ Updated with Raju BAB data |
| Momentum 12-1 | ✅ Basic | ✅ Extended with 52-week high variant |
| Quality-momentum | ✅ Basic | ✅ Extended with ROE-profitability specifics |
| FII/DII flows | ✅ Overview | ✅ Specific construction + AMFI SIP floor |
| Promoter shareholding | ✅ Mentioned | ✅ Full pledging signal + MCA21 charges |
| Transaction costs | ✅ STT overview | ✅ Full statutory breakdown + spread estimates |
| **SEBI insider trading disclosures** | ❌ Missing | 🆕 Full PIT signal construction |
| **Bulk/block deals as signal** | ❌ Missing | 🆕 NSEPython data access |
| **PEAD (post-earnings drift)** | ❌ Missing | 🆕 India-specific evidence |
| **Accruals anomaly failure** | ❌ Missing | 🆕 India-specific failure documented |
| **IPO grey market / lock-up** | ❌ Missing | 🆕 GMP signal construction |
| **India VIX variance risk premium** | ❌ Missing | 🆕 Straddle-based VRP harvest |
| **NSE options: PCR / max pain** | ❌ Missing | 🆕 Practical evidence |
| **GST / auto / PMI macro signals** | ❌ Missing | 🆕 Added |
| **Factor replication failures** | ❌ Missing | 🆕 Full failure table |
| **Full data source table with URLs** | ❌ Missing | 🆕 35+ sources mapped |

---

## 1. SEBI Public Data Signals

### 1.1 Bulk Deals and Block Deals

**Definitions:**
- **Bulk deal**: Any single transaction ≥ 0.5% of total shares traded in one day (on-market, continuous session).
- **Block deal**: Pre-arranged large trade, executed in two 15-minute windows only — 08:45–09:00 AM and 02:05–02:20 PM — at a price within ±1% of prior closing. Used by institutions to cross large blocks without market impact.

**Data access:**
- NSE live API: `https://www.nseindia.com/api/snapshot-capital-market-largedeal?bandtype=bulk_deals`
- NSE archive: `nseindia.com/report-detail/display-bulk-and-block-deals`
- Python: `nse_large_deal_historical()` function in NSEPython; returns date, symbol, client name, buy/sell, qty, price
- Historical archive back to 2003; same-day SEBI mandated disclosure after market close

**Signal construction:**
```python
from nsepython import nse_large_deal_historical

# Download bulk deals for specific stock
deals = nse_large_deal_historical('RELIANCE', '01-01-2020', '31-12-2024')
# Filter: promoter buys in bulk = bullish signal
promoter_buys = deals[(deals['client'].str.contains('promoter|group', case=False)) &
                       (deals['buy_sell'] == 'B')]

# Signal logic:
# 1. Promoter open-market buy > 0.5% float → long signal, hold 20 days
# 2. FII bulk buy in thin-float mid-cap → momentum acceleration signal
# 3. PE/VC bulk sell at market (not pre-arranged block) → distribution warning
```

**What the data shows vs what it doesn't:**
- Names disclosed: includes institution name (e.g., "Vanguard Emerging Markets", "ICICI Prudential MF")
- Price disclosed: whether trade was above/below market
- NOT disclosed: rationale, direction of future trades
- No published peer-reviewed backtest exists — this is a research gap

**Caution:** FII bulk buys are often momentum reinforcement, not contrarian. Promoter open-market buys after price declines have the strongest theoretical basis (skin in the game + information advantage). Promoter buys via rights issue or preferential allotment are weaker signals (regulatory compulsion possible).

---

### 1.2 SEBI PIT Insider Trading Disclosures

**Regulatory framework:** SEBI (Prohibition of Insider Trading) Regulations 2015 (amended March 2025). Mandatory disclosure by:
- All promoters and promoter group on any trade
- Designated Persons (DPs: directors, senior management) when trading > ₹10 lakh in a rolling calendar quarter

**Data access:**
```
BSE: bseindia.com/corporates/Insider_Trading_new.aspx
NSE: nseindia.com/companies-listing/corporate-filings-insider-trading
Aggregated: insiderscreener.com/en/india/insider-trading/
            (free, covers NSE + BSE, filterable by category, buy/sell, date)
```

**Signal evidence:**
- US parallel: Cohen, Malloy & Pomorski (2012, *JF*) — "Decoding Inside Information." Officer (non-director) insider purchases predict future returns more than director purchases. 12-month DGTW-adjusted return: +1.5% per month following officer buys.
- India-specific academic paper: No direct peer-reviewed equivalent, but PEAD evidence (Section 5) implies that corporate insiders likely have an information edge in India given slower price discovery.

**Signal construction:**
```python
# Insider buy signal: promoter open-market purchases
# Criteria:
# 1. Category = Promoter (not ESOP exercise)
# 2. Transaction type = 'Market Purchase' (not rights/preferential)
# 3. Post a ≥15% drawdown in the stock price (buying into weakness)
# 4. Quantity ≥ 0.1% of outstanding shares

# Signal: long for 30 days post-disclosure
# Exit: if price recovers to pre-drawdown level or 30 days elapsed

# Data cleaning notes:
# - Filter out ESOP exercises (form type 'C' vs 'D')
# - Filter out transfers between group entities
# - Lag signal by 1 trading day (disclosures arrive after market close)
```

**Key data quality issue:** Many DP disclosures are ESOP exercises (non-discretionary). True "insider conviction buys" require filtering to market-purchase-type transactions by promoters, not ESOPs.

---

### 1.3 Promoter Pledging as Crash Risk Signal

**Academic evidence (India-specific):**

| Study | Sample | Key Finding |
|---|---|---|
| Chauhan (IIMB, 2020) | 1,452 NSE/BSE firms | Pledging exacerbates volatility; adversely affects firm value and long-term performance |
| BSE 500 study (2024) | BSE 500, 10 years | Pledging significantly positive predictor of future stock price **crash risk** |
| MDPI JRF (2023) | NSE small-cap-value | Rising promoter stake (paradoxically) negative for returns in small-cap-value — supply-side effects |

**Signal construction:**
```python
# From quarterly SHP filings (NSE/BSE)
# pledge_ratio = pledged_shares / total_promoter_shares

# Short signal criteria:
# 1. pledge_ratio > 50%  AND rising QoQ → high crash risk flag
# 2. pledge_ratio increased > 10% in a single quarter → deteriorating control
# 3. Promoter pledge AND simultaneous rising debt on balance sheet → double negative

# Implementation: use as risk filter, not directional alpha
# - Exclude from long portfolios when pledge_ratio > 40%
# - Short via F&O when pledge_ratio > 60% AND stock near all-time-high
```

**MCA21 charges as leading indicator:**
- New charges (secured loans) filed on MCA21 before balance sheet disclosure date
- `CHG-1` form filing = new charge creation (lender taking security on assets)
- Aggregators: tofler.in, accumn.ai (paid, ₹500–2,000/company for one-off data)
- Signal: sudden burst of `CHG-1` filings + pledging increase = balance sheet stress incoming

---

### 1.4 Shareholding Pattern (SHP) Quarterly Signals

**Filing cadence:** Within 21 days of quarter end. Post-June 2022 SEBI circular, format expanded to separately disclose FDI, SWF, FPI Cat I, FPI Cat II, domestic MF, insurance, NBFC — each as distinct line items.

**Systematic signals:**

| Pattern | Signal | Theory |
|---|---|---|
| FPI accumulation 3+ consecutive quarters | Positive momentum | Smart money trend-following |
| MF conviction increase in mid-cap (low float) | Positive | MF does due diligence; long holding period |
| Rapid public float decline | Squeeze setup | Promoters buying from market |
| Rising retail % + falling institutional % | Distribution warning | Smart money exiting into retail buying |
| FPI declining + DII increasing | Counter-cyclical support zone | DII absorbs FPI selling |

**Data access:** NSE/BSE SHP filings machine-readable. Screener.in aggregates into queryable interface. Historical SHP to 2001 on BSE. Python: `jugaad-data` library or BseIndiaApi.

---

### 1.5 FII/DII Daily Flows Signal

**Official source:** `nseindia.com/reports/fii-dii` — daily CSV, covers equity cash, equity F&O, and debt separately for FPIs and DIIs (MF + insurance + banks).

**Strategy construction:**
```python
# 5-day rolling net flows as trend indicator
fpi_5d = fpi_daily_net.rolling(5).sum()
dii_5d = dii_daily_net.rolling(5).sum()

# Signal 1: FPI momentum — positive flows → Nifty likely to continue up 2–3 days
nifty_signal = np.sign(fpi_5d.shift(1))

# Signal 2: FPI-DII divergence (contrarian)
# When FPIs net sell > ₹3,000 crore AND DIIs net buy > ₹2,000 crore
# → mean-reversion long on Nifty 50 (5-day holding)
divergence_signal = (fpi_5d < -3000) & (dii_5d > 2000)

# Structural floor note: SIP flows now > ₹30,000 crore/month (up from ₹8,000 crore 2019)
# Creates structural demand for Nifty 200 stocks regardless of FPI activity
# → reduces crash risk in index stocks vs prior cycles
```

---

## 2. India-Specific Factor Anomalies

### 2.1 Primary Academic Dataset

**IIMA Fama-French Library:**
- URL: `faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/`
- Built by: Agarwalla, Jacob & Varma, IIM Ahmedabad (CMIE Prowess data)
- Universe: All BSE + NSE listed companies (~4,900–5,400)
- Period: July 1993 onwards (monthly factors)
- Portfolio formation: **September rebalancing** (matches Indian fiscal year; key distinction from Fama-French July)
- Factors available: SMB, HML, MOM (12-1), RMW, CMA
- Updated: 3 times/year (March, September, December)
- **Freely downloadable as CSV**

**Rajan Raju Library (SSRN 5008269 — November 2024):**
- Built on: Refinitiv Datastream (vs CMIE Prowess) → independent cross-validation of IIMA
- Additional factors: **BAB (Betting Against Beta)**, **Low Volatility factor** — not in IIMA library
- Finding: expanded universe and updated size classification have minimal statistically significant impact on factor returns
- Key related papers: SSRN 4054146 (four-factor), SSRN 4190426 (five-factor), SSRN 4133389 (factor indices), SSRN 4587697 (52-week high effect)

---

### 2.2 Momentum — Strongest and Most Robust Factor

**Evidence:**
- Agarwalla, Jacob & Varma (2017, *Vikalpa*): Momentum provides annualised alpha of **~17%** in India. Works in equal-weighted and value-weighted portfolios.
- Raju SSRN 4587697 (52-week high, Oct 2004–Aug 2023, NSE): **52-week high variant delivers more stable alpha** than 12-1 momentum; weaker long-term reversals; less severe momentum crashes.
- Momentum crashes: visible in IIMA factor returns — March 2020 drawdown ~35% in one month.

**Best construction for India:**
```python
# Standard 12-1 vol-adjusted
ret_12m = monthly_returns.rolling(12).sum().shift(1)  # skip last month
vol_12m = monthly_returns.rolling(12).std()
mom_score = ret_12m / vol_12m  # vol-adjusted

# 52-week high variant (Raju 2023, more stable)
high_52w = price.rolling(252).max()
dist_to_high = price / high_52w  # ratio; closer to 1 = near high = momentum
```

**Transaction cost implication:** Monthly rebalancing of momentum on Nifty 200 costs ~0.5–0.7% round-trip per stock. Quarterly rebalancing halves this. Recommend **quarterly rebalancing** to preserve net alpha.

**Capacity:** Nifty 50 momentum (top 10 by score): very liquid, scalable. Nifty 200 momentum: requires ₹3–10 crore position sizing per stock to avoid market impact. Above ₹50 crore AUM, momentum begins to move the market in Nifty 200 names.

---

### 2.3 Profitability (RMW) and Quality

**Five-factor model tests (NSE 500, Oct 1995–Sep 2022, Zenodo 2025):**
- RMW and CMA together raise adjusted R² from ~71% (three-factor) to ~94% (five-factor)
- **Strong negative correlation between HML and RMW: −0.61** — value stocks have lower profitability in India

**Six-factor model (TandFonline 2024 — Kedia):**
- Adds Human Capital factor (wages proxy); separately significant
- ROE confirmed as best profitability proxy for India (outperforms gross profitability or operating profitability)

**Quality-momentum interaction:**
- High quality (high ROE) + high momentum (near 52-week high) = most stable long signal in India
- CAGR ~17–18% documented by multiple practitioners over 10y periods
- Logic: quality prevents value traps; momentum ensures price confirmation

**Construction:**
```python
# Quality score: percentile rank across Nifty 500
quality_score = (roe_rank + low_debt_rank + high_fcf_rank) / 3
# Momentum score: 52-week high variant
mom_score = price / price.rolling(252).max()
# Combined signal: equal-weight
combined = (quality_score + mom_score) / 2
# Long top quartile, avoid bottom quartile
```

---

### 2.4 Size Factor — Weak in India

**Evidence:**
- Agarwalla et al. (2017): SMB annualised return only **0.36%** with 14.5% volatility (vs. 17% for momentum).
- Sharma et al. (2021): Size and volume anomalies have **faded substantially** vs. earlier evidence.
- Explanation: Indian small-caps are highly illiquid; the premium is liquidity compensation, not a true size factor.

**Recommendation:** Do not run a standalone long-short SMB. Instead, combine size with profitability (profitable small-caps survive the quality screen) — this captures size-quality interaction that survives liquidity adjustment.

---

### 2.5 Accruals Anomaly — Does NOT Replicate Naively

**India-specific evidence (Sehgal, Subramaniam & Deisting, SSRN 2128978):**
- Sample: 493 BSE companies, 1997–2010
- Finding: Earnings persistence more attributable to **cash flows than accruals** (same as US)
- BUT: Indian investors **under-price accruals and over-price cash flows** — this is the **OPPOSITE** of the US Sloan (1996) finding
- Result: **Low-accrual firms do NOT systematically outperform** in India in the US-replication sense
- The anomaly is explained by the three-factor model (size + value risk) — it is not alpha

**Correct signal for India:**
- Not: short high-accrual firms (US approach)
- Instead: **long high operating cash flow / net income ratio** (cash earnings quality)
- Rationale: Indian investors over-price accrual-based earnings; punish when cash flow doesn't match → signal is in the cash flow quality direction, not the accruals direction

---

### 2.6 Value Factor — Cyclical, Regime-Dependent

**Post-2020 evidence:**
- Value underperformed badly 2018–2022 in India (as globally); recovered strongly 2022–2024 as rates rose
- PSU banks (classic deep-value) went from PE 3–4× in 2020 to PE 8–12× by 2024 — a once-in-a-decade re-rating
- HML in India is heavily correlated with interest rate cycles: rising rates → value outperforms growth

**Construction:**
- P/B ratio: standard, works but cyclical
- E/P (earnings yield): better; accounts for earnings quality
- EV/EBIT: preferred by practitioners (avoids leverage games; cross-company comparable)
- Combined value: equal-weight of B/P + E/P + CF/P (cash flow yield)

---

### 2.7 Investment Factor (CMA) — Weak But Present

**Five-factor model (NSE 500, 2025):** CMA statistically significant, but in India the investment factor faces:
- Family-controlled businesses over-invest without market discipline → signal noisier
- Capital misallocation by promoters is common in India — `q`-factor logic weaker

**Practical signal:** Use CMA as a filter, not a standalone factor. Screen out heavy capex companies unless profitability is commensurate (ROE adjusted for growth capex).

---

## 3. Post-Earnings Announcement Drift (PEAD)

**Key papers:**

| Study | Sample | Finding |
|---|---|---|
| SCIRP/Researchgate (2018) | NSE, 2002–2017 | PEAD statistically significant, robust across sub-periods; persists after controlling for beta, size, P/B, illiquidity, idiosyncratic vol |
| Dsouza & Mallikarjunappa (2016) | BSE 500 event study | Market fails to absorb publicly available information quickly; future returns forecastable from earnings surprise |

**Signal construction (without I/B/E/S):**
```python
# Proxy for earnings surprise: Standardized Unexpected Earnings (SUE)
# computed from company quarterly filings (NSE/BSE announcements)

# Step 1: compute implied consensus = seasonal random walk
# (this quarter's EPS = same quarter last year's EPS)
implied_consensus = eps.shift(4)  # 4 quarters ago
actual_eps = eps  # this quarter (from NSE corporate filings)
earnings_surprise = (actual_eps - implied_consensus) / price_before_announcement

# Step 2: PEAD position
# Long top surprise quartile, hold 30–60 days
# Short bottom surprise quartile (if F&O available)

# Practical note: focus on Nifty 200–500 range
# - Nifty 50: too efficiently priced, PEAD arbitraged quickly
# - Below Nifty 500: too illiquid to execute profitably
```

**Binding constraint:** Execution on mid-cap earnings trades requires entering within 1–2 days of earnings release at tight spreads. Limit orders in Nifty 200–500 stocks may not fill at modelled price; use VWAP execution.

---

## 4. IPO and Listing Aftermarket

### 4.1 Grey Market Premium (GMP) Signal

**Evidence:**
- 270 IPOs study: **Spearman rank correlation of 0.886** between GMP and listing day returns
- JAAFR (2025 mainboard IPOs): GMP positive correlation with listing performance (r = 0.497, p < 0.001)
- TPREF (2025): GMP increasingly efficient as grey market has matured (digital adoption curve); high GMP now partially crowded for listing gain trades

**Signal construction:**
```
Data: chittorgarh.com, ipowatch.in, mainboardgmp.com (free, updated daily)
Signal: GMP > 40% of issue price AND subscription > 50× → strong listing gain candidate
Risk: GMP can collapse 48 hours before listing if market deteriorates
Exit: Apply for allotment; sell on listing day open (not close)
Capacity: Limited to retail allotment (₹2–15 lakh per application)
```

**Systematic approach:** Track all mainboard IPOs; apply formula-based allotment decisions. Not a large-AUM strategy — purely retail-scale.

### 4.2 Lock-Up Expiry Short Signal

**SEBI schedule (post-2022):**
- Promoter lock-in: 18 months
- Pre-IPO investors (VC/PE, >1 year holding): **6 months** — most actionable
- Anchor investors: 30 days only

**Market evidence:**
- Bloomberg (2025): ~$4 billion in lockup expirations early 2025 added visible downward pressure (BrainBees/FirstCry, Ola Electric notable cases)
- US parallel: Field & Hanka (2001, *JF*) — 1–3% negative return around lockup expiry

**Implementation:**
```
Monitor: SEBI SHP + IPO prospectus (available on SEBI EDGAR / DRHP filings)
Calendar: NSE corporate actions calendar for IPO date → compute 6-month + 18-month expiry
Signal: Short via F&O (where available on stock) 2–3 weeks before VC/PE lockup expiry
Exit: Cover within 5 days of expiry date
Best candidates: Recent large IPOs with significant PE/VC shareholding (>20% of float)
```

---

## 5. Options Market Signals

### 5.1 India VIX — Variance Risk Premium

**Data:** NSE publishes India VIX daily since March 2008.
Download: `nseindia.com` → Historical Data → VIX

**VRP construction:**
```python
india_vix = pd.read_csv('india_vix.csv')  # from NSE
nifty = pd.read_csv('nifty_close.csv')

# Realized vol (30-day close-to-close)
nifty_returns = nifty['close'].pct_change()
realized_vol = nifty_returns.rolling(21).std() * np.sqrt(252) * 100  # annualised %

# VRP = India VIX - realized vol
vrp = india_vix['vix'] - realized_vol

# Harvest signal:
# Short monthly Nifty ATM straddle when VRP > 5 vol points (implied expensive)
# Position size: target fixed premium received; stop at 2× premium received
```

**Evidence:** VRP in India averages +3–5 vol points (implied consistently above realized). Monthly straddle sellers profitable ~65–70% of months. Catastrophic risk in crisis months (March 2020: −10 to −15× premium in worst case).

**Practical execution (Indian retail-friendly):**
- Sell Nifty 50 weekly ATM straddle (Thursday expiry) — extremely liquid
- Delta-hedge if large directional move
- Max risk: 2× premium received (hard stop via stop-limit order)

### 5.2 Put-Call Ratio (PCR)

**Data:** `niftytrader.in/nifty-put-call-ratio`, `niftyinvest.com/put-call-ratio/NIFTY`

**Interpretation:**
- PCR < 0.7 → contrarian bearish (too many calls = excessive optimism)
- PCR > 1.5 → contrarian bullish (excessive fear/put buying)
- Normal range for Nifty: 0.85–1.15

**Limitation:** As standalone signal, signal-to-noise is poor. Works best as a multi-signal sentiment overlay alongside India VIX and OI distribution analysis.

### 5.3 Max Pain

**Theory:** Strike where total P&L to option buyers is minimized = where market makers benefit most from expiry. "Gravitational pull" in final sessions before expiry.

**Evidence:** 60–70% alignment between max pain and Nifty expiry in calm weeks; breaks completely on event weeks (RBI policy, Fed decisions, election results).

**Tracking:** `niftyinvest.com/max-pain/NIFTY`, `stockmojo.in/max-pain/nifty`

**Practical use:** Prefer to sell premium near max pain strikes in non-event weeks. Do not use as directional timing signal.

---

## 6. Macro Signals for India Sector Rotation

### 6.1 GST E-Way Bills

**Source:** `ewaybillgst.gov.in` (monthly totals); CEIC aggregates at `ceicdata.com/en/india`

**Signal:** Monthly YoY growth in e-way bills generated → leading indicator for:
- FMCG/consumer discretionary: direct demand signal
- Logistics: freight movement leading indicator
- Auto ancillary: component movement proxy

**Lag:** Data released ~7–10 days after month-end. May 2026: fourth-highest ever. Jan 2025: 136.83M bills, +42.6% YoY.

### 6.2 Auto Sales Monthly Data

**Sources:**
- SIAM wholesale: released 10th–15th of following month
- FADA retail: released slightly later

**Sector mapping:**
| Segment | Key Stocks |
|---|---|
| PV (passenger vehicle) | Maruti, M&M, Tata Motors |
| 2-Wheeler | Hero MotoCorp, TVS, Bajaj |
| CV (commercial vehicle) | Ashok Leyland, Tata Motors — most cyclically sensitive |

**Signal:** 3-month rolling YoY growth in PV sales. CV growth is the best GDP proxy.

### 6.3 PMI Data

**Sources:**
- India Manufacturing PMI: S&P Global Markit, ~1st of each month
- India Services PMI: ~3rd of each month
- Historical: `tradingeconomics.com/india/manufacturing-pmi`

**Sector rotation logic:**
```
PMI accelerating (rising) → overweight industrials, metals, auto, BFSI
Services PMI accelerating → overweight IT, consumer discretionary, financials
Composite PMI < 50 → defensive rotation (FMCG, pharma, utilities)
```

**Note:** India Manufacturing PMI has been continuously >50 since mid-2021. Rate of change is more informative than level.

---

## 7. Factor Replication Failures in India

Based on Hanauer & Lauterbach (2019, *EM Review*, SSRN 3233614) and India-specific studies:

| Factor | Status in India | Evidence |
|---|---|---|
| Pure Size (SMB) | **VERY WEAK** — 0.36% annualised | Agarwalla et al. 2017 |
| Accruals (Sloan US version) | **DOES NOT REPLICATE** — sign different | Sehgal et al. SSRN 2128978 |
| Standard HML (book P/B) | **WEAKENING** — risk-explained, not alpha | Sharma et al. 2021 |
| BAB (Betting Against Beta) | **MODERATE** — works but weaker than US | Raju data library |
| Short-term reversal (1-week, close-to-close) | **ABSENT** — only in overnight/intraday windows | Practitioner analysis |
| Volume/turnover anomaly | **FADED** substantially post-2016 | Sharma et al. 2021 |

| Factor | Status in India | Evidence |
|---|---|---|
| Momentum (12-1, 52-week high) | **STRONG** — 17% annualised, most robust | Agarwalla 2017, Raju 2023 |
| Profitability (RMW via ROE) | **SIGNIFICANT** — five-factor model confirmed | Zenodo 2025, Kedia 2024 |
| PEAD | **SIGNIFICANT** — robust across sub-periods | SCIRP 2018, Dsouza 2016 |
| GMP-to-listing gain | **STRONG** correlation (~0.7–0.9 Spearman) | Multiple 2025 studies |
| Promoter pledging → crash risk | **DOCUMENTED** | Chauhan IIMB 2020, BSE 500 study 2024 |

**Key academic reference:** Sharma, Subramaniam & Sehgal (2021, Sage): "Are Prominent Equity Market Anomalies in India Fading Away?" — value and momentum anomalies now risk-explained in many tests; size and volume anomalies significantly weakened. Dataset through 2016; post-SIP-boom data likely shows further convergence to efficiency.

---

## 8. Transaction Costs — Full Breakdown

### 8.1 Statutory Charges

| Charge | Rate | Applied To |
|---|---|---|
| STT — Delivery (buy) | 0.1% | Traded value |
| STT — Delivery (sell) | 0.1% | Traded value |
| STT — Intraday (sell only) | 0.025% | Traded value |
| STT — F&O Futures (sell) | 0.02% | Futures turnover |
| STT — F&O Options (sell) | 0.1% | Options premium |
| Stamp Duty — Delivery (buy) | 0.015% | Traded value |
| Stamp Duty — Intraday (buy) | 0.003% | Traded value |
| SEBI Turnover Fee | ₹10/crore = 0.0001% | Total turnover |
| NSE Transaction Charge | ~0.00297% | Delivery equity |
| GST | 18% | On brokerage + exchange charges |

### 8.2 All-In Round-Trip Cost Estimates

| Strategy Type | Estimated Round-Trip Cost |
|---|---|
| Nifty 50, equity delivery, monthly rebalance | ~0.22–0.25% statutory + 0.02–0.05% spread = **~0.25–0.30%** |
| Nifty 200, equity delivery, monthly rebalance | ~0.25% statutory + 0.10–0.15% spread = **~0.35–0.40%** |
| Nifty 500, equity delivery, monthly rebalance | ~0.25% statutory + 0.30–0.60% spread = **~0.55–0.85%** |
| Nifty F&O futures, intraday | ~0.04–0.06% round-trip |
| Nifty 200, intraday equity, daily signal | ~0.10–0.20% per trade = **20–40% annual drag** at 100% daily turnover |

**Critical threshold:** Factor strategy on Nifty 500, monthly rebalancing, 200% turnover/year → ~1–1.7% annual transaction cost. Needs **gross alpha > 3–5%** just to break even on costs.

### 8.3 Bid-Ask Spreads by Universe

| Universe | Typical Bid-Ask Spread | Market Impact (₹1 crore order) |
|---|---|---|
| Nifty 50 (large-cap top quartile) | 0.02–0.05% | < 0.05% |
| Nifty 100–200 (upper mid-cap) | 0.05–0.15% | 0.05–0.15% |
| Nifty 200–500 (lower mid-cap) | 0.15–0.40% | 0.30–1.0% |
| NSE 500–1000 (small-cap, listed 3y+) | 0.40–1.5% | 1–5% |
| SME / illiquid small-cap | 2–10%+ | Significant |

---

## 9. Comprehensive Data Source Map

### Free / Public Sources

| Source | URL | Data Available |
|---|---|---|
| NSE Historical Data | `nseindia.com` → Data & Reports | EOD prices, delivery, bulk/block deals, FII/DII, SHP, corporate actions |
| NSE FII/DII | `nseindia.com/reports/fii-dii` | Daily institutional flows, 2003+ |
| NSE Insider Trading | `nseindia.com/companies-listing/corporate-filings-insider-trading` | PIT disclosures, 2015+ |
| BSE Insider Trading | `bseindia.com/corporates/Insider_Trading_new.aspx` | PIT disclosures, BSE-listed |
| IIMA Factor Library | `faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/` | Monthly factors, Jul 1993+ |
| Rajan Raju Library | SSRN 5008269 (download link in paper) | Monthly factors incl. BAB, Low-Vol |
| India VIX | `nseindia.com` → Historical Data | Daily VIX, March 2008+ |
| RBI DBIE | `data.rbi.org.in/DBIE/` | Interest rates, credit, forex, CPI, WPI, BoP |
| jugaad-data (Python) | `pip install jugaad-data` | NSE EOD stock+F&O, RBI rates |
| NSEPython | `pip install nsepython` | Live + historical; bulk deals; corporate data |
| BseIndiaApi | `github.com/BennyThadikaran/BseIndiaApi` | BSE announcements, corporate actions |
| InsiderScreener | `insiderscreener.com/en/india/insider-trading/` | Aggregated PIT disclosures, filterable |
| Screener.in | `screener.in` | Fundamentals P&L/BS/CF, ~5,000 stocks |
| Trendlyne | `trendlyne.com` | Bulk/block deals, IPO data, screener; freemium |
| StockInsights.ai | `docs.stockinsights.ai` | AI-tagged BSE/NSE announcements |
| GMP trackers | `chittorgarh.com`, `ipowatch.in` | IPO grey market premium; free |
| GlobalDairyTrade | `globaldarytrade.info` | Dairy auction results (free; biweekly) |
| SEBI EDGAR | `sebi.gov.in/curation/corporate_filings.html` | Annual reports, rights issues, QIPs |
| MCA21 | `mcaservices.gov.in/MCA21` | Company filings, CHG-1 charges, director changes |

### Paid / Institutional Sources

| Source | Cost (Indicative) | Notes |
|---|---|---|
| CMIE Prowess DX | ~₹2–5 lakh/year (academic) | Gold standard; 1990+; 50,000+ companies; used by IIMs for IIMA library |
| Refinitiv Datastream | $30,000–$80,000/year | Used by Rajan Raju; I/B/E/S estimates included |
| Bloomberg Terminal | ~$24,000/year per seat | BEst estimates, BFV yields, analytics |
| TrueData | ₹3,000–15,000/month | Low-latency India data API; retail-quant friendly |
| NSE Data & Analytics (NDAL) | ₹5–20 lakh/year (tick data) | Real-time + historical tick; F&O greeks |
| ACE Equity / Capitaline | ₹50,000–3 lakh/year | Comparable to CMIE; BSE/NSE fundamentals |
| tofler.in / accumn.ai | ₹500–2,000/company | Structured MCA21 data |

---

## 10. Strategy Prioritisation — Updated

### Tier 1: Deployable with Free Data

| Strategy | Expected Gross Sharpe | Net Sharpe (est.) | Rebalance | Universe |
|---|---|---|---|---|
| Momentum 12-1 (52-week high variant) | 1.5–2.0 | 1.0–1.5 | Quarterly | Nifty 200 |
| Quality-Momentum combined | 1.0–1.5 | 0.7–1.2 | Quarterly | Nifty 500 |
| PEAD (earnings surprise drift) | 1.0–1.5 | 0.6–1.0 | Event-driven | Nifty 200–500 |
| India VIX VRP harvest (short straddles) | 1.0–1.5 | 0.7–1.2 | Monthly expiry | Nifty index options |

### Tier 2: Promising, Needs Backtesting

| Strategy | Data Needed | Key Risk |
|---|---|---|
| Promoter bulk buy post-drawdown | NSEPython (free) | ESOP filtering, announcement lag |
| FPI/DII divergence signal (contrarian Nifty) | NSE FII/DII (free) | Works best at extremes; false signals in trending markets |
| SHP FPI accumulation overlay | NSE SHP (free) | Quarterly lag; slow signal |
| Promoter pledging short screen | SEBI SHP (free) | Need F&O availability on specific stocks |
| Lock-up expiry short (6-month VC/PE) | IPO prospectus (free) | Limited F&O availability on smaller IPOs |

### Tier 3: Research Gap — No Systematic Backtest Published

| Strategy | Data Needed | Why Interesting |
|---|---|---|
| Bulk/block deal insider buy signal | NSEPython (free) | No published peer-reviewed backtest; potentially significant |
| PEAD proxy via SUE from company filings | NSE corporate announcements (free) | No I/B/E/S required if built from filing data |
| MCA21 charge filing early warning | tofler.in (paid, ~₹1k/company) | Pre-dates balance sheet stress by 1–2 quarters |
| GMP-to-listing allotment strategy | GMP trackers (free) | Documented correlation but capacity-constrained |
| Analyst revision proxy from sell-side filings | SEBI research analyst portal | Untapped public data source |

---

*v2 adds SEBI regulatory data signals (bulk deals, PIT disclosures, pledging, SHP), full factor evidence with replication failures, IPO signals, options market signals, macro rotation signals, complete data source map with URLs, and precise transaction cost breakdown. Momentum on Nifty 200 (52-week high variant, quarterly rebalance) and PEAD are the highest-confidence deployable signals.*
