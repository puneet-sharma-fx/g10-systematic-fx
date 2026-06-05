# Indian Equities: Quantitative Strategy Scoping Document

Systematic factor strategies for NSE/BSE-listed Indian equities. Covers what works, what data is available publicly, market microstructure constraints, and implementation priorities.

---

## Executive Summary

India's equity market exhibits most global factor premia — **momentum is the strongest** (net Sharpe ~0.5–1.0+ in backtests), **low volatility is the best risk-adjusted** (Sharpe 0.47 vs 0.32 for Nifty 50 over 18 years), value is cyclical and unreliable as a standalone, quality is practitioner-adopted but less academically formalised. Three India-specific signals — FII flows, promoter shareholding changes, and options PCR — have directional logic but weak academic formalisation.

**Key structural differences from US/Europe:**
- Short-selling is effectively constrained (F&O only for overnight shorts; direct equity SBL market is thin)
- STT (Securities Transaction Tax) of 0.1% each side on delivery — major cost drag on frequent rebalancing
- Circuit breakers on individual stocks (±5–20% daily limits) create execution trap risk in mid/small caps
- Long-only implementations capture more of the premium than in markets with frictionless shorting (consistent with Stambaugh/Yu/Yuan 2012 on sentiment and the short leg)

---

## 1. Factor Evidence in India

### 1.1 Momentum — Strongest Documented Factor

**Construction.** Cross-sectional momentum using 12-month trailing return, skipping most recent month (12-1 standard). Universe: Nifty 500 or top-500 stocks by market cap. Rank all stocks; go long top quintile, rebalance monthly or semi-annually.

**Volatility-adjusted variant (recommended).** Normalise each stock's 12-1M return by its trailing 12-month daily return volatility:
```
MomScore[i,t] = Return[i, t-12M:t-1M] / RealVol[i, t-12M:t]
```
This is what the NSE's official **Nifty 500 Momentum 50 Index** uses.

**Evidence.**
- NSE Nifty 500 Momentum 50 Index: live since 2021; backtested CAGR materially above Nifty 500 benchmark.
- Raju (SSRN 4687044, 2024): monthly rebalancing captures momentum more effectively than quarterly or annual in India. Improved Sharpe, lower drawdown vs Nifty.
- Raju (SSRN 4977717, 2024): Volatility-adjusted and information-discreteness momentum > raw price momentum in India.
- Arxiv 2302.13245: 2–12 month formation momentum portfolios outperform Nifty; portfolio VaR 25% lower than Nifty.
- ScienceDirect (2023): Standard Jegadeesh-Titman pattern confirmed in India — 1-month reversal, 2–12M momentum, 36M+ reversal.

**Post-publication decay.** NSE launched live momentum indices 2021–2022; crowding risk increasing. No systematic decay documented yet.

**Formation/holding recommendation.** 12-1 skip-month, monthly rebalance. Use volatility-adjusted scoring.

**Data.** yfinance `.NS` suffix; NSEpy; NSE historical index data.

---

### 1.2 Low Volatility — Best Risk-Adjusted Return

**Construction.** Rank Nifty 500 universe by trailing 12-month realised volatility (daily returns). Long bottom quintile (lowest volatility), equal-weight, annual rebalance.

**18.5-year NSE backtest (backtestindia.com, Dec 2006 – Jun 2025, top-100 by market cap, 30 stocks):**

| Metric | Low-Vol Strategy | Nifty 50 Benchmark |
|---|---|---|
| CAGR (gross) | 12.85% | 10.42% |
| CAGR (net after tax/costs) | 12.38% | 10.42% |
| Annual Volatility | 16.70% | 20.78% |
| Max Drawdown | −44.46% | −55.12% |
| **Sharpe Ratio** | **0.47** | **0.32** |
| Recovery from max DD | 7 months | 60 months |
| 10-year rolling win rate | 102/102 (100%) | — |

**Why it works in India.** BAB mechanism (Frazzini-Pedersen 2014, JFE) — Indian retail investors tilt toward high-beta, volatile stocks seeking lottery-like payoffs. This excess demand overprices high-volatility stocks. Low-vol stocks are systematically underpriced relative to their risk-adjusted fundamentals.

