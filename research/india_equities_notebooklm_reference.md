# Systematic Equity Investing in India: A Comprehensive Reference for Quant Research

*Prepared June 2026 — NotebookLM Reference Document*
*Author: Puneet Sharma | Universe: NSE/BSE India | Intended Use: Self-contained learning and strategy research*

---

## How to Use This Document

This document is designed to be fully self-contained. Every concept is explained from first principles, every claim is sourced, and every strategy includes implementable construction details. It is divided into ten sections that progress from market structure → factors → signals → implementation. Mathematical notation uses standard LaTeX-style inline expressions. Code examples use Python 3.x.

---

# Section 1: Indian Equity Market Structure and History

## 1.1 The Two Exchanges: NSE vs. BSE

India operates two major national stock exchanges that compete directly for order flow and listings.

**Bombay Stock Exchange (BSE)** is Asia's oldest exchange, founded in 1875 under a banyan tree in Mumbai. It lists over 5,000 companies. Its flagship index is the **Sensex** (S&P BSE Sensex), a 30-stock price-weighted index. BSE has historically dominated SME listings but lost significant derivatives market share to NSE.

**National Stock Exchange (NSE)** was founded in 1992 as a technology-first, demutualised exchange. It introduced electronic order-matching, ending the era of open-outcry trading. NSE now handles approximately 70–75% of India's equity cash market volume and dominates the derivatives market. Its flagship indices are the **Nifty 50** (50 stocks, free-float market-cap weighted) and the **Nifty 500** (500 stocks, representing approximately 92–94% of total listed market capitalisation on NSE). The Nifty 500 is the standard quant research universe for India.

**Sub-universes relevant to quant strategies:**

| Index | Composition | Typical Use |
|---|---|---|
| Nifty 50 | Top 50 by free-float market cap | Macro signals, most liquid derivatives |
| Nifty Next 50 | Ranks 51–100 | Liquid large-caps with more alpha potential |
| Nifty 100 | Top 100 | Broad large-cap factor portfolios |
| Nifty 200 | Top 200 | Recommended universe for deployable factor strategies |
| Nifty 500 | Top 500 | Full academic universe; best coverage of size/value effects |
| BSE SmallCap / NSE SmE IND | Ranks 501+ | Illiquid premium research only; not deployable at scale |

**SME (Small and Medium Enterprise) segment:** NSE Emerge and BSE SME are dedicated platforms for smaller companies. These operate under a market-maker model with compulsory market-making. They are *not* suitable for systematic quant strategies due to extreme illiquidity (trades of ₹1–5 lakh can move prices by 1–2%), thin disclosure standards, and circular trading risks. Exclude these from any systematic universe definition.

---

## 1.2 Settlement: T+1 and Its Implications

**History of Indian settlement:**
- Pre-2002: Weekly settlement (badla — a rolling futures system integrated into the cash market)
- 2002: Introduction of T+3 rolling settlement, abolition of badla
- 2003: Shortened to T+2 rolling settlement
- February 2022 – January 2023: **Phased rollout of T+1 settlement** on an opt-in basis
- January 27, 2023: All NSE/BSE securities moved to mandatory T+1 settlement

**What T+1 means:** Trades executed on day T settle on day T+1. The seller delivers securities by end of T+1; the buyer pays by end of T+1. India became the first major economy to implement universal T+1 equity settlement.

**Implications for quant strategies:**

1. **Faster capital recycling:** Proceeds from a sale on Monday are available by Tuesday, enabling daily rebalancing without waiting for settlement. This makes daily momentum rebalancing more feasible.

2. **FII friction:** Foreign portfolio investors (FPIs) invest in USD but settle in INR. Under T+1, FPIs must pre-fund INR or use currency hedges, because the settlement window is too narrow to execute FX after trade confirmation. This adds operational cost and contributed to FPI selling during the October 2024 correction. FPIs from the US face a particular challenge: the settlement window falls during US night hours.

3. **Short-selling constraint amplified:** With T+1, securities delivered before confirmation of settlement are immediately absorbed. This reduces the practical window for delivery-based short selling even further (see Section 1.4).

4. **Impact on rebalancing frequency:** Monthly rebalancing remains optimal for most factor portfolios. Daily rebalancing at scale faces transaction costs that erode most factor returns (see Section 9).

---

## 1.3 Index Construction and the SEBI 2018 Mutual Fund Re-Categorisation

In October 2017 (effective April 2018), SEBI issued a landmark circular on mutual fund categorisation. Prior to this, each asset management company (AMC) defined "large-cap," "mid-cap," and "small-cap" however it wished — a "mid-cap" fund at one AMC might hold stocks that another AMC classified as large-cap.

**Post-2018 SEBI definitions (by full market capitalisation ranking on NSE+BSE combined):**
- **Large-cap:** Companies ranked 1–100
- **Mid-cap:** Companies ranked 101–250
- **Small-cap:** Companies ranked 251 and below

This list is published semi-annually by AMFI (Association of Mutual Funds in India) and updated every six months.

**Critical implication for factor research:** Academic papers written before 2018 using "small-cap" as a category are not directly comparable to post-2018 research because the composition of small-cap changed substantially. Post-2018, institutional flows into formally-defined small-caps increased dramatically, compressing the illiquidity premium that previously showed up as an apparent size effect.

---

## 1.4 Short Selling: The Single Biggest Constraint for India Quant Strategies

**The fundamental rule:** India does not permit naked short selling in the cash equity market. The only mechanism to maintain an overnight short position is via **Futures and Options (F&O)**.

**What you *can* do:**
- Sell short intraday in cash market (must cover by end of day)
- Sell futures short (near-month, mid-month, far-month contracts on NSE)
- Buy put options or sell call options
- Use short-side of pair trades via futures

**What you *cannot* do:**
- Maintain overnight short positions in cash market securities without borrowing shares (Securities Lending and Borrowing [SLB] mechanism exists but is thin and expensive)
- Short stocks not in the F&O permitted list (approximately 180 stocks approved for F&O; the rest cannot be systematically shorted overnight)

**F&O short mechanism:** NSE permits shorting via the Futures segment. A short Nifty 50 futures position is straightforward and cheap. Individual stock futures exist for ~180 names. Outside these names, systematic short alpha is essentially inaccessible.

**SLB (Securities Lending and Borrowing):** NSE operates an SLB platform. In practice, it is illiquid — most securities trade zero volume in SLB for weeks at a time, and borrowing fees can be 5–20% annualised. This makes SLB unsuitable for systematic short strategies.

**Practical implication:** Most India quant strategies are **long-only** or **long + Nifty futures hedge** (market-neutral). Pure long-short factor portfolios (as constructed in academic papers) are not directly replicable for retail or small institutional investors. Large institutional investors (hedge funds with prime brokerage relationships) have better access to SLB.

---

## 1.5 Circuit Breakers: Constraints on Systematic Execution

India operates a two-tier circuit-breaker system. These are non-trivial constraints for any strategy that trades individual stocks.

**Market-wide circuit breakers (triggered by Nifty 50 or Sensex movement, whichever triggers first):**

| Movement | Duration of Halt | Post-Halt |
|---|---|---|
| ±10% | 45 minutes (before 1 PM); 15 minutes (after 1 PM but before 2:30 PM) | Pre-open call auction |
| ±15% | 1 hour 45 minutes (before 2 PM); Rest of Day (after 2 PM) | Pre-open call auction |
| ±20% | Trading halted for rest of day | Next day opens normally |

**Individual stock circuit breakers:** Stocks are assigned to circuit bands based on category, average trading volume, and institutional ownership:
- **±2%** band: Illiquid stocks, some SME segment
- **±5%** band: Less liquid NSE-listed stocks
- **±10%** band: Mid-cap stocks
- **±20%** band: Most liquid Nifty 200 stocks (and all F&O stocks)

When an individual stock hits its upper or lower circuit limit, trading pauses for that stock *only* — no broader market halt occurs unless a market-wide threshold is breached.

**Critical strategy implication:** A momentum portfolio concentrated in small-cap or mid-cap stocks (±5% or ±10% bands) faces a "stuck long" problem during market stress. If a portfolio stock hits the lower circuit at ±5%, you may be unable to exit for multiple consecutive days. This is not hypothetical — during March 2020, thousands of mid- and small-cap stocks hit lower circuits continuously for 8–10 trading sessions. Position sizing rules must account for this.

**Rule of thumb:** Only hold stocks in the ±20% circuit band (i.e., F&O eligible or Nifty 200) in any systematic strategy intended to be rebalanced monthly. Reserve ±10% and lower band stocks for very long-horizon (12+ month) portfolios where daily liquidity is not required.

---

## 1.6 Trading Sessions

| Session | Time (IST) | Purpose |
|---|---|---|
| Pre-open Call Auction | 09:00–09:15 AM | Price discovery; orders accumulate, matched at clearing price at 9:08 AM (random close within 9:08–9:12); results implemented at 9:15 AM |
| Normal Trading | 09:15 AM–03:30 PM | Continuous order matching |
| Post-Close Session | 03:40–04:00 PM | Closing price auction (weighted average of last 30 minutes trades) |
| After-Market Orders | 03:45–08:59 AM | Orders stored, released at 09:00 AM next day |

**The pre-open call auction matters for quant strategies:** The opening price for all Nifty 50 stocks is determined by the call auction. Institutional orders placed during 09:00–09:08 reveal information about overnight sentiment and order flow. Some practitioners use order imbalance during the pre-open as a very short-term signal. For factor portfolios, the key implication is that large rebalancing orders should typically be submitted as limit orders in the continuous session (not market orders in the pre-open), to avoid adverse execution.

---

## 1.7 Retail vs. Institutional Participation

**Historical context:** India has had one of the highest retail participation rates globally. Retail investors historically accounted for approximately 50–65% of total equity cash market volume on NSE. As of FY2025–26, retail's share of daily turnover is approximately 50–52%, with the remainder split between institutions (domestic + foreign) and proprietary trading desks.

**Retail equity account growth:** The number of demat (electronic) accounts grew from ~35 million in 2019 to over 185 million by March 2026, driven by COVID-era retail investing surge, Zerodha and discount broker democratisation, and SEBI's simplified KYC requirements.

**Why high retail participation matters for factor investing:**
1. **Slower price discovery:** Retail investors are less likely to trade on fundamental information or factor signals quickly, allowing factor mispricings to persist longer.
2. **Disposition effect at scale:** Indian retail investors heavily exhibit the disposition effect — holding losers too long and selling winners too early. This mechanically sustains momentum anomalies because recent winners are underowned by retail (who have sold) and more fundamentally-owned by institutions.
3. **Herding into narratives:** Indian retail investors cluster into narrative-driven stocks (defence, railways, PSU capex themes). This creates momentum-within-narrative and subsequent reversal, exploitable by contrarian factor portfolios.
4. **Anchoring to IPO prices:** Retail investors anchor to IPO prices. Stocks that fall below their IPO price see reduced retail selling (anchoring prevents stop-losses) but also reduced retail buying, creating information asymmetry exploitable via PEAD signals.

---

## 1.8 FII vs. DII Dynamics

**Key participants:**
- **FII/FPI (Foreign Portfolio Investor):** Foreign investors registered with SEBI. Hold approximately 16–18% of listed market cap. Primarily from US, UK, Singapore, Mauritius.
- **DII (Domestic Institutional Investor):** Primarily domestic mutual funds (particularly SIP-backed equity funds), insurance companies (LIC being the largest single participant), and bank treasuries.
- **Retail:** Direct equity investors and HNI.

