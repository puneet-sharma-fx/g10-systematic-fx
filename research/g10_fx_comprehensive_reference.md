# G10 FX Systematic Trading: A Comprehensive Reference Document

*For NotebookLM / Self-Study — June 2026*
*Author: Puneet Sharma | Based on primary academic literature*

---

## Preface

This document is a self-contained reference for practitioners building systematic G10 FX strategies. Every major concept is derived from first principles before citing empirical evidence. The document covers exchange rate economics, the three core factors (carry, momentum, value), advanced signals, portfolio construction, risk management, and data infrastructure. It is intended to be read linearly on a first pass and used as a reference thereafter.

The G10 currency universe: USD, EUR, JPY, GBP, CHF, AUD, CAD, NZD, SEK, NOK. Trading these requires understanding why exchange rates move, which systematic signals exist to exploit predictable patterns, and how to combine them into a well-managed portfolio.

---

## Section 1: Exchange Rate Economics — First Principles

### 1.1 What Determines an Exchange Rate

An exchange rate is the relative price of two monies. In a flexible exchange rate regime (post-Bretton Woods, 1973), this price is determined by supply and demand in the spot and forward foreign exchange markets. Three broad forces govern it:

**Trade Flows**: If Country A imports more from Country B than it exports, it must convert its currency into B's currency to pay, creating demand for B's currency and downward pressure on A's. This is the current account channel. However, trade flows settle slowly (weeks to months) and are dwarfed in size by financial flows.

**Capital Flows**: Investors moving money across borders create immediate FX demand. A German investor buying US Treasuries must sell EUR and buy USD. Capital flows dominate spot FX — the BIS estimates daily FX turnover at $7.5 trillion (2022), of which most is financial, not trade-related. Capital flows respond to interest rate differentials, risk appetite, and growth expectations.

**Portfolio Balance**: The stock equilibrium view (Kouri 1976, Branson 1977) says the exchange rate clears the market for stocks of foreign assets. If the private sector holds "too many" foreign assets relative to its desired allocation, it will sell them, appreciating the domestic currency.

These three forces interplay continuously. In practice, over short horizons (days to months), capital flows and risk appetite dominate. Over long horizons (years), trade balances and relative price levels matter more. This time-horizon dependence is crucial for understanding why different signals work at different frequencies.

### 1.2 Uncovered Interest Parity (UIP): Derivation and Statement

UIP is the bedrock arbitrage relationship in international finance. It says: if capital is mobile and investors are risk-neutral, the expected change in the exchange rate must exactly offset the interest rate differential between two countries. Otherwise, investors would shift capital to the higher-yielding country until the return differential is closed through exchange rate movements.

**Formal Derivation**

Let:
- $i_t$ = domestic short-term interest rate (annualized)
- $i^*_t$ = foreign short-term interest rate (annualized)
- $S_t$ = spot exchange rate (domestic per foreign unit, e.g. USD per EUR)
- $E_t[S_{t+1}]$ = expected spot rate next period

A domestic investor can earn $1 + i_t$ by investing at home. Alternatively, she can convert to foreign currency ($1/S_t$ units), invest abroad ($1/S_t \times (1 + i^*_t)$ units), and convert back, earning:

$$\frac{(1 + i^*_t) \cdot E_t[S_{t+1}]}{S_t}$$

For no-arbitrage (assuming risk neutrality):

$$1 + i_t = \frac{(1 + i^*_t) \cdot E_t[S_{t+1}]}{S_t}$$

Rearranging and using the approximation $\ln(1+x) \approx x$ for small $x$:

$$\boxed{E_t[\Delta s_{t+1}] = i_t - i^*_t}$$

where $\Delta s_{t+1} = \ln(S_{t+1}/S_t)$ is the log change in the spot rate (positive = domestic appreciation).

**What UIP Predicts**: If the domestic interest rate is 3% and the foreign rate is 1%, UIP predicts the domestic currency will *depreciate* by 2% over the next year, so that the net return is equalized. High-interest-rate currencies are predicted to fall in value, exactly offsetting their yield advantage.

### 1.3 The Forward Premium Puzzle: UIP Violation

UIP fails catastrophically in the data. This is the single most important empirical fact for systematic FX trading, because its failure is the source of the carry trade premium.

**The Fama (1984) Test**

Eugene Fama (1984, "Forward and Spot Exchange Rates," *Journal of Monetary Economics*) ran the canonical regression:

$$\Delta s_{t+1} = \alpha + \beta (f_t - s_t) + \varepsilon_{t+1}$$

where $(f_t - s_t)$ is the forward premium, which equals the interest rate differential by covered interest parity (see Section 1.4). Under UIP, $\alpha = 0$ and $\beta = 1$.

**The Empirical Finding**: Fama found $\beta < 0$ for all currencies in his sample. The average $\beta$ across 75 published estimates surveyed by Froot (1990) is **-0.88**. Not just less than 1 — negative. This means high-interest-rate currencies *appreciate* on average, rather than depreciate as UIP predicts.

This is the **Forward Premium Puzzle** or **Fama puzzle**. It implies a simple strategy: go long high-interest-rate currencies and short low-interest-rate currencies (the carry trade) earns positive expected returns.

**Why Does UIP Fail?** Three competing explanations:

1. **Risk Premium**: Investors demand compensation for holding high-yield currencies because they carry systematic risk (they tend to fall sharply during global risk-off episodes). The negative $\beta$ reflects a time-varying risk premium, not irrational behaviour.

2. **Peso Problem**: High-yielding currencies may face small but catastrophic crash risk (e.g., EM currency devaluations). The historical sample underweights these tail events; the true expected return is zero, but realized returns look positive.

3. **Behavioral / Rational Inattention**: Investors underreact to interest rate signals due to information costs. Capital moves slowly, and the currency appreciates before the full adjustment occurs.

The "New Fama Puzzle" (Chinn-Quayyum 2012) documents that the $\beta$ has become *less* negative post-1990, possibly reflecting financial globalization and faster arbitrage, but the violation remains significant.

### 1.4 Covered Interest Parity (CIP): The Other Arbitrage Relationship

CIP is an arbitrage relationship involving the *forward* exchange rate rather than the *expected* future spot rate. It is explicitly riskless (no currency view required).

**CIP Condition**:

$$\frac{F_t}{S_t} = \frac{1 + i_t}{1 + i^*_t}$$

where $F_t$ is the forward rate for delivery at $t+1$. In log form:

$$\boxed{f_t - s_t = i_t - i^*_t}$$

The forward premium equals the interest differential. If this holds exactly, there is no riskless arbitrage from borrowing in one currency and lending in another while hedging via the forward market.

**Why CIP Held Pre-2008**: Pre-GFC, arbitraging CIP deviations required only small amounts of capital, no collateral, and intermediated through bank balance sheets. Deviations were tiny (a few basis points) and quickly arbitraged away.

**Why CIP Broke Post-2008**: Du, Tepper, and Verdelhan (2018, *Journal of Finance*, Vol. 73, pp. 915-957) documented that CIP deviations ("the basis") became large, persistent, and systematic after the GFC. For major G10 pairs, the dollar cross-currency basis averaged **-20 to -50 basis points** — meaning borrowing in USD and lending synthetically via EUR was cheaper than borrowing in USD directly. This is not supposed to happen in arbitrage-free markets.

The mechanism: post-GFC regulation (Basel III leverage ratio, supplementary leverage ratio) made it costly for bank dealers to expand their balance sheets to arbitrage away the basis. The regulatory constraint created a wedge between the "textbook" CIP world and reality. Quarter-end spikes in the basis are particularly large because banks window-dress their balance sheets at quarter-end.

**Implication for FX Trading**: The CIP basis (specifically, the cross-currency basis swap spread) has become a distinct market signal — see Section 5.5.

### 1.5 Purchasing Power Parity (PPP)

PPP is the long-run anchor for exchange rates. It says that the exchange rate between two currencies should equal the ratio of price levels in the two countries.

**Absolute PPP**: $S = P/P^*$ where $P$ is the domestic price level, $P^*$ is foreign. A Big Mac costing $5 in the US and £4 in the UK implies an equilibrium exchange rate of 1.25 USD/GBP.

**Relative PPP**: Exchange rates change to offset inflation differentials:
$$\Delta s = \pi - \pi^*$$
where $\pi$ is domestic inflation and $\pi^*$ is foreign inflation. This is a weaker, more empirically supported version.

**Why PPP is Slow to Hold**: PPP has an estimated "half-life of deviations" of 3-5 years (Rogoff 1996 "The Purchasing Power Parity Puzzle," *JEL*). Reasons:
- Prices are sticky (goods markets clear slowly vs. financial markets)
- Transport costs, tariffs, and non-traded goods create permanent deviations
- Financial flows can push currencies far from PPP for extended periods

**The Balassa-Samuelson Effect**: A structural reason why absolute PPP fails between rich and poor countries. Balassa (1964) and Samuelson (1964) showed:

If a country has higher productivity in traded goods (manufacturing) relative to non-traded goods (services) than the rest of the world, its price level will be higher. Because wages are set in the traded sector and equalized across sectors within the country, higher productivity in traded goods translates into higher wages in *both* sectors, raising the price of non-tradable services.

Implication: Rich countries (high traded-sector productivity) systematically have overvalued real exchange rates relative to PPP predictions — not because of misalignment, but because of structural differences. For G10 FX research, this matters primarily for very long-run valuation anchors and less for tactical signals.

**PPP as a Trading Signal**: Despite its long mean-reversion time, PPP-based value can be a useful *slow* portfolio position — 3-5 year expected payoff horizon, Sharpe ratio around 0.4-0.5 standalone. See Section 4 for full treatment.

### 1.6 The Meese-Rogoff Puzzle (1983)

Richard Meese and Kenneth Rogoff published "Empirical Exchange Rate Models of the Seventies: Do They Fit Out of Sample?" in the *Journal of International Economics* in 1983. Their finding remains one of the most cited results in all of international finance.