**Additional evidence.**
- Raju (SSRN 4398656): Low-risk anomaly confirmed across 4,400-company universe over 19 years using multiple risk measures (vol, beta, idiosyncratic vol).
- Joshipura (SSRN 2672764): Confirmed in S&P CNX 200, 2004–2013.
- NSE live index: Nifty100 Low Volatility 30, Nifty Low Volatility 50 — investable live products.
- Multiple mutual funds track these indices (DSP, Nippon India, Motilal Oswal).

**Data.** yfinance `.NS`; NSE historical data.

**Cost.** Annual rebalance = minimal STT drag (two legs per year per stock = 0.2% STT + brokerage).

---

### 1.3 Quality — Strong Practitioner Adoption, Academic Support

**Construction.** Composite of three sub-signals:
1. **Profitability**: ROE or ROCE (higher = better)
2. **Balance sheet**: Debt-to-equity ratio (lower = better; invert when scoring)
3. **Earnings stability**: Standard deviation of EPS growth over 3–5 years (lower = better; invert when scoring)

NSE **Nifty200 Quality 30 Index** uses exactly this triplet — the industry standard.

**Why India-specific.** Corporate governance is weaker than developed markets. The spread between high-quality and low-quality companies (cash conversion, earnings manipulation, related-party transactions) is wider in India — making the quality signal more informative.

**Forensic accounting extension (Marcellus MeritorQ approach).** Check for:
- Unusually smooth receivables growth relative to revenue growth
- Consistently low cash taxes relative to book taxes
- High accruals relative to cash earnings
These are signs of earnings manipulation that quality alone misses.

**Evidence.**
- Raju (SSRN 4190426): Profitability factor (RMW — robust minus weak operating profitability) statistically significant in India, consistent with Fama-French 5-factor global evidence.
- Wright Research: Quality is one of the four strongest factors in India (alongside earnings momentum, price momentum, size).
- WhiteOak Capital (Jan 2025): India's first "actively managed quality factor fund" using ROE, D/E, earnings stability, FCF.
- BacktestIndia: Quality-Momentum combined CAGR **17.95%**, Sharpe **0.86** — the best single documented combination for India.

**Data.** Screener.in (free CSV export of P/E, P/B, ROE, ROCE, D/E, EPS growth for all NSE stocks); Tijori Finance (paid, more detailed); yfinance for prices.

---

### 1.4 Value — Positive Long-Term, Cyclically Unreliable

**Construction.** Rank by P/B (book-to-market), P/E (earnings yield), or composite value score. NSE Nifty500 Value 50 uses composite.

**Evidence in India.**
- Raju (SSRN 4054146): Value (HML) statistically significant in India but weaker than in US. Suffered during growth-led bull markets 2017–2021.
- Capitalmind NSE strategy index analysis: Value indices show high variance — excellent in some sub-periods, poor in others.
- Sharma et al. (2021): Value anomaly present but declining in NSE 500 (2005–2016).

**Recommendation.** Value works best combined with quality (avoid "value traps" — cheap stocks that are cheap for a reason). Standalone value factor has too much cyclical variance for systematic use.

---

### 1.5 Size — Weak, Liquidity-Constrained

**Evidence.** Negative returns in recent sample periods (RRJOURNALS). Consistently weak in Raju's multi-factor models (SMB factor small coefficient).

**Practical problem.** India's small-cap universe has many stocks with daily turnover under ₹1 crore. Execution impact dominates any factor signal for portfolios above ~₹50–100 crore AUM. The size premium, if real, is concentrated in untradeable illiquid names.

**Recommendation.** Restrict universe to **Nifty 500 or top-500 by ADV** (average daily volume). Ignore the size premium as a standalone signal.

---

## 2. India-Specific Signals

### 2.1 FII / DII Daily Flows

**Data.** NSE India publishes daily FII/DII net buy/sell data at nseindia.com/reports/fii-dii. Released ~6:30–7:00 PM IST after market close. Free to download. Historical archives available.

**Signal logic.** FII net buying → positive; sustained 3-week net selling → negative for Nifty.

**Documented behavior.**
- Sustained FII selling over 3+ consecutive weeks → Nifty 50 drawdowns of 3–8%.
- DIIs act as structural counterbalancing force (retail SIP inflows).
- ScienceDirect India momentum paper: net FII inflows are a significant predictor of momentum return generation (momentum amplifier, not standalone directional signal).

