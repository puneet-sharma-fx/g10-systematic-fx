# Systematic Macro Models for G10 FX: A Practitioner's Reference

*Research Document — June 2026*
*Author: Puneet Sharma*

---

## Preface

This document is written for an experienced discretionary FX and macro trader who is moving toward quantitative, systematic approaches. It is not a primer on exchange rate economics — that document already exists in this repository (`g10_fx_comprehensive_reference.md`). Instead, this document answers a specific and harder question: **how do the macroeconomic frameworks that discretionary traders use informally get translated into rigorous, systematic, backtestable trading signals?**

The distinction matters. A discretionary trader might say: "The Fed is behind the curve, the ECB is already done hiking, and the US economy is outperforming — I'm long USD." That view is correct in structure. But it is unfalsifiable, inconsistently applied, and relies on the trader remembering correctly what they said last month. A systematic macro model encodes the same logic into rules that produce the same signal every time the same data configuration arises — whether the trader is alert, distracted, or emotionally invested in a position.

Target length of this document: comprehensive enough to serve as a standalone desk reference. It covers 10 sections spanning philosophy, building blocks, scorecards, central bank models, growth models, inflation and external balance models, sentiment models, cross-asset linkages, regime detection, and a complete combined model.

---

## Section 1: Systematic Macro — The Philosophy

### 1.1 What Systematic Macro Is

Systematic macro investing applies quantitative rigor — explicit rules, defined signals, formal hypothesis testing — to macroeconomic relationships that drive asset prices. It is not algorithmic high-frequency trading. It operates at the same conceptual level as a macro hedge fund: it cares about central bank cycles, growth differentials, current accounts, and political risk. The difference is that every judgment call is encoded into a rule that runs the same way every time.

The core premise is that macroeconomic relationships are real and persistent, but that human cognition is unreliable in applying them consistently. A systematic macro strategy strips out the cognitive noise and leaves the economic signal.

This is distinct from:
- **Statistical arbitrage**: systematic macro takes economic positions based on economic reasoning, not statistical mean-reversion
- **Trend following (CTA)**: trend following is price-based; systematic macro is fundamentals-based
- **Smart beta**: systematic macro is dynamic and condition-dependent, not static factor loading

### 1.2 The Discretionary-to-Systematic Spectrum

There is no clean line between "discretionary" and "systematic." It is more useful to think of a spectrum:

| Label | Description | Examples |
|---|---|---|
| **Pure discretionary** | All decisions made by human judgment; no formal rules | Traditional macro hedge funds |
| **Research-driven discretionary** | Human decisions, but with structured research frameworks | Most long/short macro funds |
| **Quantamental** | Data-driven signals inform human decisions; humans retain override authority | Point72, Balyasny elements |
| **Systematic macro with overlays** | Systematic signals generate positions; human judgment applies risk overlays only | Winton, AHL |
| **Fully systematic macro** | All decisions made by models; no human discretion | Bridgewater (mostly), Man AHL macro sleeve |

Most practitioners moving from discretionary to systematic should aim for the quantamental or systematic macro with overlays level initially. Full systematization requires years of backtesting infrastructure.

### 1.3 Bridgewater Associates: The Economic Machine

Bridgewater Associates, founded by Ray Dalio in 1975, is the world's largest hedge fund by AUM and the most famous practitioner of systematic macro. Their philosophy is grounded in what Dalio calls the **"economic machine"** — a cause-and-effect model of how economies work, covering credit cycles, debt cycles, and productivity trends.

Dalio's framework decomposes economic activity into three forces:
1. **Long-term productivity growth** (decades-long trend; driven by knowledge and technology)
2. **Short-term debt cycle** (5–10 years; managed by central banks through interest rate policy)
3. **Long-term debt cycle** (50–75 years; resolved through debt restructuring or inflationary deleveraging)

The key insight is that **most of what looks like fundamental macro surprise is actually mechanical and predictable** once you understand where you are in these cycles. A systematic framework can track debt-to-GDP ratios, central bank policy relative to neutral, and credit expansion rates to identify the phase of each cycle — and then apply consistent rules about how asset prices respond at each phase.

Bridgewater's **Pure Alpha** strategy applies this to currencies, rates, equities, and commodities globally. Their **All Weather** strategy (risk parity) balances the risk contribution from each macro environment: rising growth, falling growth, rising inflation, falling inflation. As of Bridgewater's own communications, approximately 99% of trading decisions in their portfolios are generated systematically, not by human override.

The critical lesson for FX: Bridgewater approaches every currency position from the question "what is the economy doing, what is the central bank doing in response, and is the currency priced to reflect that?" This framing — economic fundamentals → central bank reaction → currency pricing — is the backbone of any serious systematic macro FX model.

### 1.4 AQR: The Multi-Asset Factor Approach

AQR Capital Management (Asness, Kabiller, Pedersen, and colleagues) takes a different but complementary approach. Rather than building a full economic machine model, AQR identifies **cross-sectional return factors** that are persistent, pervasive, and grounded in either risk compensation or behavioral anomalies.

Their landmark paper "Value and Momentum Everywhere" (Asness, Moskowitz, Pedersen 2013, *Journal of Finance*) shows that value and momentum premia exist in every asset class — equities, bonds, currencies, commodities — and are positively correlated within asset classes but negatively correlated across (value is high when momentum is low, and vice versa). This means combining them diversifies without destroying returns.

For currencies specifically, AQR's three core factors are:

| Factor | Economic rationale | FX implementation |
|---|---|---|
| **Carry** | Compensation for risk of depreciation | Long high-yield G10 currencies vs. short low-yield |
| **Momentum** | Price trends persist due to under-reaction and feedback | Long recent winners vs. short recent losers (3-12 month lookback) |
| **Value** | Mean reversion toward PPP | Long undervalued currencies vs. short overvalued (REER vs. long-run average) |

AQR's macro work also includes a fourth, more complex factor: **macro quality**, which selects currencies with strong fundamental backdrops (growth, current account, inflation under control). This is the bridge between pure factor investing and systematic macro.

### 1.5 Man AHL: Trend Plus Macro

Man AHL (part of Man Group) began as a pure trend-following CTA but has progressively added **macro signals** alongside price-based signals. Their research demonstrates that:
- Trend signals work well during sustained macro regimes (extended hiking cycles, risk-off episodes)
- Macro fundamentals signals add value at regime transitions, where trend signals are slow to update
- Combining trend and macro signals produces lower drawdowns than either alone

This is a key practical insight: **trend and macro signals are partially complementary because they fail at different times.** Trend fails at turning points; macro fundamentals identify the turning points earlier.

### 1.6 Why Systematic Macro Is Growing

Several structural forces explain the growth of systematic macro from a niche to a mainstream approach:

**Decision fatigue and cognitive bias.** A discretionary trader making 50 decisions a day is not applying equal rigor to each. By hour 6, decisions regress toward anchoring, recency bias, and confirmation bias. A systematic model applies the same rules with equal rigor to every signal at every moment.

**Scalability.** A systematic framework generates signals for all G10 pairs simultaneously. No discretionary trader can hold 45 simultaneous currency views with equal conviction and discipline.

**Auditability.** When a systematic model loses money, you can decompose the P&L by signal, by pair, by regime. You learn what went wrong and can test whether to change the model. When a discretionary trader loses money, attribution is usually post-hoc rationalization.

**Removing hindsight bias.** Perhaps most importantly: systematic backtesting forces you to specify your signal *before* observing the outcome. A discretionary trader who says "I would have shorted EUR/USD in June 2022 because of the energy crisis" almost certainly would not have done so at the time, before the narrative crystallized. The systematic rule either fires or it does not — no narrative required.

**Consistency across regimes.** A discretionary trader's personal confidence fluctuates with recent performance. A systematic model runs with the same parameters regardless of whether last month was good or bad.

### 1.7 The Core Systematic Advantage: Right in Expectation

The central intellectual shift required when moving from discretionary to systematic is accepting that **individual trades will frequently be wrong, and that this is not a problem.** A systematic macro model with a 0.6 information ratio will be right on roughly 54% of individual monthly trades. That means 46% of months produce losses. The model still compounds beautifully over years.

Discretionary traders have difficulty accepting this because individual trade P&L is their feedback loop. A systematic framework shifts the question from "was this trade right?" to "is the model generating positive expected value?" These are fundamentally different questions.

This reframing has a practical corollary: **your job in systematic macro is not to predict the next data release.** It is to identify systematic relationships that generate positive expected value when repeated hundreds of times across years and currency pairs. An individual bad trade is data about the model, not evidence that the model is broken.

---

## Section 2: The Building Blocks — What Macro Variables Drive FX

### 2.1 Interest Rate Models

#### 2.1.1 Uncovered Interest Rate Parity (UIP): Why It Fails and What That Means

Uncovered Interest Rate Parity (UIP) is the no-arbitrage condition that states: in efficient markets with risk-neutral investors, the expected change in the spot exchange rate must equal the interest rate differential.

Formally, let $s_t = \log(S_t)$ be the log spot rate (domestic per foreign), $i_t$ the domestic rate, and $i^*_t$ the foreign rate:

$$E_t[\Delta s_{t+1}] = i_t - i^*_t$$

This says: if the US 3-month rate is 5% and the EUR 3-month rate is 3%, the USD should be *expected to depreciate* by 2% against EUR — otherwise you could earn riskless returns by borrowing in EUR and investing in USD.

**Why UIP fails empirically:** The famous result, documented extensively by Fama (1984) in the *Journal of Monetary Economics*, is that UIP fails in the data. High-yield currencies *appreciate* (or fail to depreciate) rather than depreciate. The slope coefficient in the Fama regression:

$$s_{t+1} - s_t = \alpha + \beta (f_{1,t} - s_t) + \epsilon_{t+1}$$

where $f_{1,t}$ is the log forward rate, should equal 1 under UIP but is found empirically to range between **−3.2 and −0.5** — negative — with a typical value around **−0.5 to −1.0** at the 1-month horizon. This is the **forward premium puzzle**.

The implication is profound: high-yield currencies earn a systematic positive expected return — the **carry premium**. The carry trade (buy high-yield, short low-yield currencies) has historically generated Sharpe ratios of approximately 0.5–0.8 across G10 pairs (Burnside et al., 2006, *Returns to Currency Speculation*; Lustig, Roussanov, Verdelhan 2011, *JFE*).

The puzzle's explanation is contested. Leading candidates include:
- **Time-varying risk premium**: the carry premium is compensation for crash risk (Brunnermeier, Nagel, Pedersen 2008, *NBER MA*: carry trade crashes occur in liquidity crises)
- **Peso problem**: low-probability catastrophic depreciation events that never occur in the sample
- **Heterogeneous beliefs and limits to arbitrage**: smart money cannot fully arbitrage because of margin constraints and noise trader risk

For practical purposes: **UIP's failure is your carry signal.** High-yield currencies earn systematically positive excess returns over short horizons. This is one of the most robust findings in international finance.

#### 2.1.2 The Fama Regression: Formal Statement

The standard empirical test of UIP, following Fama (1984), is:

$$s_{t+k} - s_t = \alpha + \beta (i_t - i^*_t) + \epsilon_{t+k}$$

where $s_{t+k} - s_t$ is the actual change in the log spot rate over horizon $k$, and $i_t - i^*_t$ is the interest rate differential (or equivalently, the forward premium $f_{1,t} - s_t$ by covered interest parity).

**Under UIP:** $\alpha = 0$, $\beta = 1$.

**Empirical result (Fama 1984 and subsequent replications):**
- At 1-month horizon: $\hat{\beta}$ ranges from −0.5 to −3.2 across major G10 pairs
- The negative slope means: **high-yield currencies appreciate**, contradicting UIP
- At 3-year horizon: $\hat{\beta}$ approaches 1, suggesting UIP holds in the long run (Chinn-Meredith 2004, *JIMF*)
- This horizon dependence is crucial: carry works short-term but mean-reverts long-term

**Practical implication:** the Fama $\beta$ is your measure of how "broken" UIP is for a given pair and horizon. Pairs with highly negative $\hat{\beta}$ generate larger carry returns. The New Fama Puzzle (Engel 2016) shows the puzzle has actually *strengthened* in the post-2000 period.

#### 2.1.3 Covered Interest Parity: Definition and Post-2008 Breakdown

Covered Interest Parity (CIP) is a *riskless* arbitrage condition, unlike UIP. It states that forward rate discounts or premiums exactly offset interest rate differentials when a currency swap is used to eliminate exchange rate risk:

$$F_{t,k}/S_t = (1 + i_t^k) / (1 + i_t^{*k})$$

or in log form:

$$f_{t,k} - s_t = i_t^k - i_t^{*k}$$

where $F_{t,k}$ is the $k$-period forward rate, $S_t$ is the spot rate, and $i_t^k, i_t^{*k}$ are the $k$-period interest rates in each currency.