**The Test**: Meese and Rogoff took state-of-the-art structural exchange rate models of the time — the Dornbusch (1976) sticky-price monetary model, the Frankel (1979) real interest rate differential model, and others — and tested their out-of-sample forecasting performance against a simple benchmark: the random walk (today's exchange rate is the best forecast of tomorrow's).

**The Finding**: Even when the structural models were *given the actual future values of their right-hand-side variables* (money supply, output, interest rates, prices), they could not beat the random walk in mean squared error at horizons of 1, 6, and 12 months. This is a devastating result — the models fail even with cheating.

**Why It Persists**: The puzzle persists because:

1. **Structural instability**: Exchange rate models estimated in one period break down in another. The relationship between macro variables and exchange rates shifts as monetary regimes change.

2. **High noise-to-signal ratio**: Macro variables explain little of the high-frequency variance in exchange rates. FX markets react to news about *changes* in fundamentals, not levels.

3. **Simultaneity**: Exchange rates respond to macro variables, but macro variables also respond to exchange rates, making identification hard.

**Modern Progress**: Machine learning has partially addressed the Meese-Rogoff puzzle. Neely and Rapach (2011), Ferraro, Rogoff, and Rossi (2015), and more recent work using elastic net regularization on large macroeconomic panels show statistically significant out-of-sample R² values — but these are small (1-5%), and the gains are concentrated in specific periods and currencies. The random walk remains competitive overall.

**The Key Takeaway for Practitioners**: Do not build directional fundamental forecasts for exchange rates at horizons under 6 months. Carry, momentum, and value work *not* because they forecast exchange rates precisely, but because they exploit systematic risk premia and slow-moving structural forces that do not require precise point forecasts.

### 1.7 Risk Premium Decomposition

The return on a carry trade can be decomposed into two parts:

$$\underbrace{i_t - i^*_t}_{\text{interest differential}} = \underbrace{E_t[\Delta s_{t+1}]}_{\text{expected spot change}} + \underbrace{\lambda_t}_{\text{risk premium}}$$

Under UIP, $\lambda_t = 0$. The carry return is entirely eroded by expected depreciation. In the data, $E_t[\Delta s_{t+1}] < i_t - i^*_t$, so $\lambda_t > 0$ — there is a positive risk premium for holding high-yield currencies.

The research question is: is $\lambda_t$ compensation for bearing systematic risk, or is it irrational? The evidence (reviewed in Sections 2-4) suggests primarily risk premium, with some behavioral amplification.

---

## Section 2: The Carry Factor — Complete Treatment

### 2.1 Mathematical Construction

The carry trade is the most studied and most profitable systematic FX strategy. In its simplest form:

1. **Rank** all currencies by their short-term interest rate (or equivalently, by the 1-month forward premium/discount against the base currency, typically USD).
2. **Long** the highest-yielding currencies (top tercile or quartile).
3. **Short** the lowest-yielding currencies (bottom tercile or quartile).
4. **Rebalance** monthly.

The currency-level carry signal for currency $i$ against USD:

$$\text{Carry}_i = f_{i,t} - s_{i,t} \approx i_{i,t} - i_{\text{USD},t}$$

where the approximation follows from CIP (before the post-2008 basis disruption).

**Cross-Sectional Carry**: Sort currencies by carry score each month; go long the top quartile, short the bottom quartile. This is the standard portfolio formation.

**Time-Series Carry**: For each currency pair in isolation, take a long position when carry is positive, short when negative. This is the binary version of a bilateral carry trade and is less efficient than cross-sectional because it ignores the relative attractiveness across all pairs.

**The HML_FX Factor**: Lustig, Roussanov, and Verdelhan (2011, *American Economic Review*, Vol. 101, pp. 3477-3500) formalize the carry factor as HML_FX (high-minus-low carry), constructed by sorting a broad cross-section of currencies into six portfolios by 1-month forward discount, then going long portfolio 6 (highest carry) and short portfolio 1 (lowest carry). They show this factor, along with the dollar factor (DOL), explains most of the cross-sectional variation in currency returns.

### 2.2 The Dollar Factor (DOL)

Lustig, Roussanov, and Verdelhan (2011) decompose currency returns into two systematic components:

$$r_{i,t} = \beta_i \cdot \text{DOL}_t + \gamma_i \cdot \text{HML}_{FX,t} + \varepsilon_{i,t}$$

- **DOL** = simple average return of all currencies against USD. This reflects global appetite for dollar risk. When investors globally sell USD risk (e.g., in a risk-on environment), DOL is positive.
- **HML_FX** = carry factor (long high-yield, short low-yield currencies). This captures the cross-sectional dispersion in returns associated with interest rate differentials.

**Why DOL Matters for Portfolio Construction**: If your carry portfolio has a large positive DOL beta, you are inadvertently taking a directional view on the USD. In periods like 2014-2015 (USD strengthening) or 2020 (COVID dollar spike), an unhedged DOL exposure would wipe out carry returns. Monitoring the portfolio DOL exposure and keeping it close to zero is a risk management priority.

### 2.3 Why Carry Works: Risk Premium vs. Behavioral Explanation

**Risk Premium View**: Carry earns a premium because high-yield currencies carry systematic risk. They tend to depreciate sharply during global recessions, risk-off episodes, and financial crises. Lustig and Verdelhan (2007) show carry returns correlate with consumption growth — high-yield currencies deliver low returns exactly when investors' marginal utility of consumption is highest (recessions). From a CAPM perspective, these currencies have positive betas to aggregate risk.

Menkhoff, Sarno, Schmeling, and Schrimpf (2012, *Journal of Finance*, Vol. 67, pp. 681-718) show that **global FX volatility** is the dominant risk factor: high-yield currencies load positively on global FX volatility innovations and earn higher average returns as compensation. The volatility risk premium explains roughly 90% of the cross-sectional variation in carry returns.

**Behavioral / Gradual Adjustment View**: Investors process interest rate information slowly. Capital flows to high-yield currencies gradually, causing them to appreciate before the adjustment is complete. This underreaction generates positive carry returns in the early part of the cycle. However, as more capital arrives and the trade becomes crowded, crash risk builds up.

Both explanations have empirical support. The truth is likely a combination: structural risk compensation amplified by behavioral crowding dynamics.

### 2.4 The Carry Crash Mechanism: Brunnermeier-Nagel-Pedersen (2009)

Markus Brunnermeier, Stefan Nagel, and Lasse Pedersen (2009, *NBER Macroeconomics Annual*, Vol. 23) provided the definitive analysis of carry crash risk. Key findings:

**Negative Skewness**: The distribution of carry returns is negatively skewed. Positive carry returns accumulate slowly (months to years of gradual appreciation and yield collection), while losses occur suddenly (sharp reversal in days to weeks). The skewness of monthly carry returns is approximately **-1.0 to -2.0** in most sample periods.

**The Crash Mechanism** (the margin spiral):

1. Carry trades accumulate. Speculators borrow in JPY/CHF (low yield) and invest in AUD/NZD (high yield).
2. A negative shock (global risk-off) hits. High-yield currencies drop slightly.
3. This triggers margin calls. Speculators are forced to unwind: sell AUD, buy JPY/CHF.
4. Forced selling amplifies the price move: AUD drops further, JPY/CHF spike.
5. More margin calls trigger. The spiral feeds on itself.
6. The unwinding is rapid and violent — the crash.

**JPY and CHF as Safe Havens**: During carry crashes, JPY and CHF — the traditional funding currencies with the lowest interest rates — appreciate sharply. They provide negative carry but positive return in crises. This safe-haven property is a structural feature, not a coincidence.

**The CFTC COT Signal**: Brunnermeier et al. show that speculative positioning in currency futures (available from the CFTC Commitments of Traders report) predicts crash risk. When net long positions in high-yield currencies (AUD, NZD, CAD) are at extremes, the next-period downside skewness is large.

### 2.5 Carry Sharpe Ratios: Evidence Across Periods

| Period | Sample | Annualized Sharpe | Notes |
|--------|--------|-------------------|-------|
| 1990-2007 (pre-GFC) | G10 pairs | ~0.88-1.08 | Near-zero rate differentials don't distort |
| 2008-2023 (post-GFC) | G10 pairs | ~0.25-0.40 | ZIRP compressed differentials; multiple crashes |
| Full 1990-2023 | G10 pairs | ~0.57 | Dragged down by 2008 (-20%), 2015, 2022 |
| EM + G10 broad universe | 30+ currencies | ~0.80-1.20 | Larger differentials improve ratio |

Sources: Currency carry trade decline analysis (Burnside et al. 2011; post-GFC performance from ScienceDirect 2021 study showing drop from Sharpe ~1.08 to ~0.25 post-GFC).

The post-2008 decline has two causes: (1) ZIRP and near-zero rate differentials within G10 reduced the raw carry signal, and (2) the 2008 carry crash and subsequent bouts of deleveraging imposed large drawdowns.

### 2.6 Vol-Normalised Carry: Dupuy (2021)

Dupuy (2021, *Journal of Banking & Finance*) constructs a volatility-normalised carry signal:

$$\text{Vol-Carry}_i = \frac{i_{i,t} - i_{\text{base},t}}{\sigma_{i,t}}$$

where $\sigma_{i,t}$ is the realized volatility of currency $i$ over the past month (or quarter).

**Why This Works**: Raw carry is high for currencies that are simply more volatile — they need to offer higher yields to attract capital. By dividing by volatility, you isolate the *risk-adjusted* carry signal. Currencies with high carry *per unit of volatility* are genuinely attractive, not just high-risk bets.

**Key Finding**: Vol-normalised carry **flips the skewness from negative to approximately zero or slightly positive**. The crash mechanism is dampened because you are automatically underweighting volatile currencies (which are most prone to sharp reversals) and overweighting the stable high-yielders. Sharpe ratio improvements are in the range of 20-40% versus raw carry.