**Evidence quality.** ⚠️ Practitioner-level; no rigorous peer-reviewed paper isolated FII flow predictive power at 1-day/1-week horizon.

**Recommended use.** Use as a position-sizing filter: reduce long equity exposure when 20-day rolling FII net flow is negative. Do not use as a directional signal alone.

**Construction.**
```python
# Rolling 20-day FII flow signal
fii_signal = fii_net_flow.rolling(20).sum()
position_scalar = np.clip(np.sign(fii_signal), 0, 1)  # long-only: 0 or 1
```

---

### 2.2 Promoter Shareholding Changes

**Data.** SEBI requires quarterly shareholding pattern disclosure (within 21 days of quarter-end). Available at BSE India, NSE India, and aggregated by Trendlyne.com and Screener.in.

**Signal.** Promoter increasing stake > 1% in a quarter → positive signal (insiders buying). Promoter decreasing stake or pledge increasing → negative.

**Why strong in India.** Promoters are controlling shareholders with full information access. "Creeping acquisition" rule allows promoters above 25% to buy up to 5%/year — creates a systematic buy signal.

**Evidence quality.** ⚠️ Widely used by discretionary PMs in India; no rigorous peer-reviewed backtest published.

**Data pipeline.** Quarterly scraping from BSE/NSE XML filings or Trendlyne subscription. Not trivially automatable — requires data pipeline effort.

**Priority.** 🟡 Medium — strong logic but requires data pipeline build.

---

### 2.3 Options PCR (Put-Call Ratio)

**Data.** NSE option chain — free download in real time. Historical PCR available from NiftyTrader.in and OptionX.trade.

**Signal.** PCR > 1.4 → extreme fear → contrarian bullish. PCR < 0.7 → extreme call activity → bearish.

**Evidence quality.** ⚠️ Widely used practitioner tool; no rigorous academic backtest for India PCR. Best used as a sentiment/regime indicator rather than a primary signal.

**Max Pain.** Strike where option sellers profit most → gravitational target for Nifty near expiry. Used for expiry-day positioning only.

---

### 2.4 SEBI SAST / Bulk Deals / Insider Trading

**Data.**
- SAST filings: NSE/BSE within 2 trading days of threshold crossing (currently 2% for entities above 5% total holding)
- Bulk deals: single transactions > 0.5% of total shares, reported at end of day
- Block deals: large trades in 15-minute windows (8:45–9:00 AM, 2:05–2:20 PM), disclosed in real time

**Aggregators.** Trendlyne.com (best); SEBI at sebi.gov.in.

**Limitation.** SAST filings typically delayed T+2 to T+5. More useful for medium-term (1–4 week) signals than same-day execution.

---

## 3. Macro Signals for Indian Equities

| Signal | Best Instrument | Relationship | Data Source |
|---|---|---|---|
| RBI rate change (surprise vs consensus) | Bank Nifty, Nifty Realty | Rate cut → bullish; rate hike → bearish | RBI MPC minutes (rbi.org.in) |
| S&P 500 previous night close | Nifty 50 futures (GIFT Nifty) | US close predicts Nifty open with 75–85% directional accuracy | Yahoo Finance (^GSPC) |
| INR/USD | Nifty IT vs OMCs | Weak INR → IT outperforms; OMCs underperform | Yahoo Finance (USDINR=X) |
| WTI crude oil | ONGC vs OMCs | High crude → upstream wins, OMCs/FMCG/Paints lose | FRED DCOILWTICO |
| GIFT Nifty pre-market | Nifty 50 cash open | Best same-day directional indicator for Nifty open | NSE / Bloomberg (^NIFTY) |

---

## 4. Publicly Available Data Sources