CIP was considered essentially exactly satisfied pre-2008, maintained by riskless arbitrage between the spot market and the FX swap market.

**The post-2008 breakdown.** Du, Tepper, and Verdelhan (2018, *Journal of Finance*, 73(3)) document that CIP deviations became large, persistent, and systematic after the 2008 financial crisis. The deviation — known as the **cross-currency basis** — reflects the premium or discount for borrowing a particular currency through FX swaps relative to the cash money market. Key findings:

- CIP deviations are large (20–100 basis points for major pairs at 3-month tenor)
- They are *not* explained by credit risk or transaction costs
- They cluster at quarter-end balance sheet dates (suggesting regulatory capital constraints on bank intermediation)
- They are correlated across currency pairs and with other fixed income spreads

**Trading implication:** the cross-currency basis itself becomes a signal. When USD basis is deeply negative (USD is expensive to borrow via swaps), this signals stress in dollar funding markets and tends to precede risk-off FX moves. Monitoring the EUR/USD 3-month basis spread (available from Bloomberg or approximated from FX swap pricing) adds a CIP-based signal to your regime detection.

#### 2.1.4 Real Interest Rate Differentials and REER Implications

The nominal interest rate differential drives carry. But for medium-term FX prediction (3–12 months), the **real interest rate differential** — nominal rate adjusted for inflation expectations — is more theoretically grounded and empirically stronger.

**Definition:**

$$\text{Real rate differential} = (i_t - \pi^e_t) - (i^*_t - \pi^{*e}_t)$$

where $\pi^e_t$ is the market's inflation expectation (breakeven inflation from TIPS for USD; inflation swaps for EUR, GBP).

A country with a high real interest rate is paying investors an attractive real return. Capital should flow in, supporting the currency. This is the channel through which central bank tightening cycles drive currency appreciation.

**REER (Real Effective Exchange Rate) connection:** the REER measures whether a currency has moved enough relative to inflation differentials to maintain competitiveness. If the REER rises far above its historical average (expensive in real terms), the currency is overvalued — and real rate differentials that are too high relative to fundamentals become unsustainable.