**Construction in Practice**:
```python
import pandas as pd
import numpy as np

# rate_diff: DataFrame of interest rate differentials (currency vs USD)
# spot_returns: DataFrame of log spot returns

# 1. Compute 21-day realized volatility for each currency
vol = spot_returns.rolling(21).std() * np.sqrt(252)

# 2. Compute vol-normalised carry
vol_carry = rate_diff / vol

# 3. Cross-sectional z-score for portfolio formation
def cross_sectional_zscore(df):
    return df.subtract(df.mean(axis=1), axis=0).divide(df.std(axis=1), axis=0)

vol_carry_z = cross_sectional_zscore(vol_carry)

# 4. Position sizing: proportional to z-score, capped at ±2
positions = vol_carry_z.clip(-2, 2)
```

### 2.7 Conditional Carry: Global FX Vol Regime

Menkhoff et al. (2012) show that carry returns are strongly *conditional on the global FX volatility regime*. In low-volatility regimes, carry earns well; in high-volatility regimes, carry loses.

**Construction**: Build a global FX vol index as the average implied volatility (or realized volatility) across all G10 currency pairs. Condition the carry position on this:

$$w_t = \bar{w} \times \Phi\left(\frac{\text{GlobalVol}_t - \mu_{\text{vol}}}{\sigma_{\text{vol}}}\right)^{-\gamma}$$

A simpler step-function version: if global FX vol is above its 75th percentile, halve carry position size. Above the 90th percentile, go to zero or slight short. This regime-conditioning removes the worst crash risk while preserving most of the upside.

**Why Global FX Vol is Better than VIX**: While VIX (S&P 500 implied vol) is correlated with carry risk, global FX vol is more directly informative about the specific risks in the FX market. During some periods (e.g., oil shocks, bond sell-offs), VIX is elevated while FX vol is contained and carry still earns. The global FX vol index avoids these false signals.

---

## Section 3: The Momentum Factor — Complete Treatment

### 3.1 Price Momentum in FX: Construction

FX momentum is the tendency of currencies that have appreciated over the past 12 months to continue appreciating, and vice versa.

**Standard 12-1 Construction**:
- Look-back period: 12 months
- Skip period: omit last 1 month (skip-last-month)
- Holding period: 1 month

$$\text{Mom}_{i,t} = \ln(S_{i,t-1}) - \ln(S_{i,t-13})$$

The signal for currency $i$ is the cumulative log return from month $t-13$ to $t-1$.

**Why Skip the Last Month?** In equities, Jegadeesh and Titman (1993) documented a short-term reversal at the 1-month horizon overlaid on the 2-12 month momentum. FX shows similar short-term reversal — likely due to bid-ask bouncing and market-making microstructure noise. Skipping month $t-1$ avoids buying into this noise.

### 3.2 Time-Series vs. Cross-Sectional Momentum

**Cross-Sectional Momentum (CSMoM)**: Sort currencies by past return. Long top third, short bottom third. The signal is *relative* — it captures which currencies are strong *relative to the peer group*, independent of whether all currencies are moving in the same direction.

**Time-Series Momentum (TSMoM)**: For each currency pair, if the past 12-month return is positive, go long; if negative, go short. Moskowitz, Ooi, and Pedersen (2012, *Journal of Financial Economics*, Vol. 104, pp. 228-250) show this works across 58 liquid instruments including FX. Portfolio-level Sharpe ratio exceeds 1.20 when diversified across all asset classes; FX standalone is approximately **0.8**.

**Which Matters More for G10 FX?** Both, but for different reasons:
- **CSMoM** requires a broad cross-section (9 pairs is thin — see below).
- **TSMoM** works on each pair individually, so it is more robust in small universes.
- **Combination**: Use CSMoM for pair selection and TSMoM for direction filter. A currency that ranks high in CSMoM *and* has a positive TSMoM signal gets a full position; rank high but negative TSMoM gets a half position.

### 3.3 The Cross-Sectional Size Problem

Menkhoff, Sarno, Schmeling, and Schrimpf (2012, *Journal of Financial Economics*, Vol. 106, pp. 660-684) document that FX momentum is profitable but note that it requires a sufficiently large cross-section. With only 9 G10 pairs, the cross-sectional dispersion of 12-month returns is limited, and the strategy may pick up idiosyncratic noise rather than systematic momentum.

Their recommendation: use at least 40 currencies (including EM) for robust CSMoM. For G10-only strategies, TSMoM is more reliable than CSMoM.

The Sharpe ratio of the 1-month formation / 1-month holding momentum strategy (MOM(1,1)) in their sample is approximately **0.95**, but this uses a broader cross-section.

### 3.4 Why Momentum Works in FX

Three complementary mechanisms:

1. **Underreaction to Macro News**: Interest rate changes, growth surprises, and policy shifts are not instantly priced into exchange rates. Gradual portfolio rebalancing means a trend develops as investors slowly process the information.

2. **Herding and Trend-Following Flows**: CTAs and trend-following funds operate on rule-based systems. As they observe a trend developing, they allocate capital in the same direction, reinforcing the trend. This is self-fulfilling until the trend reverses.

3. **Carry-Momentum Interaction**: High-yield currencies tend to appreciate (carry + momentum aligned) until a crash, after which they tend to continue falling briefly (post-crash momentum in reverse). This creates momentum *within* the carry factor cycle.

### 3.5 Momentum Crashes and the Volatility Link

FX momentum, like equity momentum (Daniel and Moskowitz 2016), is subject to crashes. The crash pattern:

- Momentum crashes occur predominantly *after carry crashes*.
- After a carry crash, the previous winners (high-yield currencies) continue to fall as deleveraging persists. Momentum portfolios that were long high-yield (because they appreciated pre-crash) now hold the worst-performing assets.
- During volatility spikes (VIX > 30 or global FX vol > 90th percentile), momentum returns are sharply negative.

**Volatility-Scaling as a Crash Mitigant**: Moskowitz et al. (2012) show that scaling TSMoM positions inversely by realized volatility significantly improves the risk-adjusted performance and reduces crash risk. This is structurally similar to the vol-normalised carry construction.

### 3.6 The 50-DMA Overlay: Why It Degrades Carry Signal

A natural impulse is to add a trend filter (e.g., 50-day moving average) on top of carry. If the currency is above its 50-DMA, allow the carry position; if below, exit or reduce.

**Strategy #14 Finding (This Repo)**: Testing the 50-DMA trend filter overlay on top of the carry signal degraded performance, reducing the Sharpe ratio from **2.73** (Strategy #12, carry + vol) to **1.59** (Strategy #14, carry + vol + 50-DMA). Why?

1. **Signal Redundancy**: Carry already contains *some* trend information — high-yield currencies tend to appreciate precisely because capital flows in, creating momentum. Adding a trend filter re-incorporates signal that is already partially captured.

2. **Overfitting Risk**: Moving average crossovers have many variants (period length, fast/slow combinations). Any specific choice is likely curve-fitted.

3. **Regime-Dependent Performance**: The 50-DMA filter works well in trending markets (2014-2015 USD trend) but whipsaws in choppy regimes (2011-2013 post-QE oscillations).

4. **Transaction Costs**: The filter adds churn (more frequent position reversals) which, after realistic transaction costs (see Section 8.5), is net negative.

The lesson: momentum and carry are related but not identical. The momentum factor as a *cross-sectional ranking signal* adds value to carry; moving-average rules as *individual pair* trend filters generally do not.

---

## Section 4: The Value Factor — Complete Treatment

### 4.1 PPP-Based Value: Construction

FX value is the systematic tendency of undervalued currencies (relative to their long-run equilibrium) to appreciate, and overvalued currencies to depreciate. The standard value construction:

$$\text{Value}_{i,t} = -\left(\ln(S_{i,t}) - \ln(\text{PPP}_{i,t})\right)$$

where $\text{PPP}_{i,t}$ is the PPP-implied exchange rate, computed as:

$$\ln(\text{PPP}_{i,t}) = \ln(S_{i,t_0}) + \int_{t_0}^{t} (\pi_i - \pi_{\text{base}}) \, dt$$

More practically (Asness, Moskowitz, and Pedersen 2013, *Journal of Finance*, Vol. 68, pp. 929-985), the 5-year lagged real exchange rate change is used as a proxy for value:

$$\text{Value}_{i,t} = -\left(\ln(S_{i,t}) - \ln(S_{i,t-60})\right) + (\pi_{i,t_{-60:t}} - \pi_{\text{base},t_{-60:t}})$$

This is the negative of the real appreciation over the past 5 years. A currency that has appreciated in real terms for 5 years is "expensive" (negative value signal); one that has depreciated is "cheap" (positive value signal).

### 4.2 FX Value vs. Equity Value

In equities, value is anchored to earnings, book value, or cash flows — fundamental economic quantities that define what a company is intrinsically worth. In FX, there is no analogous anchor. The valuation benchmark is either:

1. **PPP**: Based on price levels (Big Mac index, CPI basket comparison). Informative but has structural biases (Balassa-Samuelson).
2. **BEER (Behavioural Equilibrium Exchange Rate)**: Econometric model relating the real exchange rate to economic fundamentals (terms of trade, relative productivity, net foreign assets). More sophisticated but requires macroeconomic data.
3. **FEER (Fundamental Equilibrium Exchange Rate)**: Normative concept — the exchange rate consistent with current account balance at full employment. Used by the IMF. Not directly tradeable.

**The Key Difference**: FX value is *relative* (compared to historical real exchange rate) rather than *absolute* (compared to an independent fundamental anchor). This makes the signal noisy and slow to resolve.

### 4.3 Evidence and Horizon Dependency

| Metric | FX Value | Equity Value |
|--------|----------|-------------|
| Horizon to full realization | 3-5 years | 1-3 years |
| Standalone Sharpe ratio | ~0.4-0.5 | ~0.4-0.7 |
| t-statistic (monthly returns) | ~2.5-3.5 | ~3.0-5.0 |
| Correlation with momentum | ~-0.5 | ~-0.3 to -0.5 |