| Source | Content | Cost | Key Use |
|---|---|---|---|
| **yfinance** (`.NS` / `^NSEI`) | Daily OHLCV for 5,000+ NSE/BSE stocks + indices | Free | Primary prices source. `yf.download("RELIANCE.NS")`. Nifty 50: `^NSEI` |
| **NSE India** (nseindia.com) | Historical index data, FII/DII flows, F&O OI, bulk deals, shareholding | Free | Official source for flows and market data |
| **Screener.in** | P/E, P/B, ROE, ROCE, D/E, EPS growth (10-year) for all NSE stocks | Free (CSV export) | Fundamental factor construction |
| **Rajan Raju Data Library** (SSRN 5008269) | Monthly Fama-French 5 factors + momentum for India, multiple universes, ~2000 to present | Free (SSRN download) | Academic factor benchmarking; the "CRSP of India" |
| **Trendlyne.com** | SAST, insider trading, bulk deals, shareholding changes, PCR history | Freemium | Best aggregator for SEBI disclosure signals |
| **RBI DBIE** (database.rbi.org.in) | Repo rate history, CPI, WPI, IIP, INR/USD | Free | Macro signals for equity strategies |
| **NSEpy** (Python) | NSE equity + derivatives + index historical data | Free/open source | Python pipeline for NSE data |
| **EODHD Financial APIs** | NSE/BSE OHLCV including delisted stocks, 20+ year history | Paid ($20–80/month) | Survivorship-bias-free backtesting |
| **CMIE Prowess** | Comprehensive fundamentals, 20+ year history, delisted companies | Paid (~₹2–5L/year) | Used in most published India academic papers |
| **Tijori Finance** | Detailed fundamentals, segment breakdowns | Freemium | Better than Screener.in for segment data |

**⚠️ Survivorship bias warning.** yfinance and Screener.in only cover currently listed stocks. For rigorous factor backtesting, delisted stocks must be included — use EODHD Financial APIs or Rajan Raju's data library for survivorship-bias-free factor research.

---

## 5. Market Microstructure — What Changes vs US/Europe

### 5.1 Transaction Costs (Critical)

**Securities Transaction Tax (STT) — post-October 2024 rates:**

| Instrument | Rate | Applied to |
|---|---|---|
| Equity delivery | 0.1% | Both buy and sell sides |
| Equity intraday | 0.025% | Sell side only |
| Equity futures | 0.02% | Sell side only |
| Equity options (premium) | 0.1% | Sell side |

**Full cost stack for monthly-rebalancing equity strategy:**
- STT: ~2.4%/year (delivery both sides, monthly rebalance)
- Brokerage: ₹20/order (Zerodha flat) or 0.01–0.1% per leg
- STCG tax: 20% on gains (positions < 1 year)
- LTCG tax: 12.5% on gains (positions > 1 year, from Budget 2024)
- SEBI/exchange fees: ~0.003–0.005% per side

**Implication.** Monthly rebalancing is expensive due to STT. **Semi-annual or annual rebalancing** dramatically reduces STT drag at the cost of slower signal response. Low-volatility (annual rebalance) is therefore significantly more cost-efficient than momentum (monthly rebalance).

**Compare to G10 FX.** No STT equivalent. The Indian equity cost hurdle for alpha is structurally higher.

### 5.2 Short Selling

- **Retail:** Intraday only (MIS orders, must cover same day). No overnight short equity positions.
- **Institutional:** Securities borrowing/lending (SBL) market exists via NSCCL, but is thin and expensive (1–5% annualised borrow for most names).
- **F&O:** Short futures or buy puts — the practical shorting mechanism. Cash settled for index; physically settled for single stocks.

**Implication for strategy design.** Long-short equity strategies must use F&O for the short leg or operate long-only. Long-only factor strategies capture more of the premium in India than in markets with frictionless shorting (consistent with Stambaugh/Yu/Yuan 2012: in India, overpriced stocks remain overpriced longer because shorting is constrained).

### 5.3 Settlement

- **T+1** mandatory for equities since January 2023 (phased from large-caps).
- **T+0** optional introduced 2024–2026 for select stocks.
- Benefit: Capital released faster, supports more frequent rebalancing without tying up cash.

### 5.4 Circuit Breakers

- **Index-wide halts:** 10% move → 45 min halt (before 1 PM); 15% → 1h 45m; 20% → rest-of-day.
- **Stock-specific price bands:** ±5%, ±10%, or ±20% daily limits (most mid/small caps). Stocks in F&O have no individual circuit filter.
- **Execution trap risk.** A mean-reversion or stop-loss strategy on mid/small caps can get trapped at the circuit limit with no ability to exit. This is a real risk with no US analog.

---

## 6. Strategy Prioritisation for a Public-Data Researcher

