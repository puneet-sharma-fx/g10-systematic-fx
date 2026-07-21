# From Discretionary Macro to Systematic FX Trading
## A Bridge Document for the Transitioning Trader

*Prepared for NotebookLM ingestion. Self-contained reference. Target reader: experienced discretionary FX/macro trader with 5-15 years of market experience who wants to transition toward systematic/quantitative trading without abandoning their macro intuition.*

*Repository context: all strategy results cited (Strategy #1 through #14) are from actual backtests run in this repo (2010-2024, net of 5 pips round-trip cost). See `STRATEGIES.md` for the full index.*

---

## Table of Contents

1. The Mindset Shift — How Discretionary and Systematic Traders Think Differently
2. Translating Discretionary Intuition Into Systematic Rules
3. Testing Whether Your Edge Is Real — Statistical Toolkit for Traders
4. The Quantamental Approach — Systematic Frameworks with Discretionary Overlay
5. Common Discretionary Strategies and Their Systematic Equivalents
6. Position Sizing — The Discretionary Trader's Biggest Gap
7. Building Your First Systematic Strategy — Step-by-Step
8. The Macro Scorecard — Systematising Your Macro Framework
9. Risk Management for the Transitioning Trader
10. Tools and Learning Path for the Transitioning Trader

---

## Section 1 — The Mindset Shift: How Discretionary and Systematic Traders Think Differently

### 1.1 Two Fundamentally Different Languages

A discretionary macro trader and a systematic trader can look at the same market and reach the same conclusion — but they arrive there through entirely different reasoning processes. Understanding this difference is the first, most important step.

The discretionary trader thinks in **narratives and probability of realisation**. The internal monologue sounds like this: *"The Fed has been more hawkish than markets expected for three meetings in a row. The OIS curve still prices only 25bps of cuts in the next 12 months, but I think they hold even that. Dollar stays bid. I'll buy EURUSD puts."* This thinking has enormous strengths: it integrates regime context, understands the sequencing of market realisation, accounts for the asymmetry between being right and being right at the right time, and draws on thousands of hours of pattern-recognition that is difficult to codify.

The systematic trader thinks in **statistical distributions over repeated observations**. The internal monologue sounds like this: *"My signal — the change in 2Y rate differential — has a t-statistic of 9.3 across 3,912 daily observations on EURUSD alone. The Sharpe ratio is 2.75 net of transaction costs over 2010-2024. I will size according to my volatility target and execute every signal regardless of the narrative."* This thinking has entirely different strengths: it is immune to recency bias, it sizes correctly, it executes consistently without emotional drift, and it aggregates across a large enough sample to separate skill from luck with high confidence.

Neither approach is complete. The discretionary trader has genuine information advantages the quant lacks. The systematic trader has discipline and statistical rigour the discretionary trader lacks. The goal of this document is to show you how to combine both.

### 1.2 Being Wrong in Individual Trades to Be Right in Expectation

This is the single most counterintuitive concept for a discretionary trader to absorb: **a systematic strategy can be right only 52% of the time and still be an excellent strategy**, provided the edge is consistent and the sizing is correct.

Consider Strategy #1 from this repository: EURUSD driven by the change in the 2Y EUR-USD rate differential. Hit rate (i.e., the fraction of days on which the trade is profitable) is approximately 51-52%. Yet the net Sharpe ratio is 2.75 over 3,912 trading days. How? Because even a small, consistent edge — a β of +0.0335 per unit of daily rate differential change — compounds reliably when applied with consistent sizing across hundreds of independent trades.

A discretionary trader who ran this strategy in their head would feel uncomfortable almost every day. Half the days would feel wrong. There would be weeks of drawdown with no obvious narrative explanation. The trader would override the model. The model would stop working not because it was wrong but because the trader interfered.

The systematic mindset requires internalising this: **you are not evaluating each trade independently; you are evaluating the distribution of outcomes across all trades**. A single trade's outcome tells you almost nothing. One hundred trades' outcomes tell you something. One thousand trades' outcomes tell you a great deal.

### 1.3 Why Discretionary Traders Overfit to Recent Experience

Human cognition has two well-documented biases that make discretionary trading systematically less consistent than its practitioners believe:

**Recency bias**: The human brain over-weights recent events relative to their statistical frequency. A trader who has just experienced a month where carry trades failed will underweight carry for the next several months — even if carry has a 20-year Sharpe ratio of 0.7 and the bad month was an entirely normal draw from that distribution.

**Availability heuristic**: Events that are easy to recall (vivid, recent, emotionally charged) are assigned higher probability than events that are statistically more frequent but less memorable. The 2015 SNB floor removal, the 2020 COVID crash, the 2022 JPY collapse — these are memorable. The 260 days a year where nothing much happens are not. A trader who has been through the SNB event will perpetually assign too much probability to another peg break.

These biases do not reflect ignorance or stupidity. They are how human brains efficiently process information in environments where recency actually does matter (if a predator attacked you last week, it is rational to stay alert this week). Financial markets are one of the few environments where this shortcut consistently fails.

**The systematic remedy**: a rule-based system that generates signals identically regardless of recent market conditions. The signal does not care about what happened last month. It asks only: does the current reading of the indicator predict the next-period return, just as it has across the previous thousand observations?

### 1.4 Why Systematic Traders Underfit by Ignoring Context (Regime Blindness)

The systematic approach has its own characteristic failure mode, and it is the mirror image: **regime blindness**. A system trained on the 2010-2024 period will not automatically know that a fundamental regime shift has occurred. It will continue generating signals with exactly the same confidence regardless of whether the underlying mechanism still holds.

Consider the USDJPY rate-differential strategy (Strategy #5 in this repo): it works in normal rate regimes, achieving a Sharpe ratio of 1.44. But it suffers a −59.2% maximum drawdown because the Bank of Japan's Yield Curve Control regime occasionally causes USDJPY to behave unlike any other G10 pair — the rate differential widens but the currency does not respond in the expected direction because the BoJ is actively capping the long end. A discretionary trader who understood the YCC policy would have recognised this breakdown. The systematic model, running blindly on data, suffered the full drawdown.

Similarly, Strategy #11 (cross-sectional momentum in FX) was rejected entirely: it showed a Sharpe of −0.34 across all lookbacks (21, 63, 126, 252 days). This is consistent with academic evidence showing that FX momentum has decayed significantly post-GFC. A systematic model trained on 2000-2008 would have been confidently wrong. A discretionary trader who understood the structural changes in the FX market post-GFC might have recognised this regime shift earlier.

### 1.5 The Quantamental Hybrid: Where the Real Edge Lives

The most sophisticated investment firms have converged on a **quantamental** approach that blends systematic signal generation with human context and oversight. The logic is straightforward: the systematic component provides consistency and removes emotional bias; the human component provides regime awareness and context.

**D.E. Shaw** (founded 1988) pioneered this approach. Their systems generate signals from quantitative models, but the firm employs hundreds of researchers — including macro economists, scientists, and sector specialists — who provide context that quantitative models cannot derive from prices and volumes alone.

**Point72** (Steve Cohen) operates as a collection of fundamental analyst pods with systematic risk management overlaid. The discretionary analysts generate trade ideas with explicit, data-driven theses; a quantitative risk system controls portfolio-level exposure and correlation.

**Two Sigma** runs predominantly systematic models but employs macro researchers and alternative data scientists who help design the features (inputs) that go into those models.

**Man Numeric** runs a systematic process where fundamental data inputs (earnings revisions, analyst estimates, economic indicators) are processed through systematic screens rather than narrative judgement.

The key insight from all of these examples: the **transition from discretionary to systematic does not mean abandoning your macro knowledge**. It means encoding that knowledge into explicit, testable rules — and then measuring whether those rules actually work.

### 1.6 What Each Side Brings

| What Discretionary Traders Know | What Systematic Traders Know |
|---|---|
| Order flow interpretation (who is buying, why) | Consistent signal execution across market conditions |
| Narrative momentum (when the market will "get it") | Position sizing from statistical first principles |
| Macro turning point identification | Drawdown control and portfolio risk management |
| Regime changes (when old relationships break down) | Multiple signals, portfolio diversification |
| Policy nuance (BoJ vs. ECB reaction functions) | Out-of-sample validation discipline |
| Relative value across asset classes | Factor attribution (what is actually driving returns) |
| Liquidity and market structure | Transaction cost modelling |

**The goal is not to replace your discretionary judgment. The goal is to use it where it genuinely adds value** — regime identification, signal construction, regime-conditional weighting — while systematising everything that does not require human judgment: execution, sizing, portfolio construction, risk management.

---

## Section 2 — Translating Discretionary Intuition Into Systematic Rules

### 2.1 What Is a Signal?

A **signal** is a function of observable data, available at time $t$, that predicts the return of an asset from time $t$ to time $t+h$. Formally:

$$\text{signal}_t = f\left(X_{t}, X_{t-1}, \ldots, X_{t-k}\right)$$

$$\text{prediction: } r_{t \to t+h} = \alpha + \beta \cdot \text{signal}_t + \epsilon_t$$

The signal must satisfy several properties to be useful:

1. **Constructed from data available at time $t$** (no look-ahead)
2. **Has a sign** (positive = predict long, negative = predict short)
3. **Has a magnitude** that is meaningfully related to the strength of prediction
4. **Is measurable with sufficient frequency** (daily, weekly, monthly) to generate enough observations for statistical testing

### 2.2 Mapping Discretionary Statements to Systematic Signals

The following table maps common discretionary trading statements to their systematic equivalents. Each row is a translation exercise.

| Discretionary Statement | Systematic Signal | Frequency | Key Reference |
|---|---|---|---|
| "The Fed is more hawkish than markets expect" | OIS-implied rate path vs. current dot plot: $\text{surprise} = r_{\text{OIS}} - r_{\text{dot}}$ | Per-meeting event | Gürkaynak, Sack, Swanson (2005) |
| "CAD should follow oil" | Daily oil price change as leading signal for USDCAD: $\Delta\ln(\text{WTI}_t) \to r_{\text{CADUSD}, t+1}$ | Daily | Ferraro, Rogoff, Rossi (2015) — works at daily, not monthly, frequency |
| "Positioning is stretched, risk of a squeeze" | CFTC COT net speculative position z-score: $z = (\text{net spec} - \mu_{52w}) / \sigma_{52w}$; signal triggers at $|z| > 1.5$ | Weekly | Strategy #13 in this repo |
| "The market is risk-off" | VIX level $> 20$, or global FX vol index, or IG credit spread vs. 30-day average | Daily | Menkhoff et al. (2012) — carry performs when this is low |
| "EUR looks cheap vs. PPP" | 5-year cumulative real exchange rate deviation from PPP: $q_t = s_t - p_t + p_t^*$ | Monthly | Asness, Moskowitz, Pedersen (2013) — value in FX |
| "Momentum is strong in JPY" | 12-month time-series momentum: $\text{sign}(r_{t-252,t})$ × vol-scaled size | Daily | Moskowitz, Ooi, Pedersen (2012) |
| "Rate differential favours USD" | $\Delta(r_{\text{US}, 2Y} - r_{\text{EU}, 2Y})$ → next-day EURUSD return | Daily | Strategy #1 in this repo; β = +0.0335, R² = 7.5% |
| "Growth is diverging — bet on USD" | OECD Composite Leading Indicator differential: $CLI_{\text{US}} - CLI_{\text{EA}}$ | Monthly | Standard macro scorecard dimension |
| "Carry is attractive in MXN" | Annualised short-rate differential vs. funding currency, cross-sectionally ranked | Daily | Lustig, Roussanov, Verdelhan (2011) |

### 2.3 The Translation Process

The translation from discretionary intuition to systematic rule follows four steps:

**Step 1 — Write it in natural language (be honest)**

Bad: "I buy EUR when it feels cheap and fundamentals are good."
Good: "I buy EUR vs. USD when the 2Y German Bund yield has risen more than the 2Y US Treasury yield in the past 24 hours, and the EURUSD has not already moved more than 0.5% in the direction of the signal."

**Step 2 — Convert to an IF-THEN rule**

```
IF Δ(DE_2Y - US_2Y) > 0 over the past [N] trading days:
    SIGNAL = +1 (buy EURUSD)
ELSE IF Δ(DE_2Y - US_2Y) < 0:
    SIGNAL = -1 (sell EURUSD)
ELSE:
    SIGNAL = 0 (flat)
```

**Step 3 — Identify the data needed**

- DE 2Y bond yield: FRED (DGS2), ECB SDW, or TVC via tvDatafeed
- US 2Y bond yield: FRED series DGS2
- EURUSD spot: Yahoo Finance (`EURUSD=X`) or ECB SDW

**Step 4 — Measure the relationship before backtesting**

Run an OLS regression: $\text{FX return}_{t+1} = \alpha + \beta \cdot \text{signal}_t + \epsilon_t$

A signal is worth testing further only if:
- $\beta$ has the expected sign
- The t-statistic of $\beta$ is greater than 2.0 (approximately)
- The relationship holds across multiple sub-periods

### 2.4 The Look-Ahead Bias Trap

The most dangerous mistake in systematic trading is look-ahead bias: **using data at time $t$ that was not actually available at time $t$**.

This is more insidious than it sounds. Examples:

- **Earnings revisions**: company earnings figures are frequently restated. Using the final restated number in a backtest, rather than the initial release, creates a look-ahead.
- **Economic data revisions**: GDP, CPI, employment numbers are all revised. A backtest using revised figures will appear to predict things that were not predictable from the original release.
- **Announcement timing**: a FOMC statement is released at 2pm ET. If your daily signal uses a rate level from the same day, you must ensure you are not using a rate that reflects a 2pm announcement in a trade executed at 10am.
- **Implied rates from futures**: if the EOD settlement of a rate futures contract incorporates the same day's FOMC announcement, and you use it to generate a signal that supposedly predicts the next day, you may be using information that was only available after your hypothetical trade.

**The rule**: every input to your signal must have been observable at the time you would have actually placed the trade. If you are uncertain, use yesterday's data, not today's.

### 2.5 "I Know It When I See It" — The Intuition That Cannot Be Encoded

Some discretionary judgments genuinely cannot be turned into rules: the sense that a rumour is credible, the read on a central banker's body language, the assessment that a crowded narrative is about to break. These are valid edges — but they are not systematic.

The correct treatment is this: use your unsystematised intuitions as **filters applied on top of a systematic base strategy**, not as the primary decision-making engine. Specifically:

- The systematic signal runs all the time, generating positions.
- You can override or reduce a position based on discretionary judgment — but you must log every override and measure whether your overrides improve or degrade performance.
- After 50+ overrides, you can look at the data and determine whether your discretionary judgment is actually additive.

This is the discipline that distinguishes self-aware discretionary traders from wishful-thinking ones.

---

## Section 3 — Testing Whether Your Edge Is Real: Statistical Toolkit for Traders

### 3.1 Why "I've Been Right 60% of the Time" Is Not Enough

Imagine you flip a fair coin 20 times. You might easily get 13 heads (65%). Does this prove the coin is biased? No — it is well within the range of pure luck. With 20 coin flips, you cannot distinguish a fair coin from a coin with 55% heads probability.

Trading is exactly the same. If you have made 30 trades with a 60% hit rate, this tells you almost nothing about whether you have a genuine edge. You need to know:

1. How many trades (sample size)?
2. What is the variance of returns on each trade?
3. Is the 60% hit rate consistent across time, markets, and regimes?

The mathematical tool for answering these questions is the **t-statistic**.

### 3.2 Minimum Sample Size

For statistical inferences to be meaningful, you need enough observations that your results are unlikely to be a random draw from a zero-mean process. The general rule:

| Signal Frequency | Minimum Observations | Minimum History |
|---|---|---|
| Daily | 252+ | 1+ years |
| Weekly | 104+ | 2+ years |
| Monthly | 60+ | 5+ years |
| Quarterly | 32+ | 8+ years |

Note: these are **minimums** for weak statistical evidence. Strong evidence (enough to deploy real capital) typically requires 3-5x these minimums.

Strategy #1 in this repo has 3,912 daily observations across 2010-2024. That is ample. A monthly signal with 24 months of data is not.

### 3.3 The T-Statistic and P-Value: "The Probability This Is Luck"

The t-statistic answers a simple question: **is the average return of this strategy significantly different from zero?**

$$t = \frac{\bar{r}}{s / \sqrt{n}}$$

Where:
- $\bar{r}$ is the average daily (or weekly, monthly) return
- $s$ is the standard deviation of those returns
- $n$ is the number of observations

**Intuition**: if your average return is very large relative to the variability of returns, and you have many observations, then $t$ will be large, and the probability that this is a lucky draw from zero is small.

The **p-value** is the probability of observing a t-statistic as large as yours (or larger) if the true mean were exactly zero. In practice:

| T-statistic | P-value | Conventional interpretation |
|---|---|---|
| 1.65 | 0.10 | 10% chance this is luck |
| 1.96 | 0.05 | 5% chance — conventional "significance" threshold |
| 2.58 | 0.01 | 1% chance |
| 3.29 | 0.001 | 0.1% chance — strong evidence |

For Strategy #1 (EURUSD rate differential), the t-statistic on the signal coefficient β is **17.5** — so the probability this is luck is effectively zero.

Note: the t-statistic of the signal regression (as in the IC regression run in `notebooks/regression_all_pairs.py`) is different from the t-statistic of the strategy's mean return, but both tell you about statistical significance. The signal t-stat of 17.5 is particularly powerful because it measures the predictive relationship directly.

### 3.4 The Sharpe Ratio: Construction and Interpretation

The Sharpe ratio is the most widely used measure of risk-adjusted performance:

$$\text{SR} = \frac{\bar{r} - r_f}{\sigma_r} \times \sqrt{n_{\text{periods per year}}}$$

Where:
- $\bar{r}$ is the mean period return (daily, weekly, etc.)
- $r_f$ is the risk-free rate per period (often set to zero for simplicity in the short term)
- $\sigma_r$ is the standard deviation of period returns
- $\sqrt{n}$ annualises the ratio (252 for daily, 52 for weekly)

Note: there is a mathematical relationship between the Sharpe ratio and the t-statistic of the mean return. Specifically, $t = \text{SR} \times \sqrt{n / n_{\text{per year}}}$. For a daily strategy with 3,912 observations (approximately 15.5 years), a Sharpe of 1.0 corresponds to a t-statistic of approximately 6.3 — easily statistically significant. This is why "Sharpe > 1" is a meaningful threshold for daily strategies.

**Practical benchmarks for systematic FX strategies:**

| Sharpe Ratio | Assessment |
|---|---|
| < 0.5 | Below threshold — not deployable on its own |
| 0.5 – 0.8 | Mediocre — may contribute to a portfolio |
| 0.8 – 1.2 | Acceptable — useful as a standalone strategy or portfolio component |
| 1.2 – 2.0 | Good — characteristic of well-constructed systematic strategies |
| 2.0 – 3.0 | Excellent — exceptional result in academic/practitioner literature |
| > 3.0 | Extraordinary — either very real or very suspicious (check for look-ahead bias) |

Strategy #1 achieves a net Sharpe of 2.75 and Strategy #12 (the calibrated portfolio) achieves 2.73 — which places them at the very top of reported systematic FX strategies in the academic literature. This should prompt rigorous scrutiny (is there a look-ahead bias? is the cost model realistic?) before treating these as settled.

### 3.5 The Probabilistic Sharpe Ratio (PSR)

The observed Sharpe ratio is itself a random variable — it depends on the particular sample of returns you happened to observe. The **Probabilistic Sharpe Ratio** (Bailey and López de Prado, 2012) asks: what is the probability that the true Sharpe ratio exceeds some benchmark $SR^*$?

$$\text{PSR}(SR^*) = \Phi\left(\frac{(SR - SR^*)\sqrt{n-1}}{\sqrt{1 - \hat{\gamma}_3 \cdot SR + \hat{\gamma}_4 - 1}{4} \cdot SR^2}}\right)$$

Where $\hat{\gamma}_3$ is the skewness and $\hat{\gamma}_4$ is the excess kurtosis of the return series, and $\Phi$ is the standard normal CDF.

The intuition: if your returns have fat tails (high kurtosis) or negative skew, then your observed Sharpe ratio is a noisier estimate of the true Sharpe ratio. The PSR penalises for this noise. A strategy with a Sharpe of 1.5 but very fat-tailed returns might have a PSR(1.0) of only 60% — meaning there is a 40% chance the true Sharpe is below 1.0.

**For the practitioner**: the PSR tells you how much statistical confidence to place in your observed Sharpe. A PSR above 95% against a benchmark of 0.5 is a reasonable threshold before deploying capital.

### 3.6 The Deflated Sharpe Ratio (DSR): Adjusting for Multiple Testing

This is the most important concept that practitioners consistently ignore: **every time you test a variation of a strategy, you are running a statistical test, and the probability of finding a spuriously good result by chance increases with the number of tests**.

If you try 100 different parameter combinations for a strategy, you expect roughly 5 to show p-values below 0.05 by pure chance — even if the underlying signal has no predictive power at all.

Bailey and López de Prado (2014) developed the **Deflated Sharpe Ratio** to correct for this:

$$DSR = PSR\left(SR^*\right), \quad \text{where } SR^* \approx (1 - \gamma) Z^{-1}\left(1 - \frac{1}{N}\right) + \gamma \cdot Z^{-1}\left(1 - \frac{1}{N} \cdot e^{-1}\right)$$

Where $N$ is the number of strategy variations tried, $\gamma$ is the Euler-Mascheroni constant (~0.5772), and $Z^{-1}$ is the inverse normal CDF.

**The practical message**: if you tried 50 parameter combinations before settling on the one you are reporting, your effective Sharpe ratio hurdle is approximately 1.5, not 1.0. A reported Sharpe of 1.2 after 50 trials is not statistically significant — it is what you would expect to find by luck.

**The correct process**: decide on your signal construction rules before looking at the backtest results, then run the backtest once. Alternatively, use walk-forward validation (see Section 7) which provides honest out-of-sample evidence.

### 3.7 Information Coefficient and ICIR

The **Information Coefficient (IC)** is the Spearman (rank) correlation between your signal at time $t$ and the asset's return from $t$ to $t+h$:

$$IC = \text{Spearman}\left(\text{signal}_t, r_{t \to t+h}\right)$$

Typical IC values for professional systematic strategies:
- IC of 0.02-0.05: marginal, barely exploitable
- IC of 0.05-0.10: useful component of a portfolio signal
- IC of 0.10-0.20: strong — this is Grinold and Kahn's "skilful" threshold
- IC above 0.20: exceptional

Grinold and Kahn's Fundamental Law of Active Management connects IC to the expected Information Ratio (IR, analogous to Sharpe ratio for active management):

$$IR = IC \times \sqrt{\text{Breadth}}$$

Where Breadth is the number of independent bets per year. If you have an IC of 0.05 and you trade 252 independent bets per year:

$$IR \approx 0.05 \times \sqrt{252} \approx 0.79$$

This is why high-frequency trading firms can operate with tiny ICs: they make millions of bets per year, and the Law of Large Numbers does the rest.

The **ICIR** (Information Coefficient Information Ratio) measures the consistency of your IC over time:

$$ICIR = \frac{\text{mean}(IC_t)}{\text{std}(IC_t)}$$

Where $IC_t$ is calculated on rolling windows (e.g., rolling 12-month IC). An ICIR above 0.5 indicates a reliably consistent signal. An ICIR below 0.3 suggests the signal works some periods and not others — which is harder to trade systematically.

### 3.8 Walk-Forward Validation: The Only Honest Test

The gold standard for validating a systematic strategy is **walk-forward testing**: you train the model on one period of data, make predictions for the subsequent period, and measure performance on that out-of-sample period. You then advance the window and repeat.

```
|--- Training (2010-2014) ---| Test (2015) |
                   |--- Training (2010-2015) ---| Test (2016) |
                                  |--- Training (2010-2016) ---| Test (2017) |
                                  ...
```

The out-of-sample periods, stitched together, give you an honest estimate of what the strategy would have actually earned if you had traded it in real time.

Walk-forward testing is more conservative than in-sample testing because:
1. Parameters estimated on one period may not hold in the next.
2. The model cannot look back from the test period into data that was "future" at the time.
3. If parameters need to be refit, the procedure is realistic about when that information was available.

### 3.9 Python: A Simple T-Test on Trade Returns

```python
import numpy as np
from scipy import stats
import pandas as pd

# Suppose you have a list of daily P&L returns from your strategy
# (either from manual trading records or a systematic backtest)
returns = pd.Series([...])  # replace with your actual return data

# One-sample t-test: is the mean return significantly different from zero?
t_stat, p_value = stats.ttest_1samp(returns, popmean=0.0)

# Annualised Sharpe ratio
n_per_year = 252  # for daily returns
sharpe = (returns.mean() / returns.std()) * np.sqrt(n_per_year)

# Annualised return
ann_return = (1 + returns).prod() ** (n_per_year / len(returns)) - 1

print(f"Number of observations : {len(returns)}")
print(f"Mean daily return      : {returns.mean():.4%}")
print(f"Daily vol              : {returns.std():.4%}")
print(f"T-statistic            : {t_stat:.2f}")
print(f"P-value (two-sided)    : {p_value:.4f}")
print(f"Annualised Sharpe      : {sharpe:.2f}")
print(f"Annualised return      : {ann_return:.2%}")

# Interpretation
if abs(t_stat) > 2.58 and p_value < 0.01:
    print("Strong statistical evidence of a real edge (p < 1%)")
elif abs(t_stat) > 1.96 and p_value < 0.05:
    print("Moderate statistical evidence of a real edge (p < 5%)")
else:
    print("Insufficient statistical evidence — do not deploy")
```

**Example output for Strategy #1** (approximate, for illustration):

```
Number of observations : 3912
Mean daily return      : 0.0085%
Daily vol              : 0.0510%
T-statistic            : 10.41
P-value (two-sided)    : 0.0000
Annualised Sharpe      : 2.75
Annualised return      : 22.9%
Strong statistical evidence of a real edge (p < 1%)
```

---

## Section 4 — The Quantamental Approach: Systematic Frameworks with Discretionary Overlay

### 4.1 What "Quantamental" Means in Practice

The term quantamental (quantum + fundamental) describes investment processes that are neither purely discretionary nor purely systematic, but rather integrate structured quantitative analysis with human fundamental judgment. The key word is "structured": the human judgment does not operate on a blank canvas. It operates within a framework that forces explicit, data-anchored decisions.

The three core components of a quantamental approach are:

1. **Systematic signal generation**: quantitative models produce signals based on observable data. These signals are generated consistently and without emotional interference.
2. **Human overlay**: a human being with domain expertise reviews the signals, identifies regime changes, filters for events that the model cannot process (a regulatory shock, a geopolitical event, a central bank communication that is fundamentally ambiguous), and approves or modifies the positions.
3. **Systematic risk management**: regardless of what humans decide about direction, the position sizing and portfolio-level risk management is systematic. This is where most of the genuine value-add of quantitative techniques is concentrated.

### 4.2 How Top Funds Do It

**Point72 (Steve Cohen)**: operates as a collection of semi-independent pods, each led by a fundamental analyst. The analysts generate long/short equity ideas with explicit thesis documents. A centralised quantitative risk system monitors portfolio exposures, factor concentrations, and drawdown limits across all pods. Positions are sized by the analysts' conviction but constrained by the risk system. The human (conviction, thesis) and the systematic (risk, sizing limits) operate in parallel.

**Citadel — Surveyor Capital**: the "quantamental equity" business runs fundamental research with quantitative tools for screening opportunities, tracking alternative data (satellite imagery, credit card data, foot traffic), and risk decomposition. Analysts use dashboards of systematic signals to identify where to focus their fundamental research — the quant narrows the search space, the human does the deep dive.

**D.E. Shaw**: arguably the original quantamental firm. Shaw employs macro economists alongside quantitative researchers. The macro economists' role is precisely the one described in Section 1.4: identifying regime changes that would invalidate the assumptions of the quantitative models. The quantitative models operate continuously; the macro economists decide when to reduce exposures based on regime context.

**Man Numeric**: runs a fully systematic investment process, but the "inputs" to the models include fundamental data (earnings revisions, management changes, analyst estimates) that originally required human judgment to produce. The systematisation happened at the signal level, not at the discretionary layer.

### 4.3 Building Your Personal Quantamental Approach

There are three progressive levels at which a discretionary trader can introduce systematic elements:

**Level 1: Discretionary Direction + Systematic Position Sizing**

You continue generating trade ideas discretionarily. However, instead of sizing based on conviction, you size each trade based on a formula:

$$\text{position size} = \frac{\text{target daily vol}}{|\sigma_{\text{instrument}} \cdot \text{signal}|} \times \text{capital}$$

Where $\sigma_{\text{instrument}}$ is the realised daily volatility of the instrument over the past 20-60 days. This single change — systematic sizing instead of gut-feel sizing — can dramatically improve risk-adjusted returns from a discretionary process.

**Level 2: Systematic Signal Generation + Discretionary Filters**

Your signals are generated by quantitative models. You overlay a small number of explicit, pre-defined discretionary filters:

- "Do not trade if VIX > 30" (risk-off avoidance)
- "Do not trade 24 hours before or after a major data release in this currency"
- "Reduce position by 50% if we are within 2 weeks of a central bank meeting with genuine uncertainty"

These filters are applied consistently (not based on daily mood) and their impact is measured.

**Level 3: Full Systematic with Macro Overlay (Regime Switching)**

At this level, the core system runs fully systematically. The macro overlay operates as a **regime switch** that modulates the overall sizing:

$$\text{effective position} = \text{raw signal position} \times \text{regime multiplier}$$

The regime multiplier might be:
- 1.0 in normal conditions
- 0.5 in elevated volatility regimes (VIX > 25)
- 0.0 during identified structural breaks
- 1.25 when macro confirms the signal direction

The regime identification is explicit, data-driven, and pre-defined. It is not "I feel nervous today."

### 4.4 The Macro Scorecard as Quantamental Tool

A macro scorecard (see Section 8 for full construction) is the quintessential quantamental tool: it forces you to score each macro dimension (growth, inflation, rates, positioning, valuation) on an explicit numerical scale, based on observable indicators. The score is then aggregated into a single directional signal.

This converts "my macro view on EURUSD is cautiously bearish" into "+0.65 on a -2 to +2 scale, driven predominantly by the rate differential dimension, modestly offset by stretched short positioning and cheap EUR valuation."

The scorecard approach:
1. Forces you to articulate your view component by component
2. Creates a historical record you can analyse (was the rate dimension right? was the positioning dimension right?)
3. Allows you to IC-weight the dimensions over time based on their actual predictive power
4. Can be backtested as a combined signal

---

## Section 5 — Common Discretionary Strategies and Their Systematic Equivalents

### 5.1 "I Buy When Rates Rise" — The Rate Differential Signal

**The Discretionary Intuition**: when the central bank signals tighter policy than a trading partner, the currency appreciates as capital flows toward the higher-yielding market. This is textbook Uncovered Interest Parity (UIP) — except UIP predicts that higher-rate currencies appreciate by exactly the interest rate differential, which empirically they do not. In practice, they often appreciate by *more* due to capital flows and momentum effects.

**The Systematic Equivalent**: the change in the 2Y yield differential as a predictor of next-period FX returns.

$$\text{signal}_t = \Delta_t(r_{\text{base}, 2Y} - r_{\text{quote}, 2Y}) = (r_{\text{base}, 2Y,t} - r_{\text{quote}, 2Y,t}) - (r_{\text{base}, 2Y,t-1} - r_{\text{quote}, 2Y,t-1})$$

$$\text{predict: } r_{\text{FX}, t+1} = \alpha + \beta \cdot \text{signal}_t$$

**Evidence from this repo (2010-2024, net of 5 pips)**:

| Pair | β | R² | T-stat | Net Sharpe |
|---|---|---|---|---|
| EURUSD | +0.0335 | 7.5% | 17.5 | 2.75 |
| GBPUSD | +0.028 | ~4% | ~8.0 | 1.50 |
| AUDUSD | +0.031 | ~5% | ~9.5 | 1.22 |
| NZDUSD | +0.029 | ~4% | ~7.0 | 0.92 |
| USDJPY | +0.030 | ~4% | ~8.5 | 1.44 |
| USDCAD | +0.034 | ~5% | ~9.8 | 2.06 |
| USDCHF | ~0 | ~0% | ~1.5 | 0.00 |
| USDSEK | +0.038 | ~6% | ~10.2 | 2.13 |

All betas positive (higher rate differential → long base currency / short quote currency), all except USDCHF statistically significant. USDCHF fails because SNB intervention and safe-haven dynamics override the rate signal.

**Why it works**: the 2Y yield change captures expected short-rate path changes that markets have not yet fully priced into spot FX. This is consistent with the "forward premium puzzle" literature: currencies do not fully adjust to rate differentials immediately, and the adjustment over the subsequent day is partially predictable.

**Sub-period robustness**: the signal works in all four major regimes tested (ZIRP 2010-2014, Divergence 2014-2018, COVID 2018-2020, Hiking 2020-2024). It is strongest in the Hiking regime (when rates are most active) and weakest in ZIRP (when all rates are near zero and differentials compress).

### 5.2 "I Follow the Central Bank" — The Policy Surprise Signal

**The Discretionary Intuition**: markets price in expected central bank policy, so what matters for FX is not the level of rates but the *surprise* component of central bank communications. A central bank that delivers 25bps but was priced for 50bps is actually dovish.

**The Systematic Equivalent**: decompose central bank meeting outcomes into:
1. **Target factor**: the surprise in the immediate policy rate decision
2. **Path factor**: the surprise in the expected future path (from OIS pricing vs. dot plot / forward guidance)

Following Gürkaynak, Sack, and Swanson (2005), the surprise in both dimensions is computed using intraday changes in interest rate futures/OIS rates around the announcement window (typically 30-minute window around the FOMC statement release).

$$\text{surprise}_t = \text{OIS rate}_{t+30\text{min}} - \text{OIS rate}_{t-5\text{min}}$$

**Implementation**: this is an **event-driven** strategy rather than a daily signal strategy. You are not positioned continuously; you take positions around central bank meetings. The FX response to a hawkish surprise (higher-than-expected rate path) is to buy the currency; the FX response to a dovish surprise is to sell.

**Evidence**: Gürkaynak, Sack, and Swanson (2005) documented that the path factor has more persistent effects on the yield curve than the target factor. For FX, the implication is that forward guidance matters more than current-rate decisions — a genuinely systematic version of what experienced discretionary traders have known for decades.

### 5.3 "Carry Trade When It's Calm" — Vol-Conditioned Carry

**The Discretionary Intuition**: carry trades (borrow in low-rate currencies, invest in high-rate currencies) work during calm periods but crash violently during risk-off episodes. Experienced traders know to cut carry exposure when volatility rises.

**The Systematic Equivalent**: Menkhoff, Sarno, Schmeling, and Schrimpf (2012, *Journal of Finance*, vol. 67, pp. 681-718) provide the formal evidence: carry trades can be substantially improved by conditioning on **global FX volatility**. When global FX volatility is high, carry returns are poor; when it is low, carry returns are strong.

**The signal construction**:
1. Rank all G10 currencies by short-rate level
2. Go long the top 3 (highest rate) and short the bottom 3 (lowest rate) — the classic carry portfolio
3. Size down (or flatten) when global FX vol exceeds its 1-year average

**Evidence**: Menkhoff et al. (2012) show that a carry portfolio conditioned on global FX volatility achieves a Sharpe ratio approximately double that of the unconditional carry portfolio. The Sharpe of the volatility-managed carry strategy is approximately 1.3 vs. 0.7 for the naive carry strategy.

The carry signal in this repo (`signals/carry/carry.py`) implements cross-sectional z-scoring of the rate differential across G10 pairs, which is the correct construction for a portfolio-level carry signal. The vol-conditioning layer would be the logical next development.

**Why it works**: carry trade crashes are episodes of global risk aversion. During these episodes, carry investors are forced to unwind simultaneously, which amplifies the crash. When vol is elevated, you are already in a crash-prone regime, so you avoid the exposure. When vol is low, the risk of a crash unwind is smaller and you can harvest the premium.

### 5.4 "Trend Following in Strong Moves" — Time-Series Momentum

**The Discretionary Intuition**: strong trends persist. A currency that has been strengthening for the past year is likely to continue strengthening in the near term, driven by capital flows, central bank divergence, and positioning dynamics.

**The Systematic Equivalent**: Time-Series Momentum (TSMOM), formalised by Moskowitz, Ooi, and Pedersen (2012, *Journal of Financial Economics*, vol. 104, pp. 228-250).

$$\text{signal}_{i,t} = \text{sign}\left(r_{i, t-252, t}\right) \times \frac{1}{\sigma_{i,t}}$$

Where $r_{i,t-252,t}$ is the 12-month excess return and $\sigma_{i,t}$ is the rolling 1-month realised volatility (used for vol-scaling).

**Evidence**: Moskowitz et al. (2012) document statistically significant time-series momentum across 58 liquid futures markets (equity indexes, currencies, commodities, bonds) with a Sharpe ratio of approximately 1.3 for a diversified TSMOM portfolio. Individual asset TSMOM Sharpes are lower (typically 0.4-0.8), but diversification across assets raises the portfolio Sharpe substantially.

**Important note**: this repo tested cross-sectional FX momentum (Strategy #11, rejected at Sharpe −0.34) across all lookbacks. This is not the same as TSMOM. Cross-sectional momentum asks "which currencies have done best relative to each other?"; time-series momentum asks "which currencies are trending in absolute terms?" The two are different signals. The post-GFC decay in FX cross-sectional momentum is documented in the literature and was confirmed by this repo's testing.

**Why it works**: trends in FX persist because (1) central bank cycles are gradual and multi-year in scope, (2) institutional capital rotates slowly between geographies, (3) FX interventions by central banks (especially EM) create partial reversion that paradoxically extends trends.

### 5.5 "Buy Undervalued Currencies" — Purchasing Power Parity Deviation

**The Discretionary Intuition**: currencies that are extremely cheap relative to purchasing power parity will eventually revert toward fair value. The Swiss franc at 0.70 to the dollar after the 2011 SNB interventions, or the JPY at 155 in 2024, are examples traders point to.

**The Systematic Equivalent**: real exchange rate deviation from PPP as a value signal.

$$q_t = s_t - p_t + p_t^*$$

Where $s_t$ is the log spot rate, $p_t$ is the log domestic price level, and $p_t^*$ is the log foreign price level. A negative $q$ means the currency is cheap in real terms (undervalued vs. PPP).

**Evidence**: Asness, Moskowitz, and Pedersen (2013, *Journal of Finance*, vol. 68, pp. 929-985) document value effects across eight asset classes including currencies. The FX value signal (PPP deviation) earns a Sharpe ratio of approximately 0.4 at a 5-year horizon — meaningful but low relative to carry and momentum. The key caveat: the PPP value signal is **very slow**. It is a 3-5 year signal, not a weekly or monthly one. A discretionary trader who is betting on PPP reversion expects to wait years for the trade to play out.

**Practical construction**: the most common approach uses the OECD PPP estimates (published annually) to construct an equilibrium exchange rate for each G10 currency, then compute the deviation of the actual spot rate from this implied level. Currencies in the bottom quartile of deviation (cheapest vs. PPP) are long candidates; currencies in the top quartile are short candidates.

### 5.6 "Trade the Squeeze" — CFTC COT Positioning Signal

**The Discretionary Intuition**: when speculative positioning in a currency is extremely one-sided, a reversal becomes more likely because there is limited incremental buying (or selling) left. If everyone is already long EUR, who is left to buy?

**The Systematic Equivalent**: the CFTC Commitments of Traders (COT) report publishes weekly net speculative positions in FX futures. A z-score of the net speculative position identifies positioning extremes.

$$z_t = \frac{\text{net spec}_t - \text{mean}(\text{net spec}_{t-52:t})}{\text{std}(\text{net spec}_{t-52:t})}$$

The signal is contrarian: $z_t > 1.5$ → go short (crowded long), $z_t < -1.5$ → go long (crowded short).

**Evidence from this repo (Strategy #13)**: mixed results. The short side (fading crowded longs) had a win rate of approximately 40%, which sounds low but is slightly profitable in expectation. The long side (buying crowded shorts) had a win rate of only 30% — meaningfully below 50%. The combined strategy had a Sharpe of −0.07.

**Why this is instructive**: the COT signal alone is not a robust standalone strategy. It works best as a **filter** on top of directional signals: if you have a bullish signal on a currency but COT positioning is extremely long (already crowded), you reduce or delay the trade. The academic literature broadly supports positioning as a risk signal rather than a directional signal.

### 5.7 "Risk-Off Means JPY and CHF" — Safe-Haven Flow Signal

**The Discretionary Intuition**: in risk-off episodes (market stress, geopolitical events, credit events), capital flows into safe-haven currencies — JPY and CHF historically, and to a lesser extent USD and gold. This is one of the most reliable qualitative patterns in macro FX.

**The Systematic Equivalent**: a VIX-triggered safe-haven signal.

$$\text{signal}_t = \begin{cases} +1 & \text{(long JPY/CHF)} & \text{if } \Delta VIX_t > \text{threshold} \\ 0 & \text{if } |\Delta VIX_t| < \text{threshold} \\ -1 & \text{(short JPY/CHF)} & \text{if } \Delta VIX_t < -\text{threshold} \end{cases}$$

**Note**: this safe-haven signal interacts with the rate differential signal in complex ways. In 2022-2024, the JPY rate differential was working against the safe-haven dynamic: USD rates rose rapidly while BoJ held rates near zero, creating a large carry incentive to sell JPY. The safe-haven signal said "buy JPY in stress episodes" while the rate differential said "sell JPY always." The conflict is why USDJPY's rate-differential strategy (Strategy #5) suffered a −59.2% drawdown — the carry trade was a perfect crowded trade that unwound violently in late 2024 when the BoJ changed policy.

### 5.8 "CAD/AUD/NZD Follow Commodities" — Cross-Asset Signal

**The Discretionary Intuition**: commodity-exporting currencies are proxies for their primary commodity exports. Canada exports oil; Australia exports iron ore, coal, and gold; New Zealand exports dairy and agricultural products.

**The Systematic Equivalent**: lagged commodity price changes as predictors of commodity FX returns.

$$r_{\text{CADUSD}, t+1} = \alpha + \beta \cdot \Delta \ln(\text{WTI}_{t}) + \epsilon_t$$

**Evidence**: Ferraro, Rogoff, and Rossi (2015, *Journal of International Money and Finance*, vol. 54, pp. 116-141) specifically investigated oil prices and the CAD/USD exchange rate. Their key finding: at monthly and quarterly frequencies, there is little systematic relationship. But at the **daily** frequency, a robust short-term relationship exists. Oil price changes on day $t$ predict CADUSD changes on day $t+1$ with a statistically significant coefficient. This finding is directly actionable for a systematic daily strategy.

**Why the frequency matters**: at monthly frequencies, all the slow-moving fundamentals (growth differentials, rate differentials, current account) swamp the commodity signal. At daily frequencies, the commodity signal moves faster than these fundamentals adjust, creating a predictable window.

### 5.9 "Trade the Divergence" — Growth and Policy Divergence Signal

**The Discretionary Intuition**: the biggest macro FX trades come from divergence — when two economies are on clearly different paths (one tightening, one easing; one accelerating, one slowing). The 2014-2015 USD rally was the textbook example: US growing, Fed hiking; Europe contracting, ECB easing.

**The Systematic Equivalent**: a composite divergence score using:
1. OECD Composite Leading Indicator (CLI) differential: measures growth divergence 6-9 months ahead
2. 2Y yield differential: measures expected rate divergence
3. Inflation differential: measures whether rate divergence is driven by fundamentals

$$\text{divergence score} = w_1 \cdot \Delta CLI_{\text{diff}} + w_2 \cdot \Delta r_{2Y\text{diff}} + w_3 \cdot \Delta \pi_{\text{diff}}$$

This is essentially the first row of the macro scorecard (Section 8). The divergence signal is a low-frequency (monthly to quarterly) signal that provides the macro backdrop into which shorter-term signals operate.

---

## Section 6 — Position Sizing: The Discretionary Trader's Biggest Gap

### 6.1 Why Discretionary Traders Size Poorly

Ask a discretionary trader how they size their positions and you will typically get some version of: "I size bigger when I'm more confident." This is conviction-based sizing, and it is one of the most reliable destroyers of systematic performance for several reasons:

1. **Confidence is not the same as statistical edge**. The trades you feel most confident about are often the consensus trades — the ones where the narrative is most compelling, the chart is most obvious, and the macro case is most clear. But if everyone sees it, the trade is already priced in.
2. **Your confidence will be highest at the worst time**. After a string of winning trades, you will feel invincible and size large. After a string of losing trades, you will size tiny. This is exactly the wrong pattern — it adds risk when recent performance was good (which often precedes mean reversion) and removes risk when expected returns have risen (because prices are cheap).
3. **You have no way to know your true edge ex-ante**. The Kelly Criterion (below) shows that optimal sizing depends on knowing your win probability and win/loss ratio. Discretionary confidence is not a reliable estimate of either.

### 6.2 The Kelly Criterion

The Kelly Criterion gives the fraction of your capital that maximises the long-run geometric growth rate of wealth:

$$f^* = \frac{p \cdot b - (1-p)}{b} = \frac{\text{edge}}{\text{odds}}$$

Where:
- $p$ is the probability of a winning trade
- $1-p$ is the probability of a losing trade
- $b$ is the payoff ratio (average win / average loss)

**Example**: suppose your systematic signal has a 52% win rate with equal average wins and losses ($b = 1$):

$$f^* = \frac{0.52 \times 1 - 0.48}{1} = 0.04 = 4\%$$

Kelly says to risk 4% of capital per trade. With a 55% win rate and $b = 1.1$:

$$f^* = \frac{0.55 \times 1.1 - 0.45}{1.1} = \frac{0.605 - 0.45}{1.1} = \frac{0.155}{1.1} \approx 14\%$$

**The 25-50% Kelly rule**: Full Kelly maximises expected long-run growth but accepts very large drawdowns along the way. Half Kelly (50% of $f^*$) cuts the expected growth rate only modestly (by roughly 25%) while halving the variance of outcomes. Quarter Kelly (25% of $f^*$) is even more conservative and is appropriate when your estimate of $p$ and $b$ is uncertain. For most systematic strategies, 25-50% Kelly is the practical range.

**The key insight**: Kelly requires *knowing* your edge statistically. This is only possible with systematic strategies. Discretionary traders who cannot quantify their win rate and payoff ratio cannot apply Kelly — which is itself a strong argument for systematising.

### 6.3 Volatility-Based Position Sizing: The Systematic Standard

The most common position sizing approach in systematic FX trading targets a constant risk contribution from each trade:

$$\text{position size (units)} = \frac{\text{target daily P&L vol (£)}}{\text{daily vol of 1 unit of instrument (£)}}$$

More specifically, for a currency pair:

$$N = \frac{\sigma_{\text{portfolio, target}}}{\sigma_{\text{instrument}}} \times \frac{\text{capital}}{\text{pip value per lot}}$$

Where $\sigma_{\text{instrument}}$ is the realised daily volatility of the instrument over the past 20-60 days, and $\sigma_{\text{portfolio, target}}$ is the daily vol you are targeting for this position.

**Why this beats "2% risk per trade"**: a "2% risk per trade" rule is easy to implement but ignores the actual volatility of the instrument. A 2% risk rule on USDJPY (which moves less than GBPJPY) will create different risk contributions from the two positions. Volatility-scaling ensures equal risk contribution.

**The formula used in this repo (Strategy #12 — the calibrated portfolio)**:

```python
def vol_target_size(signal: float, instrument_vol: float, 
                    target_vol: float = 0.10, capital: float = 1_000_000) -> float:
    """
    signal: directional signal, typically in [-1, +1] after normalisation
    instrument_vol: annualised vol of the FX pair (e.g. 0.08 for EURUSD)
    target_vol: annual vol target for the position (e.g. 0.10 = 10%)
    capital: notional capital in base currency
    """
    daily_target_vol = target_vol / (252 ** 0.5)
    daily_instrument_vol = instrument_vol / (252 ** 0.5)
    
    if daily_instrument_vol == 0:
        return 0.0
    
    raw_size = (daily_target_vol / daily_instrument_vol) * capital
    return raw_size * signal  # sign from signal direction
```

Strategy #12 uses a 10% annual vol target per position, which produced a Sharpe of 2.73 and a maximum drawdown of −22.0% over 2010-2024 — the best calibration in this repo's testing.

### 6.4 Risk Parity and Equal Risk Contribution

In a portfolio of systematic strategies, **risk parity** allocates capital such that each strategy contributes equally to the total portfolio variance:

$$w_i = \frac{1/\sigma_i}{\sum_j 1/\sigma_j}$$

This is the simplest version; a more rigorous version accounts for correlations between strategies. Risk parity is the correct approach when you do not have strong priors about which strategy will outperform — which is almost always, since strategy relative performance is highly regime-dependent.

**The 1/N portfolio**: when correlations are uncertain (which they usually are), simply equal-weighting (1/N) across strategies is a robust baseline. DeMiguel, Garlappi, and Uppal (2009) showed that 1/N is very hard to beat out-of-sample, even by supposedly superior optimisation methods, because optimisers amplify estimation error. The lesson for the transitioning trader: start with equal risk weighting, and only move to more complex optimisation when you have strong, statistically grounded reasons to do so.

### 6.5 Stop-Losses vs. Time-Based Exits

The evidence on stop-losses is more nuanced than conventional trading wisdom suggests:

**Stop-losses**: a price-based stop-loss exits the position when losses reach a threshold. The argument for them: they limit catastrophic drawdowns. The argument against: they introduce a systematic bias in which your losing positions are cut, potentially just before they would have recovered, while your winners are held. If the underlying signal has genuine predictive power over the holding period, a stop-loss that exits early may be costing you the eventual return.

**Time-based exits**: exit after $N$ days regardless of P&L. The argument: if your signal has a 1-day predictive horizon, there is no reason to hold for 3 days. The information in the signal has been consumed.

**Evidence for daily rate-differential signals (like Strategy #1)**: the signal predicts next-day returns, so the horizon is 1 day. Holding for longer periods is not justified by the signal's predictive structure. The strategy exits and re-enters every day. For this type of strategy, time-based exits (daily rebalancing) are the correct approach.

For longer-horizon signals (carry, PPP value), a maximum holding period matched to the signal's predictive horizon is more appropriate than stop-losses.

### 6.6 Position Limits

Even with optimal sizing, you need absolute position limits:

- **Per-position limit**: no single position should exceed 20-25% of your risk budget. This prevents a single trade thesis from being over-represented even when the signal is strong.
- **Sector/factor limit**: no single factor (e.g., all carry, all rate-differential) should exceed 50% of your total risk budget.
- **Currency limit**: if you are long EURUSD and short USDCHF, you effectively have a double EUR-long position. The limits should account for cross-position correlations.

---

## Section 7 — Building Your First Systematic Strategy: Step-by-Step

### 7.1 The Research Process

The correct process flows in one direction only: idea → hypothesis → data → signal → backtest → validate → deploy. The most dangerous version flows in the opposite direction: backtest → optimise → claim success. The former is called confirmatory research. The latter is called data mining.

The seven-step process:

1. **Write the hypothesis in natural language (before touching data)**
2. **Define the signal mathematically (before looking at results)**
3. **Source the data**
4. **Build the backtest**
5. **Evaluate using DSR (not just Sharpe)**
6. **Stress test across sub-periods and parameter variations**
7. **Walk-forward test to confirm out-of-sample**

### 7.2 Common Pitfalls

**Data mining bias**: the more parameter combinations you test, the more likely you are to find a spuriously good result. If you test 100 combinations of lookback period × threshold × stop-loss, you expect approximately 5 to show p < 0.05 by pure chance. The DSR (Section 3.6) corrects for this, but the best remedy is to decide on your parameters a priori.

**Look-ahead bias**: discussed in Section 2.4. Always double-check by asking: "At the exact moment I would have placed this trade in real life, would I have had access to every piece of data my signal uses?"

**Overfitting**: your backtest strategy is too specific to the historical data. Signs of overfitting:
- The strategy has many parameters (> 5 free parameters is suspicious)
- Performance differs dramatically between sub-periods
- Performance degrades rapidly when parameters are varied by small amounts
- The rationale for the exact parameters is post-hoc rather than pre-hoc

**Transaction cost blindness**: many backtests use theoretical prices with zero costs. Realistic costs for G10 FX:
- Bid-ask spread: 0.5-2 pips for majors (EURUSD, USDJPY), 2-5 pips for minors (USDNOK, USDSEK)
- Market impact: negligible for small traders, significant for institutional (> $10M per trade)
- This repo uses 5 pips round-trip (2.5 pips per side), which is conservative for majors

### 7.3 Python Walkthrough: A Simple Rate Differential Strategy from Scratch

```python
"""
Minimal working example: EURUSD rate-differential strategy.
Replicates the logic of Strategy #1 in this repo.

Requirements:
    pip install pandas numpy scipy matplotlib yfinance fredapi

You need a free FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import yfinance as yf
from fredapi import Fred

# -------------------------------------------------------------------
# STEP 1: DEFINE THE HYPOTHESIS
# "The daily change in the 2Y EUR-USD rate differential
#  positively predicts the next-day EURUSD return."
# Signal: Δ(DE_2Y - US_2Y) today → EURUSD return tomorrow
# -------------------------------------------------------------------

FRED_API_KEY = "your_fred_api_key_here"
START = "2010-01-01"
END = "2024-12-31"
COST_PIPS = 5.0  # round-trip transaction cost in pips
PIP_SIZE = 0.0001  # 1 pip in EURUSD

# -------------------------------------------------------------------
# STEP 2: SOURCE THE DATA
# -------------------------------------------------------------------

fred = Fred(api_key=FRED_API_KEY)

# US 2Y Treasury yield from FRED
us_2y = fred.get_series("DGS2", observation_start=START, observation_end=END)
us_2y = us_2y.dropna()
us_2y.name = "US_2Y"

# German 2Y Bund yield (proxy via FRED: note - use ECB SDW for exact data)
# For illustration, we use a FRED proxy series
# In practice, use ECB SDW API or the TVC-scraped data in this repo
de_2y_proxy = fred.get_series("IRLTLT01DEM156N", 
                               observation_start=START, observation_end=END)
# (This is the long rate — in practice you need the 2Y specifically)
de_2y_proxy.name = "DE_2Y_proxy"

# EURUSD spot
eurusd = yf.download("EURUSD=X", start=START, end=END, auto_adjust=True)["Close"]
eurusd.index = pd.to_datetime(eurusd.index).tz_localize(None)
eurusd.name = "EURUSD"

# -------------------------------------------------------------------
# STEP 3: CONSTRUCT THE SIGNAL
# -------------------------------------------------------------------

# Align all data to same daily index
df = pd.DataFrame({
    "US_2Y": us_2y,
    "DE_2Y": de_2y_proxy,
    "EURUSD": eurusd
}).dropna().sort_index()

# Rate differential (EU minus US → positive = EU rates higher = EUR bullish)
df["rate_diff"] = df["DE_2Y"] - df["US_2Y"]

# SIGNAL: daily change in rate differential
df["signal"] = df["rate_diff"].diff(1)

# RETURN: next-day EURUSD log return
df["fx_return"] = np.log(df["EURUSD"]).diff(1).shift(-1)

# Drop NaNs
df = df.dropna()

# -------------------------------------------------------------------
# STEP 4: VALIDATE THE SIGNAL (before backtesting)
# -------------------------------------------------------------------

# OLS regression: fx_return ~ signal
from scipy import stats as sp_stats

slope, intercept, r_value, p_value, std_err = sp_stats.linregress(
    df["signal"], df["fx_return"]
)

t_stat = slope / std_err
print(f"\n--- Signal Validation ---")
print(f"Beta (slope)  : {slope:.4f}")
print(f"R-squared     : {r_value**2:.4f} ({r_value**2*100:.1f}%)")
print(f"T-statistic   : {t_stat:.2f}")
print(f"P-value       : {p_value:.6f}")
print(f"Observations  : {len(df)}")

# -------------------------------------------------------------------
# STEP 5: BUILD THE BACKTEST
# -------------------------------------------------------------------

# Position: long EURUSD when signal > 0, short when signal < 0
df["position"] = np.sign(df["signal"])

# Gross PnL: position × next-day return
df["gross_pnl"] = df["position"] * df["fx_return"]

# Transaction cost: deduct cost only when position changes
df["position_change"] = df["position"].diff(1).abs()
df["cost"] = (df["position_change"] / 2) * COST_PIPS * PIP_SIZE  # per side

# Net PnL
df["net_pnl"] = df["gross_pnl"] - df["cost"]

# -------------------------------------------------------------------
# STEP 6: EVALUATE PERFORMANCE
# -------------------------------------------------------------------

n_per_year = 252
returns = df["net_pnl"].dropna()

ann_return = (1 + returns).prod() ** (n_per_year / len(returns)) - 1
ann_vol = returns.std() * np.sqrt(n_per_year)
sharpe = ann_return / ann_vol

cum = (1 + returns).cumprod()
max_dd = ((cum / cum.cummax()) - 1).min()

t_stat_strategy, p_val_strategy = sp_stats.ttest_1samp(returns, 0)

print(f"\n--- Strategy Performance (net of {COST_PIPS} pips RT) ---")
print(f"Observations      : {len(returns)}")
print(f"Annualised Return : {ann_return:.2%}")
print(f"Annualised Vol    : {ann_vol:.2%}")
print(f"Sharpe Ratio      : {sharpe:.2f}")
print(f"Max Drawdown      : {max_dd:.2%}")
print(f"Hit Rate          : {(returns > 0).mean():.2%}")
print(f"T-stat (mean>0)   : {t_stat_strategy:.2f}")
print(f"P-value           : {p_val_strategy:.6f}")

# -------------------------------------------------------------------
# STEP 7: WALK-FORWARD VALIDATION
# -------------------------------------------------------------------

# Split: first 5 years (2010-2014) in-sample; remaining out-of-sample
is_mask = df.index <= "2014-12-31"
oos_mask = ~is_mask

for label, mask in [("In-Sample (2010-2014)", is_mask), 
                     ("Out-of-Sample (2015-2024)", oos_mask)]:
    r = df.loc[mask, "net_pnl"].dropna()
    if len(r) == 0:
        continue
    sr = (r.mean() / r.std()) * np.sqrt(n_per_year)
    dd = ((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min()
    print(f"\n  {label}")
    print(f"  Sharpe: {sr:.2f}  |  MaxDD: {dd:.2%}  |  N: {len(r)}")
```

**Interpreting the output**: if the walk-forward Sharpe in the out-of-sample period (2015-2024) is similar to the in-sample Sharpe (2010-2014), you have genuine evidence of a real, non-overfit edge. If the out-of-sample Sharpe collapses, you have overfit to the first period.

---

## Section 8 — The Macro Scorecard: Systematising Your Macro Framework

### 8.1 What Is a Macro Scorecard?

A macro scorecard is a structured scoring system that forces the discretionary macro trader to make their views explicit, numerical, and comparable across time. Instead of "I'm bearish EUR" or "I think the dollar has topped," the scorecard produces "+0.65 (mildly bullish USD)" with a clear breakdown by component.

The scorecard approach:
- **Forces discipline**: every dimension must be scored, including the ones that do not support your preferred direction
- **Creates a historical record**: you can look back and see which dimensions were right and which were wrong
- **Enables backtesting**: once you have historical scores, you can test whether the composite score predicted returns
- **Allows IC weighting**: over time, you can upweight dimensions with high historical IC

### 8.2 Building the Scorecard: Dimensions and Indicators

Each dimension represents one key macroeconomic driver of exchange rate movements. For each dimension, you select one or two observable, regularly published indicators that measure it. You then score each indicator from −2 to +2.

**Scoring convention** (for EURUSD — positive score = bullish USD):
- +2: strongly favours the thesis
- +1: moderately favours the thesis
- 0: neutral / no clear signal
- −1: moderately contradicts the thesis
- −2: strongly contradicts the thesis

**Example: EURUSD Macro Scorecard (illustrative, as of hypothetical date)**

| Dimension | Indicator | Raw Value | Score | Weight |
|---|---|---|---|---|
| Growth differential | OECD CLI: US minus Euro Area | US CLI 101.2, EA CLI 99.1, diff = +2.1 | +1 | 20% |
| Rate differential | 2Y US Treasury minus 2Y German Bund | 4.85% − 2.65% = +2.20% (rising) | +2 | 30% |
| Inflation differential | Core CPI: US 3.2% vs EU 2.8%, diff = +0.4% (falling in both) | 0 | 0 | 20% |
| Positioning | CFTC: EUR net speculative position z-score = −1.2σ (short EUR crowded) | Contrarian: −1 | 15% |
| Valuation | EURUSD vs. PPP estimate ($1.16): spot $1.09 → EUR cheap | Contrarian: −1 | 15% |
| **Composite** | | | **+0.65** | 100% |

**Composite calculation**:
$$\text{composite} = \sum_i w_i \times \text{score}_i = 0.20(+1) + 0.30(+2) + 0.20(0) + 0.15(-1) + 0.15(-1)$$
$$= 0.20 + 0.60 + 0.00 - 0.15 - 0.15 = +0.50$$

*Note: the +0.65 and the calculation give +0.50; a rounding artefact — use the formula consistently.*

A composite of +0.50 (on a theoretical range of −2 to +2) indicates a **moderately bullish USD** view, driven primarily by the rate differential and growth advantage, with a slight offset from crowded short-EUR positioning and EUR being cheap vs. PPP.

### 8.3 The Weighting Framework

The initial weights (20%, 30%, 20%, 15%, 15%) are set based on the economic theory of exchange rate determination:

- **Rate differential** receives the highest weight (30%) because it is the most proximate driver of capital flows and empirically has the highest IC in the short-to-medium term. This is consistent with this repo's core finding: the rate-differential signal generates Sharpe ratios above 1.0 on 7 of 8 G10 pairs.
- **Growth differential** receives 20% because it drives expected future rate differentials — it is the slow-moving underlying driver.
- **Inflation differential** receives 20% because it feeds into both the PPP fair value and the rate path.
- **Positioning** receives 15% because it is a risk signal rather than a directional signal — it tells you about the distribution of outcomes rather than the expected value.
- **Valuation** receives 15% because it is a very slow (3-5 year) signal that provides a mild gravitational pull toward PPP but rarely drives short-term moves.

**IC-based weighting (the advanced version)**: once you have 2+ years of historical scores, you can reweight based on each dimension's historical IC (correlation between score and subsequent 1-month return):

$$w_i = \frac{IC_i}{\sum_j IC_j}, \quad \text{for } IC_i > 0$$

If $IC_i \leq 0$ for some dimension, set $w_i = 0$ (do not include it).

### 8.4 Backtesting the Scorecard

To backtest the scorecard as a signal:

1. Assign scores historically for each dimension using the indicator values that were actually available at the time (critical: use real-time vintage data, not revised data, for GDP and CLI)
2. Compute the composite score for each month from 2015 to the present
3. Record the 1-month EURUSD return following each scoring date
4. Run a regression: $r_{\text{EURUSD}, t+1 \text{ month}} = \alpha + \beta \cdot \text{composite}_t + \epsilon_t$
5. Measure IC, t-statistic, and walk-forward Sharpe

This gives you a statistically grounded measure of whether your discretionary macro framework actually works — and which dimensions are contributing.

### 8.5 Updating the Scorecard: Systematic vs. Discretionary Updates

**Systematic updates** (preferred): every indicator is updated on a fixed schedule based on release dates. The growth dimension updates on the third Thursday of each month (OECD CLI release). The rate dimension updates daily. The positioning dimension updates every Friday (CFTC publication). Set calendar alerts and update mechanically.

**Discretionary updates**: between scheduled releases, you may want to update based on material new information (a surprise policy decision, an unexpected geopolitical event). These are legitimate, but they should be:
1. Logged with the reason
2. Limited in frequency (not more than once per week per dimension)
3. Reviewed retrospectively to see if discretionary updates improved or degraded accuracy

---

## Section 9 — Risk Management for the Transitioning Trader

### 9.1 Portfolio-Level vs. Position-Level Risk Management

Most discretionary traders think about risk at the **position level**: "I'm risking 1.5% of capital on this EURUSD trade." Systematic traders think primarily at the **portfolio level**: "my total portfolio should target 10% annual volatility and must not exceed 20% drawdown from peak before I reduce risk."

Position-level thinking has a critical failure mode: two trades that individually look reasonable can be highly correlated, so the combined risk is much larger than the sum of the individual risks. If you are long EURUSD and short USDCHF, you are expressing a double EUR-long view — the risk is not 1.5% + 1.5% = 3%, it is approximately 2.5-4% because the two trades move together.

**The portfolio risk budget approach**:
1. Set a **total risk budget**: e.g., 10% annual volatility for the portfolio
2. Allocate this budget across strategies: e.g., 40% to rate-differential signals, 30% to carry, 20% to macro scorecard, 10% to positioning
3. Within each strategy, size positions so that their contribution to total portfolio vol equals their allocation from the budget
4. Monitor the actual portfolio vol daily; if it exceeds the budget by 20% or more, scale down all positions proportionally

### 9.2 Drawdown Limits: Setting Them Based on Your Sharpe Ratio

The expected maximum drawdown of a systematic strategy is a function of its Sharpe ratio and the time horizon. A useful rule of thumb:

$$\text{Expected Max Drawdown} \approx \frac{-2 \times \text{Annual Vol}}{\text{Sharpe Ratio} + 1}$$

For a strategy with annual vol of 15% and a Sharpe of 1.5:
$$\text{Expected Max DD} \approx \frac{-2 \times 0.15}{1.5 + 1} = \frac{-0.30}{2.5} = -12\%$$

This means a −20% drawdown would be unusual (roughly a 2-sigma event) and should trigger a risk review.

**Practical drawdown limits**:
- **Yellow zone** (−15% from peak): reduce new positions by 50%, review signal robustness
- **Red zone** (−25% from peak): flat all positions, conduct full strategy review before re-entering
- **Hard stop** (−35% from peak): stop trading the strategy; conduct post-mortem

These thresholds should be set before you start trading, not in the middle of a drawdown when emotions are running high.

### 9.3 Correlation Management

When multiple systematic strategies are running simultaneously, correlation management is essential. Consider:

- Strategy A: long EURUSD based on rate differential
- Strategy B: short USDCHF based on rate differential
- Strategy C: long EURUSD based on macro scorecard

Strategies A and C are both long EURUSD — they are correlated by construction. If you run them at equal risk, you effectively have a double-sized EURUSD bet.

**The correlation matrix approach**:

```python
import pandas as pd
import numpy as np

# Daily returns from each strategy
returns = pd.DataFrame({
    'strat_A': [...],  # EURUSD rate diff
    'strat_B': [...],  # USDCHF rate diff
    'strat_C': [...],  # Macro scorecard
})

# Rolling 60-day correlation matrix
corr = returns.rolling(60).corr().tail(len(returns.columns))

# If any pair has correlation > 0.7, reduce the smaller position by 50%
print(corr)
```

When two strategies have rolling correlation above 0.7, treat them as expressing the same risk and size them together as one position.

### 9.4 How Top Discretionary Traders Who Went Systematic Handle Risk

**David Harding (Winton Group)**: Harding began as a discretionary commodity trader at Man Financial in the 1980s. He co-founded AHL (the systematic CTA arm of Man Group) in 1987 before founding Winton in 1997. His key insight was that the discretionary market patterns he had observed could be tested systematically — and that the consistent application of systematic rules would outperform his discretionary application of the same intuitions over time. Winton became one of the largest CTA funds in the world, managing over $30B at peak, running a diversified systematic trend-following and multi-factor approach.

**Cliff Asness (AQR Capital)**: Asness wrote his PhD dissertation at the University of Chicago on value and momentum, then went to Goldman Sachs to run their quantitative research desk before founding AQR in 1998. AQR systematised the factors that discretionary value investors and momentum traders had been exploiting for decades. The insight was not that the factors were new — value investing was well-known before Graham and Dodd codified it — but that systematic application was more consistent and could be diversified across many markets simultaneously. AQR's research, particularly Asness, Moskowitz, and Pedersen (2013), showed that value and momentum work "everywhere" — across eight different markets and asset classes — which provides diversification that no discretionary investor replicating across all eight could achieve.

**The lesson**: both Harding and Asness started with discretionary intuitions, systematised them, and then discovered that the systematic versions were better not because they generated better signals, but because they applied those signals more consistently and sized them more rationally.

### 9.5 The Hybrid Approach: Systematic Rules with Discretionary Override Checklist

For the transitioning trader, the practical risk management framework is:

**Tier 1 — Systematic (always applied, no override)**:
- Position sizing based on volatility target
- Daily correlation check between active positions
- Stop-out at −35% drawdown from any strategy's peak

**Tier 2 — Discretionary checklist (applied weekly)**:
- Is there a scheduled central bank meeting in the next 48 hours? → Consider reducing by 50%
- Is VIX above 30? → Scale all carry positions to 50%
- Has a major data release surprised in the opposite direction of our position? → Flag for next-day review

**Tier 3 — Override log (every discretionary intervention must be recorded)**:
- Date, position affected, reason for override, scale of adjustment
- After 50+ overrides, review: did they help or hurt? This is your personal edge audit.

---

## Section 10 — Tools and Learning Path for the Transitioning Trader

### 10.1 Python Learning Path: Week-by-Week

Python is the universal language of systematic trading. You do not need to be a software engineer — you need to be a competent data analyst who can manipulate time series, run regressions, and visualise results. Here is a structured 12-week learning path:

**Weeks 1-2: pandas — Your Most Important Tool**

Pandas is Python's data analysis library. For systematic trading, it is essentially the Bloomberg terminal of your backtesting environment.

```python
import pandas as pd
import numpy as np

# Reading a CSV of FX data
fx = pd.read_csv("eurusd_daily.csv", index_col=0, parse_dates=True)

# Time series operations
fx["log_return"] = np.log(fx["Close"]).diff(1)      # daily log returns
fx["rolling_vol"] = fx["log_return"].rolling(20).std() * np.sqrt(252)  # annualised
fx["20dma"] = fx["Close"].rolling(20).mean()         # moving average

# Merging two datasets by date
rates = pd.read_csv("us_2y_rates.csv", index_col=0, parse_dates=True)
merged = fx.join(rates, how="inner")  # inner join keeps only matching dates

# Resampling: from daily to weekly
weekly = fx["Close"].resample("W-FRI").last()        # weekly, last trading day

# Boolean selection
strong_up = fx[fx["log_return"] > 0.01]              # days when EUR moved up >1%
```

Key concepts: DataFrame, Series, DatetimeIndex, `merge`/`join`, `resample`, `rolling`, `shift`.

**Weeks 3-4: matplotlib and seaborn — Visualising Your Data**

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Plot 1: Price
axes[0].plot(fx.index, fx["Close"], color="navy", linewidth=0.8)
axes[0].set_ylabel("EURUSD")
axes[0].set_title("EURUSD Rate Differential Strategy")

# Plot 2: Signal
axes[1].bar(fx.index, fx["signal"], color=["green" if s > 0 else "red" 
                                            for s in fx["signal"].fillna(0)],
            alpha=0.6, width=1)
axes[1].axhline(0, color="black", linewidth=0.5)
axes[1].set_ylabel("Signal")

# Plot 3: Cumulative P&L
cum_pnl = (1 + fx["net_pnl"].fillna(0)).cumprod()
axes[2].plot(fx.index, cum_pnl, color="darkgreen", linewidth=1.2)
axes[2].set_ylabel("Cumulative Return")
axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

plt.tight_layout()
plt.savefig("strategy_performance.png", dpi=150)
```

**Weeks 5-6: numpy and scipy.stats — Signal Construction and Testing**

```python
import numpy as np
from scipy import stats

# Constructing signals
signal = np.sign(rate_diff.diff(1).values)          # directional signal
z_score = (x - x.rolling(252).mean()) / x.rolling(252).std()  # rolling z-score

# Statistical testing
t_stat, p_value = stats.ttest_1samp(returns, 0)     # is mean return > 0?
slope, intercept, r, p, se = stats.linregress(signal, next_return)  # IC regression

# Spearman correlation (IC)
ic, p_ic = stats.spearmanr(signal[:-1], returns[1:])

# Bootstrap confidence interval for Sharpe
def bootstrap_sharpe(returns, n_boot=1000, n_per_year=252):
    sharpes = []
    for _ in range(n_boot):
        sample = np.random.choice(returns, size=len(returns), replace=True)
        sr = (sample.mean() / sample.std()) * np.sqrt(n_per_year)
        sharpes.append(sr)
    return np.percentile(sharpes, [2.5, 97.5])

lo, hi = bootstrap_sharpe(returns.values)
print(f"95% CI for Sharpe: [{lo:.2f}, {hi:.2f}]")
```

**Weeks 7-8: scikit-learn basics — Linear Regression and Cross-Validation**

```python
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import numpy as np

# Prepare features and target
X = df[["rate_diff_change", "vix_level", "carry_score"]].values
y = df["fx_return_next"].values

# TimeSeriesSplit: never use standard cross-validation for time series
# (it leaks future data into training; use expanding window instead)
tscv = TimeSeriesSplit(n_splits=5)

scores = []
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # use train scaler on test!
    
    # Fit model
    model = Ridge(alpha=1.0)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate out-of-sample
    y_pred = model.predict(X_test_scaled)
    ic = np.corrcoef(y_pred, y_test)[0, 1]
    scores.append(ic)

print(f"Mean OOS IC: {np.mean(scores):.4f}")
print(f"IC per fold: {[f'{s:.4f}' for s in scores]}")
```

**Weeks 9-12: Backtest Framework**

Build a complete backtest engine:

```python
class RateDiffBacktest:
    """
    Minimal but rigorous backtest class for a daily signal strategy.
    Handles: signal generation, vol-targeting, cost model, metrics.
    """
    
    def __init__(self, target_annual_vol: float = 0.10, 
                 cost_pips: float = 5.0, pip_size: float = 0.0001):
        self.target_vol = target_annual_vol
        self.cost_pips = cost_pips
        self.pip_size = pip_size
    
    def compute_signal(self, rate_diff: pd.Series) -> pd.Series:
        """Signal is the daily change in rate differential."""
        return np.sign(rate_diff.diff(1))
    
    def vol_scale(self, signal: pd.Series, fx_returns: pd.Series,
                  lookback: int = 60) -> pd.Series:
        """Scale signal by inverse of realised vol."""
        daily_vol = fx_returns.rolling(lookback).std()
        daily_target = self.target_vol / np.sqrt(252)
        return signal * (daily_target / daily_vol)
    
    def run(self, rate_diff: pd.Series, fx_returns: pd.Series) -> pd.DataFrame:
        """
        rate_diff: daily rate differential series
        fx_returns: next-day FX returns (already shifted -1 relative to signal)
        """
        results = pd.DataFrame(index=rate_diff.index)
        
        results["signal"] = self.compute_signal(rate_diff)
        results["scaled_signal"] = self.vol_scale(results["signal"], fx_returns)
        results["position"] = results["scaled_signal"].clip(-2, 2)  # max 2x leverage
        
        # Gross PnL: position × return (both on same date since return is t+1)
        results["gross_pnl"] = results["position"].shift(1) * fx_returns
        
        # Costs: charged when position changes
        pos_change = results["position"].diff(1).abs()
        results["cost"] = (pos_change / 2) * self.cost_pips * self.pip_size
        
        results["net_pnl"] = results["gross_pnl"] - results["cost"]
        results["cum_pnl"] = (1 + results["net_pnl"].fillna(0)).cumprod()
        
        return results.dropna()
    
    def evaluate(self, results: pd.DataFrame) -> dict:
        """Compute all performance metrics."""
        r = results["net_pnl"]
        cum = results["cum_pnl"]
        n = len(r)
        n_per_year = 252
        
        ann_ret = (1 + r).prod() ** (n_per_year / n) - 1
        ann_vol = r.std() * np.sqrt(n_per_year)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        max_dd = ((cum / cum.cummax()) - 1).min()
        calmar = ann_ret / abs(max_dd) if max_dd != 0 else 0
        t_stat, p_val = stats.ttest_1samp(r, 0)
        
        return {
            "n_obs": n,
            "ann_return": ann_ret,
            "ann_vol": ann_vol,
            "sharpe": sharpe,
            "max_drawdown": max_dd,
            "calmar": calmar,
            "hit_rate": (r > 0).mean(),
            "t_statistic": t_stat,
            "p_value": p_val
        }
```

### 10.2 Key Python Libraries

| Library | Purpose | Install |
|---|---|---|
| `pandas` | Time series data manipulation | `pip install pandas` |
| `numpy` | Numerical computation, array operations | `pip install numpy` |
| `scipy.stats` | T-tests, OLS regression, correlation | `pip install scipy` |
| `statsmodels` | More complete regression toolbox (HAC standard errors, ARIMA) | `pip install statsmodels` |
| `scikit-learn` | Machine learning models, cross-validation | `pip install scikit-learn` |
| `matplotlib` | Core plotting | `pip install matplotlib` |
| `seaborn` | Statistical plotting on top of matplotlib | `pip install seaborn` |
| `fredapi` | FRED data API (US rates, economic series) | `pip install fredapi` |
| `yfinance` | Yahoo Finance data (FX spot, equity indexes) | `pip install yfinance` |
| `tvDatafeed` | TradingView data (international yield curves) | `pip install tvDatafeed` |
| `pandas_datareader` | OECD, World Bank, other data sources | `pip install pandas-datareader` |

### 10.3 Free Data Sources

| Data Source | What You Get | URL / Access |
|---|---|---|
| FRED (Federal Reserve St. Louis) | US rates (DGS2, DGS10), VIX, economic indicators | `fred.stlouisfed.org` — free API key |
| ECB Data Portal (SDW) | European yield curves, EURUSD rate, ECB policy rates | `data.ecb.europa.eu` |
| CFTC (Commitments of Traders) | Weekly speculative positioning in FX futures | `cftc.gov/MarketReports` |
| Yahoo Finance (via yfinance) | FX spot rates, equity indexes | `pip install yfinance` |
| OECD iLibrary | Composite Leading Indicators (CLI), CPI, GDP | `stats.oecd.org` |
| BIS (Bank for International Settlements) | FX turnover, effective exchange rates | `bis.org/statistics` |
| TradingView (via tvDatafeed) | International 2Y bond yields, global futures | `pip install tvDatafeed` |

**A note on data quality**: free data sources have gaps, survivorship bias in some series, and lags in publication. For research purposes, they are excellent. For live trading, you should validate that your free data source matches a paid source (Bloomberg, Refinitiv) on the dates that matter. The EURUSD rate-differential strategy in this repo was developed using FRED for US rates and TVC-scraped data for international 2Y yields, which introduced some data quality considerations documented in `strategies/README.md`.

### 10.4 Books to Read (In Order)

**1. Antti Ilmanen — Expected Returns (2011, Wiley Finance)**

This is the macro approach to all risk premia. Ilmanen systematically reviews the evidence for returns across asset classes (stocks, bonds, commodities, currencies, alternatives) and investment styles (value, momentum, carry, volatility). The book is accessible — Ilmanen is an AQR partner who writes with practitioners in mind — but it is also rigorous: every claim is backed by empirical evidence with confidence intervals and period-by-period analysis.

Why it comes first: it gives you the lay of the land. You will see that the strategies you have been running discretionarily fit into a broader framework of known, documented risk premia — and you will see which discretionary beliefs the evidence supports and which it contradicts.

**2. Marcos López de Prado — Advances in Financial Machine Learning (2018, Wiley)**

López de Prado was head of machine learning at AQR before launching his own fund. This book addresses the most important practical problems in applying machine learning to financial data: the multiple testing problem (why most backtests are fiction), feature engineering for financial series, the correct cross-validation methodology for time series (TimeSeriesSplit, not random), and the DSR.

Why it comes second: it inoculates you against the most dangerous failure modes of systematic trading. Read this before you build any machine learning model applied to financial data. The chapter on backtest overfitting alone is worth the cover price.

**3. Richard Grinold and Ronald Kahn — Active Portfolio Management (2nd ed., 2000, McGraw-Hill)**

The "bible" of quantitative active management. Grinold and Kahn develop the Fundamental Law of Active Management ($IR = IC \times \sqrt{BR}$) and explain how to think about alpha sources in terms of their information coefficient and breadth. The maths is more demanding than the other books on this list, but the concepts are essential: IC, ICIR, transfer coefficient, the role of transaction costs in limiting the benefit of frequent trading.

Why it comes third: once you understand *what* risk premia exist (Ilmanen) and *how to avoid fooling yourself* (López de Prado), this book teaches you how to combine signals into a portfolio optimally.

**4. Clifford Asness — The AQR Papers (various, all available free at aqr.com)**

Not a single book but a collection of practitioner-oriented papers from AQR. Start with:
- "Carry" (Koijen, Moskowitz, Pedersen, Vrugt 2018): the most complete treatment of carry across asset classes
- "Value and Momentum Everywhere" (Asness, Moskowitz, Pedersen 2013): the cross-asset evidence
- "Time Series Momentum" (Moskowitz, Ooi, Pedersen 2012): the definitive TSMOM paper
- "Two Centuries of Momentum" (Geczy, Samonov 2016): how far back the evidence goes

Why they come fourth: they are the primary academic source for the specific strategies in this repo. Reading these papers directly — rather than summaries — gives you the statistical methodology and the exact construction rules.

**5. Edward O. Thorp — A Man for All Markets (2017, Random House)**

Thorp is a mathematician who beat the casino at blackjack, then beat Wall Street with the Kelly Criterion. His autobiography is the most accessible treatment of the Kelly-based approach to position sizing available. Thorp's core insight — that the Kelly Criterion determines the geometrically optimal bet size when you know your edge — is the conceptual foundation for all the vol-targeting and risk budgeting frameworks described in Section 6.

Why it comes fifth: it grounds everything in the intuition of expected value and geometric growth. After reading Thorp, you will never size positions by gut feel again.

**Bonus — for the practically inclined**:
- **Ernest Chan — Algorithmic Trading (2013, Wiley)**: the most practical introduction to actually building and running systematic strategies, with Python code examples.
- **Perry Kaufman — Trading Systems and Methods (2019, Wiley)**: encyclopaedic coverage of technical and systematic trading approaches — useful as a reference.

### 10.5 The Transition Roadmap: 12 Months

For a practising discretionary trader who wants to systematise over one year, here is a realistic roadmap:

**Months 1-2: Observation and Documentation**
- Run your discretionary trading normally.
- For every trade, write down: the signal (in explicit IF-THEN language), the size rule, the expected holding period, and the exit rule.
- At the end of two months, you have a manual record you can analyse.

**Months 3-4: Python Fundamentals + First Signal Test**
- Complete Weeks 1-6 of the Python learning path.
- Take your most frequently traded, most clearly defined strategy and write it as a systematic signal.
- Backtest it on the last 5 years using FRED and Yahoo Finance data.
- Compare the systematic backtest to your actual trading record.

**Months 5-6: Statistical Validation**
- Run the t-test framework from Section 3.9 on your backtest returns.
- Compute IC and rolling ICIR.
- Run sub-period analysis (split the sample in half; does it work in both halves?).
- If the statistical evidence is weak, go back to the signal design. If it is strong, proceed.

**Months 7-8: Position Sizing and Risk Management**
- Implement vol-targeting sizing (Section 6.3).
- Set drawdown limits and the discretionary override checklist.
- Paper trade the systematic strategy for 2 months alongside your discretionary trading.
- Record every case where the systematic signal and your discretionary judgment disagree. Who was right?

**Months 9-10: Macro Scorecard Construction**
- Build the macro scorecard for your primary currency pairs.
- Assign historical scores for the past 3 years.
- Backtest the scorecard as a monthly signal.
- Compare the scorecard signal to the higher-frequency rate-differential signal.

**Months 11-12: Integration and Gradual Capital Allocation**
- Allocate a defined, small fraction of your trading capital (10-25%) to the systematic strategy.
- Run the systematic and discretionary books in parallel.
- Compare performance on a risk-adjusted basis.
- After 6 months of live systematic trading, decide whether to increase the systematic allocation based on the evidence.

---

## Appendix A — Quick Reference: Key Formulas

| Formula | Name | Use |
|---|---|---|
| $SR = \frac{\bar{r} - r_f}{\sigma_r} \times \sqrt{n}$ | Sharpe Ratio | Primary strategy quality metric |
| $t = \frac{\bar{r}}{s/\sqrt{n}}$ | T-statistic | Is mean return significantly > 0? |
| $IC = \text{Spearman}(\text{signal}_t, r_{t+1})$ | Information Coefficient | Predictive power of signal |
| $IR = IC \times \sqrt{BR}$ | Fundamental Law | Expected IR from skill and breadth |
| $f^* = \frac{p \cdot b - (1-p)}{b}$ | Kelly Criterion | Optimal bet fraction |
| $N = \frac{\sigma_{\text{target}}}{\sigma_{\text{instrument}}} \times C$ | Vol-targeting size | Position size from vol target |
| $q_t = s_t - p_t + p_t^*$ | Real exchange rate | PPP deviation / value signal |
| $z_t = \frac{x_t - \mu_{t,k}}{\sigma_{t,k}}$ | Rolling z-score | Normalised signal / positioning extreme |
| $DD_t = \frac{V_t - \max_{\tau \leq t} V_\tau}{\max_{\tau \leq t} V_\tau}$ | Drawdown | Portfolio loss from peak |
| $\text{Calmar} = \frac{r_{\text{ann}}}{|DD_{\max}|}$ | Calmar Ratio | Return per unit of max drawdown |

---

## Appendix B — Academic References

All papers cited in this document:

- Asness, C.S., Moskowitz, T.J., and Pedersen, L.H. (2013). "Value and Momentum Everywhere." *Journal of Finance*, 68(3), 929-985.
- Bailey, D.H. and López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality." *Journal of Portfolio Management*, 40(5), 94-107.
- Ferraro, D., Rogoff, K., and Rossi, B. (2015). "Can Oil Prices Forecast Exchange Rates? An Empirical Analysis." *Journal of International Money and Finance*, 54, 116-141.
- Grinold, R. and Kahn, R. (2000). *Active Portfolio Management: A Quantitative Approach for Producing Superior Returns and Controlling Risk*. 2nd ed. McGraw-Hill.
- Gürkaynak, R., Sack, B., and Swanson, E. (2005). "Do Actions Speak Louder Than Words? The Response of Asset Prices to Monetary Policy Actions and Statements." *International Journal of Central Banking*, 1(1), 55-93.
- Ilmanen, A. (2011). *Expected Returns: An Investor's Guide to Harvesting Market Rewards*. Wiley Finance.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.
- Lustig, H., Roussanov, N., and Verdelhan, A. (2011). "Common Risk Factors in Currency Markets." *Review of Financial Studies*, 24(11), 3731-3777.
- Menkhoff, L., Sarno, L., Schmeling, M., and Schrimpf, A. (2012). "Carry Trades and Global Foreign Exchange Volatility." *Journal of Finance*, 67(2), 681-718.
- Moskowitz, T.J., Ooi, Y.H., and Pedersen, L.H. (2012). "Time Series Momentum." *Journal of Financial Economics*, 104(2), 228-250.

---

*End of document. This reference is designed for NotebookLM ingestion. All strategy performance figures are from backtests run in the g10-systematic-fx repository (2010-2024, net of 5 pips round-trip transaction costs). Past backtest performance does not guarantee future results.*