Sources: Asness et al. (2013); Menkhoff et al. (2017 "Currency Value," *Review of Financial Studies*).

The slow realization horizon means FX value is a *position overlayer* rather than a primary signal. In a portfolio context, the 3-5 year mean-reversion acts as a gentle tilt — it shifts the portfolio toward cheap currencies but does not drive tactical allocation on a monthly basis.

### 4.4 Negative Correlation with Momentum: The AQR Triplet Effect

A structurally critical property: FX value and momentum are negatively correlated (approximately -0.5). This creates powerful diversification:

$$\text{Var}(\text{Value} + \text{Momentum}) = \text{Var(Value)} + \text{Var(Mom)} + 2\text{Cov(V,M)}$$

With $\text{Cov(V,M)} < 0$, the combined variance is *less than the sum of individual variances*. If both value and momentum have Sharpe ratios of 0.5 and correlation of -0.5, the equal-weighted combination achieves approximately:

$$\text{SR}_{\text{combined}} \approx \frac{0.5 + 0.5}{\sqrt{0.5^2 + 0.5^2 + 2(-0.5)(0.5)(0.5)}} = \frac{1.0}{\sqrt{0.25}} \approx 1.0 + $$

The exact gain depends on assumptions, but the combination reliably delivers Sharpe ratios well above either component alone. This is the mathematical basis for the AQR triplet: carry + momentum + value.

Asness et al. (2013) report combined Sharpe ratios across 8 asset classes of approximately **1.0-1.5** for the three-factor combination, compared to **0.4-0.8** for individual factors.

### 4.5 BEER and FEER Models

**BEER (Behavioural Equilibrium Exchange Rate)**: Estimated using cointegrating relationships between the real exchange rate and fundamentals like:
- Terms of trade
- Relative GDP per capita
- Net foreign asset position
- Government debt differential

The deviation of the actual real exchange rate from the BEER estimate is the mispricing signal. BEER adds predictive power over raw PPP by controlling for structural factors.

**FEER (Fundamental Equilibrium Exchange Rate)**: A normative concept from Williamson (1994), defining the exchange rate that would produce a sustainable current account position at full employment. The IMF's External Balance Assessment uses FEER-type methods to assess currency misalignment. FEER is not easily operationalized for trading signals due to data lag and model dependence.

---

## Section 5: Advanced Signals — Each Explained from First Principles

### 5.1 Vol-Normalised Carry

**Mechanism**: Carry divided by realized volatility isolates risk-adjusted yield. Currencies that offer more yield per unit of risk are genuinely more attractive.

**Construction**: See Section 2.6.

**Evidence**: Dupuy (2021, *Journal of Banking & Finance*, Vol. 133) documents Sharpe ratio improvement of ~0.3 over raw carry, with skewness flipping from approximately -1.5 to approximately +0.2. The key driver is the automatic underweighting of volatile high-yielders (e.g., AUD/JPY) that drive carry crashes.

**Data Sources**: Short-term rate differential (FRED for US, ECB for EUR, respective central bank APIs for others); realized vol from daily spot returns (Yahoo Finance or ECB).

### 5.2 Carry-TSMOM Filter

**Mechanism**: A meta-signal that combines carry direction with time-series momentum to determine regime. When both carry *and* the currency's recent momentum are aligned (e.g., AUD has positive carry AND has been appreciating on a 12-month basis), the signal is high-conviction. When they diverge (positive carry but recent depreciation), the signal is low-conviction and position is halved.

**Construction**:
```python
# carry_signal: +1 (long) or -1 (short) from cross-sectional carry ranking
# tsmom_signal: +1 if 12-month return > 0, -1 otherwise

# Agreement: full position
# Disagreement: 50% position or zero
combined_signal = np.where(
    carry_signal == tsmom_signal,
    carry_signal * 1.0,   # full position
    carry_signal * 0.5    # half position on disagreement
)
```

**Evidence**: Momentum as a filter on carry is documented in Daniel and Moskowitz (2016) for equity momentum crashes, and the principle extends to FX. Post-carry-crash, momentum turns negative on the previous long currencies — the filter exits before the full unwind.

### 5.3 Global FX Vol Conditioning vs. VIX

**Mechanism**: Carry returns are highest in low-volatility environments and turn negative when global FX volatility spikes. Conditioning on the volatility regime allows dynamic risk allocation.

**Global FX Vol Construction**:
```python
# G10 pairs: EURUSD, GBPUSD, AUDUSD, NZDUSD, CADUSD, USDCHF, USDJPY, USDSEK, USDNOK
# Use 1-month implied vol (from options markets) or 21-day realized vol

vol_cols = ['EURUSD_vol', 'GBPUSD_vol', 'AUDUSD_vol', 'USDJPY_vol', ...]
global_fx_vol = fx_vols[vol_cols].mean(axis=1)

# Percentile rank (rolling 252-day window)
vol_percentile = global_fx_vol.rolling(252).apply(
    lambda x: pd.Series(x).rank(pct=True).iloc[-1]
)

# Position scalar: 1.0 below 50th percentile, scaling down to 0 at 95th
position_scalar = np.clip(1.0 - (vol_percentile - 0.5) / 0.45, 0, 1)
```

**VIX vs. Global FX Vol**: VIX measures S&P 500 30-day implied vol. It captures equity market stress. Global FX vol captures FX-specific stress. The correlation between the two is high (~0.7) but not perfect. In commodity-driven risk-off events (e.g., 2015-16 China slowdown), FX vol spikes while equity vol is more moderate. Using global FX vol avoids these false signals from the equity market.

Menkhoff et al. (2012 JF) show that global FX vol innovations have a **t-statistic of approximately -5** in the cross-section of carry returns — it is the dominant risk factor.

### 5.4 CIP Basis as a Crash Indicator

**Mechanism**: The cross-currency basis (CIP deviation) widens sharply before and during carry crashes. When the basis is very negative (dollar funding is expensive), it signals dollar scarcity and risk-off conditions that are historically associated with carry unwinds.

**The Cross-Currency Basis**:
$$x_t = (f_t - s_t) - (i_t - i^*_t)$$

In equilibrium, $x_t = 0$ (CIP holds). Post-2008, $x_t$ is persistently negative for EUR, JPY, CHF.

**As a Signal**: 
- When the EUR-USD basis swings sharply more negative (e.g., below -50 bps), reduce carry positions — this signals funding stress.
- Quarter-end spikes are mechanical (balance sheet window-dressing) and should be filtered.

**Data Source**: Cross-currency basis swap rates from Bloomberg (Bloomberg EURUSD1M XCCY Curncy, etc.). Approximated from money market rates for research purposes: compute the implied 3-month forward rate from OIS rates and compare to market forward.

Du, Tepper, and Verdelhan (2018) show the basis has an average magnitude of **20-50 bps** for major G10 pairs and is strongly correlated with bank CDS spreads and repo rates.

### 5.5 Term Structure Slope Differential

**Mechanism**: The slope of the yield curve (e.g., 10-year rate minus 2-year rate) is a proxy for the business cycle phase and future short rate expectations. A steeper curve signals expansion ahead; an inverted curve signals recession. Countries with steeper yield curves (relative to peers) tend to have currencies that appreciate as the rate cycle turns upward.

**Construction**:
$$\text{Slope}_i = y_{i,10y} - y_{i,2y}$$
$$\text{Slope Signal}_i = \text{Slope}_i - \text{Slope}_{\text{USD}}$$

Positive slope differential: currency $i$ has a steeper curve than USD → expectation of rate hikes ahead → currency likely to appreciate.

**Evidence**: Ang and Chen (2010) and Lustig, Roussanov, and Verdelhan (2014, *Journal of Financial Economics*) document that the slope differential predicts currency returns with t-statistics of 2-3 at the 1-year horizon. The signal complements carry (which uses the short end only) by incorporating term structure information.

**Data Source**: 2-year and 10-year government bond yields. FRED for USD (DGS2, DGS10), ECB for EUR, Bank of England for GBP, respective central bank APIs.

### 5.6 Business Cycle Differential (OECD CLI)

**Mechanism**: Countries at different phases of the business cycle have different monetary policy outlooks and risk sentiment. A country whose growth is accelerating relative to trading partners will likely see its central bank hike rates and its currency appreciate.

**The OECD Composite Leading Indicator (CLI)**: Monthly index designed to identify turning points in the business cycle approximately **6-9 months** ahead. Constructed from a variety of financial and economic variables (new orders, housing starts, share prices, yield curve slope, etc.).

**Construction**:
$$\text{CLI Signal}_i = \text{CLI}_i - \text{CLI}_{\text{USD}}$$

A positive CLI differential (country $i$ accelerating faster than US) is a positive FX signal for currency $i$.

**Evidence**: Macro-based signals tend to be slow (3-12 month predictive window) with t-statistics of 1.5-2.5 in rolling cross-sections. The CLI signal is best used as a *portfolio tilt* rather than a primary trading signal. It is particularly valuable as a diversifier against carry, which tends to be growth-agnostic.

**Data Source**: OECD.Stat API (`DP_LIVE` dataset, `MEI_CLI` series), updated monthly with a 4-6 week lag.

### 5.7 Taylor Rule Deviation

**Mechanism**: The Taylor (1993) rule prescribes the central bank's optimal policy rate as a function of inflation and the output gap:

$$i_t^* = r^* + \pi^* + 1.5(\pi_t - \pi^*) + 0.5 y_t^{\text{gap}}$$

where $r^*$ is the neutral real rate, $\pi^*$ is the inflation target, and $y_t^{\text{gap}}$ is the output gap.

The **Taylor Rule Deviation** is the gap between the actual policy rate and the Taylor rule prescription:

$$\text{TRD}_i = i_i - i_i^*$$

A positive TRD (actual rate above Taylor rule) means the central bank is tight relative to fundamentals — bearish for the economy but potentially supportive of the currency (high rates attract capital).