| Rank | Strategy | Instrument | Data | Evidence | Cost | Priority |
|---|---|---|---|---|---|---|
| **1** | **Low-volatility** (annual rebalance, Nifty 500 top 100) | Direct equity delivery | yfinance `.NS` | Strong (18y backtest, academic papers) | Low (annual rebalance minimises STT) | 🔴 First |
| **2** | **12-1 momentum** (monthly or semi-annual, Nifty 200) | Direct equity delivery | yfinance `.NS` | Strong (NSE live index, Raju papers) | Medium | 🔴 First |
| **3** | **Quality-Momentum composite** (ROE + ROCE + price momentum) | Direct equity delivery | yfinance + Screener.in | Moderate-strong | Medium | 🟡 Second |
| **4** | **Nifty index momentum via futures** (3M return signal, Nifty futures) | Nifty index futures | NSE F&O data (free) | Moderate | Low (cash settled) | 🟡 Second |
| **5** | **FII flow filter** (long Nifty when 20d FII net positive) | Nifty ETF or futures | nseindia.com FII reports | Weak-moderate | Very low | 🟢 Third |
| **6** | **Sectoral rotation** (IT vs Banks via INR/crude signals) | Nifty sectoral ETFs | yfinance + FRED | Moderate (macro channel documented) | Low | 🟢 Third |
| **7** | **Promoter-change signal** | Individual stocks | Screener.in + Trendlyne | Weak (no rigorous backtest) | Medium (pipeline effort) | 🔵 Later |

---

## 7. Key Academic References

| Paper | SSRN/Source | Key Finding |
|---|---|---|
| "Timing the Tide" — Rajan Raju | SSRN 4687044 | Monthly rebalance captures momentum more effectively |
| "Shades of Momentum" — Rajan Raju | SSRN 4977717 | Volatility-adjusted > raw price momentum in India |
| "Low-Risk Anomaly: Evidence from India" — Rajan Raju | SSRN 4398656 | Low-risk anomaly across 4,400 companies, 19 years |
| "Four and Five-Factor Models in India" — Rajan Raju | SSRN 4054146 | HML and RMW significant; CMA weaker |
| "Momentum, Reversals, Liquidity: Indian Evidence" | ScienceDirect 2023 | Standard J-T pattern confirmed in India |
| "Are Prominent Anomalies in India Fading?" — Sharma et al. | SAGE 2021 | Anomalies present but declining 2005–2016 |
| "Risk Anomaly — Empirical Evidence from India" — Joshipura | SSRN 2672764 | Low-risk anomaly in S&P CNX 200 |
| Low Volatility Anomaly India — 18-year backtest | backtestindia.com | SR 0.47 vs Nifty 0.32; 100% 10-year win rate |
| NSE Multi-Factor Indices Whitepaper | NSE / nseindia.com | Nifty200 Momentum 30 spent 64%+ of time in top quartile |
| September 2024 Factor Library Update — Rajan Raju | SSRN 5008269 | Full factor data for 5,447 firms; expanded universes |

**Start here:** Download Rajan Raju's data library from SSRN (SSRN 5008269) — monthly FF5 factors + momentum for India. This is the benchmark for any India factor replication work.

---

## 8. India vs Developed Markets: Summary Differences

| Dimension | India | US/Europe |
|---|---|---|
| Short selling | F&O only (overnight); SBL thin/expensive | Freely available; deep SBL |
| Transaction tax | STT 0.1% each side (delivery) | None (US); UK stamp duty 0.5% buy-side only |
| Settlement | T+1 mandatory; T+0 optional | T+1 (US since May 2024) |
| Stock price limits | ±5–20% daily circuit filters | No daily limits (index breakers only) |
| F&O settlement | Physical delivery (single stocks); cash (index) | Cash settled (standard) |
| Promoter structure | Controlling families own 40–75% most cos | Diffuse ownership |
| Forensic accounting | Related-party transactions prevalent | Less prevalent; SEC enforcement stronger |
| Data (free) | Survivorship bias severe; yfinance + Screener.in | CRSP/Compustat via WRDS for academics |
| Key academic dataset | Rajan Raju SSRN data library | Ken French Data Library |
| Best factor evidence | Momentum > Low-Vol > Quality > Value | Momentum > Value > Quality > Low-Vol |

*Last updated: June 2026*