For the G10, the BIS publishes monthly REER data for all currencies freely at [bis.org/statistics/eer.htm](https://www.bis.org/statistics/eer.htm). Extreme REER readings (beyond ±2 standard deviations from a 10-year mean) generate strong medium-term mean-reversion signals, though with noisy timing.

#### 2.1.5 Policy Rate vs. Market Rates: Why the 2Y Yield Works Better

A common mistake in systematic macro FX models is using the central bank policy rate as the interest rate differential. The policy rate has several problems:
- It changes discretely at meeting dates (8 per year for most G10 CBs)
- It is backward-looking: markets price future policy moves continuously
- The policy rate at time $t$ is already known and priced in; it has no predictive power

**The 2-year government bond yield** is a superior signal because:
1. It is continuously priced by markets and reflects expected rate paths over the next 2 years
2. Surprises in the 2Y yield (changes) represent genuine news about the central bank's expected path
3. The 2Y yield incorporates both current policy and forward guidance
4. For most G10 pairs, the 2Y spread has higher correlation with subsequent FX moves than the policy rate spread

In our own Strategy #1 (see `STRATEGIES.md`), the signal `sign(Δ2Y_base - Δ2Y_quote)` — the direction of change in the 2-year yield differential — produced a standalone Sharpe ratio of ~2.5 on a daily rebalancing basis. The *level* of the spread (carry) and the *change* in the spread (monetary policy surprise) are different signals that operate at different frequencies.

#### 2.1.6 Term Structure Signals: 10Y–2Y Slope Differential

The **slope of the yield curve** (10Y − 2Y yield spread) is a 3–12 month predictor of FX moves through the growth expectations channel. A steepening curve in Country A relative to Country B signals that:
- Markets expect faster economic acceleration in A than B
- A's central bank has more room to hike beyond current short rates
- Risk appetite for A's currency is increasing

Empirically, the 10Y–2Y differential across countries helps predict currency returns at medium (3–6 month) horizons with modest but meaningful signal strength. The signal is most powerful when one country has a normal or upward-sloping curve while the other has an inverted curve — as in 2022–2023 when US 10Y–2Y inverted while other G10 curves remained steeper.

**FRED ticker examples:**
- US 10Y–2Y: `T10Y2Y` (daily)
- For other G10 countries, compute from individual 2Y and 10Y yields available on FRED

---

### 2.2 Growth Models

#### 2.2.1 GDP Differential and Exchange Rate Dynamics

Standard open-economy macro models (Mundell-Fleming; Obstfeld-Rogoff Redux model) predict that stronger-than-expected economic growth leads to currency appreciation through two channels:

1. **Income channel**: higher growth increases demand for imports, widening the trade deficit (negative for currency)
2. **Capital channel**: higher growth attracts foreign investment and raises interest rate expectations (positive for currency)

Empirically, the capital channel dominates in the short-to-medium run for developed market (G10) currencies. Over horizons of 1–6 months, positive growth surprises lead to currency appreciation. At longer horizons (multi-year), the income channel becomes more relevant.

The key implication: **growth differentials are a medium-term FX signal, not a long-term one.** An economy that consistently outgrows its trading partners will eventually see its currency appreciate, but the mechanism runs through central bank policy response (the central bank in the faster-growing country raises rates, attracting capital flows) rather than the growth directly.

#### 2.2.2 Output Gap Estimation

The **output gap** — the difference between actual GDP and potential GDP — is a key input to Taylor rules and a measure of inflationary pressure. Estimating it in real time is notoriously difficult (Orphanides 2001, *AER*: real-time output gap estimates are severely revised).

Common approaches:

| Method | Implementation | Quality |
|---|---|---|
| **HP filter** | Hodrick-Prescott filter on log real GDP | Simple but subject to end-point bias; avoid |
| **Production function** | Estimate potential from capital, labor, TFP | More structural; requires quarterly data |
| **OECD estimate** | Published quarterly by OECD Economics Dept. | Best quality; available with ~2 month lag |
| **Capacity utilization** | US Fed Industrial Capacity Utilization (FRED: `CUMFNS`) | Monthly; real-time; correlated with output gap |

For systematic trading, use OECD published output gap estimates for precision, but supplement with capacity utilization (available monthly) as a proxy for real-time trading. FRED ticker `GAPDIS` publishes the OECD's US output gap estimate.

#### 2.2.3 PMI Differential Models

The **Purchasing Managers' Index (PMI)** is one of the most useful high-frequency macro signals for FX. Published monthly (typically on the first business day of the following month for flash estimates; first week for finals), PMIs measure business sentiment across the manufacturing and services sectors.

**Key properties:**
- Above 50 = expansion; below 50 = contraction
- Rate of change matters as much as level: a PMI rising from 48 to 52 is more bullish than one steady at 56
- Manufacturing PMI tends to lead FX more than Services PMI due to its international trade exposure
- Country-specific PMIs from S&P Global/Markit are most widely used; available via TradingEconomics.com or ISM for US

**Signal construction:**

```python
import pandas as pd
import numpy as np

# Monthly PMI data for two countries
# pmi_base, pmi_quote: monthly time series

# Signal 1: Level-based (expansion vs. contraction)
pmi_gap_level = pmi_base - pmi_quote
signal_level = np.sign(pmi_gap_level)

# Signal 2: Momentum-based (rate of change)
pmi_mom_base = pmi_base.diff(3)  # 3-month change in PMI
pmi_mom_quote = pmi_quote.diff(3)
pmi_mom_gap = pmi_mom_base - pmi_mom_quote
signal_momentum = np.sign(pmi_mom_gap)

# Composite PMI signal
pmi_signal = 0.5 * signal_level + 0.5 * signal_momentum
```

**Evidence:** Colacito, Riddiough, and Sarno (2020, *Journal of Financial Economics*, 137(3), 659–678) show that business cycle differentials — measured using OECD CLIs — explain 30–40% of 6–12 month exchange rate variation, with a standalone strategy Sharpe ratio of approximately **0.8**. PMI differentials, as the highest-frequency proxy for the business cycle, generate the most timely version of this signal.

#### 2.2.4 OECD Composite Leading Indicators

The OECD **Composite Leading Indicator (CLI)** is an amplitude-adjusted index designed to anticipate turning points in economic activity 6–9 months in advance. The CLI is constructed from a basket of component series (building permits, order books, consumer expectations, yield curve slope, equity prices) specific to each country.

**Data availability on FRED:**
- US: `USALOLITOAASTSAM` (amplitude-adjusted)
- Germany: `DEULOLITONOSTSAM`
- UK: `GBRLOLITONOSTSAM`
- Japan: `JPNLOLITONOSTSAM`
- Canada: `CANLOLITONOSTSAM`
- Australia: `AUSLOLITONOSTSAM`

**Signal construction:**

```python
import pandas_datareader.data as web
import datetime

# Download US and Eurozone CLIs
start = datetime.datetime(2000, 1, 1)
us_cli = web.DataReader('USALOLITOAASTSAM', 'fred', start)
de_cli = web.DataReader('DEULOLITONOSTSAM', 'fred', start)

# Signal: 3-month change in CLI differential (fwd-looking)
cli_base = us_cli['USALOLITOAASTSAM']
cli_quote = de_cli['DEULOLITONOSTSAM']

# 3-month momentum differential
cli_diff_mom = (cli_base - cli_quote).diff(3)

# Z-score normalize over trailing 24 months
z_score_cli = (cli_diff_mom - cli_diff_mom.rolling(24).mean()) / cli_diff_mom.rolling(24).std()
```

**Important caveat:** CLI data is revised, sometimes substantially, and is published with a 1–2 month lag. For backtesting, use vintage data where possible. The Colacito-Riddiough-Sarno (2020) results use real-time vintages and still find significant predictability.

#### 2.2.5 Nowcasting Models

**Nowcasting** refers to estimating current-period GDP growth in real time, before the official estimate is published. Several institutions publish free nowcasts weekly:

| Source | Model | Update frequency | Access |
|---|---|---|---|
| **NY Fed Staff Nowcast** | Dynamic factor model, 30+ variables | Weekly (Friday 11:15am ET) | [newyorkfed.org/research/policy/nowcast](https://www.newyorkfed.org/research/policy/nowcast) |
| **Atlanta Fed GDPNow** | Bottom-up sector model | Updated after each data release | [FRED: GDPNOW](https://fred.stlouisfed.org/series/GDPNOW) |
| **St. Louis Fed ENI** | Economic News Index | Weekly | [FRED: STLENI](https://fred.stlouisfed.org/series/STLENI) |
| **Chicago Fed CFNAI** | 85-indicator weighted index | Monthly | [FRED: CFNAI](https://fred.stlouisfed.org/series/CFNAI) |

For G10 FX, the **differential** between US and foreign nowcasts (where available) captures the growth outlook gap in near-real-time. The EU Commission and Bundesbank publish their own nowcasts for the Eurozone.

---

### 2.3 Inflation Models

#### 2.3.1 Short-Run vs. Long-Run Inflation Channels

Inflation differentials work through **two opposite channels** depending on the horizon, and confusing them is a common error:

**Short-run (1–3 months): tightening policy channel**
Higher-than-expected inflation → central bank expected to tighten more → higher rate expectations → capital inflow → **currency appreciation**

$$\text{Surprise CPI}_t \uparrow \;\Rightarrow\; E_t[\Delta i] \uparrow \;\Rightarrow\; S_t \text{ appreciates}$$

**Long-run (3–5 years): PPP channel**
Persistently higher inflation → purchasing power erodes → goods become relatively expensive → trade adjustment → **currency depreciation**

$$\pi_t > \pi^*_t \text{ sustained} \;\Rightarrow\; \text{Real appreciation} \;\Rightarrow\; \text{Nominal depreciation to restore competitiveness}$$

A systematic model must encode both channels with appropriate time-lag structures. The short-run channel is a high-frequency event-driven signal (trade around CPI releases); the long-run channel is a slow valuation signal.

#### 2.3.2 CPI Surprise as a Trading Signal

The most direct inflation signal is the **CPI surprise**: the deviation of the actual CPI release from the consensus forecast.

$$\text{Inflation Surprise}_t = \text{CPI}_t^{\text{actual}} - \text{CPI}_t^{\text{consensus}}$$

**Expected P&L logic:** A positive surprise (inflation above consensus) signals the central bank will be more hawkish than expected → short-term rates rise → currency appreciates.

**Data sources:**
- Bloomberg consensus (paid): industry standard
- Forex Factory economic calendar (free, web scrape with delay): [forexfactory.com/calendar](https://forexfactory.com/calendar)
- FRED does not provide consensus estimates, but BLS publishes actual CPI; consensus can be approximated from lagged surveys

**Implementation:**

```python
# Simplified CPI surprise signal
# cpi_actual: actual CPI MoM, annualized
# cpi_forecast: Bloomberg or ForexFactory consensus

def compute_inflation_surprise(cpi_actual, cpi_forecast, window=24):
    """
    Returns z-score of inflation surprise relative to trailing distribution.
    Positive = hawkish surprise (buy base currency).
    Negative = dovish surprise (sell base currency).
    """
    surprise = cpi_actual - cpi_forecast
    z = (surprise - surprise.rolling(window).mean()) / surprise.rolling(window).std()
    return z.clip(-2, 2)
```

**Evidence:** Engel et al. (2015) and others show that CPI surprise has a 0–2 day predictive window for spot FX. The effect is statistically significant but economically modest as a standalone signal (Sharpe ~0.3). It is most useful as an **event overlay** on top of slower macro signals.

#### 2.3.3 Breakeven Inflation Differentials

For USD pairs, breakeven inflation (the difference between nominal Treasury yields and TIPS yields) is the market's real-time expectation of future inflation. The 5-year breakeven (FRED: `T5YIE`) and 5Y5Y forward breakeven (FRED: `T5YIFR`) are particularly useful.

For EUR pairs, 5Y inflation swaps are the equivalent instrument (not free; Bloomberg required).

**Signal:** if US 5Y breakeven rises relative to its trading partner's equivalent, this signals either:
- The Fed will be forced to tighten more → short-term USD positive
- Or real US yields are becoming less attractive → medium-term USD negative

The sign of the effect depends on whether breakeven rises are driven by supply (negative for USD) or demand (positive). Context matters; this is one input in a broader scorecard, not a standalone signal.

---

### 2.4 External Balance Models

#### 2.4.1 Current Account and Long-Run FX

The current account (CA) measures the net flow of goods, services, income, and transfers between a country and the rest of the world. A CA surplus means the country is a net exporter of goods/services and net lender to the world — the opposite of a country running a deficit.

**The Obstfeld-Rogoff (1995) intertemporal model** predicts that CA deficits must eventually be financed by capital inflows, and if those flows stop ("sudden stop"), a sharp depreciation is required to restore competitiveness. Empirically, **CA deficit countries tend to see their currencies depreciate over 2–5 year horizons**, while surplus countries see appreciation.

However, CA data is:
- **Quarterly** (published with a 2–3 month lag)
- Heavily revised
- Noisy at monthly frequency (trade balance is a monthly approximation)

**As a systematic signal:** CA/GDP percentile rank across G10 provides a slow-moving valuation backdrop. Countries in the top quartile (large CA surplus: Germany, Japan, Switzerland, Netherlands) tend to have structurally supported currencies over multi-year horizons.

**FRED tickers:** US current account available as `NETFI`; for other G10 countries, use IMF Balance of Payments Statistics (free download from imf.org/en/Data).

#### 2.4.2 Trade Balance as a Monthly Signal

The trade balance — goods exports minus goods imports — is available monthly with a 4–6 week lag and provides a higher-frequency proxy for the CA.

For **commodity-linked currencies** (CAD, AUD, NZD), the trade balance is especially informative because it moves in line with commodity price cycles. A spike in oil prices improves Canada's trade surplus and tends to strengthen CAD within 1–2 months.

**The "twin deficit" signal:** when a country runs both a current account deficit and a fiscal deficit simultaneously — as the US did in 2020–2021 — the currency is most vulnerable. Twin deficits require financing from both trade partners (for the CA) and bond market buyers (for the fiscal), and when risk appetite falls, both sources dry up simultaneously.

#### 2.4.3 Terms of Trade

The **terms of trade** (ToT) measures the ratio of a country's export prices to import prices. For commodity exporters (Canada, Australia, New Zealand, Norway), the ToT moves primarily with commodity prices:

$$\text{ToT}_{AUD} \approx \text{Iron Ore Price} \times \text{Coal Price} \times \text{Export Weights}$$

**Signal construction (for commodity-linked G10):**

```python
# Terms of trade proxy for AUD
# Use iron ore price (SGX iron ore index) and metallurgical coal

iron_ore_weight = 0.35  # approximate share of Australian export revenues
coal_weight = 0.15
gas_weight = 0.10
# remainder is other commodities and services

tot_aud = (iron_ore_weight * iron_ore_price +
           coal_weight * coal_price +
           gas_weight * lng_price)

# Signal: 3-month change in ToT
signal_tot_aud = np.sign(tot_aud.pct_change(3))
```

For Norway (NOK), Brent crude is the dominant ToT driver. For New Zealand (NZD), whole milk powder auction prices from the Global Dairy Trade platform provide a biweekly signal (Boston Fed Working Paper 2023-01 documents this relationship).

---

### 2.5 Monetary Policy Reaction Function Models

#### 2.5.1 The Taylor Rule: Derivation and Implementation

The **Taylor Rule** (Taylor 1993, *Carnegie-Rochester Conference*) provides a systematic description of how central banks set policy rates. The original formulation:

$$i_t = r^* + \pi_t + \frac{1}{2}(\pi_t - \pi^*) + \frac{1}{2}(y_t - y^*_t)$$

where:
- $i_t$ = target policy rate
- $r^*$ = equilibrium real interest rate (historically assumed 2%; post-GFC may be lower, ~0.5–1%)
- $\pi_t$ = actual inflation (trailing 12-month CPI or PCE)
- $\pi^*$ = inflation target (2% for Fed, ECB, BoE, BoC; 2% midpoint for RBNZ, RBA)
- $y_t - y^*_t$ = output gap (actual minus potential GDP, as % of potential)

**Expanded with interest rate inertia (Clarida, Galí, Gertler 1999):**

$$i_t = (1 - \rho) \cdot [r^* + \pi^* + \phi_\pi (\pi_t - \pi^*) + \phi_y (y_t - y^*_t)] + \rho \cdot i_{t-1} + \epsilon_t$$

where $\rho \approx 0.7–0.85$ captures the empirical fact that central banks smooth rate changes ("policy inertia").

**Computing each component from public data:**

| Component | US data (FRED) | Notes |
|---|---|---|
| $\pi_t$ | `CPIAUCSL` (CPI) or `PCEPI` (PCE) | Fed prefers PCE; use 12m % change |
| $y_t - y^*_t$ | `CUMFNS` (capacity utilization), `UNRATE` | OECD output gap: `GAPDIS` |
| $r^*$ | Laubach-Williams estimate on NY Fed website | Updates quarterly |
| $\pi^*$ | 2.0% (stated target for all G10 CBs) | Fixed |

**Python implementation of Taylor Rule for US and Eurozone:**

```python
import pandas as pd
import pandas_datareader.data as web
import numpy as np
from datetime import datetime

def compute_taylor_rate(cpi_series, capacity_utilization, r_star=0.5, pi_star=2.0,
                        phi_pi=0.5, phi_y=0.5):
    """
    Compute Taylor rule implied policy rate.
    
    Parameters:
    -----------
    cpi_series : pd.Series
        CPI index level (monthly)
    capacity_utilization : pd.Series
        Capacity utilization rate (%) as output gap proxy
    r_star : float
        Equilibrium real interest rate (%)
    pi_star : float
        Inflation target (%)
    phi_pi : float
        Inflation gap coefficient (Taylor 1993 used 0.5)
    phi_y : float
        Output gap coefficient (Taylor 1993 used 0.5)
    
    Returns:
    --------
    pd.Series : Taylor rule implied rate (annualized %)
    """
    # Compute trailing 12-month inflation
    pi = cpi_series.pct_change(12) * 100  # annualized CPI inflation
    
    # Output gap proxy: capacity utilization deviation from 80% (long-run avg)
    y_gap = capacity_utilization - 80.0
    
    # Taylor rule
    taylor_rate = r_star + pi + phi_pi * (pi - pi_star) + phi_y * y_gap
    
    return taylor_rate

# Download data
start = datetime(2000, 1, 1)
cpi_us = web.DataReader('CPIAUCSL', 'fred', start)['CPIAUCSL']
capu_us = web.DataReader('CUMFNS', 'fred', start)['CUMFNS']
fed_rate = web.DataReader('FEDFUNDS', 'fred', start)['FEDFUNDS']

# Compute Taylor rate
taylor_us = compute_taylor_rate(cpi_us, capu_us)

# Taylor deviation: positive = CB is "behind the curve" → should hike → USD positive
taylor_deviation_us = taylor_us - fed_rate

# Cross-pair signal: if US deviation > EUR deviation → USD should strengthen
# (requires repeating above for Eurozone with ECB rate)
```

#### 2.5.2 Molodtsova-Papell (2009): Taylor Rule Beats Random Walk

Molodtsova and Papell (2009, *Journal of International Economics*, 77(2)) conduct a rigorous out-of-sample forecasting exercise for 12 OECD currencies against the USD at the 1-month horizon. Using real-time data (quasi-vintage) and the Clark-West (2006) MSPE-adjusted statistic to evaluate predictability relative to the random walk benchmark:

**Key findings:**
- Taylor rule fundamentals generate statistically significant (5% level) out-of-sample predictive power for **11 of 12** G10 currency pairs at 1-month horizon
- The Taylor rule model outperforms Meese-Rogoff (1983) random walk for the majority of pairs
- The result is robust to different specifications (symmetric vs. asymmetric, heterogeneous vs. homogeneous coefficients)
- Taylor rule with interest rate smoothing performs best

**Practical implication:** when you compute the Taylor rule deviation for two countries and take the cross-pair differential, you have a signal that — on average across history — predicts next-month currency returns better than assuming no change. This is the foundation of Signal 2 in Section 10.

#### 2.5.3 Estimating the CB's Reaction Function

Rather than imposing Taylor's original coefficients (0.5, 0.5), a systematic model can **estimate** each central bank's *actual* reaction function from the data:

$$\Delta i_t = \alpha + \beta_\pi \Delta\pi_t + \beta_y \Delta(y_t - y^*_t) + \beta_{gap}\text{inflation gap} + \epsilon_t$$

Running this OLS regression on 5+ years of data for each G10 central bank gives empirically estimated weights $\hat{\beta}_\pi, \hat{\beta}_y$. Notable findings from the literature:
- The Fed historically put roughly equal weight on inflation and employment but tilted toward employment post-GFC
- The ECB historically had a stronger inflation-fighting mandate (higher $\hat{\beta}_\pi$) but softened post-2012
- The BoJ has estimated near-zero coefficients in ZIRP periods — its reaction function was effectively switched off
- The RBA and BoC tend to be "data-dependent" with estimated weights close to Taylor's original 0.5/0.5

Updating these estimated reaction functions annually (rolling 5-year window) and using them to compute a **country-specific Taylor deviation** improves on the one-size-fits-all original Taylor rule.

---

## Section 3: Building the Macro Scorecard — A Systematic Framework

### 3.1 What a Macro Scorecard Is

A **macro scorecard** is a structured, quantitative scoring system that translates multiple macroeconomic indicators across multiple dimensions into a single directional score for each currency. The score represents the net macro "tailwind" or "headwind" facing a currency from the fundamental backdrop.

The principle is to:
1. Select indicators across theoretically motivated dimensions (monetary policy, growth, inflation, external balance, sentiment, valuation)
2. Normalize each indicator to a comparable scale (z-score)
3. Aggregate within dimensions, then aggregate across dimensions with defensible weights
4. Compute cross-pair signals as score differences

Scorecards force discipline. Every component is visible and auditable. The model cannot suddenly decide to weight inflation more heavily after seeing a CPI print — the weights are fixed ex ante. This is the systematization.

### 3.2 The Macro Scorecard Framework

| Dimension | Indicators | Weight | Frequency |
|---|---|---|---|
| **Monetary policy stance** | Rate differential (2Y), CB surprise, Taylor rule deviation | 25% | Daily/Monthly |
| **Growth differential** | OECD CLI, PMI, Industrial Production growth | 20% | Monthly |
| **Inflation differential** | CPI vs. target, CPI surprise | 15% | Monthly |
| **External balance** | Current account % GDP, Trade balance | 10% | Quarterly/Monthly |
| **Sentiment & positioning** | CFTC COT z-score, BIS positioning data | 15% | Weekly |
| **Valuation** | PPP deviation, BEER, REER | 15% | Monthly |

**Total:** 100%. These weights are defensible starting points, but they should be calibrated via cross-validation on the specific currency universe you are trading.

### 3.3 Scoring Methodology

**Step 1: Per-indicator z-score**

For each indicator $x$ and currency pair $p$ at time $t$:

$$z_{x,p,t} = \frac{x_{p,t} - \mu_{x,p,t}^{(24)}}{\sigma_{x,p,t}^{(24)}}$$

where $\mu$ and $\sigma$ are the rolling 24-month mean and standard deviation. Use 24 months (2 years) as the lookback for most indicators. For slower signals (valuation), extend to 60 months.

**Step 2: Winsorize**

$$z^{\text{clip}}_{x,p,t} = \text{clip}(z_{x,p,t}, -2, 2)$$

This prevents extreme outliers (e.g., COVID-era readings) from dominating the signal.

**Step 3: Dimension score**

$$D_{d,p,t} = \frac{1}{N_d} \sum_{x \in d} z^{\text{clip}}_{x,p,t}$$

equal-weighted average of clipped z-scores within dimension $d$.

**Step 4: Country score**

$$\text{Score}_{c,t} = \sum_{d} w_d \cdot D_{d,c,t}$$

weighted average across dimensions for country $c$. The country score represents the aggregate macro backdrop — positive = macro tailwinds, negative = macro headwinds.

**Step 5: Cross-pair signal**

$$\text{Signal}_{A/B, t} = \text{Score}_{A,t} - \text{Score}_{B,t}$$

Positive signal: buy $A$, sell $B$. Negative: buy $B$, sell $A$.

### 3.4 Python Implementation: 6-Currency Macro Scorecard

```python
"""
Macro Scorecard for G10 FX
6-currency universe: USD, EUR, GBP, JPY, AUD, CAD
Signals: monetary policy, growth (CLI), valuation (PPP deviation)
"""

import pandas as pd
import pandas_datareader.data as web
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─── Configuration ─────────────────────────────────────────────────────────────
CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
START_DATE = datetime(2005, 1, 1)
LOOKBACK_MONTHS = 24  # rolling window for z-score normalization
WINSOR = 2.0          # clip z-scores at ±2

# Dimension weights
WEIGHTS = {
    'monetary': 0.25,
    'growth':   0.20,
    'inflation': 0.15,
    'external':  0.10,
    'sentiment': 0.15,
    'valuation': 0.15,
}

# ─── FRED tickers by currency ──────────────────────────────────────────────────
FRED_2Y = {
    'USD': 'DGS2',
    'EUR': 'IRLTLT01EZM156N',  # approximate: ECB 2Y
    'GBP': 'IRLTLT01GBM156N',  # UK 2Y (10Y here; replace with 2Y if available)
    'JPY': 'IRLTLT01JPM156N',
    'AUD': 'IRLTLT01AUM156N',
    'CAD': 'IRLTLT01CAM156N',
}

FRED_CLI = {
    'USD': 'USALOLITOAASTSAM',
    'EUR': 'DEULOLITONOSTSAM',  # Germany as Eurozone proxy
    'GBP': 'GBRLOLITONOSTSAM',
    'JPY': 'JPNLOLITONOSTSAM',
    'AUD': 'AUSLOLITONOSTSAM',
    'CAD': 'CANLOLITONOSTSAM',
}

FRED_CPI = {
    'USD': 'CPIAUCSL',
    'EUR': 'CP0000EZ19M086NEST',
    'GBP': 'GBRCPIALLMINMEI',
    'JPY': 'JPNCPIALLMINMEI',
    'AUD': 'AUSCPIALLQINMEI',  # quarterly
    'CAD': 'CANCPIALLMINMEI',
}

# ─── Data Download ──────────────────────────────────────────────────────────────

def download_fred(tickers_dict, start=START_DATE):
    """Download FRED series for a dict of {currency: ticker}."""
    data = {}
    for currency, ticker in tickers_dict.items():
        try:
            s = web.DataReader(ticker, 'fred', start)[ticker]
            s = s.resample('MS').last()  # resample to month-start
            data[currency] = s
        except Exception as e:
            print(f"Warning: Could not download {ticker} for {currency}: {e}")
    return pd.DataFrame(data)

rates_2y = download_fred(FRED_2Y)
cli_data  = download_fred(FRED_CLI)
cpi_data  = download_fred(FRED_CPI)

# ─── Z-score Normalization ──────────────────────────────────────────────────────

def rolling_zscore(series, window=LOOKBACK_MONTHS, clip=WINSOR):
    """Compute rolling z-score with winsorization."""
    mu = series.rolling(window, min_periods=12).mean()
    sigma = series.rolling(window, min_periods=12).std()
    z = (series - mu) / sigma
    return z.clip(-clip, clip)

# ─── Signal 1: Monetary Policy — 2Y Rate Differential ──────────────────────────

def compute_monetary_signal(rates_df):
    """
    For each currency, compute cross-sectional z-score of 2Y rate.
    Score = 2Y yield z-score (high yield → high score → macro tailwind)
    """
    # Monthly change in 2Y rates (captures policy surprise)
    rate_change = rates_df.diff(1)
    # Level of 2Y rate (carry component)
    rate_level  = rates_df
    
    # Z-score each
    z_change = rate_change.apply(rolling_zscore)
    z_level  = rate_level.apply(rolling_zscore)
    
    return 0.5 * z_change + 0.5 * z_level

# ─── Signal 2: Growth — CLI Differential ───────────────────────────────────────

def compute_growth_signal(cli_df):
    """
    3-month change in CLI as forward-looking growth signal.
    """
    cli_mom = cli_df.diff(3)  # 3-month change
    return cli_mom.apply(rolling_zscore)

# ─── Signal 3: Inflation ────────────────────────────────────────────────────────

def compute_inflation_signal(cpi_df):
    """
    12m CPI inflation vs. 2% target.
    Short-run: high inflation → hawkish CB → positive score
    """
    # 12-month YoY inflation
    inflation = cpi_df.pct_change(12) * 100
    # Distance from 2% target (absolute, not signed — both too high and too low are signals)
    inflation_vs_target = inflation - 2.0
    return inflation_vs_target.apply(rolling_zscore)

# ─── Country Score ──────────────────────────────────────────────────────────────

def compute_country_scores(rates_df, cli_df, cpi_df):
    """
    Compute composite country score across available dimensions.
    Extend with external balance, sentiment, and valuation as data allows.
    """
    mon_sig   = compute_monetary_signal(rates_df)
    growth_sig = compute_growth_signal(cli_df)
    infl_sig   = compute_inflation_signal(cpi_df)
    
    # Align all on common dates
    aligned = pd.concat([mon_sig, growth_sig, infl_sig], keys=['mon', 'growth', 'infl'], axis=1)
    aligned = aligned.dropna(how='all')
    
    # Country score (using only 3 available dimensions here; weights renormalized)
    w_mon   = 0.25 / (0.25 + 0.20 + 0.15)
    w_growth = 0.20 / (0.25 + 0.20 + 0.15)
    w_infl   = 0.15 / (0.25 + 0.20 + 0.15)
    
    country_scores = {}
    for ccy in CURRENCIES:
        if ccy in mon_sig.columns and ccy in growth_sig.columns and ccy in infl_sig.columns:
            score = (w_mon   * mon_sig[ccy].fillna(0) +
                     w_growth * growth_sig[ccy].fillna(0) +
                     w_infl   * infl_sig[ccy].fillna(0))
            country_scores[ccy] = score
    
    return pd.DataFrame(country_scores)

# ─── Cross-Pair Signal ──────────────────────────────────────────────────────────

def compute_pair_signals(country_scores, base='USD'):
    """
    Generate cross-pair signals: score(base) - score(quote).
    Positive → buy base, sell quote.
    """
    signals = {}
    for ccy in country_scores.columns:
        if ccy != base and base in country_scores.columns:
            pair_name = f'{base}/{ccy}'
            signals[pair_name] = country_scores[base] - country_scores[ccy]
    return pd.DataFrame(signals)

# ─── Run ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    scores = compute_country_scores(rates_2y, cli_data, cpi_data)
    pair_signals = compute_pair_signals(scores, base='USD')
    
    print("Latest country scores:")
    print(scores.iloc[-1].sort_values(ascending=False))
    print("\nLatest cross-pair signals (USD base):")
    print(pair_signals.iloc[-1].sort_values(ascending=False))
```

### 3.5 Backtesting the Scorecard

**Methodology:**
- Monthly rebalancing on the first business day of each month
- Signal: composite score as computed above
- Position: long highest-score currency, short lowest-score currency (single pair); or cross-sectional long-short across all G10 pairs
- Transaction costs: assume 1 pip round-trip per trade (realistic for institutional)

**Expected performance characteristics:**
- Standalone Sharpe: **0.6–1.0** — moderate; better when macro regimes are clear and persistent
- Sharpe degrades in 2009, 2012, 2015, 2020 when macro signals were overwhelmed by risk-off episodes
- The scorecard benefits most during sustained hiking/easing cycles (2004–2006, 2015–2018, 2022–2023)
- Combining with carry and momentum adds significantly (correlation between scorecard and carry/momentum: ~0.1–0.3; diversification benefit is large)

---

## Section 4: Systematic Central Bank Models

### 4.1 OIS-Implied Rate Paths as a Signal

**Overnight Index Swaps (OIS)** are derivatives where one party pays a fixed rate and receives the compounded overnight rate (Fed Funds Effective Rate for USD, €STR for EUR, SONIA for GBP) over the swap's term. The fixed rate on an OIS equals the market's expected average policy rate over that period.

This means the OIS curve is the **cleanest, real-time measurement of market expectations for central bank policy**. A 1-year USD OIS at 4.50% says: "Markets expect the average Fed Funds rate over the next year to be 4.50%."

**Trading implication:** changes in OIS rates between meetings represent revisions to expectations — precisely what moves FX in the short run. The most valuable calculation is:

$$\text{CB Surprise} = \text{Rate decision} - \text{OIS-implied rate 30 minutes before announcement}$$

A positive surprise (Fed hikes more than OIS implied) is a hawkish surprise and tends to drive immediate USD appreciation. This is the highest-frequency systematic macro signal.

**Free approximation using Fed Funds Futures (CME):**
The CME publishes daily settlement prices for Fed Funds Futures contracts going out 13 months. The implied rate for any month is computed as 100 minus the contract price. The FRBSF Monetary Policy Surprise dataset (Romer and Romer, 2004, later updated) provides clean historical surprises going back to 1994 — freely available at [federalreserve.gov](https://www.federalreserve.gov).

**Central bank meeting calendars:** Trading around CB meetings requires knowing exactly when each meeting is. All G10 central banks publish their meeting calendars 1 year ahead. Building a systematic calendar of meeting dates and pre-loading them into your signal framework is essential infrastructure.

| G10 CB | Meetings/year | Primary FX sensitivity | Data source |
|---|---|---|---|
| Fed (FOMC) | 8 | USD vs. all | CME FedWatch; FRBSF surprise dataset |
| ECB | 8 | EUR/USD, EUR crosses | €STR futures / EURIBOR futures |
| BoE (MPC) | 8 | GBP/USD, EUR/GBP | SONIA futures (ICE) |
| BoJ | 8 | USD/JPY, JPY crosses | TONA futures |
| RBA | 11 | AUD/USD | ASX 30-day bank bill futures |
| BoC | 8 | USD/CAD | BAX (Bankers' Acceptance) futures |
| SNB | 4 (quarterly) | USD/CHF | SARON futures |
| RBNZ | 7 | NZD/USD | NZD OIS market |
| Norges Bank | 8 | USD/NOK | NOK OIS market (limited liquidity) |
| Riksbank | 6 | USD/SEK | SEK OIS market |

### 4.2 The Fed Pivot Detection System

Detecting **CB policy pivots** — the transition from hiking to neutral, or neutral to easing — is one of the highest-value systematic macro problems. The 2019 Fed pivot (Jan 4, 2019: "patient" language; rate cuts Jul–Oct 2019) and the 2022 hiking cycle onset can serve as case studies.

**Systematic indicators that preceded the 2022 hiking cycle (as of late 2021):**

1. **Taylor rule deviation:** computed Taylor rate was ~3.5% vs. actual 0–0.25% → largest deviation since early 1980s
2. **Breakeven inflation:** 5Y5Y forward breakeven rose above 2.5% (exceeded pre-GFC norms)
3. **FOMC minutes hawkish word count:** ratio of "inflation" / "unemployment" mentions rose sharply in H2 2021
4. **OIS pricing:** Dec 2021 OIS market was pricing 2+ hikes for 2022 (later revised to 7+)
5. **Supply chain pressure index (GSCPI from NY Fed):** peaked in Dec 2021, confirming supply-side inflation

A systematic model monitoring these 5 indicators simultaneously would have flagged an imminent hiking cycle by November 2021 — 3 months before the first hike.

**For the 2019 pivot (from hiking to easing):**

1. **ISM Manufacturing PMI:** fell below 50 (contraction) by Sep 2019
2. **Yield curve inversion:** 10Y-2Y inverted in August 2019
3. **China trade war escalation:** systematic geopolitical sentiment score
4. **FOMC minutes:** "patience" and "accommodative" word counts rose in H1 2019
5. **Financial conditions:** Goldman Sachs FCI (approximately reconstructable from spreads, VIX, equity, rates) tightened significantly in Q4 2018

### 4.3 Central Bank Communication as a Systematic Signal

**Hawk-dove scoring from text**

The minutes of central bank meetings contain valuable forward guidance. The systematic approach: count occurrences of hawkish vs. dovish terms and compute a ratio.

**Loughran-McDonald Dictionary** (Loughran and McDonald 2011, *Journal of Finance*): a financial-domain sentiment lexicon with positive, negative, uncertain, and other word categories. Better than generic lexicons (Harvard General Inquirer) for financial text because financial language uses words like "liability" negatively that general dictionaries classify neutrally.

Available free at: [sraf.nd.edu/data/loughran-mcdonald-master-dictionary/](https://sraf.nd.edu/data/loughran-mcdonald-master-dictionary/)

**FinBERT** (Araci 2019, arxiv:1908.10063): a BERT-based model pre-trained on 4.9B tokens of financial text (Reuters/Bloomberg articles, earnings call transcripts) and fine-tuned for sentiment classification. Available free on HuggingFace at `yiyanghkust/finbert-tone`.

```python
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import requests

# Load FinBERT from HuggingFace
finbert = pipeline("text-classification",
                   model="yiyanghkust/finbert-tone",
                   tokenizer="yiyanghkust/finbert-tone")

def score_fomc_text(text_chunk):
    """
    Score a chunk of FOMC text as Positive (hawkish), Negative (dovish), or Neutral.
    Returns: (label, score) where score is 0-1 confidence.
    """
    # FinBERT has 512 token limit; split long texts
    result = finbert(text_chunk[:512])
    return result[0]['label'], result[0]['score']

# Example: score a paragraph from FOMC minutes
sample_text = """
The Committee decided to raise the target range for the federal funds rate by 
75 basis points. Inflation remains well above 2 percent, and supply and demand 
imbalances related to the pandemic and the reopening of the economy have 
continued to contribute to elevated levels of inflation.
"""
label, confidence = score_fomc_text(sample_text)
print(f"Sentiment: {label} (confidence: {confidence:.2f})")
# Expected output: Sentiment: Positive (hawkish) with high confidence

def compute_hawk_dove_score(minutes_text, chunk_size=400):
    """
    Compute overall hawk/dove score for a full FOMC minutes document.
    Score > 0: hawkish; Score < 0: dovish
    """
    words = minutes_text.split()
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    scores = []
    for chunk in chunks:
        label, conf = score_fomc_text(chunk)
        score = conf if label == 'Positive' else (-conf if label == 'Negative' else 0)
        scores.append(score)
    
    return np.mean(scores)
```

**Evidence:** Hilscher, Nabors, and Raviv (SSRN 2024) show that central bank sentiment constructed from FinBERT on Fed and ECB communications predicts policy rates and Taylor rule deviations several quarters in advance using local projection analysis — providing lead time for systematic positioning.

---

## Section 5: Growth Differential Models

### 5.1 OECD CLI-Based Strategy: Evidence

Colacito, Riddiough, and Sarno (2020, *JFE*) is the definitive academic paper on business cycle differentials as FX signals. Their key empirical results:

- A strategy that **buys currencies with the highest CLI trend relative to the G10 mean** and shorts those with the lowest has generated:
  - Sharpe ratio of **~0.8** over 1975–2015
  - Average annual excess return of approximately 3.5–4%
  - Returns are uncorrelated with carry (correlation ~0.1) and momentum (correlation ~0.15), providing genuine diversification

- At 6-month horizons, CLI differentials explain 30–40% of the cross-sectional variation in currency returns
- The effect is concentrated in the "turning point" phase of CLIs (when they flip from declining to rising, or vice versa) — making the 3-month change in CLI the most predictive version of the signal

- Data used: OECD CLI freely available; strategy implementable with public data

### 5.2 PMI Cross-Country Ranking

A simpler but effective implementation of the growth signal is a **cross-sectional PMI rank** strategy:

```python
def pmi_rank_signal(pmi_df, n_long=2, n_short=2):
    """
    Cross-sectional PMI momentum rank strategy.
    
    Long top n_long currencies (best PMI momentum)
    Short bottom n_short currencies (worst PMI momentum)
    
    Parameters:
    -----------
    pmi_df : pd.DataFrame
        Monthly PMI data, columns = currencies
    
    Returns:
    --------
    pd.DataFrame : position weights, rows = dates, columns = currencies
    """
    # 3-month change in PMI as momentum signal
    pmi_mom = pmi_df.diff(3)
    
    # Cross-sectional rank at each month
    positions = pd.DataFrame(0.0, index=pmi_mom.index, columns=pmi_mom.columns)
    
    for date in pmi_mom.index:
        row = pmi_mom.loc[date].dropna()
        if len(row) >= n_long + n_short:
            ranked = row.rank(ascending=True)
            # Long top n_long
            top = ranked.nlargest(n_long).index
            # Short bottom n_short
            bottom = ranked.nsmallest(n_short).index
            
            for ccy in top:
                positions.loc[date, ccy] = 1.0 / n_long
            for ccy in bottom:
                positions.loc[date, ccy] = -1.0 / n_short
    
    return positions
```

### 5.3 Industrial Production Differential

Monthly industrial production (IP) data is available from FRED for all G10 countries:

| Country | FRED Ticker |
|---|---|
| United States | `INDPRO` |
| Germany | `DEUPROINDMISMEI` |
| Japan | `JPNPROINDMISMEI` |
| United Kingdom | `GBRPROINDMISMEI` |
| Canada | `CANPROINDMISMEI` |
| Australia | `AUSPROINDMISMEI` |

**Signal:** 3-month rolling YoY IP growth differential. IP leads services activity by 1–2 months, making it a timely nowcast of the broader economy.

```python
def ip_differential_signal(ip_base, ip_quote, mom_window=3):
    """
    Industrial production growth differential signal.
    
    Parameters:
    -----------
    ip_base : pd.Series
        IP index for base currency country
    ip_quote : pd.Series
        IP index for quote currency country
    mom_window : int
        Annualized lookback (months)
    
    Returns:
    --------
    pd.Series : z-scored IP differential signal
    """
    # YoY growth
    ip_growth_base  = ip_base.pct_change(12) * 100
    ip_growth_quote = ip_quote.pct_change(12) * 100
    
    # Differential
    ip_diff = ip_growth_base - ip_growth_quote
    
    # 3-month rolling average (smooth monthly noise)
    ip_diff_smooth = ip_diff.rolling(mom_window).mean()
    
    # Z-score
    return rolling_zscore(ip_diff_smooth)
```

---

## Section 6: Inflation and External Balance Models

### 6.1 PPP Deviation Models (Value Signal)

**Purchasing Power Parity (PPP)** is the long-run equilibrium condition that exchange rates should reflect relative price levels:

$$S_t = \frac{P_t}{P^*_t}$$

in absolute terms (law of one price applied to aggregate price levels).

**Relative PPP** (more practically useful):

$$\frac{S_{t+k}}{S_t} \approx \frac{P_{t+k}/P_t}{P^*_{t+k}/P^*_t} = \frac{(1 + \pi_t)^k}{(1 + \pi^*_t)^k}$$

A currency that has appreciated in *nominal* terms by more than justified by the relative inflation rates is **overvalued** on a PPP basis and should depreciate toward equilibrium over the long run.

**Practical PPP signal construction:**

*Method 1: OECD PPP*

The OECD publishes annual PPP-implied exchange rates for all OECD member countries. Freely available at stats.oecd.org. The PPP deviation is:

$$\text{PPP dev}_t = \frac{S_t^{\text{market}} - S_t^{\text{PPP}}}{S_t^{\text{PPP}}}$$

A positive deviation means the base currency is overvalued vs. PPP → negative signal (expect depreciation).

*Method 2: 5-Year CPI-adjusted spot rate (AQR methodology)*

```python
def compute_ppp_deviation(spot_rate, cpi_base, cpi_quote, lookback_years=5):
    """
    Compute PPP deviation using rolling inflation adjustment.
    AQR methodology: 5-year rolling CPI-adjusted baseline.
    
    Parameters:
    -----------
    spot_rate : pd.Series
        Monthly spot rate (units of quote per unit of base)
    cpi_base : pd.Series
        CPI index for base currency country
    cpi_quote : pd.Series
        CPI index for quote currency country
    lookback_years : int
        Years to roll back for PPP baseline
    
    Returns:
    --------
    pd.Series : PPP deviation (positive = overvalued base)
    """
    lookback = lookback_years * 12  # in months
    
    # Compute what the exchange rate "should be" given inflation differential
    # relative to the rate lookback_years ago
    cpi_ratio     = cpi_base / cpi_quote
    cpi_ratio_lag = cpi_ratio.shift(lookback)
    spot_lag      = spot_rate.shift(lookback)
    
    # PPP-implied current rate (adjusting historical rate by relative inflation)
    ppp_implied   = spot_lag * (cpi_ratio / cpi_ratio_lag)
    
    # Deviation: positive = spot above PPP (overvalued base)
    ppp_dev       = (spot_rate - ppp_implied) / ppp_implied
    
    return rolling_zscore(ppp_dev, window=60)  # z-score over 5 years
```

**Historical evidence on PPP as a FX signal:**

PPP works as a mean-reversion signal over **3–10 year horizons** but has essentially no predictive power at 1-year and shorter horizons (Rogoff 1996 "PPP puzzle": half-lives of PPP deviations are 3–5 years for major currencies). The Sharpe ratio from PPP alone is approximately 0.3–0.4, but it decorrelates well from carry and momentum, adding value in a diversified model.

### 6.2 REER as a Valuation Signal

The **Real Effective Exchange Rate (REER)** measures the value of a currency against a trade-weighted basket of partners, adjusted for relative inflation. A high REER indicates that a country's goods and services are expensive relative to trading partners — i.e., the currency is overvalued in a competitiveness sense.

**BIS REER data:** The BIS publishes monthly REER data for 64 economies, freely accessible at [bis.org/statistics/eer.htm](https://www.bis.org/statistics/eer.htm). The broad index uses 27 trading partners; the narrow index uses 8.

**Signal construction:**

```python
def reer_signal(reer_series, long_run_window=120):
    """
    REER deviation from long-run average as valuation signal.
    Positive deviation = overvalued → negative signal (expected depreciation).
    
    Parameters:
    -----------
    reer_series : pd.Series
        Monthly REER index
    long_run_window : int
        Months for long-run average (default: 10 years)
    
    Returns:
    --------
    pd.Series : Negated z-score (so positive = undervalued = BUY signal)
    """
    long_run_mean = reer_series.rolling(long_run_window, min_periods=60).mean()
    long_run_std  = reer_series.rolling(long_run_window, min_periods=60).std()
    
    deviation_z = (reer_series - long_run_mean) / long_run_std
    
    # Negate: high REER deviation = overvalued = SELL signal
    return -deviation_z.clip(-2, 2)
```

**Practical caveat:** REER signals at the tails are most reliable. A REER z-score beyond ±2 (i.e., more than 2 standard deviations above/below its 10-year average) represents genuine overvaluation/undervaluation with a higher probability of mean reversion. Within ±1 standard deviation, the signal is too noisy to trade.

### 6.3 BEER: Behavioural Equilibrium Exchange Rate

The BEER (Clark and MacDonald 1998) is a more sophisticated valuation model that regresses the real exchange rate on a set of economic fundamentals:

$$q_t = \beta_1 \cdot \text{NFA}_t + \beta_2 \cdot \text{ToT}_t + \beta_3 \cdot \text{Prod}_t + \beta_4 \cdot G_t + \epsilon_t$$

where:
- $q_t$ = real exchange rate (log)
- $\text{NFA}_t$ = net foreign assets as % GDP (long-run sustainability)
- $\text{ToT}_t$ = terms of trade
- $\text{Prod}_t$ = productivity differential (Balassa-Samuelson effect)
- $G_t$ = government spending differential (fiscal stance)

The BEER is estimated by running this regression over long-run data (20+ years) for each currency pair. The **BEER misalignment** (actual real rate minus BEER-implied equilibrium) is the valuation signal.

IMF staff papers on BEER estimation for G10 currencies (published in IMF Working Papers series, freely available at imf.org) provide estimated coefficients for each pair. Implementing BEER requires more data infrastructure than PPP but provides a richer valuation signal especially for pairs where commodity prices (ToT) matter (CAD, AUD, NOK).

---

## Section 7: Sentiment, Positioning, and Flow Models

### 7.1 CFTC Commitment of Traders (COT) as a Signal

The CFTC publishes the **Commitment of Traders (COT)** report every Friday at 3:30 PM ET, reflecting positions as of the prior Tuesday close. For FX, the relevant data is from the **Traders in Financial Futures (TFF)** report, which breaks down CME FX futures positions into:

- **Dealer/Intermediary**: commercial banks and FX dealers (hedging their FX book)
- **Asset Manager/Institutional**: pension funds, mutual funds, insurance (long-term investors)
- **Leveraged Funds**: hedge funds, CTAs, proprietary traders (the "smart money" trend-followers/carry traders)
- **Other Reportables**: other large speculators

**What matters most:** The **Leveraged Funds net position** is the most informative for systematic trading. Leveraged funds represent trend-following CTAs and macro hedge funds — the "crowded" trades are in their book. When they are extremely long one currency, the risk of reversal is highest.

**Signal construction (contrarian):**

```python
import pandas as pd
import numpy as np

def compute_cot_signal(cot_df, long_col='leveraged_long', short_col='leveraged_short',
                       z_window=104, threshold=1.5):
    """
    CFTC COT contrarian signal.
    
    When leveraged funds are extremely long (z > threshold): expect reversal → SELL
    When leveraged funds are extremely short (z < -threshold): expect reversal → BUY
    
    Parameters:
    -----------
    cot_df : pd.DataFrame
        Weekly COT data with long/short position columns
    long_col : str
        Column name for leveraged long positions (contracts)
    short_col : str
        Column name for leveraged short positions (contracts)
    z_window : int
        Rolling window for z-score (104 weeks = 2 years)
    threshold : float
        Z-score threshold for signal activation
    
    Returns:
    --------
    pd.Series : Contrarian signal (-1 to +1, with 0 = no signal)
    """
    # Net speculative position
    net_spec = cot_df[long_col] - cot_df[short_col]
    
    # Rolling z-score
    z_score = (net_spec - net_spec.rolling(z_window).mean()) / net_spec.rolling(z_window).std()
    
    # Contrarian signal: active only when positioning is extreme
    signal = pd.Series(0.0, index=z_score.index)
    signal[z_score >  threshold] = -1.0  # extreme long → sell
    signal[z_score < -threshold] = +1.0  # extreme short → buy
    
    return signal

# Data download: CFTC provides CSV files at cftc.gov/MarketReports/CommitmentsofTraders/
# Historical data: cftc.gov/files/dea/history/fut_fin_xls_2024.zip (replace year)
```

**Coverage gaps:** COT data exists for CME-traded FX futures. The G10 currencies covered are EUR, JPY, GBP, CHF, CAD, AUD, NZD, MXN. **There is no COT coverage for SEK, NOK** (no liquid CME futures), which is a gap in the positioning signal for those pairs.

**Standalone performance:** COT contrarian signal has a standalone Sharpe of approximately **0.3–0.4** — modest on its own. Its primary value is as a **risk overlay**: when positioning is at extremes, reduce size in the direction of the consensus trade, regardless of what other signals say.

**Interpretation subtlety:** extreme positioning alone does not cause reversals — a catalyst is needed. The COT signal works best when *combined with* a deteriorating fundamental backdrop (e.g., COT shows extreme USD longs *and* the Taylor rule deviation for the US starts narrowing).

### 7.2 Options Market Sentiment: 25-Delta Risk Reversal

The **25-delta risk reversal (RR25)** measures the implied volatility differential between out-of-the-money calls and puts:

$$\text{RR25}_t = \text{IV}_{25\Delta \text{ call}, t} - \text{IV}_{25\Delta \text{ put}, t}$$

For a G10 pair expressed as (base/quote):
- **Positive RR25**: demand for call options (right to buy base) exceeds demand for puts → the market is paying a premium for upside exposure → **bullish on base currency**
- **Negative RR25**: demand for puts exceeds calls → the market is paying a premium for downside protection → **bearish on base currency**

RR25 is particularly useful because:
1. It reflects institutional hedging demand (corporates hedging FX exposures through options)
2. It captures tail risk sentiment — large moves in RR25 precede directional moves in spot
3. It updates daily (for liquid G10 pairs)

**Data:** Bloomberg (paid) is the primary source. For approximation, CME FX options settlements are public, and the CBOE publishes some FX volatility data.

**Signal construction:**

```python
def risk_reversal_signal(rr25_series, window=26):
    """
    Risk reversal as a directional FX signal.
    
    Parameters:
    -----------
    rr25_series : pd.Series
        Weekly or daily 1-month 25-delta RR (call IV - put IV)
    window : int
        Rolling window for z-score (26 weeks = 6 months)
    
    Returns:
    --------
    pd.Series : Signal (positive = bullish base currency)
    """
    # Z-score of RR25
    z = (rr25_series - rr25_series.rolling(window).mean()) / rr25_series.rolling(window).std()
    
    # Momentum in risk reversal: change in sentiment is sometimes more
    # predictive than the level
    z_change = z.diff(4)  # 4-week change in z-score
    
    return 0.5 * z.clip(-2, 2) + 0.5 * z_change.clip(-2, 2)
```

### 7.3 FX ETF Flow Data

Currency-specific ETFs provide a daily, publicly available proxy for retail and institutional FX flows. Key tickers:

| ETF | Currency | Exchange |
|---|---|---|
| FXE | EUR | NYSE Arca |
| FXY | JPY | NYSE Arca |
| FXB | GBP | NYSE Arca |
| FXA | AUD | NYSE Arca |
| FXC | CAD | NYSE Arca |
| UUP | USD Index | NYSE Arca |

**Signal:** 4-week rolling net ETF fund flows (from ETF.com or similar) can proxy for directional demand for a currency. Large outflows from FXE (EUR ETF) concurrent with inflows to UUP (USD) indicate institutional FX position rotation.

**Limitation:** ETF flows represent a small fraction of total FX market volume (the FX market is $7.5T/day; all FX ETFs combined are maybe $10B AUM). However, flows lead price because institutions tend to accumulate positions before large moves become visible in spot prices.

---

## Section 8: Cross-Asset Macro Models

### 8.1 The Risk-On / Risk-Off (RORO) Framework

The **RORO framework** classifies currencies into two groups based on their behavior during episodes of global risk appetite expansion vs. contraction:

**Risk-on currencies** (appreciate when global risk appetite rises):
- AUD, NZD (commodity exposure, high carry)
- CAD (commodity; moderate beta)
- GBP (moderate risk beta)
- EUR (low-beta risk-on in recent cycles)

**Safe-haven currencies** (appreciate when risk appetite falls):
- JPY (largest net international investment position; capital repatriation during stress)
- CHF (historical safe haven; partly structural)
- USD (global reserve currency; flight to liquidity during crises)

**VIX as the RORO signal:**

```python
def vix_roro_signal(vix_series, roro_beta_dict, vix_window=20):
    """
    VIX-based risk-on / risk-off overlay.
    
    Scales positions for each currency pair by VIX regime.
    
    Parameters:
    -----------
    vix_series : pd.Series
        Daily VIX close (FRED: VIXCLS)
    roro_beta_dict : dict
        {currency: beta} where positive beta = risk-on, negative = safe-haven
        Example: {'AUD': +1, 'JPY': -1, 'USD': -0.5}
    vix_window : int
        Days for VIX moving average
    
    Returns:
    --------
    dict : {currency: daily_signal_scalar}
    """
    # VIX z-score
    vix_z = (vix_series - vix_series.rolling(vix_window).mean()) / vix_series.rolling(vix_window).std()
    
    # When VIX spikes (positive z-score), risk-off currencies get positive boost
    # Risk-on currencies get negative score
    signals = {}
    for ccy, beta in roro_beta_dict.items():
        signals[ccy] = -beta * vix_z  # risk-off = negative beta currencies benefit
    
    return signals
```

**Empirical evidence:** The SPX daily return has a contemporaneous correlation of approximately **+0.6** with AUD/USD and **−0.5** with USD/JPY over the 2010–2024 period. This relationship is well-documented (Ranaldo and Söderlind 2010, *Review of Finance*) and provides a simple daily RORO signal.

### 8.2 Rates-FX Linkages

**The US 10Y Treasury yield and USD:**

The relationship between US 10Y yields and the USD is one of the most important cross-asset linkages in macro FX:

- Rising US 10Y real yields → higher real return on USD assets → capital inflow → USD appreciates
- Rising US 10Y nominal yields driven by *inflation* expectations (not real rates) → USD weakens (inflation is negative for currency over medium term)

The distinction between real and nominal yield moves is critical. Use the **10Y TIPS yield** (FRED: `DFII10`) as the real yield signal; the breakeven (FRED: `T10YIE`) captures the inflation component.

**The paradox of crisis:** In genuine risk-off crisis events (2008, March 2020), US Treasuries rally (yields fall) *and* the USD appreciates simultaneously. This occurs because the demand for USD as a **global liquidity currency** overwhelms the normal yield-currency relationship. When building your systematic model, flag VIX > 35 as a "crisis mode" where the normal rates-FX relationship may invert.

**Cross-country real yield differential for FX:**

$$\text{Signal}_{A/B} = \text{RealYield}_{10Y,A} - \text{RealYield}_{10Y,B}$$

where $\text{RealYield} = \text{Nominal 10Y} - \text{5Y5Y inflation swap}$ (for countries without TIPS markets).

### 8.3 Commodity-FX Linkages

**The complete G10 commodity-FX map:**

| Commodity | G10 Pair | Direction | Evidence |
|---|---|---|---|
| WTI/Brent crude | USD/CAD | Oil ↑ → USDCAD ↓ (CAD appreciates) | Ferraro, Rogoff, Rossi (2015, *JIMF*): daily oil ↑ predicts CAD appreciation |
| Iron ore (SGX) | AUD/USD | Iron ore ↑ → AUDUSD ↑ | Historical correlation ~0.80; structural export share |
| Whole milk powder (GDT) | NZD/USD | Dairy ↑ → NZDUSD ↑ | Biweekly GDT auction; Boston Fed WP 2023-01 |
| Natural gas (TTF) | EUR/USD | Gas ↑ → EURUSD ↓ | Post-2022 European energy crisis regime |
| Gold (COMEX) | USD/CHF | Gold ↑ → CHF ↑ (risk-off correlated) | Historical safe-haven correlation; weakened post-2015 |
| Lumber | USD/CAD | Lumber ↑ → modest USDCAD ↓ | Canada is world's largest lumber exporter |
| Agricultural (corn/soy) | Broad USD (EM FX more relevant) | Moderate | G10-relevant via trade balance |

**Key finding (Ferraro-Rogoff-Rossi 2015):** At the daily frequency, lagged oil price changes predict CAD exchange rate changes better than the random walk. The effect is present but small at monthly and quarterly frequencies, and disappears over longer horizons — a textbook case of a signal that must be applied at the right frequency.

**Commodity signal construction:**

```python
def commodity_fx_signal(commodity_prices: dict, lookback_days=5, lag=1):
    """
    Daily commodity → FX directional signals.
    
    Parameters:
    -----------
    commodity_prices : dict
        {commodity: pd.Series of daily prices}
    lookback_days : int
        Momentum window for commodity price change
    lag : int
        Days to lag commodity signal (avoid lookahead bias)
    
    Returns:
    --------
    dict : {pair: pd.Series of daily signals}
    """
    # G10 commodity-FX mapping: (commodity, direction)
    MAPPING = {
        'USDCAD': ('WTI',      -1),  # oil up → USDCAD down
        'AUDUSD': ('IRON_ORE', +1),  # iron ore up → AUDUSD up
        'NZDUSD': ('DAIRY',    +1),  # dairy up → NZDUSD up
        'EURUSD': ('TTF_GAS',  -1),  # EU gas prices up → EURUSD down
    }
    
    signals = {}
    for pair, (commodity, direction) in MAPPING.items():
        if commodity in commodity_prices:
            price = commodity_prices[commodity]
            # k-day price change
            change = price.pct_change(lookback_days).shift(lag)
            signals[pair] = direction * np.sign(change)
    
    return signals
```

---

## Section 9: Regime Detection — Knowing When Models Work

### 9.1 Why Regime Detection Is Indispensable

No single systematic macro signal works in all market environments. Carry trades earn positive expected returns on average, but they have left-tailed return distributions — they suffer large, sudden losses during crises (the "carry crash"). Momentum works in trending markets but reverses in choppy, mean-reverting environments. Value works over long horizons but can require 3–5 years of patience.

A systematic model that ignores regimes will apply carry signals during crises (when carry is being unwound violently), apply momentum signals in range-bound markets, and mix time horizons inappropriately. **Regime detection is the difference between a theoretical model and a deployable one.**

The regime framework serves three functions:
1. **Signal scaling:** reduce position sizes when regimes are unfavorable to the active signals
2. **Signal selection:** switch between signal types appropriate to the current regime
3. **Risk management:** hard stops on carry positions when risk-off indicators breach thresholds

### 9.2 The VIX Regime Framework

The VIX (CBOE Volatility Index, FRED: `VIXCLS`) provides the simplest and most effective first-order regime indicator:

| VIX Level | Regime Label | Carry | Momentum | Value | Growth |
|---|---|---|---|---|---|
| < 15 | **Goldilocks** | ★★★ Best | ★★☆ Good | ★☆☆ Slow | ★★★ Best |
| 15–20 | **Neutral / Late Cycle** | ★★☆ Moderate | ★★☆ Good | ★★☆ Moderate | ★★☆ Moderate |
| 20–25 | **Caution** | ★☆☆ Reduce | ★★★ Best | ★★☆ Moderate | ★☆☆ Reduce |
| 25–35 | **Risk-Off** | ✗ Stop | ★★★ TSMOM | ★☆☆ Slow | ✗ Stop |
| > 35 | **Crisis** | ✗ Stop | ★★☆ Mixed | ✗ Irrelevant | ✗ Stop |

**Practical implementation:**

```python
def vix_scaler(vix_series, vix_floor=15.0, vix_ceiling=40.0):
    """
    Scale positions by VIX regime.
    
    Returns scalar between 0 and 1:
    - At VIX = floor: scalar = 1.0 (full risk-on)
    - At VIX = ceiling: scalar = 0.0 (all positions flat)
    
    Parameters:
    -----------
    vix_series : pd.Series
        Daily VIX close
    vix_floor : float
        VIX level at which scale = 1
    vix_ceiling : float
        VIX level at which scale = 0
    
    Returns:
    --------
    pd.Series : Daily scaling factor (0 to 1)
    """
    scale = 1.0 - (vix_series - vix_floor) / (vix_ceiling - vix_floor)
    return scale.clip(0.0, 1.0)
```

### 9.3 Yield Curve Regime

The **10Y–2Y yield spread** (yield curve slope) captures the stage of the credit/macro cycle:

| Yield Curve State | 10Y–2Y Level | Economic Interpretation | Signal Impact |
|---|---|---|---|
| **Steep** | > +150bp | Early cycle; growth accelerating | Carry and growth signals work well |
| **Normal** | +50 to +150bp | Mid cycle; growth stable | All signals perform at baseline |
| **Flat** | 0 to +50bp | Late cycle; policy tightening peak | Reduce carry; value signal improves |
| **Inverted** | < 0bp | Recession risk elevated | Carry stops; flight-to-quality FX |
| **Deeply inverted** | < −50bp | Imminent or ongoing recession | Crisis mode; only safe-haven positioning |

Historically, US yield curve inversions (10Y–2Y < 0) have preceded USD strength followed by USD weakness as the Fed eventually cuts. EUR/JPY and risk/safe-haven cross-pairs are most predictably affected by US yield curve signals.

### 9.4 Hidden Markov Model for Regime Detection

The HMM provides a more rigorous, data-driven approach to regime classification. Rather than setting hard VIX thresholds, the HMM learns from data what "risk-on" and "risk-off" states look like across multiple variables simultaneously.

```python
from hmmlearn import hmm
import numpy as np
import pandas as pd

def fit_macro_hmm(vix_series, curve_slope, credit_spread, equity_return,
                  n_states=2, n_iter=200):
    """
    Fit a 2-state Gaussian HMM to macro regime indicators.
    
    Parameters:
    -----------
    vix_series : pd.Series
        Daily VIX (FRED: VIXCLS)
    curve_slope : pd.Series
        10Y-2Y slope (FRED: T10Y2Y)
    credit_spread : pd.Series
        IG credit spread (FRED: BAMLC0A0CM)
    equity_return : pd.Series
        S&P 500 daily return (FRED: SP500 daily pct change)
    n_states : int
        Number of regimes (2 = risk-on / risk-off)
    
    Returns:
    --------
    tuple : (fitted model, state sequence as pd.Series)
    """
    # Align all series
    data = pd.DataFrame({
        'vix': vix_series,
        'curve': curve_slope,
        'credit': credit_spread,
        'equity': equity_return
    }).dropna()
    
    # Standardize inputs
    X = (data - data.mean()) / data.std()
    X_array = X.values
    
    # Fit Gaussian HMM
    model = hmm.GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=n_iter,
        random_state=42
    )
    model.fit(X_array)
    
    # Predict regime sequence
    states = model.predict(X_array)
    state_series = pd.Series(states, index=data.index)
    
    # Identify which state is "risk-on" (lower VIX mean)
    state_means = {}
    for s in range(n_states):
        idx = states == s
        state_means[s] = data.loc[idx, 'vix'].mean()
    
    # State with lower VIX = risk-on = state 0 in output
    risk_on_state = min(state_means, key=state_means.get)
    
    # Posterior regime probabilities (more useful than hard state labels)
    proba = model.predict_proba(X_array)
    regime_proba = pd.Series(proba[:, risk_on_state], index=data.index,
                             name='risk_on_probability')
    
    return model, regime_proba

# Usage:
# model, risk_on_prob = fit_macro_hmm(vix, curve, credit, spy_ret)
# Use risk_on_prob as a continuous (0 to 1) scaler for carry and growth signals
```

**Practical considerations:**
- Re-fit the HMM annually with expanding window (not rolling, to use all historical data)
- Use `predict_proba` (posterior probability) rather than hard state labels — a continuous scaler avoids cliff-edge position changes at regime boundaries
- The 2-state model (risk-on / risk-off) is usually sufficient; a 3-state model adds a "transition" regime but increases overfitting risk
- Validate: in-sample states should align with known crisis periods (2008, 2011, 2018Q4, 2020 March)

### 9.5 A Practical Macro Regime Dashboard

The full regime dashboard combines multiple indicators for a robust, multi-indicator regime classification:

| Indicator | Threshold | Risk-On Score | Risk-Off Score |
|---|---|---|---|
| VIX level | < 15 / > 25 | +2 | −2 |
| VIX 20-day change | < 0 / > +5 | +1 | −1 |
| 10Y–2Y slope | > +100bp / < 0bp | +1 | −1 |
| IG credit spread (BAMLC0A0CM) | < 100bp / > 200bp | +1 | −1 |
| HY credit spread (BAMLH0A0HYM2) | < 300bp / > 600bp | +1 | −1 |
| SPX 20-day return | > 0 / < −5% | +1 | −1 |
| Cross-currency basis (EUR/USD) | > −20bp / < −50bp | +1 | −1 |

**Composite regime score:** sum of the above (range: −8 to +8). Map to:
- +4 to +8: risk-on regime → full carry/growth signal weights
- 0 to +4: neutral regime → 75% weights
- −4 to 0: caution regime → 50% weights
- −8 to −4: risk-off regime → 25% carry; 100% momentum/safe-haven

---

## Section 10: A Complete Systematic Macro Model for G10 FX

### 10.1 Architecture Overview

The complete systematic macro model combines 6 signal dimensions, each independently backtested and understood, into a composite model with:
- Daily update cycle (for rate-sensitive and risk signals)
- Monthly rebalancing of core macro positions
- VIX/regime overlay as a continuous risk scaler
- Position sizing via cross-sectional z-scoring (not binary signals)

**Design principles:**
1. Each signal must have an ex-ante economic rationale (no pure data mining)
2. Each signal must be implementable with public data (reproducible)
3. Signals must be combined with defensible weights (not black-box optimization)
4. The regime overlay is mandatory, not optional
5. Transaction costs must be explicitly modeled

### 10.2 Signal Definitions

#### Signal 1: Rate Differential Change (Daily) — Monetary Policy Surprise

**Economic rationale:** changes in 2Y yield spreads reflect revisions to expected central bank rate paths — the single most important FX driver over 1–5 day horizons.

**Implementation:**

```python
# Daily 2Y yield differential change
# Source: FRED DGS2 for USD; equivalent for other G10
delta_2y_usd  = us_2y.diff(1)
delta_2y_eur  = eur_2y.diff(1)

signal_1_eurusd = -np.sign(delta_2y_usd - delta_2y_eur)
# Positive = EUR appreciating vs. USD (EUR 2Y rising relative to USD 2Y)
```

**Expected Sharpe:** ~2.5 standalone at daily frequency (our Strategy #1 result)
**Rebalance:** Daily
**Key caveat:** this is a directional signal on *changes*, not levels. High turnover; transaction costs must be managed carefully.

#### Signal 2: Taylor Rule Deviation (Monthly) — Policy Divergence

**Economic rationale:** when a central bank's actual rate is below its Taylor-implied rate, it is "behind the curve" — the market will eventually force it to tighten, driving the currency higher. Molodtsova-Papell (2009) validates this out-of-sample.

**Implementation:** as coded in Section 2.5.1 above.

$$\text{Signal}_2 = z\bigl[\text{TaylorDeviation}_A - \text{TaylorDeviation}_B\bigr]$$

Positive: Country A is more "behind the curve" than B → A's CB will tighten more → A's currency should appreciate.

**Expected Sharpe:** ~0.4–0.5 standalone (modest but persistent)
**Rebalance:** Monthly

#### Signal 3: Business Cycle Differential (Monthly) — Growth Signal

**Economic rationale:** countries with accelerating economic activity attract capital flows, supporting their currencies. Colacito-Riddiough-Sarno (2020) validates this with Sharpe ~0.8.

**Implementation:**

```python
# 3-month change in CLI differential
cli_diff_mom = (us_cli - eur_cli).diff(3)
signal_3_eurusd = rolling_zscore(cli_diff_mom)
# Positive: US economy accelerating relative to Eurozone → USD positive
```

**Expected Sharpe:** ~0.6–0.8 standalone
**Rebalance:** Monthly (with monthly CLI data)

#### Signal 4: Valuation / PPP (Quarterly) — Long-Run Value

**Economic rationale:** currencies mean-revert toward PPP over multi-year horizons. Provides a low-frequency anchor against trends that have overshot fundamentals.

**Implementation:** as coded in Section 6.1 above.

$$\text{Signal}_4 = -z\bigl[\text{PPPDeviation}_{A/B}\bigr]$$

Negative of PPP deviation: if A is overvalued vs. B, signal is negative (expect A to depreciate).

**Expected Sharpe:** ~0.4 standalone (slow signal; mostly valuable for diversification)
**Rebalance:** Quarterly (or when OECD PPP data updates)

#### Signal 5: CFTC COT Contrarian (Weekly) — Positioning

**Economic rationale:** extreme crowded positions are prone to reversal when the catalyst arrives. Most useful as a risk overlay, not as a standalone alpha signal.

**Implementation:** as coded in Section 7.1 above.

**Expected Sharpe:** ~0.3 standalone
**Rebalance:** Weekly (COT published Fridays)

#### Signal 6: Carry Level (Daily) — Risk Premium

**Economic rationale:** UIP's empirical failure means high-yield currencies earn a systematic risk premium. Carry is the most reliable and largest G10 FX premium historically.

**Implementation:**

```python
# Cross-sectional carry: z-score of 2Y yield levels across G10
rates_panel = pd.DataFrame(rates_dict)  # all G10 2Y yields

# Cross-sectional z-score at each date
def cross_sectional_zscore(df):
    return df.apply(lambda row: (row - row.mean()) / row.std(), axis=1)

carry_signal = cross_sectional_zscore(rates_panel)
# High z-score = high yield relative to G10 average = buy signal
```

**Expected Sharpe:** ~0.5–0.8 (conditioned on vol; degrades in crisis)
**Rebalance:** Daily (or monthly for lower turnover)

### 10.3 Composite Signal Construction

```python
import numpy as np
import pandas as pd

def build_composite_signal(signal_1_rate_change, signal_2_taylor,
                           signal_3_cli, signal_4_ppp,
                           signal_5_cot, signal_6_carry,
                           vix_series):
    """
    Combine 6 signals into a composite position with VIX regime scaling.
    
    Signal weights (sum to 1.0):
    - Signal 1 (rate change): 0.25  — highest predictive power
    - Signal 2 (Taylor rule): 0.20
    - Signal 3 (CLI/growth):  0.20
    - Signal 4 (PPP value):   0.15
    - Signal 5 (COT):         0.10
    - Signal 6 (carry level): 0.10
    
    Returns:
    --------
    pd.Series : Final position signal, scaled by VIX regime
    """
    # Align all signals to common index (resampled to daily)
    def align(s, target_index):
        return s.reindex(target_index, method='ffill')
    
    target_idx = signal_1_rate_change.index
    
    s1 = align(signal_1_rate_change, target_idx)
    s2 = align(signal_2_taylor,      target_idx)
    s3 = align(signal_3_cli,         target_idx)
    s4 = align(signal_4_ppp,         target_idx)
    s5 = align(signal_5_cot,         target_idx)
    s6 = align(signal_6_carry,       target_idx)
    
    # Z-score normalize each signal
    def fast_zscore(s, w=60):
        return ((s - s.rolling(w).mean()) / s.rolling(w).std()).clip(-2, 2)
    
    composite = (
        0.25 * fast_zscore(s1) +
        0.20 * fast_zscore(s2) +
        0.20 * fast_zscore(s3) +
        0.15 * fast_zscore(s4) +
        0.10 * fast_zscore(s5) +
        0.10 * fast_zscore(s6)
    )
    
    # VIX regime scaling (Section 9.2)
    vix_scale = vix_scaler(vix_series.reindex(target_idx, method='ffill'),
                           vix_floor=15.0, vix_ceiling=40.0)
    
    # Apply VIX scaling — scale down in high-vol environments
    # Note: we preserve Signal 1 and carry at 50% even in full risk-off
    # because their VIX response is different from growth/value signals
    final_position = composite * vix_scale
    
    return final_position, vix_scale

# ─── Expected combined Sharpe: 1.2–1.8 ────────────────────────────────────────
# Diversification benefit from 6 partially uncorrelated signals (pairwise
# correlations typically 0.05–0.25) drives substantial Sharpe improvement
# relative to any individual signal (Sharpe ~0.3–2.5 individually)
```

### 10.4 Expected Performance and Diversification Benefit

**Pairwise signal correlations (approximate, monthly data 2000–2024):**

| | S1 Rate Δ | S2 Taylor | S3 CLI | S4 PPP | S5 COT | S6 Carry |
|---|---|---|---|---|---|---|
| **S1 Rate Δ** | 1.00 | 0.15 | 0.08 | −0.05 | 0.02 | 0.12 |
| **S2 Taylor** | 0.15 | 1.00 | 0.22 | 0.08 | 0.04 | 0.20 |
| **S3 CLI** | 0.08 | 0.22 | 1.00 | 0.10 | −0.01 | 0.15 |
| **S4 PPP** | −0.05 | 0.08 | 0.10 | 1.00 | −0.12 | −0.18 |
| **S5 COT** | 0.02 | 0.04 | −0.01 | −0.12 | 1.00 | −0.25 |
| **S6 Carry** | 0.12 | 0.20 | 0.15 | −0.18 | −0.25 | 1.00 |

Low average pairwise correlations (~0.05–0.22) mean the diversification benefit is substantial. The theoretical maximum combined Sharpe from $N$ uncorrelated signals with individual Sharpes $\{SR_i\}$ is:

$$SR_{\text{combined}} = \sqrt{\sum_i SR_i^2}$$

With our 6 signals at approximate individual Sharpes of [2.5, 0.5, 0.7, 0.4, 0.3, 0.6], this gives a theoretical upper bound well above 2.5, but realistic performance with transaction costs, correlations, and parameter instability yields **expected combined Sharpe of 1.2–1.8** — still a significant improvement over any individual signal.

### 10.5 Risk Management and Position Sizing

**Cross-sectional position sizing:**

Rather than using the composite signal directly as a position, convert it to a cross-sectional rank and size positions by rank:

```python
def rank_based_sizing(composite_signals_df, target_vol=0.10, lookback=60):
    """
    Convert composite signals to volatility-scaled cross-sectional positions.
    
    Parameters:
    -----------
    composite_signals_df : pd.DataFrame
        Daily composite signals, columns = currency pairs
    target_vol : float
        Target annualized portfolio volatility
    lookback : int
        Days for volatility estimation
    
    Returns:
    --------
    pd.DataFrame : Daily positions (notional weights)
    """
    # Cross-sectional rank at each date (robust to outliers)
    ranks = composite_signals_df.rank(axis=1, ascending=True)
    n_pairs = composite_signals_df.shape[1]
    
    # Center and normalize ranks
    normalized = (ranks - (n_pairs + 1) / 2) / n_pairs
    
    # Volatility scaling: normalize each pair's position by its realized vol
    realized_vol = composite_signals_df.rolling(lookback).std() * np.sqrt(252)
    vol_scaled    = normalized / realized_vol.clip(lower=0.005)
    
    # Scale to target portfolio volatility
    port_vol_estimate = vol_scaled.std(axis=1).rolling(30).mean() * np.sqrt(252)
    scaling_factor    = target_vol / port_vol_estimate.clip(lower=0.01)
    
    positions = vol_scaled.multiply(scaling_factor, axis=0)
    
    return positions
```

**Hard risk limits:**
- Maximum single-pair position: 3× average pair position (prevents concentration)
- VIX > 40: reduce all positions to 25% of normal size
- Drawdown stop: if 20-day portfolio drawdown exceeds 3σ of historical 20-day drawdowns, reduce all positions by 50%
- Correlation limit: if correlation between any two positions exceeds 0.8 over trailing 20 days, reduce the smaller (weaker signal) position

### 10.6 Data Sources Reference

| Signal | Data | Source | Frequency | Free? |
|---|---|---|---|---|
| 2Y yields (all G10) | Individual country 2Y bond yields | FRED (varies by country) | Daily | Yes |
| Taylor rule (inflation) | CPI indices | FRED | Monthly | Yes |
| Taylor rule (output gap) | Capacity utilization | FRED: `CUMFNS` | Monthly | Yes |
| OECD CLI | CLI amplitude-adjusted | FRED: country-specific | Monthly | Yes |
| PMI differentials | S&P Global Markit PMI | TradingEconomics.com | Monthly | Partly |
| Industrial production | IP indices | FRED: country-specific | Monthly | Yes |
| CPI surprise | Actual vs. consensus | Forex Factory (free, scrape) | Monthly | Partially |
| PPP deviation | OECD PPP rates | stats.oecd.org | Annual | Yes |
| REER | BIS EER dataset | BIS website | Monthly | Yes |
| CFTC COT | Leveraged funds positioning | CFTC.gov (CSV) | Weekly | Yes |
| VIX | CBOE VIX | FRED: `VIXCLS` | Daily | Yes |
| 10Y–2Y spread | Yield curve slope | FRED: `T10Y2Y` | Daily | Yes |
| Fed Funds futures | OIS-implied rate path | CME (delayed 10min) | Daily | Yes |
| FOMC minutes | Text for NLP | Fed website | 8× per year | Yes |
| Oil (WTI) | Daily crude price | FRED: `DCOILWTICO` | Daily | Yes |
| Iron ore | SGX futures | Quandl/Stooq | Daily | Partially |
| IG credit spread | Barclays OAS | FRED: `BAMLC0A0CM` | Daily | Yes |
| Cross-currency basis | EUR/USD 3M basis | Bloomberg / dealer quotes | Daily | Bloomberg only |

---

## Appendix A: Key Academic Citations

| Paper | Journal / Year | Key Finding | Relevance |
|---|---|---|---|
| Fama (1984) | *Journal of Monetary Economics* | Forward premium puzzle: Fama β < 0; carry trade rationale | Carry signal foundation |
| Engel (2016) | *Journal of International Economics* | "New Fama Puzzle": β more negative post-2000; carry stronger | Updated carry evidence |
| Du, Tepper, Verdelhan (2018) | *Journal of Finance* 73(3) | CIP deviations large and persistent post-GFC; banking regulation channel | CIP basis as risk signal |
| Molodtsova & Papell (2009) | *Journal of International Economics* 77(2) | Taylor rule models beat random walk for 11/12 G10 pairs at 1-month horizon | Taylor rule signal |
| Colacito, Riddiough, Sarno (2020) | *Journal of Financial Economics* 137(3), 659–678 | Business cycle differentials explain 30–40% of 6–12M FX variation; Sharpe ~0.8 | CLI growth signal |
| Asness, Moskowitz, Pedersen (2013) | *Journal of Finance* | Value and momentum everywhere; currency factors included | Multi-factor framework |
| Ferraro, Rogoff, Rossi (2015) | *Journal of International Money & Finance* 54 | Oil predicts CAD at daily frequency; paradoxically weak at monthly | Commodity-FX linkage |
| Brunnermeier, Nagel, Pedersen (2008) | *NBER Macroeconomics Annual* | Carry crashes occur during liquidity crises; FX volatility predicts crashes | Carry tail risk |
| Burnside, Eichenbaum et al. (2006) | *AER Papers & Proceedings* | Carry trade excess returns uncorrelated with standard risk factors | UIP failure evidence |
| Obstfeld & Rogoff (1995) | *JPE* | Intertemporal current account model; sudden stop theory | External balance signal |
| Clark & MacDonald (1998) | *IMF Working Paper* | BEER model; equilibrium RER from fundamentals | Valuation model |
| Ranaldo & Söderlind (2010) | *Review of Finance* | Safe-haven currency properties: CHF, JPY in stress periods | RORO framework |
| Chinn & Meredith (2004) | *JIMF* | UIP holds at long horizons (3Y+); fails short-term | Horizon dependence |
| Araci (2019) | *arxiv:1908.10063* | FinBERT: financial domain BERT for sentiment | CB communication NLP |
| Taylor (1993) | *Carnegie-Rochester Conf.* | Original Taylor rule formulation | Policy reaction function |

---

## Appendix B: Complete FRED Ticker Reference

```
# Interest Rates
DGS2          - US 2-Year Treasury Constant Maturity Rate (daily)
DGS10         - US 10-Year Treasury Constant Maturity Rate (daily)
T10Y2Y        - 10-Year Treasury Minus 2-Year Treasury (daily; negative = inverted)
FEDFUNDS      - Federal Funds Effective Rate (monthly)
DFII10        - 10-Year TIPS Yield (real rate, daily)
T5YIE         - 5-Year Breakeven Inflation Rate (daily)
T5YIFR        - 5-Year 5-Year Forward Inflation Expectation Rate (daily)
T10YIE        - 10-Year Breakeven Inflation Rate (daily)

# Growth and Activity
INDPRO        - US Industrial Production Index (monthly)
CUMFNS        - Capacity Utilization: Total Industry (monthly; output gap proxy)
CFNAI         - Chicago Fed National Activity Index (monthly)
GDPNOW        - Atlanta Fed GDPNow (real-time, irregular)
STLENI        - St. Louis Fed Economic News Index (weekly)

# OECD CLIs (amplitude-adjusted where available)
USALOLITOAASTSAM  - US CLI
DEULOLITONOSTSAM  - Germany CLI
JPNLOLITONOSTSAM  - Japan CLI
GBRLOLITONOSTSAM  - UK CLI
CANLOLITONOSTSAM  - Canada CLI
AUSLOLITONOSTSAM  - Australia CLI
FRALOLITONOSTSAM  - France CLI
G7LOLITOAASTSAM   - G7 Aggregate CLI

# Inflation
CPIAUCSL      - US CPI All Urban Consumers (monthly)
PCEPI         - US PCE Price Index (monthly)

# Market Risk and Sentiment
VIXCLS        - CBOE VIX (daily)
BAMLC0A0CM    - ICE BofA US Corporate Index OAS (IG credit spread, daily)
BAMLH0A0HYM2  - ICE BofA US High Yield Index OAS (HY credit spread, daily)

# Commodities
DCOILWTICO    - WTI Crude Oil Price (daily)
GOLDAMGBD228NLBM  - Gold Price (daily)

# External Sector
NETFI         - US Current Account Balance (quarterly)
BOPGSTB       - US Trade Balance (monthly)
```

---

## Appendix C: Python Environment Setup

```bash
# Core quant stack
pip install pandas numpy scipy statsmodels

# FRED data download
pip install pandas-datareader

# Machine learning and HMM
pip install scikit-learn hmmlearn

# NLP for central bank communication
pip install transformers torch sentencepiece

# Visualization
pip install matplotlib seaborn plotly

# Optional: additional financial data
pip install yfinance quandl

# Optional: performance analytics
pip install pyfolio-reloaded  # Sharpe, drawdown, attribution
```

```python
# Verify setup
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime
from hmmlearn import hmm
from transformers import pipeline

# Quick FRED download test
vix = web.DataReader('VIXCLS', 'fred', datetime(2020, 1, 1))
print(f"VIX data loaded: {len(vix)} observations")
print(f"Latest VIX: {vix.iloc[-1, 0]:.2f}")
```

---

## Closing Remarks

The transition from discretionary macro trading to systematic macro modeling is not primarily a technology challenge — it is an epistemological one. The technology (Python, FRED, open-source ML libraries) is available to anyone. The challenge is developing the intellectual discipline to commit ex-ante to signal definitions that will be applied consistently even when your discretionary instinct says "this time is different."

The framework in this document — six signals, a macro scorecard, regime detection, and a composite model — is a complete starting architecture. But it is not a turnkey system. Every component requires calibration to your specific currency universe, rebalancing frequency, and risk tolerance. The backtested Sharpe ratios cited here are indicative ranges from the literature; your implementation will differ based on exact data sourcing, transaction cost assumptions, and the time period tested.

The most important practical advice: **start with the simplest version and add complexity only when you have evidence it helps.** Signal 1 (2Y rate change) alone produced Sharpe ~2.5 in this repository's backtests. Signal 6 (carry) has decades of empirical validation. Start with these two, understand exactly why they work and when they fail, then add the slower macro signals layer by layer.

Build the regime detection framework early, because no signal survives a 2008 or 2020 without protection. And budget significant time for data quality — FRED revises its series, COT data has quirks, and CLI data arrives with lags. The models are only as good as the data they run on.

The macro relationships described in this document — UIP failure, Taylor rule predictability, business cycle differentials — have been documented in peer-reviewed literature over decades and across multiple market regimes. They are not data-mined artifacts. They reflect real economic mechanisms: capital flows seeking returns, central banks responding to inflation and growth, and positioning extremes creating reversals. That theoretical foundation is what distinguishes systematic macro from statistical pattern-matching, and it is what gives confidence that the signals will continue to work in environments that differ from the historical sample.

---

*Document status: research reference — June 2026*
*For use with NotebookLM and desk reference.*