More usefully, the **Taylor Rule Differential** between two countries:

$$\text{TRD Signal}_{i \text{ vs } j} = (i_i - i_i^*) - (i_j - i_j^*)$$

predicts exchange rate movements beyond what the raw interest differential captures.

**Evidence**: Engel, Mark, and West (2007) and Molodtsova and Papell (2009) find that Taylor rule fundamentals provide **statistically significant out-of-sample R²** for exchange rate prediction — a rare feat given the Meese-Rogoff puzzle. The out-of-sample R² is typically 1-5%, small in absolute terms but significant relative to the zero of the random walk.

**Data Source**: Policy rates (FRED, ECB); CPI inflation (FRED CPIAUCSL, Eurostat HICP); output gaps (OECD Economic Outlook, IMF WEO).

### 5.8 Central Bank Surprise (OIS-Based Identification)

**Mechanism**: FX markets react not just to the level of interest rates, but to *surprises* relative to market expectations. If the RBA hikes 25 bps and the market expected 25 bps, AUD barely moves. If the hike is 50 bps vs. expected 25 bps, AUD appreciates sharply. The signal is the surprise component.

**OIS-Based Identification**:

Overnight Index Swaps (OIS) are derivative contracts where one party pays a fixed rate and receives the compounding overnight rate (SOFR for USD, ESTR for EUR, SONIA for GBP, etc.). OIS rates for a 1-month maturity reflect the market's expectation of the average overnight rate over the next month — effectively pricing in expected central bank moves.

The monetary policy surprise on announcement day $t$:

$$\text{CB Surprise}_t = \Delta_t \text{Policy Rate} - \Delta_t^{\text{expected}} \text{Policy Rate}$$

where $\Delta_t^{\text{expected}}$ is the change priced into OIS rates immediately before the announcement.

**Signal Construction**: 
1. Download OIS rates at 1-month maturity for each G10 country.
2. Before each central bank meeting, record the OIS-implied expected rate.
3. After the decision, compute the surprise.
4. On days with large positive surprises (central bank more hawkish than expected), go long that currency for the following week.

**Evidence**: Kearns and Manners (2006, *Journal of Banking & Finance*) document exchange rate responses to monetary surprises are approximately **0.3-0.5% per 25 bps unexpected hike** on the announcement day, with partial mean reversion over the following week. The signal has a half-life of roughly 5-10 days.

**Data Source**: OIS rates (Bloomberg required for live; approximated from futures markets or estimated from bill-OIS spreads for research). FOMC meeting dates from FRED.

### 5.9 ML/Elastic Net on Macro Fundamentals

**Mechanism**: Rather than choosing specific signals ex-ante, let a regularized linear model select and weight features from a large macro-financial panel.

**Why Elastic Net?** The standard OLS regression with 30+ macro variables overfits dramatically. Elastic net combines L1 (LASSO, for variable selection) and L2 (Ridge, for shrinkage) penalties:

$$\hat{\beta} = \arg\min_{\beta} \left\{ \sum_{t=1}^{T} (r_{t+1} - X_t \beta)^2 + \lambda_1 \|\beta\|_1 + \lambda_2 \|\beta\|_2^2 \right\}$$

LASSO drives irrelevant coefficients exactly to zero; Ridge prevents coefficient explosion when variables are correlated. The combination is more stable than either alone.

**Feature Matrix Construction**:
```python
from sklearn.linear_model import ElasticNetCV
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

# Feature candidates for each currency pair (i vs USD)
features = {
    'rate_diff_1m': rate_diff['1m'],
    'rate_diff_3m': rate_diff['3m'],
    'slope_diff': slope_diff,       # (10y-2y) differential
    'ppp_gap': ppp_gap,             # real exchange rate deviation
    'mom_12_1': momentum_12_1,      # 12-1 momentum signal
    'mom_3': momentum_3m,           # 3-month momentum
    'vol_21d': realized_vol_21d,
    'cli_diff': cli_differential,
    'cip_basis': cross_currency_basis,
    'vix': vix_level,
    'global_fx_vol': global_fx_vol,
    'taylor_rule_diff': taylor_diff,
    'commodity_rel': commodity_return,  # e.g., iron ore for AUD
}

# Construct panel: T x K for each currency
X = pd.DataFrame(features).fillna(method='ffill')
y = forward_spot_return_1m  # target: 1-month ahead spot return

# Walk-forward expanding window estimation
predictions = []
for t in range(min_train_window, len(X)):
    X_train = X.iloc[:t]
    y_train = y.iloc[:t]
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X.iloc[[t]])
    
    # Elastic net with cross-validated alpha/l1_ratio
    model = ElasticNetCV(cv=5, l1_ratio=[0.1, 0.5, 0.7, 0.9, 1.0])
    model.fit(X_train_scaled, y_train)
    
    predictions.append(model.predict(X_test_scaled)[0])
```

**Evidence**: Papers using elastic net or LASSO on macro fundamentals panels typically find out-of-sample $R^2$ of **1-3%** for monthly exchange rate returns — small but statistically significant and consistent with the Goyal-Welch (2008) standard for "useful" predictability. Recent Federal Reserve research (2025) confirms that combination models using elastic net outperform the random walk, especially during financial stress periods.

**Caution**: Elastic net does not "solve" the Meese-Rogoff puzzle. It earns small predictive gains. The primary value is as a diversifier in a multi-signal portfolio, not as a standalone strategy.

### 5.10 Commodity-Currency Structural Links

**Iron Ore → AUD**

Australia is the world's largest iron ore exporter, with iron ore and metallurgical coal accounting for approximately **25-30% of total export revenue**. The structural link to AUD is strong:

- Iron ore price changes lead AUD movements with a lag of 1-5 days.
- Granger causality tests confirm iron ore prices → AUD (not the reverse).
- The correlation between iron ore 3-month change and AUD/USD 3-month change is approximately **0.60-0.70** over 2000-2023.

**Signal Construction**:
```python
# Iron ore: Platts Iron Ore Index (IODEX 62% Fe CFR China)
# Free proxy: FRED PIORECRUSDM (monthly) or TVC:IRONORE on TradingView

iron_ore_signal = iron_ore_price.pct_change(63)  # 3-month % change

# Standardize and use as an overlay on AUD carry signal
aud_commodity_signal = iron_ore_signal.rolling(21).mean()
```

**Data Source**: FRED series `PIORECRUSDM` (monthly); for daily, approximation from spot iron ore futures data available via trading platforms.

**Dairy → NZD**

New Zealand is the world's largest dairy exporter. Milk products account for approximately **25-30% of merchandise exports**. The Global Dairy Trade (GDT) auction (every two weeks) drives NZD moves.

- GDT event days show NZD intraday volatility approximately **40% higher** than non-event days.
- 3-month dairy price changes correlate with NZD at approximately **0.50-0.60**.
- The link is strongest for whole milk powder (WMP) prices, which dominate GDT volumes.

**Note on Regime Change**: The commodity-currency relationship weakened post-2015 as China's commodity demand slowed and financial flows (carry) began to dominate. The iron ore → AUD correlation was approximately 0.75 in 2005-2015 and declined to approximately 0.55 in 2015-2023.

### 5.11 Dollar Factor (DOL) as Portfolio Exposure Check

**Construction**: $\text{DOL}_t = \frac{1}{N}\sum_{i=1}^{N} (f_{i,t} - s_{i,t+1})$, the equal-weighted average return of all currencies against USD.

**Portfolio-Level Use**:
1. Compute the net USD exposure of your portfolio: $\text{DOL beta} = \sum_i w_i \beta_i^{\text{DOL}}$
2. If the portfolio has large positive DOL beta, you are implicitly betting on USD weakness.
3. If the portfolio has large negative DOL beta, you are betting on USD strength.
4. Neither is a desirable inadvertent bet. Target DOL beta of approximately **0 ± 0.2**.

**Why DOL Exposure Happens**: A carry portfolio that is long AUD, NZD, and CAD against JPY, CHF, and EUR is not balanced — it has a net short USD implicit in the structure (all high-yielders are commodity currencies that tend to be positively correlated). Monitoring DOL helps catch this.

---

## Section 6: FX Portfolio Construction

### 6.1 Cross-Sectional Z-Scoring

Before combining signals into positions, convert each raw signal to a cross-sectional z-score:

$$z_{i,t} = \frac{\text{signal}_{i,t} - \bar{\mu}_t}{\sigma_t}$$

where $\bar{\mu}_t$ and $\sigma_t$ are the cross-sectional mean and standard deviation at time $t$ across all $N$ currencies.

**Why z-score?**
1. It removes the *level* of the signal (e.g., if all currencies have positive carry, the z-score correctly centers around zero — the portfolio is relative value, not directional).
2. It normalizes signal strength, allowing different signals (carry in %, momentum in log returns) to be compared on a common scale.
3. It ensures the long-short portfolio is approximately dollar-neutral.

**Winsorizing**: After z-scoring, winsorize at ±2 or ±3 to prevent extreme observations (e.g., a currency experiencing a political shock) from dominating.

### 6.2 Volatility Targeting

Volatility targeting scales portfolio weights so that expected portfolio volatility equals a target level:

$$w_t = \frac{\sigma^*}{\hat{\sigma}_t} \cdot w_t^{\text{raw}}$$

where $\sigma^*$ is the target volatility (e.g., 10% annualized), $\hat{\sigma}_t$ is the estimated current portfolio volatility, and $w_t^{\text{raw}}$ is the raw signal-weighted position.

**Evidence from Moreira and Muir (2017, *Journal of Finance*, Vol. 72, pp. 1611-1644)**: Volatility-managed portfolios — those that reduce exposure when volatility is high and increase it when volatility is low — generate large alphas and significant Sharpe ratio improvements across many factor strategies. Their key finding: **Sharpe ratios improve from 1.441 to 1.735 (in-sample)** for a multifactor portfolio when volatility-managing. The mechanism: volatility is persistent (easily forecast with realized vol), but expected returns are not proportional to volatility, so scaling down in high-vol periods improves the Sharpe ratio.