**SIP structural floor:** Systematic Investment Plan (SIP) contributions from retail mutual fund investors have created a structural monthly demand floor. As of May 2026, SIP flows exceed ₹26,000–30,000 crore per month. This translates to approximately ₹1,200–1,400 crore of DII demand per trading day, deployed regardless of market direction (mutual funds must invest received SIP inflows promptly). This structural DII demand was a crucial shock absorber during:
- FPI selling of over ₹94,000 crore in October 2024 (Nifty fell ~8% despite DII buying absorbing ~60–70% of FII selling)
- COVID crash of March 2020 (DIIs deployed ₹55,000+ crore in March 2020)

**FII-DII divergence signal:** When FPIs are net sellers for 10+ consecutive trading days AND DIIs are net buyers at elevated rates, this has historically marked medium-term bottoms in Nifty 50 (see Section 4.4 for construction).

---

# Section 2: Why India Is Different from US and Global Markets

## 2.1 Structural Market Inefficiencies

India's equity market deviates from the efficient market hypothesis more persistently than developed markets, for structural reasons that a quant researcher must internalise:

**Retail-dominated price discovery:** In US equity markets, approximately 70–80% of volume is institutional (including HFT). In India, retail is roughly half of volume. Retail investors process information more slowly, react to news with greater delay, and make behavioural errors at scale (overconfidence, herding, anchoring). The consequence is that **prices adjust to new information over days-to-weeks, not hours** in mid- and small-cap stocks.

**Analyst coverage gaps:** A Nifty 50 stock like Reliance Industries may have 40+ analyst reports per year. A Nifty 200 stock outside the top 100 may have 3–5. A Nifty 500 stock outside the top 200 may have zero. This coverage vacuum means:
- Earnings surprises are larger and persist longer (PEAD is stronger)
- Factor signals are less crowded
- Management guidance is less scrutinised

**Sell-side structural bias:** Indian sell-side analysts, like global counterparts, issue far more "Buy" than "Sell" ratings. The ratio is approximately 75% Buy, 20% Hold, 5% Sell — more extreme than US equity research. This systematic optimism bias means consensus earnings estimates tend to be optimistic, creating systematic negative earnings surprises and negative price momentum for companies in fundamental deterioration.

---

## 2.2 Promoter Concentration and Its Implications for Factor Investing

**The promoter structure:** India's listed companies are predominantly controlled by a "promoter" — the founding family, a government entity (for PSUs), or a parent corporation. Promoter holdings in the BSE 500 average approximately 50–60% of total shares outstanding. Examples: Wipro (promoter holding 73%), HCL Technologies (60%), Jindal Steel (62%), Reliance Industries (46%).

**Free float implication:** With 50–60% promoter holding, the actual free float available to institutional investors is only 40–50%. For a ₹10,000 crore market-cap company with 55% promoter holding, the tradable float is only ~₹4,500 crore. A large domestic mutual fund with ₹1,000 crore in a single stock already owns ~22% of the float — creating illiquidity and price impact even in mid-cap names.

**Family-controlled conglomerates and governance:** The Tata Group (100+ listed companies), Adani Group, Birla Group, and Mahindra Group are India's most prominent conglomerates with shared promoter identities across their listed entities. Governance implications for factor investing:

1. **Related-party transactions:** Intra-group transactions reduce transparency of standalone financials. A quality/profitability factor built purely on standalone earnings may miss cash flows being transferred to parent entities.
2. **Capital allocation opacity:** Promoter families may deploy capital to group entities at below-market rates, reducing returns to minority shareholders. The investment factor (CMA) captures this partially — excessive asset growth in family-controlled businesses is a warning sign.
3. **Promoter pledge as governance deterioration signal:** When promoters pledge shares to borrow money for group entity needs, it creates fragility. If the stock falls and pledged shares are sold by lenders, this triggers a cascade. The 2018 IL&FS/NBFC crisis and 2019 Yes Bank crisis both involved promoter pledge unwinding.

---

## 2.3 Valuation Premium: India's Persistent "Growth Equity" Characteristics

India's equity market consistently trades at a valuation premium to both its own EM peers and historical averages. Nifty 50's trailing P/E has averaged approximately 20–22x over the past decade, compared to MSCI Emerging Markets at 12–14x.

**Why the premium is (partially) justified:**
- India has the world's fastest-growing major economy (~6.5–7% real GDP growth per annum)
- Corporate earnings for NSE 500 companies have compounded at ~12–15% annually in INR terms over the past 15 years
- Structural domestic consumption growth (rising middle class, urbanisation, formalisation)

**Why the premium creates factor challenges:**
- Traditional value factors (low P/B, low P/E) systematically point to structurally lower-quality businesses (PSU banks, commodity companies, state-owned enterprises) rather than genuinely undervalued high-quality businesses
- The HML (value) factor in India has a fundamentally different composition than in the US: the "value" portfolio is dominated by public sector banks, metals companies, and commodity businesses — sectors where low P/B reflects genuine distress or cyclical risk
- Growth stocks in India can sustain very high valuations for long periods without mean-reverting, because growth rates are genuinely high and fund flows (SIP + FPI) continue to arrive

---

## 2.4 Currency Overlay: USD/INR and Its Effect on FPI Returns

The Indian Rupee has depreciated at approximately 3–4% per annum against the USD over the long run, reflecting India's structurally higher inflation (~5–6%) versus US inflation (~2–3%). This is not random volatility — it is the approximate manifestation of purchasing power parity.

**For an unhedged FPI investor:**
- INR equity market returns ≈ 12–15% CAGR (Nifty 500 in INR, 2001–2025)
- USD/INR depreciation ≈ −3.5% per annum
- Net USD return ≈ 8–11.5% per annum (before management fees)

This is competitive with US equity returns (S&P 500 ≈ 10–11% in USD), which explains sustained FPI interest in Indian equities.

**During USD strength cycles (e.g., Fed tightening 2022–2023, 2024):** FPIs face a double headwind — Indian equity market declining AND USD appreciating. This produces disproportionate FPI selling that is currency-driven, not fundamental — creating buying opportunities for INR-denominated domestic investors. Systematic FPI flow signals must account for the INR/USD rate of change.

---

## 2.5 Tax Environment: How India's Tax Structure Differs

**Capital gains tax (effective July 23, 2024 onwards):**

| Asset | Holding Period | Tax Rate (FY 2025–26) |
|---|---|---|
| Listed equity (cash) | < 12 months | STCG: 20% (flat; previously 15%) |
| Listed equity (cash) | ≥ 12 months | LTCG: 12.5% above ₹1.25 lakh/year threshold (previously 10%) |
| Equity mutual funds | < 12 months | 20% |
| Equity mutual funds | ≥ 12 months | 12.5% above ₹1.25 lakh |
| F&O (all) | Any | Treated as business income; taxed at slab rates (~30% for high earners) |

**Securities Transaction Tax (STT):** Levied on both buyer and seller at point of trade, collected by broker. For equity delivery (cash market):
- Buy side: 0.1% of transaction value
- Sell side: 0.1% of transaction value
- Round-trip cost for a ₹1,00,000 trade: ₹200 in STT alone

**Other statutory levies (see full breakdown in Section 9):** Stamp duty (0.015% on buys), NSE transaction charges (~₹2.97/lakh), SEBI turnover fee (0.0001%), GST (18% on brokerage and exchange fees), exchange clearing fee.

**Comparison with the US:** In the US, there is no equivalent of STT on equities. The SEC fee is trivially small (~$8/million). India's statutory costs are substantially higher per rupee traded, which means:
1. Higher minimum alpha hurdle for any systematic strategy
2. Turnover control is more important in India than in US-based backtests
3. Monthly rebalancing often preferred over weekly for mid-cap universes

**Buyback taxation change (effective October 2024 – March 2026):** SEBI and the Finance Ministry treated buyback proceeds as deemed dividends taxable at slab rates for this window. From April 1, 2026, capital gains treatment was restored. This temporary change disrupted the established buyback-as-undervaluation signal during this window.

---

## 2.6 The NSE Options Market: World's Largest by Contract Volume (Historically)

NSE's derivatives market grew explosively through 2020–2024, driven by:
- Zero-brokerage platforms (Zerodha, Upstox, Angel One) reducing options trading friction for retail
- High-frequency weekly (and later daily) expiry options on Nifty 50 and Bank Nifty
- Retail speculation on short-dated options (equivalent to lottery tickets)