**FX-Specific Implementation**:
```python
# Target annualized volatility
vol_target = 0.10  # 10%

# Estimate current portfolio volatility (21-day realized)
portfolio_returns = (positions * spot_returns).sum(axis=1)
current_vol = portfolio_returns.rolling(21).std() * np.sqrt(252)

# Volatility scalar
vol_scalar = (vol_target / current_vol).clip(0.25, 2.0)  # cap leverage between 0.25x and 2x

# Apply scalar to raw positions
scaled_positions = positions.multiply(vol_scalar, axis=0)
```

**Man Group (2020) FX-Specific Findings**: Vol targeting in currency portfolios reduces maximum drawdowns by approximately **30-40%** relative to fixed-weight portfolios, with a Sharpe ratio improvement of approximately 20%. The benefit is concentrated in crisis periods.

### 6.3 Correlation Management Across G10 Pairs

G10 currencies cluster into three groups with high within-group correlation:

| Cluster | Currencies | Driver |
|---------|------------|--------|
| Commodity / Risk-On | AUD, NZD, CAD, NOK | Global growth, commodity prices |
| Safe Haven | JPY, CHF | Risk-off flows, funding currencies |
| EUR-Bloc | EUR, SEK | European monetary policy, trade |
| Independent | GBP | UK-specific politics, BOE policy |

Within-cluster correlation is approximately **0.6-0.8**. Between clusters, approximately **-0.3 to -0.5** (safe haven vs. commodity are negatively correlated).

**Implication**: A carry portfolio that is long AUD, NZD, and CAD is effectively holding one position three times. The effective breadth is much less than 3. Risk management should account for this by:

1. **Limiting cluster concentration**: Maximum 30% of portfolio risk from any single cluster.
2. **Using a correlation-aware optimization** (minimum variance or risk-parity weights instead of signal-proportional).
3. **Monitoring pairwise correlation rolling window**: If AUD-NZD correlation spikes above 0.9 (a common event), treat them as one position.

### 6.4 Long-Short vs. Long-Only FX Portfolios

FX is inherently a relative value market — buying one currency means selling another. A "long" position in EUR/USD is simultaneously long EUR and short USD.

**Long-Short Portfolio**: Systematically long the top N currencies by signal score, short the bottom N. This is dollar-neutral (approximately). It isolates the cross-sectional signal cleanly.

**Long-Only Portfolio**: Overweight attractive currencies vs. a benchmark (e.g., GDP-weighted), avoid shorting. Common for institutional investors with mandates that prohibit short selling.

For systematic G10 research, **long-short is strongly preferred** because:
- It isolates the factor signal from DOL (dollar direction) risk
- It has larger risk-adjusted returns (captures both the long and short alpha)
- It is the natural structure for academic factor research, enabling fair comparison

### 6.5 The AQR Triplet: Carry + Momentum + Value

The combination of the three uncorrelated factors produces markedly superior risk-adjusted returns. Asness, Moskowitz, and Pedersen (2013) document this for currencies specifically:

| Strategy | Annualized Return | Annualized Sharpe |
|----------|-------------------|-------------------|
| Carry only | ~4-6% | ~0.4-0.6 |
| Momentum only | ~3-5% | ~0.5-0.8 |
| Value only | ~2-4% | ~0.4-0.5 |
| Equal-weight triplet | ~6-9% | ~0.9-1.2 |

The combined Sharpe ratio substantially exceeds any individual factor because:
1. Carry and momentum are modestly positively correlated (~0.2) — both tend to work in risk-on environments
2. Carry and value are modestly negatively correlated (~-0.3) — cheap currencies often have low interest rates
3. Momentum and value are strongly negatively correlated (~-0.5) — the most powerful diversifier

**Implementation**:
```python
# Equal-weighted triplet
# Each signal individually z-scored to unit variance

carry_z = zscore(vol_carry_signal)
momentum_z = zscore(momentum_12_1)
value_z = zscore(ppp_value_signal)

# Combined signal
triplet_signal = (carry_z + momentum_z + value_z) / 3.0

# Vol-target the combined portfolio
```

### 6.6 Signal Combination: IC-Weighted vs. Equal-Weight

**IC-Weighted Combination**: Weight each signal by its historical Information Coefficient (IC = correlation with forward returns). Signals with higher predictive power get larger weights.

**Equal-Weight Combination**: Assign equal weight to all signals regardless of historical performance.

**For Small Signal Sets (≤5 signals)**: Equal-weight is strongly preferred. IC estimation is noisy with limited data, and IC-weighted portfolios are prone to overfitting (you assign larger weight to signals that happened to do well in the estimation window, which often reverses out-of-sample). Empirical studies (Gu, Kelly, and Xiu 2020 for equities) show that simple combination methods outperform or match complex optimized ones for small signal sets.

**For Large Signal Sets (>10 signals)**: IC-weighting or machine learning combination begins to add value, because there is enough data to reliably distinguish high-IC from low-IC signals.

For this G10 repo with 5-7 signals, **equal-weight is the appropriate choice**.

### 6.7 The Grinold-Kahn Formula Applied to G10 FX

The Fundamental Law of Active Management (Grinold 1989, Grinold and Kahn 1999):

$$\text{IR} = \text{IC} \times \sqrt{\text{BR}}$$

- **IR** = Information Ratio (annualized alpha / tracking error)
- **IC** = Information Coefficient (correlation between signal and forward returns)
- **BR** = Breadth (number of independent bets per year)

**Applying to G10 FX**:

With 9 pairs (actually fewer independent pairs due to cluster correlation — effective N is approximately 4-5), rebalanced monthly:

$$\text{BR} \approx 4 \text{ effective pairs} \times 12 \text{ months} = 48$$

$$\text{IR} = 0.05 \times \sqrt{48} \approx 0.35$$

An IC of 0.05 (which is reasonable for carry — a one-month correlation of 0.05 between the carry signal and next-month return corresponds to statistical significance at the 10% level over 200 months) yields an IR of only 0.35.

**Implication**: With 9 G10 pairs, the fundamental law limits achievable Sharpe ratios to roughly **0.3-0.5** per signal. To reach Sharpe ratios of 1.0+, you need either:
1. **Higher IC**: Better signals (e.g., vol-normalised carry has higher IC than raw carry)
2. **Higher BR**: More currencies (include EM, or use sub-monthly rebalancing)
3. **Signal combination**: Multiple uncorrelated signals multiply effective breadth

This is the quantitative justification for expanding the currency universe and for combining signals.

---

## Section 7: Risk Management for FX Books

### 7.1 VIX Overlay: Step Function vs. Smooth Weighting

**Step Function**: Reduce carry to zero when VIX > 30, to 50% when VIX is 20-30, full when VIX < 20.

**Smooth Weighting**: Use a sigmoid function of VIX:

$$w_{\text{VIX}} = 1 - \frac{1}{1 + e^{-k(\text{VIX} - V_0)}}$$

where $V_0$ is the threshold VIX level (e.g., 20) and $k$ controls steepness.

**Evidence**: The step function generates large whipsaws when VIX oscillates around the threshold. Smooth weighting avoids discrete position changes and reduces transaction costs. In practice, VIX overlays improve maximum drawdown by approximately **20-30%** at the cost of some alpha in high-VIX but recovering markets.

**Limitation**: The VIX overlay is most effective for the carry factor. For momentum and value, the VIX is less relevant (momentum crashes are more correlated with reversal of market direction, not level of VIX).

### 7.2 Global FX Vol as a Better Conditioning Variable

As discussed in Section 5.3, global FX vol is more directly relevant to carry risk than VIX. The optimal overlay:

1. Use global FX vol for carry position sizing
2. Use VIX for portfolio-level risk management (as a broader sentiment gauge)
3. Never allow both to simultaneously increase position size (be conservative when either is elevated)

### 7.3 Carry-TSMOM as a Regime Filter

The Carry-TSMOM filter (see Section 5.2) is particularly effective as a regime indicator because:

- In trending regimes (positive carry + positive momentum aligned), carry tends to earn well
- In reverting regimes (carry positive but momentum negative — the currency is already falling), carry tends to lose
- The transition from aligned to divergent signals often precedes crashes by 4-6 weeks

Running a backtest on the G10 universe, the Sharpe ratio when carry and TSMoM are aligned is approximately **1.5-2.0x** the unconditional Sharpe, while it is negative (-0.2 to -0.5) when they diverge.

### 7.4 Deflated Sharpe Ratio: Multiple Testing Adjustment

When you test $K$ strategies (variations of carry, momentum, different lookbacks, different filters), the best realized Sharpe ratio $\hat{SR}^*$ is inflated by selection bias. Bailey and López de Prado (2014, *Journal of Portfolio Management*) proposed the Deflated Sharpe Ratio (DSR):

$$\text{DSR}(\hat{SR}^*) = \Phi\left[\frac{(\hat{SR}^* - \hat{SR}_0)\sqrt{T-1}}{\sqrt{1 - \hat{\gamma}_3 \hat{SR}^* + \frac{\hat{\gamma}_4 - 1}{4}(\hat{SR}^*)^2}}\right]$$

where:
- $\hat{SR}_0 = \sqrt{\text{Var}[\hat{SR}_k]} \cdot \left((1-\gamma_E)\Phi^{-1}\left(1 - \frac{1}{K}\right) + \gamma_E \Phi^{-1}\left(1 - \frac{1}{Ke}\right)\right)$
- $\hat{\gamma}_3$ = skewness of returns
- $\hat{\gamma}_4$ = kurtosis of returns
- $T$ = sample length (in observations)
- $K$ = number of trials (strategy variants tested)
- $\Phi$ = standard normal CDF

**Practical Interpretation**: If you tested 14 strategy variants (as in this repo) and the best had an annualized Sharpe of 2.73, the DSR adjusts this for the fact that the best of 14 trials should be high by luck alone. A DSR above 0.95 (95% confidence that the strategy is genuinely profitable after multiple testing) is the threshold for deployment consideration.

**Rule of Thumb**: For every doubling of the number of trials $K$, the required Sharpe ratio to achieve DSR = 0.95 increases by approximately 0.1-0.2.

### 7.5 Walk-Forward Backtesting: Expanding vs. Rolling Window

**Expanding Window**: Use all data from the start of the sample through date $t$ to estimate model parameters, then produce a forecast for period $t+1$. As $t$ grows, the estimation window grows.

*Advantage*: Uses all available information; parameter estimates become more stable over time.

*Disadvantage*: Early-period parameters estimated with very little data; if there is a structural break, old data can hurt forecasts.

**Rolling Window**: Use only the most recent $W$ observations (e.g., 5 years) to estimate parameters.

*Advantage*: More adaptive to regime changes.

*Disadvantage*: Discards long-run information; noisier parameter estimates.

**Recommendation for FX Signals**: Use expanding window for signal-level parameter estimation (e.g., carry threshold, IC weights), but rolling window for vol estimation (21-day or 63-day realized vol). Carry signals have long-run statistical stability; volatility is regime-dependent.

### 7.6 Look-Ahead Bias Mechanisms in Daily FX Signals

The most common sources of look-ahead bias in FX backtests:

1. **Stale Rate Differentials**: Using a rate differential that was only published after the close, as if it were available at the open. FRED updates many series after market hours — always check FRED release timestamps.

2. **Timestamp Misalignment** (see Section 8.2): ECB reference rates are fixed at 14:15 CET; if you trade at London close (16:00 GMT ≈ 17:00 CET), you are using rates from 2 hours earlier. Ensure signal date = trade date + 1 business day.

3. **Forward-Fill of Missing Data**: Missing weekend or holiday values are often forward-filled. If you forward-fill an interest rate that changed on a holiday, you have introduced a subtle look-ahead error.

4. **Survivorship Bias in Currency Universe**: If you only include G10 currencies from 2000 onward but include CHF, you implicitly include the January 2015 SNB unpegging, which ended the carry trade in CHF dramatically. Include CHF from the start and handle the EUR peg (2011-2015) explicitly.

5. **Calendar Effects in CFTC COT**: COT data is reported on Tuesday, released Friday. If you use it for Monday signals, you have a genuine 10-day look-ahead.

### 7.7 Sub-Period Analysis: Regime Decomposition

Any strategy should be decomposed by economic regime to understand when and why it works:

| Regime | Dates | Key Feature | Carry | Momentum | Value |
|--------|-------|-------------|-------|----------|-------|
| Pre-GFC | 2000-2007 | Stable growth, clear differentials | Strong (SR ~1.0) | Moderate | Slow |
| GFC | 2008-2009 | Deleveraging, risk-off | Crash (-20%) | Reversal | - |
| ZIRP | 2010-2015 | Zero rates, QE, compressed differentials | Weak (SR ~0.3) | Moderate | Growing |
| Rate Divergence | 2015-2018 | Fed hiking, ECB negative rates | Improving | Strong | Mixed |
| COVID | 2020 | Extreme risk-off, then reflation | Crash then recovery | Strong (USD trend) | - |
| Hiking Cycle | 2022-2023 | Multi-decade inflation, rapid hikes | Strong for USD carry | Volatile | Improving |

The ZIRP regime (2011-2015) is particularly important: G10 rate differentials collapsed toward zero, removing the primary source of carry returns. In this environment, vol-normalised carry and value become relatively more important.

---

## Section 8: Data Sources and Implementation

### 8.1 Complete Data Source Guide for G10 FX Research

| Data Type | Source | Series / Endpoint | Lag | Cost |
|-----------|--------|-------------------|-----|------|
| Spot exchange rates | FRED | `EURUSD`, `DEXUSEU`, etc. | 1 day | Free |
| Spot exchange rates | ECB Data Portal | `EXR.D.*` | Same day | Free |
| Spot exchange rates | Yahoo Finance | `EURUSD=X`, `GBPUSD=X`, etc. | Same day | Free |
| Forward rates (1M, 3M) | FRED | `DEUR3` etc. (limited) | 1 day | Free |
| 3M Treasury/Libor rates | FRED | `DTB3`, `EUR3MTD156N`, etc. | 1 day | Free |
| 10Y Government yields | FRED | `DGS10` (US), `IRLTLT01DEM156N` (GER), etc. | 1 day | Free |
| CPI inflation | FRED | `CPIAUCSL` (US), `CP0000EZ19M086NEST` (EUR) | 4-6 weeks | Free |
| OECD CLI | OECD.Stat API | `DP_LIVE`, `MEI_CLI` | 4-6 weeks | Free |
| CFTC COT positioning | CFTC website | Legacy COT report | 1 week | Free |
| VIX | FRED | `VIXCLS` | Same day | Free |
| Commodity prices (iron ore) | FRED | `PIORECRUSDM` (monthly) | 1 month | Free |
| Cross-currency basis | Bloomberg / Refinitiv | EURUSD XCCY basis | Real-time | Paid |
| OIS rates | Bloomberg / Refinitiv | ESOFRRATE1W, etc. | Real-time | Paid |
| GDT dairy prices | GDT Events website | Freely scraped | Biweekly | Free |

### 8.2 The Timestamp Alignment Problem

Daily FX signal construction requires careful attention to *when* each data series is timestamped relative to when you trade.

**ECB Reference Rate**: Fixed at 14:15 CET. Published on the ECB website at approximately 16:00 CET. This is the official EUR/xxx reference rate, widely used in academic research. **Problem**: If you are trading at the New York close (~17:00 ET = 22:00 CET), the ECB rate is already 7 hours stale. For long-horizon signals (monthly carry), this is irrelevant. For high-frequency signals, it introduces a bias.

**FRED Data**: Most FX series on FRED are timestamped to the day, sourced from H.10 release (Board of Governors), which reflects noon New York quotes (approximately 17:00 CET). Lag: FRED updates 1 business day behind.

**Yahoo Finance**: Timestamps FX data to the New York market close (16:00-17:00 ET). Generally reliable for daily closing prices.

**Best Practice for Backtesting**:
```python
import pandas as pd

# Load data
ecb_rates = pd.read_csv('ecb_rates.csv', index_col=0, parse_dates=True)
fred_rates = pd.read_csv('fred_rates.csv', index_col=0, parse_dates=True)

# ECB is available same day but in early afternoon
# Assume signal computed end-of-day; trade executes NEXT day open
# Shift signals by 1 business day to avoid look-ahead bias
signal = compute_carry_signal(ecb_rates)
signal_lagged = signal.shift(1)  # Signal available at t, trade at t+1

# Verify no look-ahead: assert signal_lagged.index[-1] < trade_date
```

**The Fundamental Rule**: If your signal is constructed using data from date $t$, your position is entered at date $t+1$'s open (or close if you are using close-to-close returns). Never use date $t$ data in the return computation for the same period $t$.

### 8.3 Building a Rate Differential Feature Matrix in Python

```python
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime

# Define G10 currency pairs and corresponding 3-month rate series (FRED codes)
rate_series = {
    'USD': 'DTB3',          # 3-Month Treasury Bill: Secondary Market Rate
    'EUR': 'EUR3MTD156N',   # 3-Month Euribor
    'GBP': 'GBP3MTD156N',   # 3-Month Sterling LIBOR
    'JPY': 'JPY3MTD156N',   # 3-Month JPY LIBOR
    'CHF': 'CHF3MTD156N',   # 3-Month CHF LIBOR
    'AUD': 'IR3TIB01AUM156N',  # 3-Month Australian BBSW
    'CAD': 'CAD3MTD156N',
    'NZD': 'NZD3MTD156N',
    'SEK': 'STIBOR3M',
    'NOK': 'NOWE3M',
}

start = datetime(2000, 1, 1)
end = datetime.today()

# Download all rate series
rates = {}
for ccy, series_code in rate_series.items():
    try:
        data = web.DataReader(series_code, 'fred', start, end)
        rates[ccy] = data.squeeze() / 100  # Convert from % to decimal
    except Exception as e:
        print(f"Could not download {ccy}: {e}")

rates_df = pd.DataFrame(rates).resample('B').last().ffill()

# Compute rate differentials vs USD
usd_rate = rates_df['USD']
rate_diff = rates_df.subtract(usd_rate, axis=0).drop(columns='USD')

# Annualize (already annualized if from FRED) — verify units
# rate_diff is in decimal per year, e.g., 0.02 = 2% p.a.

print("Rate differential matrix (sample):")
print(rate_diff.tail())
print(f"\nShape: {rate_diff.shape}")
```

### 8.4 Forward Rate Computation from Interest Rate Differentials

Under CIP (approximately holding pre-2009, with basis adjustment post-2009):

$$F_{i,t}^{(n)} = S_{i,t} \times \exp\left((i_t^{(n)} - i_{i,t}^{(n)}) \times \frac{n}{360}\right)$$

where $n$ is the number of days (e.g., 30 for 1-month), $i_t^{(n)}$ is the USD rate for tenor $n$, and $i_{i,t}^{(n)}$ is the rate for currency $i$.

```python
def compute_implied_forward(spot, rate_diff_annualized, tenor_days=30):
    """
    Compute implied forward rate from spot and interest rate differential.
    Uses CIP approximation (ignores cross-currency basis).
    
    Parameters:
    -----------
    spot: pd.Series or float — spot exchange rate (units of foreign per USD)
    rate_diff_annualized: float — (foreign rate - USD rate) in decimal p.a.
    tenor_days: int — tenor in calendar days
    
    Returns:
    --------
    implied_forward: pd.Series or float
    """
    return spot * np.exp(rate_diff_annualized * tenor_days / 360)

# Example
spot_audusd = 0.65
aud_usd_rate_diff = 0.025  # AUD rate = 4.0%, USD rate = 1.5%, diff = 2.5%
forward_1m = compute_implied_forward(spot_audusd, aud_usd_rate_diff, tenor_days=30)
print(f"Implied 1-month forward AUD/USD: {forward_1m:.5f}")
# Output: ~0.6513 — AUD at a forward premium (carries at the 1m horizon)
```