At its peak (2023–2024), NSE averaged **over 1 billion contracts per day**, making it the world's largest exchange by number of contracts. However, as of mid-2025, Brazil's B3 surpassed NSE in contract volume (driven by Brazil's mini-contracts). NSE's premium turnover is still a fraction of US options markets — the scale difference is driven by India's much smaller average contract size.

**Implication for quant signals:**
- Huge retail option buying creates systematic variance risk premium: options are consistently overpriced relative to realised volatility
- Put-call ratio (PCR) data reflects retail sentiment, not smart money positioning
- Options open interest reveals concentration of retail pain around round numbers (max pain theory)
- Implied volatility surface contains information about market expectations that is exploitable via VRP harvest strategies

---

# Section 3: Factor Investing in India — Full Academic Review

## 3.0 The Academic Infrastructure

**Primary academic datasets:**

**IIMA Fama-French & Momentum Library:**
- URL: `faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/`
- Researchers: Agarwalla, Jacob & Varma (Indian Institute of Management Ahmedabad)
- Data source: CMIE Prowess
- Universe: All BSE + NSE listed companies (~4,900 at peak); excludes financial sector in some versions
- Period: July 1993 onwards (monthly frequency)
- Portfolio formation month: **September** (matches Indian fiscal year April–March, unlike Fama-French's July for US)
- Factors: MKT (market excess return), SMB, HML, MOM, RMW, CMA
- Freely downloadable as CSV; updated 3× per year

**Rajan Raju Library (SSRN 5008269, November 2024):**
- Data source: Refinitiv Datastream (independent validation of IIMA findings)
- Adds: BAB (Betting Against Beta), Low Volatility factor
- Key advantage: provides cross-validation of IIMA factors using a different data vendor
- Associated papers: SSRN 4054146 (four-factor), 4190426 (five-factor), 4133389 (factor indices), 4587697 (52-week high)

---

## 3.1 Momentum — The Strongest and Most Anomalous Factor in India

### Construction

**Standard 12-1 momentum:** At each portfolio formation date, rank all stocks by their cumulative 12-month return ending 1 month ago (skipping the last month to avoid the short-term reversal effect). Long top decile, short bottom decile.

$$\text{MOM}_{12-1} = \sum_{t=-12}^{t=-2} r_t$$

**Volatility-adjusted momentum (vol-adjusted):**

$$\text{MOM}_{vol} = \frac{\sum_{t=-12}^{t=-2} r_t}{\sigma_{12m}}$$

where $\sigma_{12m}$ is the standard deviation of daily or monthly returns over the past 12 months. This adjustment reduces drawdown during momentum crashes by downweighting recently high-volatility stocks.

**52-Week High Variant (Raju SSRN 4587697):**

$$\text{MOM}_{52H} = \frac{P_t}{\max(P_{t-252}, P_{t-1})}$$

Stocks near their 52-week high (ratio close to 1.0) are classified as momentum winners. The intuition (from George & Hwang 2004, extended to India) is that investors use the 52-week high as an anchor — they hesitate to buy above it and hesitate to sell below it, creating predictable patterns.

```python
# Standard 12-1 momentum construction
import pandas as pd
import numpy as np

def compute_momentum(prices: pd.DataFrame, skip_last: int = 1, lookback: int = 12) -> pd.Series:
    """
    prices: monthly price DataFrame, columns = tickers, rows = dates
    Returns momentum score at latest date
    """
    returns = prices.pct_change()
    # Cumulative return from t-12 to t-2 (skip last month)
    cum_ret = (1 + returns.iloc[-(lookback + skip_last):-skip_last]).prod() - 1
    vol = returns.iloc[-(lookback + skip_last):-skip_last].std()
    vol_adj_mom = cum_ret / vol
    return vol_adj_mom

# 52-week high variant
def compute_52w_high_mom(prices: pd.DataFrame) -> pd.Series:
    high_52w = prices.rolling(252).max().iloc[-1]
    current = prices.iloc[-1]
    return current / high_52w
```

### Evidence in India

**Agarwalla, Jacob & Varma (2017, Vikalpa):** Using IIMA factor library data from July 1993 to December 2014, the momentum factor delivered **annualised alpha of approximately 17%** — substantially higher than global evidence (~7–10% in the US, per Jegadeesh & Titman 1993).

**Raju SSRN 4587697 (2023):** Using a dataset from October 2004 to August 2023 on NSE, the 52-week high variant demonstrates:
- Higher Sharpe ratio than standard 12-1 momentum
- Significantly weaker long-term reversals (standard momentum reverses at 3–5 years; 52-week high reversal is muted)
- Robust to firm size controls across different weighting schemes

**Why momentum is stronger in India:**

1. **Behavioural anchoring by retail investors:** Indian retail investors anchor to recent price highs and IPO prices. This causes them to sell winners early (capturing small gains) and hold losers (avoiding realisation of losses). This systematic disposition effect means that winning stocks are systematically underowned by retail, allowing the trend to persist longer before price discovery is complete.

2. **Institutional herding:** Domestic mutual funds, particularly mid-cap funds, tend to buy into existing winners because their quarterly performance is benchmarked against peers. A fund that missed a momentum stock faces career risk; buying in late is safer than missing completely.

3. **Slow analyst upgrading:** Sell-side analysts upgrade ratings *after* price appreciation (not before), further reinforcing the trend as upgraded stocks attract institutional attention.

4. **Underreaction to fundamental information:** India's slower information dissemination means that good fundamental news (earnings beats, contract wins, margin improvement) is priced in gradually over months, not instantaneously.

### Momentum Crashes

**March 2020 COVID crash:** The momentum factor suffered a 34–35% drawdown in approximately 18 trading days. This is because:
- Momentum portfolios were long the prior year's winners (financials, consumer discretionary, IT)
- The COVID shock caused these to fall most severely (market-wide correlation spike)
- The subsequent sharp recovery (Nifty rebounded 50% in 3 months) added insult: momentum portfolios missed the early recovery and were short some of the strongest bouncers

**Short-term vs. long-term momentum in India:**
- 1–3 month momentum: Tends to reverse (short-term mean reversion)
- 6–12 month momentum: Strongest predictive alpha (the standard window)
- 24–36 month momentum: Reversal territory (long-horizon reversal documented in BSE data)

The academic evidence for India distinguishes intermediate-term momentum (6–12 months) as clearly robust, with evidence of mean reversion beyond 24 months consistent with De Bondt & Thaler (1985).

---

## 3.2 Low Volatility / Betting Against Beta (BAB)

### Theory (Frazzini-Pedersen 2014)

The BAB factor arises because of the Security Market Line being too flat relative to CAPM predictions. **Leverage-constrained investors** (insurance companies, pension funds, mutual funds with mandate restrictions on leverage) prefer to reach for return by buying high-beta stocks rather than applying leverage to low-beta stocks. This creates systematic overpricing of high-beta assets and underpricing of low-beta assets.

**BAB construction:**
1. Rank all stocks by their estimated beta against the market (rolling 12-month daily returns)
2. Long: bottom tercile of beta stocks, levered up to beta = 1
3. Short: top tercile of beta stocks, de-levered to beta = 1

$$\text{BAB} = r_L^{\beta=1} - r_H^{\beta=1}$$

where $r_L^{\beta=1}$ is the return of a leveraged low-beta portfolio scaled to market beta = 1, and $r_H^{\beta=1}$ is the return of a de-levered high-beta portfolio scaled to market beta = 1.

In the US, the BAB factor achieved a Sharpe ratio of approximately 0.78 over 1926–2012 — substantially higher than momentum's Sharpe during the same period.

### Evidence in India

**IIMA Working Paper (Betting Against Beta in the Indian Market):** The BAB factor earns significant positive returns in India. Stocks with higher volatility earn *lower* average returns, which is the opposite of CAPM prediction. The BAB factor dominates SMB, HML, and MOM in raw return terms in some specifications.

**Rajan Raju Library:** Includes a BAB factor and a Low Volatility factor, providing practitioner-accessible India-specific factor series.

**Why BAB is weaker in India than the US:**

1. **DII forced buying into index stocks regardless of beta:** Domestic mutual funds, particularly large-cap mandated funds, must hold Nifty 50 stocks. Many Nifty 50 stocks have high betas (banks, metals, auto). This artificial institutional demand props up high-beta index stocks, reducing the BAB spread.

2. **Insurance company regulatory constraints:** LIC and other large insurance companies invest predominantly in Nifty 50 stocks (often mandated by regulation). This supports high-beta index stocks beyond their fundamental warranted price.

3. **Illiquidity premium masquerading as low-vol premium:** Many genuinely low-beta stocks in India are simply illiquid (small-cap, low-turnover stocks that don't move with the market because they barely trade). The apparent low-vol/low-beta premium may partially capture an illiquidity premium rather than a true BAB effect.

---

## 3.3 Quality / Profitability (RMW)

### Factor Construction

**Novy-Marx (2013) Gross Profitability:**
$$GP/A = \frac{\text{Revenue} - \text{COGS}}{\text{Total Assets}}$$

This is a *top-line* profitability measure. Novy-Marx argued it outperforms bottom-line metrics because it is less contaminated by accounting choices in operating expenses, depreciation, and interest.

**RMW (Robust Minus Weak) from Fama-French Five-Factor Model:**
$$\text{RMW} = R_{\text{robust}} - R_{\text{weak}}$$

Stocks in the "robust" profitability bucket (high operating profits / book equity) minus stocks in the "weak" bucket.

**ROE as profitability proxy:**
$$\text{ROE} = \frac{\text{Net Income}}{\text{Book Value of Equity}}$$

### Which Profitability Metric Works Best in India?

**Six-factor model (Kedia, 2024, Cogent Economics & Finance):** Using BSE 500 data from June 2002 to July 2021 across 280 companies, the GRS test confirmed the superiority of a six-factor model for India. The paper's key contribution relevant to profitability is that **ROE outperforms gross profitability and operating profitability as a factor signal in India**. This differs from the US evidence where gross profitability (Novy-Marx 2013) dominates.

**Why ROE works better in India:**
- Indian companies more frequently carry significant other income (dividends from subsidiaries, treasury income) that inflates bottom-line ROE but is visible in reported net income
- Revenue recognition is cleaner in Indian GAAP (IndAS post-2016) than in earlier Indian GAAP, making gross margin comparisons more reliable over time — but the *comparison* across companies is still noisy
- ROE captures the return on capital deployed by promoters, which is the key metric for minority shareholder alignment

**Interaction with HML (Value Factor):**
The strong negative correlation between HML and RMW observed in India (-0.61, based on five-factor model tests on NSE 500, October 1995–September 2022, Zenodo 2025 working paper) has important portfolio construction implications. In a five-factor model regression:
- Value (low P/B) stocks are systematically low-quality (low profitability) in India
- This means holding both a value tilt AND a quality/profitability tilt partially cancels out in India
- The strategy recommendation: do *not* combine value and quality as additive tilts without careful orthogonalisation

**Quality-Momentum Interaction:**

The strongest and most consistent factor combination in India is **high quality + high momentum**:
- High quality: top quartile ROE, stable earnings, low debt/equity
- High momentum: price near 52-week high OR strong 6-12 month return

CAGR of approximately 17–18% documented over multiple 10-year periods by practitioners using this combination. The logic: quality prevents investing in value traps (structurally declining businesses with low P/B); momentum confirms that the market agrees with the quality assessment.

---

## 3.4 Value (HML)

### Construction

$$\text{HML} = R_{\text{High B/P}} - R_{\text{Low B/P}}$$

Standard HML is constructed as the return of high book-to-price (value) stocks minus low book-to-price (growth) stocks. Portfolio formation typically uses book value from the previous fiscal year-end and current market price.

**India-specific modification:** Use the fiscal year April–March. Portfolio formation in September (IIMA convention) uses March 31 balance sheet data available by June. This matters — US-style July formation using December fiscal year data gives different exposure timing for Indian companies.

### Evidence in India

**IIMA factor library (1993–2014):** Average annual return on HML = 15.3% (equal-weighted). However, this was driven heavily by the 1990s and early 2000s period.

**Sharma, Subramaniam & Sehgal (2021, Global Business Review):** "Are Prominent Equity Market Anomalies in India Fading Away?" examines NSE 500 companies from July 2005 to June 2016. Key finding: **HML is weakening in India and appears to be risk-explained rather than anomalous alpha** — controlling for market beta and size eliminates most of the HML excess return in the later period. Value does not appear to offer statistically significant alpha over a CAPM benchmark in the 2005–2016 window.

**What value actually looks like in India:**

The "value" portfolio in India is heavily concentrated in:
- **Public Sector Undertaking (PSU) banks:** State Bank of India, Punjab National Bank, Bank of Baroda trade at low P/B (0.5–1.5x) because they carry legacy NPAs (Non-Performing Assets) and have lower ROEs than private sector banks. They are cheap for a reason.
- **Commodity companies:** Steel, cement, power companies trade at low P/B due to cyclicality.
- **State-owned utilities:** NTPC, Power Grid, ONGC — low growth, high dividend, low P/B.

The "growth" portfolio in India is expensive for a reason — it is dominated by IT services (TCS, Infosys, HCL), HDFC Bank, and consumer staples (Hindustan Unilever) — companies with genuinely high and sustainable ROEs.

**The 2020–2024 Value Comeback:**
PSU banks experienced a dramatic re-rating: State Bank of India moved from 0.5× P/B in 2020 to 1.5–2.0× P/B by 2024. Bank of Baroda traded at 3× P/E in 2020 and reached 8–10× P/E by 2024. This cyclical value recovery was driven by:
- RBI's NPA clean-up (large provisioning completed by 2019–2020, recovery improving from 2021)
- Net interest margins expanding as RBI raised rates 250bps in 2022–2023
- PSU bank credit growth accelerating on government capex

**Better value metrics for India:**

EV/EBIT is superior to P/B for Indian companies because:
1. It is neutral to capital structure (avoids leverage-induced P/B distortions)
2. It captures operating efficiency rather than accounting book values
3. Indian companies frequently carry large intangible assets (brands, licences) that are not on the balance sheet, making P/B misleading

---

## 3.5 Size (SMB)

### Evidence

**IIMA factor library:** SMB in India has shown an average annual return of approximately 0.36% (economically negligible) over the full sample period. This contrasts sharply with the original Fama-French US evidence of ~2–3% per annum.

**Why SMB is very weak in India:**

1. **The "small-cap premium" in India is primarily an illiquidity premium, not a genuine size effect.** When controlling for illiquidity (Amihud 2002 measure), much of the apparent small-cap return disappears. You are compensated for being unable to exit, not for owning small firms per se.

2. **Post-2018 SEBI recategorisation:** Mandatory institutional flows into formally-defined small-cap funds (rank 251+) compressed the illiquidity premium by increasing buyer base. Post-2018, genuine small-caps (not micro-caps) saw institutional inflows that were absent in prior decades.

3. **Data biases:** Academic small-cap samples include many illiquid stocks where measured returns are noisy (stale prices, zero-return bias). After filtering for minimum trading days and volume thresholds, the size effect largely disappears.

**Practical conclusion:** Do not include a size tilt as a separate factor in Indian strategies. Instead, treat it as a risk control: ensure your factor portfolio does not inadvertently overweight small/micro-cap stocks that cannot be exited during stress.

---

## 3.6 Investment (CMA)

### Construction

$$\text{CMA} = R_{\text{Conservative}} - R_{\text{Aggressive}}$$

Stocks with low asset growth (conservative investment) minus stocks with high asset growth (aggressive investment). High investment growth predicts lower future returns (the investment anomaly, documented by Titman, Wei & Xie 2004 and formalised in the Fama-French 5-factor model).

**India-specific findings:**

Five-factor model tests on NSE 500 (Zenodo 2025 working paper) show CMA is statistically significant in India, raising adjusted R² from three-factor to five-factor specifications. However, CMA is **weaker in India than in the US** for structural reasons:

**Family-controlled business capex patterns:** In family-controlled conglomerates, capital allocation follows promoter priorities (group-level empire building, related-party capex, cross-holding investments) rather than shareholder value maximisation. High capex may be:
- Empire building by promoter (bad signal, consistent with US evidence)
- Government-mandated PSU expansion (ambiguous — PSU capex cycles are politically driven)
- Genuine capacity expansion in growth periods (positive for earnings)

**Adjustment for India:** Filter out PSU companies from CMA factor before applying. For PSUs, capex is more policy-driven than value-creating, making CMA less informative. For private-sector companies, high capex still predicts lower near-term returns in India, consistent with global evidence.

---

## 3.7 The Accruals Anomaly: India-Specific Failure

This is one of the most important distinctions between Indian and US factor evidence.

**US evidence (Sloan 1996):** High accruals (accounting earnings exceeding cash flows) predict *lower* future returns. The logic: investors over-price the accruals component of earnings, which is less persistent than cash flows. A long-short accruals strategy (short high-accruals, long low-accruals) generated ~10% annualised return in the US through the 1990s.

$$\text{Accruals} = \frac{\Delta \text{Net Operating Assets}}{\text{Average Total Assets}}$$

**India-specific evidence — the sign reversal:**

**Sehgal, Subramaniam & Deisting (SSRN 2128978, 2012):** "Testing the Accruals and Cash Flows Anomalies for the Indian Stock Market." Key finding: The standard Sloan accruals anomaly does **not replicate** in India. Moreover, the sign of the relationship differs from the US — **Indian investors appear to over-price cash flows, not accruals**. High-cash-flow stocks are systematically overvalued (retail investors love "clean cash earnings") while high-accruals stocks are discounted.

**Why the reversal:**
- Indian retail investors heavily favour stocks with high reported cash flows because they distrust Indian accounting (appropriately, given earnings manipulation history). This creates systematic *overpricing* of high-cash-flow, low-accruals companies.
- Related: Indian companies have historically understated earnings (hiding income to reduce taxes) rather than overstating them as in the US. This reverses the accruals prediction.

**The correct signal for India:**

Rather than shorting high-accruals stocks, use **cash earnings quality** as a *long* signal:
$$\text{Cash Earnings Quality} = \frac{\text{Operating Cash Flow}}{\text{Net Income}}$$

Stocks with OCF/NI ratio > 1.0 (more cash than reported profit) are undervalued in India because:
- The market discounts their reported earnings as potentially overstated
- But actual cash generation confirms or exceeds reported earnings
- These are the genuinely high-quality businesses hiding in plain sight

This is a materially different construction from applying the US Sloan accruals signal mechanically to India — which would produce negative alpha.

---

## 3.8 Factor Summary Table

| Factor | India Evidence Quality | Approx. Sharpe (IIMA Data) | Best for India? | Key Paper |
|---|---|---|---|---|
| Momentum (12-1) | Strong, replicated | ~0.8–1.0 | Yes | Agarwalla et al. (2017) |
| 52-Week High Momentum | Strong | ~0.9–1.1 | Yes (more stable) | Raju SSRN 4587697 |
| Quality/Profitability (ROE) | Strong | ~0.6–0.8 | Yes | Kedia (2024) |
| Low Volatility / BAB | Moderate | ~0.4–0.6 | Partially | IIMA WP (BAB India) |
| Value (HML) | Weak post-2005 | ~0.2–0.4 | Only cyclically | Sharma et al. (2021) |
| Size (SMB) | Very weak | ~0.0–0.1 | No | IIMA library data |
| Investment (CMA) | Moderate | ~0.3–0.5 | Partially | 5-factor India tests |
| Accruals (Sloan) | **Fails/Reverses** | Negative | **No** | Sehgal et al. SSRN 2128978 |

---

# Section 4: SEBI Public Data Signals — Complete Construction Guide

## 4.1 Bulk and Block Deals

**Definitions:**
- **Bulk deal:** Any on-market transaction(s) in a single stock totalling ≥ 0.5% of total equity shares of the company within a single trading day. Disclosed same-day after market close.
- **Block deal:** Pre-arranged large trades executed in a dedicated 15-minute pre-open window (08:45–09:00 AM) at a price within ±1% of previous closing price. Minimum: 5 lakh shares or ₹5 crore.

**Data access and code:**

```python
# Option 1: NSEPython (recommended for reliability)
from nsepython import nse_large_deal_historical

# Fetch bulk deals for a date range
bulk = nse_large_deal_historical(
    from_date='01-01-2023',
    to_date='31-12-2023',
    mode='bulk_deals'
)

# Fetch block deals
block = nse_large_deal_historical(
    from_date='01-01-2023',
    to_date='31-12-2023',
    mode='block_deals'
)

# Key columns returned:
# symbol, client_name, buy_sell, quantity, price, date

# Signal construction: promoter open-market buy signal
promo_buys = bulk[
    (bulk['buy_sell'] == 'B') &
    (bulk['client_name'].str.contains('promoter|family|sponsor', case=False))
]

# Option 2: Direct NSE API (may require session management)
import requests, json

url = "https://www.nseindia.com/api/snapshot-capital-market-largedeal?bandtype=bulk_deals"
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'en-US,en;q=0.9'
}
# Note: NSE API requires prior cookie session; use nsepython which handles this
```

**Signal logic (research-grade, no published backtest exists):**
1. Promoter open-market buy > 0.5% float, after ≥15% drawdown → *long signal, 20-day holding*
2. FII bulk buy in thin-float mid-cap (float < ₹2,000 crore) → *momentum acceleration signal*
3. PE/VC bulk sell at market (not block, not pre-arranged) → *distribution warning, reduce position*

---

## 4.2 SEBI PIT Insider Trading Disclosures

**Regulatory framework:** SEBI (Prohibition of Insider Trading) Regulations 2015, most recently amended March 2025. Mandatory disclosure when:
- Any promoter or promoter group trades in company securities (any amount)
- Designated Persons (DPs — directors, senior management, compliance officers) trade ≥ ₹10 lakh in a rolling calendar quarter

**Form types:**
- **Form C:** Promoter / promoter group transaction disclosure (filed within 2 trading days of trade)
- **Form D:** Designated Person (DP) disclosure (filed within 2 trading days)

**Data sources:**
```
BSE filings: bseindia.com/corporates/Insider_Trading_new.aspx
NSE filings: nseindia.com/companies-listing/corporate-filings-insider-trading
Aggregated + filterable: insiderscreener.com/en/india/insider-trading/
             (free; covers both exchanges; filterable by buy/sell, category, date)
```

**Signal construction (Python pseudocode):**
```python
import pandas as pd

# Load insider trading data from insiderscreener.com (exported CSV)
# or scrape NSE/BSE directly
df = pd.read_csv('insider_trades.csv')

# Filter: promoter open-market purchase (excluding ESOPs and rights)
conviction_buys = df[
    (df['category'].isin(['Promoter', 'Promoter Group'])) &
    (df['transaction_type'] == 'Market Purchase') &  # NOT ESOP exercise
    (df['quantity'] >= 0.001 * df['shares_outstanding'])  # >= 0.1% of outstanding
]

# Add price context: only count buys where stock is >= 15% below 52-week high
conviction_buys = conviction_buys[
    conviction_buys['pct_from_52w_high'] <= -0.15
]

# Signal: long from disclosure date + 1 day (to avoid forward-looking bias)
# Holding period: 30 days
# Exit: if price recovers to pre-drawdown level OR 30 days elapsed
```

**Data quality issues to clean:**
1. ESOP exercises appear as "purchases" — filter by transaction type
2. Transfers between promoter group entities appear as buy + sell — filter if counterparty is also a promoter entity
3. Lag signal by 1 trading day (disclosure arrives after market close on trade date)

---

## 4.3 Promoter Pledging as Crash Risk Signal

**What pledging is:** Promoters borrow money by pledging (hypothecating) their own shares as collateral. The lender (bank, NBFC, broker) can sell the pledged shares if the stock price falls below the margin maintenance threshold. This creates a potential cascade: stock falls → pledged shares sold → stock falls further.

**Data source:** SHP (Shareholding Pattern) quarterly filings by all listed companies (within 21 days of quarter end). Filed on NSE and BSE. The SHP separately discloses:
- Total promoter holding
- Shares pledged or otherwise encumbered (as % of total promoter holding)
- Number of shareholders in each category

```python
# Signal construction from SHP data
# Data available from nseindia.com/companies-listing/corporate-filings-shareholding-pattern
# Or via jugaad-data, BseIndiaApi

import pandas as pd

def compute_pledge_risk(shp_df: pd.DataFrame) -> pd.DataFrame:
    """
    shp_df: quarterly SHP data with columns: company, date,
            promoter_total, promoter_pledged, total_shares
    """
    shp_df['pledge_ratio'] = (
        shp_df['promoter_pledged'] / shp_df['promoter_total']
    )
    shp_df['float_pledge_pct'] = (
        shp_df['promoter_pledged'] / shp_df['total_shares']
    )
    
    # Crash risk flags:
    shp_df['high_pledge_risk'] = (
        (shp_df['pledge_ratio'] > 0.50) &  # >50% of promoter holding pledged
        (shp_df['pledge_ratio'].diff() > 0)  # AND rising
    )
    
    # Extreme risk: exclude from long portfolios entirely
    shp_df['extreme_pledge'] = shp_df['pledge_ratio'] > 0.60
    
    return shp_df[['company', 'date', 'pledge_ratio', 
                   'high_pledge_risk', 'extreme_pledge']]
```

**Academic evidence on pledging:**
- Chauhan (IIMB Management Review, 2020): Pledging exacerbates stock price volatility and adversely affects long-term firm value across 1,452 NSE/BSE firms.
- BSE 500 study (2024): Rising promoter pledge ratio is a statistically significant predictor of future stock price crash risk.

**MCA21 CHG-1 as leading indicator of balance sheet stress:**
Companies file Form CHG-1 on the Ministry of Corporate Affairs (MCA21) portal when creating a new charge (i.e., pledging assets as collateral for a loan) *before* this appears on the balance sheet. Signal: a sudden burst of CHG-1 filings + concurrent increase in promoter pledging = early warning of balance sheet stress.
- **Data aggregators:** tofler.in, accumn.ai (paid, ₹500–2,000 per company for one-off; institutional subscriptions available)
- There is a 30–60 day lag between CHG-1 filing and balance sheet recognition — this is the edge.

---

## 4.4 FII/DII Daily Flow Signal

```python
# Data source: NSE daily FII/DII report
# URL: nseindia.com/reports/fii-dii

import pandas as pd
import numpy as np

def fii_dii_signal(df: pd.DataFrame, fpi_col: str, dii_col: str,
                   fpi_threshold: float = -3000,
                   dii_threshold: float = 2000,
                   window: int = 5) -> pd.DataFrame:
    """
    df: daily data with FPI and DII net flows in crore INR
    Returns: signal series
    """
    df['fpi_5d'] = df[fpi_col].rolling(window).sum()
    df['dii_5d'] = df[dii_col].rolling(window).sum()
    
    # Trend-following signal: FPI momentum
    df['fpi_trend'] = np.sign(df['fpi_5d'].shift(1))
    
    # Contrarian signal: FPI selling + DII buying = mean-reversion long
    df['divergence_signal'] = (
        (df['fpi_5d'] < fpi_threshold) &
        (df['dii_5d'] > dii_threshold)
    ).astype(int)
    
    # SIP structural floor: ₹1,200–1,400 crore/day of DII demand is 'automatic'
    # Adjust threshold for SIP proportion
    df['net_discretionary_dii'] = df[dii_col] - 1300  # subtract SIP floor estimate
    
    return df[['fpi_5d', 'dii_5d', 'fpi_trend', 'divergence_signal']]
```

**Key context for signal calibration:**
- SIP flows as of May 2026: ~₹26,000–30,000 crore/month = ~₹1,200–1,400 crore per trading day
- This structural floor means DIIs will appear to "buy" even in markets trending down — that baseline does not constitute a contrarian signal
- True contrarian signal: DII net buying *significantly exceeds* the SIP floor (i.e., discretionary DII buying from insurance/pension rebalancing in addition to SIP flows)

---

# Section 5: PEAD (Post-Earnings-Announcement Drift) in India

## 5.1 The Phenomenon and Its India-Specific Strength

Post-Earnings-Announcement Drift (PEAD) is the empirical finding that stock prices continue to move in the direction of an earnings surprise for weeks to months after the announcement. First documented by Ball & Brown (1968) in the US, it persisted in US markets until the late 1990s–2000s, when institutional arbitrage and analyst coverage compressed the anomaly.

**In India, PEAD remains robust** because:
1. Analyst coverage is thin for the Nifty 200–500 range
2. Retail investors process earnings slowly (most don't read actual earnings reports)
3. Limited systematic algorithmic trading in mid-cap stocks to immediately arbitrage surprises
4. Management guidance is less precise; the market has wider uncertainty ranges

## 5.2 India-Specific Evidence

**Sehgal & Kulkarni (SCIRP/Theoretical Economics Letters, October 2018):** "Post-Earnings-Announcement Drift Anomaly in India: A Test of Market Efficiency." Study period: 2002–2017. Universe: Nifty 500 companies.

**Methodology:** 
- Sort stocks quarterly based on SUE (Standardised Unexpected Earnings)
- Divide into 10 portfolios (decile 1 = largest negative surprise, decile 10 = largest positive surprise)
- Measure 64-day post-announcement holding period returns

**Key findings:**
- Statistically significant PEAD across the full 2002–2017 period
- Results robust to sub-period analysis (consistent in early and later sub-periods)
- An investor buying extreme positive SUE decile (D10) and shorting extreme negative SUE decile (D1) and holding 64 days earns significant abnormal returns
- The 64-day window (approximately one quarter) is optimal — by the next earnings announcement, the drift is mostly absorbed

## 5.3 SUE Construction Without I/B/E/S

In the US, SUE is typically constructed using analyst consensus earnings estimates from I/B/E/S or Bloomberg. In India, institutional-quality consensus data is harder to access (IBES covers only ~100 Indian stocks). An alternative construction:

$$\text{SUE}_t = \frac{(EPS_t - EPS_{t-4})}{\sigma_{EPS}}$$

where:
- $EPS_t$ = actual earnings per share in quarter t
- $EPS_{t-4}$ = actual EPS from the same quarter one year ago (seasonal naive forecast)
- $\sigma_{EPS}$ = standard deviation of EPS changes over the prior 8 quarters

This seasonal random walk model is simpler but surprisingly effective for India because:
1. Indian companies grow earnings at 12–15% CAGR, so the seasonal naive model captures the base expectation
2. Quarter-to-quarter EPS is highly seasonal in India (FY Q4 March quarter is strongest for most sectors)

```python
import pandas as pd
import numpy as np

def compute_sue(eps_df: pd.DataFrame) -> pd.DataFrame:
    """
    eps_df: quarterly EPS data with columns: company, quarter_date, eps
    Returns: SUE scores per company per quarter
    """
    # Seasonal naive expected EPS = same quarter last year
    eps_df = eps_df.sort_values(['company', 'quarter_date'])
    eps_df['expected_eps'] = eps_df.groupby('company')['eps'].shift(4)
    
    # Unexpected earnings
    eps_df['ue'] = eps_df['eps'] - eps_df['expected_eps']
    
    # Standard deviation of earnings changes (8-quarter rolling)
    eps_df['ue_std'] = (
        eps_df.groupby('company')['ue']
        .transform(lambda x: x.rolling(8, min_periods=4).std())
    )
    
    # SUE
    eps_df['sue'] = eps_df['ue'] / eps_df['ue_std']
    
    # Decile rank (10 = best positive surprise)
    eps_df['sue_decile'] = eps_df.groupby('quarter_date')['sue'].transform(
        lambda x: pd.qcut(x, 10, labels=False, duplicates='drop')
    )
    
    return eps_df[['company', 'quarter_date', 'sue', 'sue_decile']]
```

## 5.4 Optimal Implementation

**Universe selection:** The Nifty 200–500 range is optimal for PEAD because:
- Nifty 50–200: Too well-covered; PEAD is compressed by institutional speed of processing
- Nifty 200–500: Liquid enough to trade (tight bid-ask on entry), under-covered enough for drift to persist
- Below Nifty 500: Too illiquid; execution costs and circuit breaker risk overwhelm the drift

**Entry timing:** Enter within 1–2 days of earnings announcement. For mid-cap stocks, spreads are tight in the first 1–2 days post-announcement (as informed traders take positions). Beyond day 2, the drift begins and catching it requires accepting wider spreads.

**Transaction cost check:** For a Nifty 400 stock with ₹500 crore market cap:
- Bid-ask spread: 0.2–0.4% (see Section 9)
- Total statutory costs round-trip: ~0.3–0.4%
- Entry + exit cost: ~0.5–0.8%
- Required gross PEAD alpha over 64 days: >1.5% to be worthwhile after costs

---

# Section 6: IPO and Corporate Event Signals

## 6.1 Grey Market Premium (GMP) as an IPO Signal

**What GMP is:** The unofficial premium at which IPO application forms and shares trade in unregulated grey markets *before* official listing. GMP represents the market's expectation of listing day gain/loss.

Grey market transactions occur outside SEBI oversight with no clearing infrastructure or legal recourse. Pricing happens via word-of-mouth networks among IPO subbrokers and IPO financing intermediaries.

**Construction of GMP Signal:**
$$\text{GMP} = \text{Grey Market Price} - \text{IPO Issue Price}$$
$$\text{GMP\%} = \frac{\text{GMP}}{\text{IPO Issue Price}} \times 100$$

**Correlation with listing day returns:**
Multiple studies document a strong positive correlation between GMP and listing day performance. Spearman correlation coefficients of approximately 0.886 have been reported in academic and practitioner literature, making GMP one of the strongest predictors of IPO listing day returns in India.

**Data sources for GMP:**
- ipowatch.in (real-time GMP tracking, updated multiple times daily)
- ipocentral.in, ipogmp.com
- These are informal aggregators of grey market prices; data quality degrades for smaller IPOs

**Limitations:**
1. GMP is self-referential: high GMP attracts more subscriptions (oversubscription), which attracts more retail interest, which further elevates GMP
2. For heavily oversubscribed IPOs (100×+), allotment probability is so low that the GMP signal is less actionable
3. GMP fails for tech/startup IPOs with uncertain fundamentals (e.g., Paytm, Zomato early period)

---

## 6.2 Lock-Up Expiry Short: The Structured Shorting Opportunity

**SEBI lock-in requirements (as of 2024–2025 rules):**
- **Promoter shares:** Mandatory lock-in of 18 months post-IPO (for minimum promoter contribution); beyond minimum, 6-month lock-in
- **Anchor investors:** Lock-in of 30 days (for 50% of allocation) and 90 days (for remaining 50%)
- **Pre-IPO investors (VC/PE):** Lock-in of 6 months post-listing
- **Other shareholders:** No mandatory lock-in unless contractually agreed

**Lock-up expiry strategy:**
When VC/PE or pre-IPO investors see their lock-up expire at 6 months, they frequently sell into the market (especially for IPOs that listed at premium; they want to book gains). This creates:
1. A predictable supply overhang
2. Price pressure around lock-up expiry dates
3. Particularly strong effect for IPOs where VC/PE holds >20% of outstanding shares

**Implementation:** Short via NSE futures (if the stock is in the F&O list) beginning 5–10 trading days before lock-up expiry. The stock must have reasonable F&O liquidity. Cover 5–10 days after lock-up expiry once supply overhang has been absorbed.

**Caution:** Not all companies with 6-month lock-ups will see significant selling — if the stock has performed poorly post-IPO, VC/PE may choose to hold rather than crystallise losses.

---

## 6.3 Buyback Signals

**Why buybacks signal undervaluation in India:**
1. Management has better information than market about intrinsic value
2. Buyback announcement is typically done after significant underperformance
3. Unlike dividends (which create tax obligations at shareholder level from FY2020 onwards), buybacks were historically more tax-efficient for promoters

**Tax efficiency context:**
- Pre-July 2019: Buybacks attracted company-level tax only
- July 2019–September 2024: Buyback tax at 20% company level; still preferable to dividend taxation for high-bracket shareholders
- October 2024–March 2026: Finance Act 2024 treated buyback proceeds as deemed dividends — eliminating the tax efficiency differential. Buyback activity declined.
- April 2026 onwards: Capital gains treatment restored; buyback efficiency premium returns

**Signal construction:**
- Open-market buyback tender offers: buy the day after announcement, tender into the offer
- Creeping buybacks (off-market, board-authorised buyback via market purchases): positive multi-month signal

**Data source:** NSE corporate actions page; BSE announcements section. Python: jugaad-data or BseIndiaApi for corporate actions.

---

## 6.4 Rights Issues and QIPs

**Rights issues:** A company offers existing shareholders new shares at a discount to market price (typically 15–25% discount). Rights issues in India signal:
- *If well-subscribed and company is growing:* No meaningful signal
- *If issued for debt repayment with low subscription:* Negative signal (distress financing)
- *If promoter is fully subscribing and the company is fundamentally strong:* Positive signal (promoter confidence)

**QIP (Qualified Institutional Placement):** A private placement of shares to qualified institutional buyers (QIBs) without public offer. QIPs are common for mid-cap companies needing fast equity capital. Pattern:
- QIP at discount to market (5–10%) → short-term negative price pressure (dilution + anchor investors selling quickly)
- Post-QIP performance depends on use of proceeds

**Ex-date effects:** Indian companies paying dividends show predictable ex-date price drops. For FPIs, dividends are subject to withholding tax (20% + surcharge for most FPI structures, though treaty-reduced rates apply for US/UK structures). This withholding tax makes dividends less attractive to FPIs, creating differential selling pressure near ex-dates that can be observed in FPI flow data.

---

# Section 7: Options Market Signals

## 7.1 India VIX: Construction and Data

**India VIX** is a real-time volatility index calculated by NSE using the model-free methodology developed by the CBOE for the S&P 500 VIX.

**Construction:**
$$\text{India VIX}^2 = \frac{2}{T} \sum_i \frac{\Delta K_i}{K_i^2} e^{rT} Q(K_i) - \frac{1}{T} \left(\frac{F}{K_0} - 1\right)^2$$

where:
- $T$ = time to expiry in years
- $K_i$ = strike price of the $i$-th OTM option
- $Q(K_i)$ = mid-price of the option with strike $K_i$
- $F$ = forward price of the index
- $K_0$ = first strike below forward price

NSE uses the **near-month and next-month** Nifty 50 ATM options to compute this. India VIX represents expected Nifty 50 volatility over the next 30 calendar days, expressed as an annualised percentage.

**Historical India VIX data:** Freely downloadable from NSE India website. Historical data from 2009 (when NSE began disseminating India VIX).

**India VIX thresholds:**
| India VIX Level | Market Regime | Options Strategy Implication |
|---|---|---|
| < 12 | Extreme complacency | Short vol strategies most profitable; watch for tail risk |
| 12–16 | Normal regime | Standard conditions for short straddle/strangle |
| 16–20 | Elevated uncertainty | Reduce short vol positions; VRP still positive |
| 20–25 | Stressed | Short-dated long vol more attractive; reduce short gamma |
| > 25 | Crisis | Long vol; short straddles dangerous; max pain unreliable |

---

## 7.2 Variance Risk Premium (VRP) in India

**Definition:** The VRP is the systematic difference between implied volatility and subsequently realised volatility:
$$\text{VRP} = \text{Implied Volatility}^2 - \text{Realised Volatility}^2$$

Equivalently in volatility terms:
$$\text{VRP}_{vol} = IV_{t} - RV_{t+\tau}$$

The VRP is positive on average globally: options are systematically overpriced relative to realised volatility because buyers pay an insurance premium. This premium is collected by option sellers (short straddles, short strangles).

**India-specific VRP evidence:**
- NSE's options market is dominated by retail buyers of options (lottery-seeking, fear-driven)
- This retail demand systematically drives up implied volatility relative to realised volatility
- The VRP in India is structurally positive, with implied vol typically exceeding realised by 3–5 volatility points in normal regimes

**Short Straddle Strategy Mechanics:**
1. Sell ATM Nifty 50 call and ATM Nifty 50 put, same strike and expiry (near-month)
2. Collect premium ≈ India VIX × √(days to expiry / 365) × Nifty level
3. Max profit: both options expire worthless if Nifty stays near strike
4. Max loss: unlimited on upside (from short call), very large on downside (from short put)

**Historical win rate:** In calm market regimes, monthly Nifty short straddles have been profitable in approximately 65–70% of months historically (i.e., realised volatility finishes below implied volatility). However, the distribution of losses is heavily left-skewed — the 30–35% losing months contain larger losses in percentage terms, requiring careful position sizing.

**Risk in crisis:** During March 2020, a short straddle position on Nifty would have lost 40–60% of notional within days (Nifty fell 38% in 2 months). VRP harvest strategies must use defined-risk structures (iron condors, ratio spreads) or maintain strict loss limits.

---

## 7.3 Put-Call Ratio (PCR)

**PCR (open interest-based):**
$$\text{PCR}_{OI} = \frac{\text{Total Put OI}}{\text{Total Call OI}}$$

**PCR (volume-based):**
$$\text{PCR}_{vol} = \frac{\text{Daily Put Volume}}{\text{Daily Call Volume}}$$

**Interpretation for Nifty 50:**

| PCR Range | Interpretation | Action |
|---|---|---|
| PCR < 0.7 | Extreme bullishness; retail piling into calls | Contrarian warning — market vulnerable |
| 0.7 – 0.85 | Moderately bullish; bullish but orderly | Normal long conditions |
| 0.85 – 1.15 | Neutral range | Normal; PCR not signalling either way |
| 1.15 – 1.3 | Elevated put buying | Moderate fear; typically near-term support |
| PCR > 1.3 | Panic/excessive put buying | Contrarian — likely bottom; retail over-hedging |

**Data sources:** NSE India website provides daily PCR data in the option chain section. Historical data downloadable as CSV from `nseindia.com/option-chain`.

**Limitation:** PCR reflects retail positioning in India's options market (which is 70–80% retail-driven). Smart money (institutional) hedges and FPI overlays may take large off-exchange (OTC) positions that are not captured in exchange PCR. Use PCR as a *sentiment* indicator, not a precise market timing tool.

---

## 7.4 Max Pain Theory and F&O Expiry Effects

**Max Pain definition:** The strike price at which the total value of outstanding options (calls + puts) is minimised at expiry. The theory posits that large option writers (institutions, market makers) have the incentive to pin the market near max pain to minimise payouts.

**Evidence in India (calm regimes):** In weeks without major macro events, Nifty 50 has historically closed within ±0.5% of the max pain strike on approximately 60–70% of weekly expiry days. This alignment is stronger in calm weeks and breaks down severely around:
- RBI monetary policy announcements
- Union Budget presentation (February)
- Major global events (US CPI, Fed decisions)
- Index F&O rollover periods

**Max pain limitations:**
1. Large enough participant can move max pain deliberately (it is not exogenous)
2. Max pain can shift significantly intraday as positions open and close
3. On weekly expiries (Thursday) the effect is weaker than on monthly expiries

**F&O Expiry Effects (arXiv 2507.04859):**
"F&O Expiry vs. First-Day SIPs: A 22-Year Analysis of Timing Advantages in India's Nifty 50" (Siddharth Gavhale, 2025). Using Nifty 50 data from 2003–2024:
- F&O expiry day SIPs (investing on monthly expiry Thursday) outperform first-trading-day SIPs by **0.5–2.5% annually** over short-to-medium horizons (1–5 year)
- This advantage decays to economically negligible over 10–20 year horizons
- NSE moved F&O expiry from last Thursday to last Monday effective April 2025 — this changes the implementation calendar for expiry-based signals

---

# Section 8: Macro and Sector Rotation Signals for India

## 8.1 GST E-Way Bills as Economic Activity Signal

**What are E-Way bills:** Under India's Goods and Services Tax (GST) system, businesses must generate an "e-way bill" for every interstate or intrastate movement of goods worth ≥ ₹50,000. E-way bill data is published monthly by the GST Network (GSTN).

**Why this matters as a signal:**
- E-way bill volume is a high-frequency proxy for goods movement and industrial activity
- Released monthly, roughly 10–15 days after the reference month ends
- YoY growth rate of e-way bills correlates strongly with IIP (Index of Industrial Production) and GDP growth

**Data access:**
- CEIC: ceicdata.com provides India GST e-way bill data
- Ministry of Finance monthly press releases
- National Informatics Centre portal: ewaybill.nic.in

**Sector mapping:**
| E-Way Bill Trend | Sector Signal |
|---|---|
| Consistent acceleration >15% YoY | Cyclical sectors: Auto, Metal, Cement, Capital Goods |
| Deceleration to <5% YoY | Defensives outperform: FMCG, IT, Pharma |
| Sharp volume decline | Early recession warning; exit capital goods |

---

## 8.2 Auto Sales Data (SIAM / FADA)

**SIAM (Society of Indian Automobile Manufacturers):** Publishes monthly wholesale data (factory dispatches to dealers). Released within first week of the following month.

**FADA (Federation of Automobile Dealers Associations):** Publishes monthly retail sales (actual retail to consumers). More relevant for demand assessment.

**Segment mapping:**
- **Passenger vehicles (PV):** Correlates with consumer discretionary sentiment; forward indicator for Nifty Auto index
- **Two-wheelers (2W):** Rural demand proxy; correlates with Kharif crop performance and rural income
- **Commercial vehicles (CV):** Best single indicator of infrastructure/logistics activity; leads capital goods stocks

**Signal construction:**
```python
# Auto sector rotation signal
# Data: SIAM/FADA monthly data (manual download or scraping)

def auto_sector_signal(cv_sales_df: pd.DataFrame, 
                        ma_short: int = 3,
                        ma_long: int = 12) -> pd.Series:
    """
    cv_sales_df: monthly CV sales with date index
    Returns: +1 (overweight auto/infra), -1 (underweight), 0 (neutral)
    """
    yoy = cv_sales_df.pct_change(12)  # YoY growth
    ma_3 = yoy.rolling(ma_short).mean()
    ma_12 = yoy.rolling(ma_long).mean()
    
    signal = pd.Series(0, index=cv_sales_df.index)
    signal[ma_3 > ma_12 + 0.05] = 1   # Accelerating CV demand
    signal[ma_3 < ma_12 - 0.05] = -1  # Decelerating CV demand
    
    return signal
```

---

## 8.3 India PMI Data

**Manufacturing PMI:** S&P Global India Manufacturing PMI. Released on the first business day of the following month. A reading above 50 = expansion; below 50 = contraction. India Manufacturing PMI has been predominantly in expansion territory since mid-2020.

**Services PMI:** S&P Global India Services PMI. Released on the third business day. India's services PMI has been one of the strongest globally, reflecting strong domestic consumption and export services (IT, BPO).

**Sector rotation logic:**
- PMI new orders component rising → overweight capital goods, metals, auto components
- PMI employment component rising → overweight consumer discretionary (disposable income)
- PMI input prices component rising → overweight commodity producers; underweight margin-sensitive consumer staples
- Services PMI rising + IT exports → overweight Nifty IT sector (proxy: TCS, Infosys, HCL)

---

## 8.4 RBI Monetary Policy and Sector Sensitivity

**RBI Monetary Policy Committee (MPC):** India's rate-setting body. Meeting schedule: 6 times per year (approximately bi-monthly). Key rate: **Repo Rate** (rate at which RBI lends to banks overnight).

**Interest rate sensitivity by sector:**

| Rate Direction | Positive Sectors | Negative Sectors | Rationale |
|---|---|---|---|
| Rate cuts | Nifty Bank (private), NBFCs, Real Estate, Auto | IT (INR strengthens slightly) | Credit costs fall; loan growth accelerates |
| Rate hikes | PSU banks (NIM expands short-term), IT (USD strengthens) | Real Estate, NBFCs with high borrowing cost | Deposit re-pricing lags loan re-pricing |
| Rate pause | Neutral | Neutral | Market focusses on earnings |

**Nifty Bank vs Nifty IT sensitivity:**

These two sectors are the largest sectoral allocations in Nifty 50 and move in approximately opposite directions relative to:
1. **Indian interest rates:** Rate cuts → Nifty Bank up (cheaper funding, more lending); Nifty IT largely neutral (IT revenue is in USD)
2. **US interest rates:** Fed rate hikes → USD strengthens → Nifty IT earnings in INR rise (revenue translates back at better rate); Nifty Bank unaffected directly

This creates a natural pairs trade: Long Nifty Bank / Short Nifty IT futures in Indian rate-cut cycles.

---

## 8.5 India-China Trade Data and "China+1" Sector Signals

**The China+1 theme:** Post-COVID supply chain risk aversion by global manufacturers seeking to diversify away from China dependency. Sectors benefiting in India: Electronics Manufacturing (PLI scheme), Pharmaceuticals (API manufacturing), Specialty Chemicals, Textiles.

**Data sources:**
- India's monthly merchandise trade data: Commerce Ministry of India, published within 14 days of month end
- India-China bilateral trade: Import substitution signals (India import of Chinese goods declining for a category = domestic manufacturing filling in)
- FDI data: India received USD 81 billion FDI in FY2025, with manufacturing FDI growing 18% YoY

**Sector mapping for China+1:**
- **PLI (Production Linked Incentive) beneficiaries:** Dixon Technologies, Tata Electronics, Kaynes Technology, Amber Enterprises (electronics)
- **Pharma API:** Divi's Laboratories, Granules India, Laurus Labs
- **Specialty chemicals:** SRF, PI Industries, Clean Science

**Caution on execution:** India has seen more limited success than Vietnam/Thailand in capturing China+1 at scale. The signal is most actionable for specific PLI beneficiaries with confirmed orders rather than the broad thematic.

---

# Section 9: Transaction Cost Environment — Complete Detail

## 9.1 Statutory Cost Breakdown (Equity Delivery, FY 2025–26)

Complete round-trip transaction cost for a ₹1,00,000 trade in a Nifty 200 stock (delivery-based, not intraday):

| Cost Component | Rate | Buy Side | Sell Side | Total (₹) |
|---|---|---|---|---|
| STT | 0.1% on buy, 0.1% on sell | ₹100 | ₹100 | ₹200 |
| Stamp Duty | 0.015% on buy turnover only | ₹15 | ₹0 | ₹15 |
| NSE Transaction Charge | ₹2.97 per lakh | ₹2.97 | ₹2.97 | ₹5.94 |
| SEBI Turnover Fee | 0.0001% per side | ₹0.10 | ₹0.10 | ₹0.20 |
| Exchange Clearing Fee | ~₹1.50 per lakh | ₹1.50 | ₹1.50 | ₹3.00 |
| Brokerage | ~₹20 flat (Zerodha) | ₹20 | ₹20 | ₹40 |
| GST on brokerage + fees | 18% on brokerage+charges | ~₹7 | ~₹7 | ~₹14 |
| **Total Statutory + Brokerage** | | **~₹147** | **~₹131** | **~₹278** |

**Effective round-trip statutory cost (exc. spread and market impact): ~0.28% of trade value** for a ₹1,00,000 Nifty 200 delivery trade.

Note: For F&O (futures), STT is lower (0.02% on sell side for futures), but for options the STT on exercise can be significant (0.125% of intrinsic value).

---

## 9.2 Bid-Ask Spread by Universe Tier

| Universe | Typical Bid-Ask Spread | Characteristic |
|---|---|---|
| Nifty 50 | 0.01–0.05% | Near-institutional quality; algorithmic market-making |
| Nifty 100 (excl. top 50) | 0.05–0.15% | Some HFT market-making; intraday spread widens slightly |
| Nifty 200 (ranks 101–200) | 0.15–0.30% | Manual market-making; spreads widen in volatile conditions |
| Nifty 500 (ranks 201–500) | 0.30–0.70% | Significant spread; multiple ticks wide in stress |
| Outside Nifty 500 | 0.50–3.00% | Effectively no liquidity in stress; circuit-breaker risk |

---

## 9.3 Market Impact Estimation

Market impact is the price movement caused by your own order. For a stock with average daily turnover (ADT) of ₹100 crore:

$$\text{Market Impact} \approx 0.1 \times \sqrt{\frac{\text{Order Size}}{\text{ADT}}}$$

This is a square-root law (commonly used in practice). For example:
- Order size: ₹1 crore = 1% of ADT → Market impact ≈ 0.1 × √0.01 = 0.01% (negligible)
- Order size: ₹10 crore = 10% of ADT → Market impact ≈ 0.1 × √0.10 = 0.032%
- Order size: ₹100 crore = 100% of ADT → Market impact ≈ 0.1 × √1.0 = 0.10%

**Capacity rule of thumb for India:**
- Nifty 50 momentum strategy: scalable to ₹500+ crore AUM
- Nifty 200 factor portfolio (monthly rebalancing): scalable to ₹50–100 crore per factor
- Mid-cap (Nifty 200–500) factor portfolio: scalable to ₹15–30 crore before serious impact

---

## 9.4 Minimum Gross Alpha Required to Be Profitable

For a monthly-rebalanced Nifty 200 factor portfolio with 50 stocks:
- Average holding per stock: ₹2 crore (₹100 crore AUM / 50 stocks)
- Monthly turnover: ~25–30% (factor portfolios replace ~12–15 stocks per month)
- Round-trip cost per trade (spread + statutory + impact): ~0.5–0.7% for Nifty 200 stocks
- Annual turnover: ~150–200%

**Annual transaction cost drag:**
$$\text{Cost}_{\text{annual}} = \text{Turnover} \times \text{Round-trip cost} = 1.75 \times 0.6\% = 1.05\%$$

**Minimum gross alpha to justify the strategy:** Approximately **1.5–2.0% per annum** above the index, before management costs. Strategies with gross alpha < 1.5% are transaction-cost-dominated in India.

---

## 9.5 Comparison with Other Major Markets

| Market | STT/TTT | Typical Spread (Large Cap) | Total Round-Trip (Large Cap) |
|---|---|---|---|
| India (Nifty 50) | 0.20% round-trip | 0.02–0.05% | ~0.25–0.30% |
| USA (S&P 500) | 0% | 0.002–0.01% | ~0.01–0.02% |
| UK (FTSE 100) | 0.5% (stamp duty, buy only) | 0.02–0.05% | ~0.55–0.60% |
| Japan (Topix) | 0% | 0.02–0.04% | ~0.05–0.10% |
| Europe (Euro Stoxx 50) | Varies 0–0.2% by country | 0.02–0.05% | ~0.05–0.25% |

India's transaction cost environment is substantially more expensive than the US (roughly 15–20× per trade in effective cost terms) but comparable to or cheaper than the UK (if a factor requires monthly rebalancing with stamp duty implications).

---

# Section 10: Data Sources — Complete Catalogue with Python Code

## 10.1 IIMA Indian Fama-French Factor Library

**Description:** The canonical academic data source for Indian equity factors. Provides monthly factor returns (MKT, SMB, HML, MOM, RMW, CMA) for India from July 1993 onwards.

**Download:**
```python
import pandas as pd

# Direct download URL (working as of 2026)
IIMA_BASE = "https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/"

# Factor data files (check IIMA website for exact filenames — they update 3× per year)
# Typical file: Indian_FF_Factors_Monthly.csv

# Example load and usage
factors = pd.read_csv(
    IIMA_BASE + "four-factors-India-90s-onwards-IIM-WP-Version.pdf",
    # Note: the actual CSV file name must be obtained from the IIMA website directly
    index_col=0, parse_dates=True
)
# Columns: date, mkt_rf (market excess return), smb, hml, mom, rf (risk-free rate)
# All in decimal (not percent): 0.01 = 1%

# Example: compute cumulative MOM factor return
mom_cumulative = (1 + factors['mom']).cumprod()
```

**Key construction details:**
- **Portfolio formation month:** September (matching Indian fiscal year)
- **Universe:** All CMIE Prowess companies on NSE and BSE
- **Size breakpoint:** Median market cap of NSE-listed companies
- **B/M breakpoint:** 30th and 70th percentile of all companies
- **Excludes:** Financial companies in some versions (check file metadata)
- **Risk-free rate:** 91-day Treasury bill rate

---

## 10.2 Rajan Raju Factor Library

**SSRN Papers:**
- SSRN 5008269: Main library paper (November 2024) — factor data and documentation
- SSRN 4054146: Four-factor model for India
- SSRN 4190426: Five-factor model for India
- SSRN 4133389: Factor indices and style analysis
- SSRN 4587697: 52-week high effect

**What it adds over IIMA:**
1. Independent data source validation (Refinitiv Datastream vs CMIE Prowess)
2. BAB (Betting Against Beta) factor — not available in IIMA library
3. Low Volatility factor
4. Updated size classifications post-SEBI 2018 recategorisation

**Access:** Factor return data available on SSRN alongside papers. Download from SSRN paper page (right panel → supplementary materials).

---

## 10.3 jugaad-data: NSE/BSE Historical Market Data

**Installation and basic usage:**
```python
# Install
# pip install jugaad-data

from jugaad_data.nse import stock_df

# Download historical stock data
# Returns OHLCV data from NSE
reliance = stock_df(
    symbol='RELIANCE',
    from_date='2020-01-01',
    to_date='2025-12-31',
    series='EQ'  # Equity series
)

# Index data
from jugaad_data.nse import index_df
nifty_50 = index_df(
    symbol='NIFTY 50',
    from_date='2020-01-01',
    to_date='2025-12-31'
)

# Available data:
# - Historical OHLCV for all NSE equities
# - Historical index data (Nifty 50, Nifty 500, sectoral indices)
# - Corporate actions (dividends, splits, bonus)
# - IPO data
# - Bulk/block deals (via nse_large_deal_historical)
```

**Key feature:** Built-in caching mechanism reduces repeated API calls. CLI interface also available for non-Python users. Note: NSE periodically updates its API authentication mechanism; check jugaad-data GitHub for latest updates.

---

## 10.4 NSEPython

**Installation and usage:**
```python
# pip install nsepython

from nsepython import nsefetch, nsepython_get

# Option chain data
from nsepython import nse_optionchain_scrapper
option_chain = nse_optionchain_scrapper('NIFTY')

# Bulk and block deals
from nsepython import nse_large_deal_historical
bulk = nse_large_deal_historical('01-01-2023', '31-12-2023', 'bulk_deals')
block = nse_large_deal_historical('01-01-2023', '31-12-2023', 'block_deals')

# India VIX historical data
from nsepython import vix_data
vix = vix_data('01-01-2020', '31-12-2024')

# FII/DII data
from nsepython import fii_dii_data
fii_dii = fii_dii_data()  # Returns current day; use date-range version for historical

# PCR (Put-Call Ratio) from option chain
oc = nse_optionchain_scrapper('NIFTY')
total_put_oi = oc['filtered']['data'][i]['PE']['openInterest'] # sum across all strikes
total_call_oi = oc['filtered']['data'][i]['CE']['openInterest']
pcr = total_put_oi / total_call_oi
```

**Caution:** NSEPython directly scrapes NSE India's website. NSE periodically changes authentication requirements. The library may break without notice when NSE updates its API. Always pin the version and check the NSEPython GitHub for maintenance status.

---

## 10.5 BseIndiaApi

```python
# pip install bse-india-api (check PyPI for latest package name)
# GitHub: BennyThadikaran/BseIndiaApi

from bseindiaapi import BSE

bse = BSE()

# Get quote data
quote = bse.get_quote('500325')  # 500325 = Reliance Industries BSE code

# Corporate actions (dividends, bonus, splits)
actions = bse.get_corporate_actions(
    scripcode='500325',
    from_date='2020-01-01',
    to_date='2025-12-31'
)

# Shareholding pattern (SHP)
shp = bse.get_shareholding_pattern(
    scripcode='500325',
    quarter='Q3 2024-25'
)
```

---

## 10.6 Screener.in: Fundamental Data Scraping

**What's available free:**
- 10 years of quarterly and annual financial data for all NSE/BSE listed companies
- Balance sheet, P&L, cash flow statement, ratios
- Screener/filter by financial criteria (ROE > 15%, P/E < 20, etc.)
- Exportable to Excel (requires free registration)

**Data access via Python:**
```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Screener.in export URL pattern
# Note: Screener API exports require authentication
def get_screener_data(company_id: str) -> dict:
    """
    company_id: company URL slug on screener.in (e.g., 'RELIANCE')
    Returns: dict with financial data
    """
    url = f"https://www.screener.in/company/{company_id}/consolidated/"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': 'your_session_cookie_here'  # requires login
    }
    response = requests.get(url, headers=headers)
    # Parse HTML tables into DataFrames
    tables = pd.read_html(response.text)
    return tables

# Screener's screen export (most useful):
# Create a screen with criteria → Export to CSV
# URL pattern: screener.in/api/screens/{screen_id}/
```

**What Screener.in does NOT have:**
- Real-time price data
- Options data
- Intraday data
- Institutional ownership details (SHP)
- Insider trading filings

---

## 10.7 SEBI EDGAR Equivalent: NSE/BSE Filing Portals

India's equivalent of the SEC EDGAR system is split across NSE and BSE:

| Data Type | NSE URL | BSE URL |
|---|---|---|
| Shareholding Pattern (SHP) | nseindia.com/companies-listing/corporate-filings-shareholding-pattern | bseindia.com/corporates/shp.html |
| Insider Trading (PIT) | nseindia.com/companies-listing/corporate-filings-insider-trading | bseindia.com/corporates/Insider_Trading_new.aspx |
| Bulk/Block Deals | nseindia.com/report-detail/display-bulk-and-block-deals | bseindia.com/markets/MarketInfo/BulkDeals.aspx |
| Corporate Announcements | nseindia.com/companies-listing/corporate-filings-announcements | bseindia.com/corporates/ann.html |
| Financial Results | nseindia.com/companies-listing/corporate-filings-financial-results | bseindia.com/corporates/results.html |

---

## 10.8 InsiderScreener.com

**URL:** insiderscreener.com/en/india/insider-trading/

**Free features:**
- All insider trades (promoter + DP) from NSE and BSE, aggregated
- Filterable by: company, category (promoter/DP), buy/sell, date range
- Exportable to CSV (limited rows on free tier)
- Calculates "cluster buying" (multiple insiders buying same stock in short period)

**Paid features:**
- Full history without row limits
- Email alerts for specific companies or screens
- API access

**Why this is valuable:** NSE and BSE disclose insider trades but their web interfaces are clunky and not easy to programmatically query. InsiderScreener aggregates and normalises the data, making it practical for systematic signal construction.

---

## 10.9 Institutional Data Providers: Cost and Coverage

| Provider | What It Provides | Approx. Cost (2026) |
|---|---|---|
| **CMIE Prowess** | Company financials, promoter data, 45,000+ Indian companies, 25-year history | ₹50,000–5,00,000/year (university: bundled) |
| **Refinitiv (LSEG) Datastream** | Historical OHLCV, fundamentals, sector indices, global coverage | USD 15,000–40,000/year |
| **NDAL (NSE Data & Analytics)** | NSE tick data, order book history, official NSE datasets | ₹5,00,000–25,00,000/year depending on depth |
| **TrueData** | NSE/BSE real-time and historical EOD data, options data | ₹5,000–15,000/month for live + historical |
| **Bloomberg India** | Full fundamental + market data; news; analyst estimates | USD 25,000/year per terminal |
| **Ace Equity** | Screener + fundamentals; cheaper alternative to Prowess | ₹30,000–60,000/year |

**For researchers without institutional budgets:**
- Screener.in (free) + IIMA factors (free) + NSEPython/jugaad-data (free) covers approximately 80% of what you need for factor research
- TrueData (~₹10,000/month) is the most affordable route to clean, properly adjusted historical price data for systematic strategies

---

## 10.10 High-Frequency and Alternative Data

| Signal Category | Data Source | Frequency | Cost |
|---|---|---|---|
| GST E-Way Bills | ewaybill.nic.in / GSTN portal | Monthly | Free |
| Auto Sales (SIAM) | siamindia.com | Monthly | Free (press releases) |
| Auto Retail (FADA) | fadaweb.com | Monthly | Free |
| PMI Manufacturing | S&P Global / IHS Markit | Monthly | Subscription or Bloomberg |
| PMI Services | S&P Global / IHS Markit | Monthly | Subscription or Bloomberg |
| RBI Data (Money supply, credit) | rbi.org.in | Weekly / Monthly | Free |
| AMFI SIP Data | amfiindia.com | Monthly | Free |
| India VIX Historical | nseindia.com | Daily (from 2009) | Free |
| NSE F&O Bhavcopy | nseindia.com | Daily | Free (bulk download available) |
| NSE Equity Bhavcopy | nseindia.com | Daily (from 1991) | Free (archive download) |

**NSE Bhavcopy is the most valuable free dataset for systematic equity research in India:** It contains complete end-of-day OHLCV data for all NSE listed stocks, options, and futures since 1991. Available for bulk download from nseindia.com/market-data/bhav-copy archives.

---

# Appendix A: Key Paper Reference Table

| Paper | SSRN/DOI | Key Contribution | India-Specific Result |
|---|---|---|---|
| Agarwalla, Jacob & Varma (2017) | faculty.iima.ac.in/~iffm | Four-factor model for India | Momentum alpha ~17% p.a.; SMB near-zero |
| Raju (2023) | SSRN 4587697 | 52-week high effect in India | More stable than 12-1; weaker reversals |
| Sehgal et al. (2012) | SSRN 2128978 | Accruals anomaly test for India | Standard Sloan anomaly fails; sign reversed |
| Kedia (2024) | doi.org/10.1080/23322039.2024.2411567 | Six-factor model | ROE best profitability proxy; HC factor significant |
| Sharma, Subramaniam & Sehgal (2021) | Global Business Review | Anomaly fading test | HML weakening; momentum persistent |
| Gavhale (2025) | arXiv 2507.04859 | F&O expiry vs SIP timing | Expiry SIP outperforms by 0.5–2.5% annually (1–5y) |
| Raju (2024) | SSRN 5008269 | Full factor library documentation | Confirms IIMA; adds BAB, Low Vol |
| Frazzini & Pedersen (2014) | Journal of Financial Economics | BAB factor theory | Global; applied to India: BAB positive, dominated by DII distortions |
| Sehgal & Kulkarni (2018) | SCIRP Theoretical Economics Letters | PEAD in India | Robust PEAD 2002–2017; 64-day optimal window |

---

# Appendix B: India-Specific Replication Failures and Cautions

The following US-derived strategies fail, are materially weaker, or require modification for India:

| Strategy | US Evidence | India Status | Reason |
|---|---|---|---|
| Sloan Accruals (Short high-accruals) | Strong positive | **FAILS; sign reverses** | Indian investors overprice cash flows, not accruals |
| Long-short SMB (size) | 2–3% p.a. | **~0.36% p.a.; negligible** | Primarily illiquidity premium, not size |
| BAB (full leverage to beta=1) | Strong; Sharpe ~0.78 | **Moderate; weaker** | DII forced buying into index stocks supports high-beta |
| HML value factor | Strong | **Weakening post-2005** | Value = PSU banks + commodity; risk-explained not anomalous |
| Long-short pair via cash short | Fully implementable | **Not feasible overnight** | No naked short selling in cash market |
| Weekly momentum rebalancing | Works in liquid markets | **Transaction cost dominated** | 0.6%+ round-trip per trade; quarterly preferred |
| US-style earnings surprise (I/B/E/S) | Direct implementation | **Requires seasonal naive proxy** | Limited analyst coverage; I/B/E/S covers only ~100 stocks |
| High-accruals long strategy | Not a US strategy | **Works in India** | Opposite of US: high-cash-flow stocks are the buy signal |

---

# Appendix C: Regulatory Calendar — Key Dates for Signal Construction

| Event | Timing | Signal Relevance |
|---|---|---|
| Quarterly earnings (NSE 500) | Q1: July–Aug; Q2: Oct–Nov; Q3: Jan–Feb; Q4: May–Jun | PEAD signal; SUE construction |
| SHP filing deadline | Within 21 days of quarter end | Promoter pledging; FPI accumulation signal |
| Insider trade disclosure deadline | Within 2 trading days of trade | Insider buying signal |
| AMFI SIP data | Monthly, first week | SIP floor calibration for DII signal |
| GST e-way bills | Monthly, ~15 days lag | Macro/sector rotation signal |
| Auto sales SIAM | Monthly, first week | Auto sector signal |
| RBI MPC policy | 6 times/year; approx. bi-monthly | Rate sensitivity sector rotation |
| NSE F&O expiry | Last Monday of month (from April 2025) | F&O expiry effect; max pain |
| SEBI AMFI market cap list | Semi-annually (March/September) | Universe definition update |
| Union Budget | First Tuesday of February | High-uncertainty period; max pain unreliable |

---

*End of Document*

*Sources consulted in preparation of this reference document:*

*Academic papers:*
- *Agarwalla, S.K., Jacob, J. & Varma, J.R. — IIMA Four-Factor India Model (faculty.iima.ac.in/~iffm)*
- *Raju, R. (2023) — "The 52-Week High Effect and Momentum Investing: Evidence from India." SSRN 4587697*
- *Raju, R. (2024) — "Indian Equity Factor Library." SSRN 5008269*
- *Sehgal, S., Subramaniam, S. & Deisting, F. (2012) — "Testing the Accruals and Cash Flows Anomalies for the Indian Stock Market." SSRN 2128978*
- *Kedia (2024) — "Superiority of Six Factor Model in Indian Stock Market." Cogent Economics & Finance. doi:10.1080/23322039.2024.2411567*
- *Sharma, G., Subramaniam, S. & Sehgal, S. (2021) — "Are Prominent Equity Market Anomalies in India Fading Away?" Global Business Review*
- *Gavhale, S. (2025) — "F&O Expiry vs. First-Day SIPs: A 22-Year Analysis." arXiv:2507.04859*
- *Sehgal & Kulkarni (2018) — "Post-Earnings-Announcement Drift Anomaly in India: A Test of Market Efficiency." SCIRP Theoretical Economics Letters*
- *Frazzini, A. & Pedersen, L.H. (2014) — "Betting Against Beta." Journal of Financial Economics. SSRN 2049939*
- *IIMA — "Betting Against Beta in the Indian Market." IIMA Working Paper*

*Regulatory sources:*
- *NSE India: nseindia.com (circuit breakers, T+1 settlement, F&O rules, India VIX methodology)*
- *SEBI: sebi.gov.in (algo trading circular, PIT regulations, MF recategorisation circular 2017)*
- *AMFI: amfiindia.com (SIP data, market cap classification)*

*Data source documentation:*
- *jugaad-data: github.com/jugaad-py/jugaad-data*
- *NSEPython: pypi.org/project/nsepython; unofficed.com/nse-python/*
- *BseIndiaApi: github.com/BennyThadikaran/BseIndiaApi*
- *CMIE Prowess: prowess.cmie.com*
- *InsiderScreener: insiderscreener.com/en/india/insider-trading/*