**Post-2008 Adjustment**: Add the cross-currency basis to get the true market-implied forward:

$$F_{i,t}^{(n)} = S_{i,t} \times \exp\left((i_t^{(n)} - i_{i,t}^{(n)} - x_{i,t}^{(n)}) \times \frac{n}{360}\right)$$

where $x_{i,t}^{(n)}$ is the cross-currency basis. For research purposes without Bloomberg access, this adjustment is often omitted for G10 analysis; it matters most for EUR, JPY, and CHF where the basis is largest.

### 8.5 Cost Model: Pip-Based Construction with JPY Exception

**Typical G10 Bid-Ask Spreads** (institutional interbank, 2024):

| Currency Pair | Typical Spread (pips) | Pip Value | Cost per Trade (round-trip) |
|--------------|----------------------|-----------|----------------------------|
| EUR/USD | 0.3-0.5 pip | $10 per pip per lot | ~0.003% |
| GBP/USD | 0.5-1.0 pip | $10 per pip | ~0.005% |
| AUD/USD | 0.5-1.0 pip | $10 per pip | ~0.005% |
| NZD/USD | 1.0-2.0 pips | $10 per pip | ~0.010% |
| USD/JPY | 0.3-0.5 pip | $9.25 per pip | ~0.003% |
| USD/CHF | 1.0-2.0 pips | $10 per pip | ~0.010% |
| USD/CAD | 1.0-2.0 pips | $10 per pip | ~0.010% |
| USD/SEK | 3.0-6.0 pips | ~$10 per pip | ~0.030% |
| USD/NOK | 3.0-6.0 pips | ~$10 per pip | ~0.030% |

**The JPY Exception**: JPY pairs are quoted to 2 decimal places (e.g., 149.50), not 4. One pip = 0.01 in JPY terms. However, the *value* of one pip depends on the current USD/JPY rate:

$$\text{Pip value (USD)} = \frac{0.01}{\text{USD/JPY rate}} \times \text{Lot size}$$

At USD/JPY = 150, one pip for 1,000,000 notional = $0.01/150 × 1,000,000 = $66.67. This is smaller than the $100 per pip for EUR/USD at 4-decimal-place quoting. Ensure your cost model computes costs consistently in USD terms, not in pips.

**Annualized Cost Estimate for Monthly Rebalancing**:

With 12 rebalancing events per year and average round-trip cost of 0.01% per trade on a portfolio of 6-8 active pairs:

$$\text{Annual cost} \approx 12 \times 7 \times 0.008\% \approx 0.67\% \text{ per year}$$

For a strategy targeting 6-8% annualized return, this represents approximately **8-10% of gross return** — non-trivial but not strategy-killing for monthly rebalancing.

**Reducing Costs**:
1. Use signal decay and only trade when the signal moves more than 0.5 standard deviations.
2. Net offsetting trades (if you are adding 10% weight to EUR and reducing 10% weight to GBP, and both are against USD, these are independent — no offsetting. But if you are reducing EUR/USD and increasing EUR/JPY, you might net the EUR leg).
3. Favour liquid pairs (EUR/USD, USD/JPY, GBP/USD) for timing-sensitive execution.

---

## Appendix A: Key Papers Reference Table

| Paper | Year | Journal | Key Finding | Section |
|-------|------|---------|-------------|---------|
| Meese & Rogoff | 1983 | *J. Int. Econ.* | Macro models can't beat random walk out-of-sample | 1.6 |
| Fama | 1984 | *J. Mon. Econ.* | UIP β ≈ -0.88 on average across 75 studies (Froot 1990 meta-analysis) | 1.3 |
| Lustig & Verdelhan | 2007 | *AER* | Carry returns price consumption risk | 2.3 |
| Brunnermeier, Nagel & Pedersen | 2009 | *NBER Mac. Annual* | Carry crashes from margin spirals; negative skewness | 2.4 |
| Moskowitz, Ooi & Pedersen | 2012 | *JFE* | TSMOM Sharpe > 1.20 across 58 instruments; FX ~0.8 | 3.2 |
| Menkhoff, Sarno, Schmeling & Schrimpf | 2012 (JF) | *J. Finance* | Global FX vol is dominant carry risk factor (t-stat ~-5) | 2.7, 5.3 |
| Menkhoff, Sarno, Schmeling & Schrimpf | 2012 (JFE) | *J. Fin. Econ.* | FX momentum Sharpe ~0.95 at 1m horizon; needs 40+ currencies | 3.1, 3.3 |
| Lustig, Roussanov & Verdelhan | 2011 | *AER* | DOL + HML_FX two-factor model for carry returns | 2.2 |
| Asness, Moskowitz & Pedersen | 2013 | *J. Finance* | Value-momentum correlation ~-0.5; triplet SR ~1.0-1.5 | 4.4, 6.5 |
| Bailey & López de Prado | 2014 | *J. Portfolio Mgmt* | Deflated Sharpe ratio corrects for multiple testing | 7.4 |
| Du, Tepper & Verdelhan | 2018 | *J. Finance* | CIP deviations 20-50 bps post-GFC; due to balance sheet regulation | 1.4 |
| Moreira & Muir | 2017 | *J. Finance* | Vol-managed portfolios: SR improves 1.441→1.735 | 6.2 |
| Dupuy | 2021 | *J. Banking & Finance* | Vol-normalised carry flips skewness positive, SR+20-40% | 2.6, 5.1 |

---

## Appendix B: Formula Cheat Sheet

**UIP Condition**:
$$E_t[\Delta s_{t+1}] = i_t - i^*_t$$

**CIP Condition (pre-2008)**:
$$f_t - s_t = i_t - i^*_t$$

**CIP Basis (post-2008)**:
$$x_t = (f_t - s_t) - (i_t - i^*_t) \neq 0$$

**Fama Regression**:
$$\Delta s_{t+1} = \alpha + \beta(f_t - s_t) + \varepsilon_{t+1}, \quad \hat{\beta}_{\text{empirical}} \approx -0.88$$

**Carry Signal**:
$$\text{Carry}_i = i_{i,t} - i_{\text{base},t} \approx f_{i,t} - s_{i,t}$$

**Vol-Normalised Carry**:
$$\text{VolCarry}_i = \frac{i_{i,t} - i_{\text{base},t}}{\hat{\sigma}_{i,t}}$$

**Momentum (12-1)**:
$$\text{Mom}_i = \ln(S_{i,t-1}) - \ln(S_{i,t-13})$$

**PPP Value**:
$$\text{Value}_i = -\left[\ln(S_{i,t}) - \ln(S_{i,t-60}) - (\pi_{i,t-60:t} - \pi_{\text{base},t-60:t})\right]$$

**Taylor Rule**:
$$i^* = r^* + \pi^* + 1.5(\pi - \pi^*) + 0.5 y^{\text{gap}}$$

**Implied Forward Rate**:
$$F = S \cdot \exp\left[(i_{\text{dom}} - i_{\text{for}}) \cdot \frac{n}{360}\right]$$

**Cross-Sectional Z-Score**:
$$z_{i,t} = \frac{\text{signal}_{i,t} - \bar{\mu}_t}{\sigma_t^{\text{cross-section}}}$$

**Grinold-Kahn Fundamental Law**:
$$\text{IR} = \text{IC} \times \sqrt{\text{BR}}$$

**Volatility-Managed Position Size**:
$$w_t = \frac{\sigma^*}{\hat{\sigma}_t} \cdot w_t^{\text{raw}}$$

---

## Appendix C: Python Environment Setup

```python
# Core dependencies for G10 FX research
# requirements.txt equivalent

pandas>=2.0
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3       # elastic net, StandardScaler
pandas-datareader>=0.10 # FRED data access
yfinance>=0.2           # Yahoo Finance fallback
statsmodels>=0.14       # OLS, cointegration tests
matplotlib>=3.7
seaborn>=0.12
requests>=2.30          # OECD API access
python-dotenv>=1.0      # API key management

# Optional but useful
pykalman>=0.9           # Kalman filter for state-space carry models
arch>=6.0               # GARCH volatility models
cvxpy>=1.3              # Convex optimization for portfolio construction
```

```python
# Quick setup: pull all G10 spot rates from Yahoo Finance
import yfinance as yf
import pandas as pd

tickers = [
    'EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'NZDUSD=X', 'CADUSD=X',
    'USDJPY=X', 'USDCHF=X', 'USDSEK=X', 'USDNOK=X'
]

data = yf.download(tickers, start='2000-01-01', auto_adjust=True)['Close']
data.columns = ['EUR', 'GBP', 'AUD', 'NZD', 'CAD', 'JPY', 'CHF', 'SEK', 'NOK']

# Convert all to "units of foreign currency per USD" convention
# EUR, GBP, AUD, NZD, CAD are quoted as USD per foreign — invert
for ccy in ['EUR', 'GBP', 'AUD', 'NZD', 'CAD']:
    data[ccy] = 1.0 / data[ccy]

# JPY, CHF, SEK, NOK are already in foreign per USD — keep as-is
# Now data[i] = foreign currency units per USD for all i

print(data.tail())
```

---

*End of Document*

*Word count: approximately 10,500 words*

*Sources: All academic citations are from primary journals. Key papers include Fama (1984), Brunnermeier-Nagel-Pedersen (2009), Menkhoff et al. (2012 JF and 2012 JFE), Lustig-Roussanov-Verdelhan (2011), Asness-Moskowitz-Pedersen (2013), Du-Tepper-Verdelhan (2018), Moskowitz-Ooi-Pedersen (2012), Moreira-Muir (2017), and Bailey-López de Prado (2014).*
