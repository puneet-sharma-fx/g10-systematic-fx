# Medium Frequency Trading (MFT): A Comprehensive Reference for the Systematic Macro Practitioner

*A complete learning resource for experienced discretionary macro traders transitioning to or studying systematic MFT strategies. Holding periods: 1–20 trading days. Prepared for NotebookLM ingestion. All mathematics derived from first principles. All code examples in Python.*

*Last updated: June 2026*

---

## Table of Contents

1. [The MFT Landscape — What It Is and Who Does It](#section-1)
2. [Signal Types That Work at MFT Frequency](#section-2)
3. [Statistical Arbitrage — The Core MFT Methodology](#section-3)
4. [Event-Driven MFT Strategies](#section-4)
5. [Momentum at MFT Frequency — The Evidence](#section-5)
6. [Risk Management at MFT Frequency](#section-6)
7. [How Top MFT Funds Actually Work](#section-7)
8. [Building an MFT Strategy for FX and Macro](#section-8)
9. [MFT vs. Other Strategy Types — Comparative Analysis](#section-9)
10. [Practical Roadmap: From Discretionary Macro to MFT](#section-10)

---

<a name="section-1"></a>
## Section 1: The MFT Landscape — What It Is and Who Does It

### 1.1 Frequency Taxonomy: The Three Regimes

The investment management industry divides systematic strategies by holding period, because the alpha source, infrastructure, competitive dynamics, and risk management requirements differ fundamentally across frequency bands. There are three regimes:

| Regime | Typical Holding Period | Signal Sources | Infrastructure |
|---|---|---|---|
| **High Frequency Trading (HFT)** | Microseconds to minutes | Order flow, latency, microstructure | Co-location, FPGA, nanosecond latency |
| **Medium Frequency Trading (MFT)** | 1–20 trading days | Price, macro, events, positioning | Standard API, end-of-day data |
| **Low-Frequency Systematic** | Weekly to quarterly | Factor tilts, valuations, macro trends | Standard execution, monthly rebalancing |

The boundaries are not sharp. A strategy holding for 3–5 days blends elements of MFT. A strategy holding for 20–30 days blends into what some practitioners call "medium-to-low frequency." The definitions above represent the core of each category.

**Why taxonomy matters:** A discretionary macro trader thinking about systematising their process almost always belongs in MFT. The signals you use — rate differentials, central bank surprises, macro data, positioning — have half-lives measured in days to weeks, not hours and not months. This places you squarely in the MFT regime.

### 1.2 Why HFT Is a Different Business

High frequency trading is not systematic macro trading with better technology. It is a distinct business model built around:

- **Market-making**: providing liquidity and earning the spread, with inventory risk managed by ultra-fast hedging. A market-maker at Citadel Securities or Virtu holds positions for milliseconds.
- **Latency arbitrage**: exploiting the time differential between when a price update arrives at two different venues. The edge is pure technology — the fastest firm wins.
- **Statistical microstructure patterns**: order flow imbalance, queue position, rebate arbitrage.

None of these require fundamental views about economies or central bank policies. The economic moat is co-location fees, proprietary fibre connections, FPGA chips, and the ability to attract order flow. The barriers to entry are capital-intensive in a very different way than MFT.

HFT capacity is also extremely limited — typically tens to hundreds of millions of dollars per strategy before market impact destroys the edge. The largest HFT firms manage their edge by operating across hundreds of strategies simultaneously.

**Key distinction for the discretionary trader:** If your edge comes from understanding economic fundamentals, interpreting central bank communication, reading positioning data, or identifying mispriced macro relationships, HFT has nothing to offer you. Your edge operates at a different frequency.

### 1.3 Why Low-Frequency Systematic Is Also Distinct

Low-frequency systematic strategies — factor investing, monthly carry rotation, quarterly value rebalancing — have a different problem: the signals are public knowledge, broadly implemented, and competitively crowded.

A classic AQR-style factor portfolio rebalances once a month. The carry trade idea, the value-in-FX idea, the 12-month momentum idea — these have been published, replicated, and implemented by hundreds of asset managers. After fees, the evidence suggests net Sharpe ratios of 0.3–0.7 for individual factors (Asness et al., 2013 JF), with diversified factor portfolios reaching 0.7–1.0.

The crowding dynamic in low-frequency systematic is extreme. When a factor goes wrong — as momentum did in 2009 and as low-volatility did during the 2022 rate shock — the correlation among low-frequency players spikes because they all hold the same positions. The liquidation cascade becomes the dominant return driver.

**MFT avoids this problem (partially):** By operating at 1–20 day holding periods, MFT strategies tap signals that decay before slow-money managers can react. The competitive set is smaller and the diversification benefit across instruments × signals × time is larger.

### 1.4 Why MFT Has Become the Dominant Institutional Alpha Frequency

The multi-strategy pod-based hedge fund model — epitomised by Millennium, Citadel, and Balyasny — has converged on MFT as the dominant frequency for two structural reasons:

**1. Statistical power through breadth.** Grinold and Kahn (2000) showed that the information ratio of a strategy grows as:

$$IR = IC \times \sqrt{BR}$$

where IC is the information coefficient (correlation between forecast and realised return) and BR is the number of independent bets per year. At MFT frequency with 20 instruments and daily signals, you generate approximately 252 × 20 = 5,040 bets per year. Even with a modest IC of 0.05, this produces an IR of:

$$IR = 0.05 \times \sqrt{5{,}040} \approx 3.5$$

(In practice, the bets are correlated, and IC varies, so actual IRs are 1.0–2.5, but the point about breadth is directionally correct and is why multi-instrument MFT dominates.)

**2. Implementation feasibility.** HFT requires co-location infrastructure that costs $1–10M per venue and continuous engineering attention. Low-frequency systematic requires enormous capital ($1B+) to meaningfully justify the infrastructure. MFT — daily signals, standard API execution, end-of-day data — is implementable by a team of 3–5 researchers with a standard Bloomberg or FRED data subscription and Python backtesting infrastructure.

### 1.5 The Major MFT Institutions

**Millennium Management (Izzy Englander)**

Founded 1989, Millennium is the archetypal multi-strategy pod-based MFT fund. As of 2025, the firm manages approximately $70B AUM across 330+ independent pods. Each pod is an autonomous P&L centre — a Portfolio Manager plus 2–8 analysts and risk specialists. The PM owns the strategy, the risk limits, and the returns.

Key facts:
- Typical pod strategy: long-short equity statistical arbitrage, sector-neutral, 5–20 day holding periods
- Signal types: earnings revision momentum, price momentum (5–60 days), valuation/quality ratios, catalyst-driven (earnings, guidance, index changes)
- Pod risk management: 5% drawdown from peak → 50% capital reduction. 7.5% → termination.
- Firm-level Sharpe: approximately 2.5 since inception (as reported by third-party analysts); 15% return in 2024 (best since 2020).
- Cross-pod risk management: central risk team strips factor exposures that aggregate across pods, ensuring no single macro factor dominates firm-wide P&L.

**Citadel (Ken Griffin)**

Multi-strategy with embedded MFT across asset classes:
- Global Fixed Income & Macro: rates relative value (swap spreads, cross-country yield curve trades, CIP deviations) at 5–20 day horizons. Applies quantitative modeling to macroeconomic fundamental views.
- Global Equities (Citadel): sector-neutral long-short equity, quantamental blend of fundamental research and systematic signals.
- FX strategy: systematic carry combined with event-driven overlays around central bank meetings.
- Scale: $65B AUM; Citadel's flagship Wellington fund has returned approximately 19.6% net since inception.

**Balyasny Asset Management (Dmitry Balyasny)**

- $29B AUM as of late 2025, approximately 125 pods.
- Emphasis on "quantamental": fundamental research that flows into systematic execution rules.
- Holding periods: 5–30 days for equity pods; 1–10 days for macro pods.
- Strong 2025: +16.7% return, driven by equity volatility, AI-related themes, and disciplined pod-level capital allocation.
- Key insight from Dmitry Balyasny: holding period is not fixed — in low-volatility 2024, pods held longer; in high-volatility 2025, pods traded more actively.

**Two Sigma (John Overdeck, David Siegel)**

- Purely algorithmic; no human discretion in execution.
- Flagship Spectrum fund: approximately $5.8B AUM. Returned 10.9% in 2024, 14.3% in Absolute Return Enhanced.
- Typical holding periods: 1–7 days across equities, futures, FX.
- Signal types: ML on alternative data (satellite imagery, credit card transaction data, NLP on news and earnings calls) combined with price signals.
- Risk: firm-wide factor model aggregates and manages all exposures centrally.

**D.E. Shaw**

- Systematic strategies across holding periods from seconds to years.
- Composite fund: the flagship runs MFT equity and macro signals at 1–20 day horizons blended with longer-term factor tilts.
- Known for early adoption of statistical arbitrage (1990s) and heavy investment in data science and ML infrastructure.

**Point72 Asset Management (Steve Cohen)**

- Blends discretionary equity L/S with systematic strategies.
- Systematic arm (Point72 Cubist Systematic Strategies): sector rotation and event-driven at MFT frequency.
- Significant earnings-related signals and macro-data-driven FX/rates overlays.

---

<a name="section-2"></a>
## Section 2: Signal Types That Work at MFT Frequency

The fundamental challenge at MFT frequency is signal decay. Every signal has a half-life — the horizon over which its predictive power decays to zero. At MFT, you are working with signals whose half-lives range from 1 to 20 days. Understanding why each signal decays is as important as understanding why it works.

### 2.1 Price-Based Signals (1–5 Day Holding Periods)

#### Short-Term Price Momentum (3–5 Days)

The canonical academic reference is Jegadeesh and Titman (1993, JF), which documented that US stocks with strong performance over the prior 3–12 months continue to outperform. However, their 1993 paper excluded the most recent one-month return because of short-term reversal. This exclusion is itself a signal.

**The decomposition:**
- 1-week to 1-month horizon: **reversal** effect dominates (price impact and market-making inventory rebalancing).
- 1–12 month horizon: **continuation** effect dominates (under-reaction to fundamental information).
- 12–36 month horizon: **reversal** again (over-reaction correction).

Gutierrez and Kelley (2008, JF) refined this further for weekly frequency. Their paper "The Long-Lasting Momentum in Weekly Returns" showed that while a brief reversal occurs in the first 1–2 weeks after ranking, a "long-lasting momentum" continuation follows, strong enough to produce a significant positive return over the full year. This has direct MFT implications: the 3–20 day holding period after a brief initial reversal may be the sweet spot for price-continuation signals.

**Mechanism:** The short-term reversal (days 1–5) is driven by market-maker inventory rebalancing after large one-directional order flow. Once inventory is balanced, the signal that caused the initial flow reasserts itself, driving continuation (days 5–20). This is the "tug of war" described by Lou, Polk, and Skouras (2019, JFE).

#### Gap-Following: Open-to-Close vs. Close-to-Open Returns

Lou, Polk, and Skouras (2019, "A Tug of War: Overnight Versus Intraday Expected Returns," JFE Vol. 134) provide one of the cleanest MFT-relevant empirical findings:

- The overnight return (close-to-open) and the intraday return (open-to-close) of the same stock are strongly negatively correlated in the short run.
- Strategies that profit in one period (overnight or intraday) tend to lose in the other.
- Reversal and momentum strategies earn profits entirely **overnight**, while the intraday component often reverses.

**Trading implication:** If you observe a large intraday move, the next overnight period may continue in the direction of that move. If you observe a large overnight gap-up at open, the intraday session may partially reverse it. This is exploitable at MFT frequency with simple rules:

```python
# Gap signal construction
# For each instrument on each day:
overnight_return = np.log(open_price / prev_close_price)
intraday_return = np.log(close_price / open_price)
total_return = overnight_return + intraday_return

# 5-day gap signal: sign of average overnight return
gap_signal = overnight_returns.rolling(5).mean().shift(1)
# Expected: positive correlation with next-day total return
```

#### Volume-Weighted Signals

Abnormal trading volume is a leading indicator of informed trading and subsequent price movement. The intuition: if a stock trades 3× its typical volume with a positive price direction, the price move is more likely to be informed (rather than a noise-driven liquidity event) and more likely to continue.

**Abnormal volume construction:**

$$AV_t = \frac{V_t}{\text{MA}_{20}(V)} - 1$$

where $V_t$ is today's volume and $\text{MA}_{20}(V)$ is its 20-day moving average. Signal: $AV_t \times \text{sign}(r_t)$ — abnormal volume times the sign of today's return predicts the next 3–5 day return.

#### Bid-Ask Spread Signals

Widening bid-ask spreads signal that market-makers are being adversely selected — they are facing informed traders and are widening the spread as compensation. A widening spread is therefore an indicator of an information event in progress. The position:

- If spread widens AND price moves up → buy signal (informed buying, price likely to continue).
- If spread narrows AND volume drops → reversion signal (noise-driven move, price likely to mean-revert).

This is more actionable in individual stocks than in G10 FX, where spreads are extremely tight and stable for most majors. In G10 FX, the spread signal is most useful around macro data releases when spreads temporarily widen.

### 2.2 Macro/Fundamental Signals (5–20 Day Holding Periods)

#### Rate Differential Change Signal

This is the core signal in this repository (see STRATEGIES.md). The mechanism:

**Theoretical foundation:** Uncovered Interest Rate Parity (UIP) states that the expected exchange rate change should equal the interest rate differential. Empirically, UIP fails in the short run (the "UIP puzzle" or "forward premium puzzle" documented by Fama 1984). The carry trade — borrowing low-rate currencies and investing in high-rate currencies — exploits this failure.

But the *change* in the rate differential is more informative at MFT frequency than the *level*:

$$\Delta\text{RateDiff}_t = (r_{US,t} - r_{EUR,t}) - (r_{US,t-1} - r_{EUR,t-1})$$

where $r_{US,t}$ is the US 2-year sovereign yield at day $t$. When this spread widens, USD is expected to strengthen against EUR at a 1–5 day horizon (repricing of carry expectation).

**Signal construction:**

```python
import pandas as pd
import numpy as np

def build_rate_diff_signal(us_2y: pd.Series, eur_2y: pd.Series) -> pd.Series:
    """
    Daily Δ(2Y spread) → next-day FX signal.
    Positive output = long USD, short EUR.
    """
    spread = us_2y - eur_2y                  # Level
    delta_spread = spread.diff(1)            # Daily change
    
    # Z-score over 60-day rolling window
    mu = delta_spread.rolling(60).mean()
    sigma = delta_spread.rolling(60).std()
    signal = (delta_spread - mu) / sigma
    
    return signal.shift(1)  # Use yesterday's signal for today's position
```

This signal has been the highest-tested performer in this repository across EURUSD, GBPUSD, and USDJPY.

#### Central Bank Communication Parsing

Central bank communication — FOMC minutes, ECB accounts, dot plot updates, press conference transcripts — contains information about the future path of policy rates. This information moves FX prices at the 1–10 day holding period.

**Quantitative approach:**

1. **Sentiment scoring:** Apply a financial NLP model (FinBERT, or a simpler bag-of-words approach) to central bank texts. Count "hawkish" vocabulary (tighten, normalise, robust, above target, concerned about inflation) vs. "dovish" vocabulary (accommodative, patience, gradual, below target, uncertainty).

2. **Revision signal:** Compute the change in the hawkishness score between the current communication and the prior one. A surprise hawkish shift predicts currency appreciation over the next 5–10 days.

3. **Dot plot update (Fed-specific):** The FOMC "dot plot" shows each member's projected policy rate path. When the median dot rises, this is a mechanically measurable hawkish surprise even before the press conference.

#### Macro Data Surprise Signals

The methodology follows Andersen, Bollerslev, Diebold, and Vega (2003, AER, "Micro Effects of Macro Announcements: Real-Time Price Discovery in Foreign Exchange"). Their key findings:

- FX prices respond to macro announcement surprises within 5–30 minutes.
- The response is persistent: the price often continues drifting in the direction of the surprise for 1–3 days.
- Asymmetric response: bad news (negative surprises) has larger price impact than good news of equal magnitude.

**Surprise construction:**

$$\text{Surprise}_t = \frac{\text{Actual}_t - \text{Consensus}_t}{\sigma_{\text{hist}}}$$

where $\sigma_{\text{hist}}$ is the historical standard deviation of surprises for that release type, used for cross-release standardisation. This allows you to compare a CPI surprise against an NFP surprise on the same scale.

**Free data sources:**
- Bloomberg consensus (institutional subscription required)
- Econoday.com (calendar and consensus)
- ForexFactory.com (free, widely used community data source)
- FRED (Federal Reserve Economic Data) for actual releases
- FRBSF Monetary Policy Surprise dataset: covers Fed meetings 1994–present with high-frequency identification of monetary policy shocks

**3-5 day drift signal:**

After a surprise release, the drift is driven by:
1. Analysts updating their economic models.
2. Institutional investors (slower to trade than HFT) repositioning.
3. Options-related hedging flows.

The 3-day post-release window is the primary target for MFT strategies. Beyond day 5, the initial signal has usually been arbitraged away.

#### Post-Earnings-Announcement Drift (PEAD)

Bernard and Thomas (1989, JAR) named and documented PEAD: after an earnings surprise, stock prices continue drifting in the direction of the surprise for 30–60 trading days. The annualised abnormal return from a long-short SUE (Standardised Unexpected Earnings) portfolio was approximately 18% in the original study.

**Why it persists:** Investors systematically underreact to earnings surprises. Bernard and Thomas showed that the market fails to "recognise fully the implications of current earnings for future earnings." The autocorrelation structure of earnings (positive quarterly autocorrelation, negative annual autocorrelation) is known but not fully priced.

**MFT application:** The first 10–20 trading days post-earnings are the highest-Sharpe window. After that, the signal weakens but the 30–60 day drift remains. For a 5–20 day holding period strategy, PEAD is one of the most robust signals available.

**Signal construction:**

```python
def compute_sue(actual_eps: float, consensus_eps: float, 
                hist_std_surprises: float) -> float:
    """Standardised Unexpected Earnings (SUE)."""
    return (actual_eps - consensus_eps) / hist_std_surprises

def pead_signal(sue: pd.Series, days_since_announcement: pd.Series) -> pd.Series:
    """
    Signal decays exponentially with days since announcement.
    Half-life: approximately 10 days.
    """
    half_life = 10
    decay = np.exp(-np.log(2) * days_since_announcement / half_life)
    return sue * decay
```

#### Earnings Revision Momentum

Analyst estimate revisions predict stock returns over a 10–20 day horizon. When analysts raise their EPS estimates for next quarter, the stock tends to outperform. The mechanism: analysts are slow to update, and each revision signals that more revisions will follow (herding behaviour among sell-side analysts).

**Signal:** Change in consensus EPS estimate over the last 5 trading days, z-scored cross-sectionally.

### 2.3 Positioning and Flow Signals (3–10 Day Holding Periods)

#### CFTC Commitment of Traders (COT)

The CFTC publishes COT reports every Tuesday, released the following Friday. The report shows the aggregate positioning of different trader types (commercial hedgers, non-commercial speculators, smaller traders) in futures markets.

**The signal:** Non-commercial speculators (hedge funds, CTA funds) are the "smart money" at medium frequency. Their net position changes predict subsequent returns. The intuition: large speculative position changes follow real information or sustained momentum; the flow continues for several days after the weekly snapshot.

**Construction:**

$$\text{COT Signal}_t = \frac{\text{Net Long (Non-Commercial)}_t - \text{MA}_{52}(\text{Net Long})}{\text{Std}_{52}(\text{Net Long})}$$

**Caution:** Academic evidence on COT predictability is mixed. One paper (Ederington-Lee style analyses of S&P500 COT data) found structural breaks in predictability. The 3-day data lag means COT is best used as a medium-term (1-2 week) confirmation signal rather than a short-term trigger. Use it for trend confirmation, not for precise entry/exit timing.

**Free data:** CFTC.gov provides free weekly COT data going back to the 1980s.

#### ETF Flow Data

Net flows into sector ETFs (e.g., XLF for financials, XLE for energy) predict short-term sector returns through a mechanical channel: large ETF inflows force the ETF manager to buy the underlying stocks, creating price pressure.

**Signal:** z-score of daily net flow (in dollars, normalised by market cap) for each ETF. Expected holding period: 2–5 days for the price pressure to be absorbed.

#### Options Market Signals

The options market is forward-looking and aggregates sophisticated investor views:

- **Put-call ratio:** Rising put-call ratio = bearish sentiment. At extreme readings (>1.5 for single-name equity), contrarian signal (too bearish = buy).
- **Implied volatility term structure:** When front-month IV exceeds back-month IV (inverted term structure), the market is pricing in near-term stress — useful as a risk-off trigger for MFT positions.
- **Skew:** Steep put skew = large institutions buying protection = bearish lean.

### 2.4 Event-Driven Signals (1–10 Days Around Events)

The central bank meeting calendar, macro data releases, and corporate events create discrete alpha opportunities. These are covered in depth in Section 4.

---

<a name="section-3"></a>
## Section 3: Statistical Arbitrage — The Core MFT Methodology

### 3.1 What Is Statistical Arbitrage?

Statistical arbitrage (stat arb) is the systematic exploitation of mean-reverting deviations from historical or structural equilibrium relationships between assets. The name is slightly misleading — it is not true arbitrage (there is no riskless profit). It is a statistical bet that a spread that has widened beyond its normal range will converge back.

The general framework:

1. **Identify two or more assets with a structural relationship** (same sector, same supply chain, same currency exposure, same index membership).
2. **Construct a spread**: a linear combination of the assets designed to be stationary.
3. **Test for stationarity**: verify empirically that the spread mean-reverts.
4. **Trade deviations**: when the spread deviates beyond a threshold, bet on reversion.

### 3.2 Pairs Trading: The Canonical Stat Arb Strategy

Pairs trading was formalised academically by Gatev, Goetzmann, and Rouwenhorst (2006, RFS, "Pairs Trading: Performance of a Relative-Value Arbitrage Rule"). Using daily data from 1962–2002, they documented that a simple rule — match stocks by minimum distance between normalised price histories; trade divergences — yielded average annualised excess returns of up to 11% for self-financing portfolios.

#### Step 1: The Engle-Granger Cointegration Test

Engle and Granger (1987, Econometrica, "Co-integration and Error Correction: Representation, Estimation and Testing") established the formal framework. Two time series $P_A(t)$ and $P_B(t)$ are cointegrated of order (1,1) if:

1. Both $P_A$ and $P_B$ are individually non-stationary (I(1) — integrated of order one).
2. There exists a $\beta$ such that the linear combination $S(t) = P_A(t) - \beta \times P_B(t)$ is stationary (I(0)).

The spread $S(t)$ is the cointegrating relationship. Its stationarity means it has a constant mean and variance over time — it mean-reverts.

**Testing procedure:**

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS

def test_cointegration(price_a: pd.Series, price_b: pd.Series) -> dict:
    """
    Engle-Granger two-step cointegration test.
    Returns: beta (hedge ratio), p-value of stationarity test,
             and the spread series.
    """
    # Step 1: Estimate the cointegrating regression
    ols_result = OLS(price_a, price_b).fit()
    beta = ols_result.params[0]
    
    # Step 2: Test residuals for stationarity (ADF test)
    spread = price_a - beta * price_b
    adf_result = adfuller(spread, maxlags=5, autolag='AIC')
    
    return {
        'beta': beta,
        'adf_statistic': adf_result[0],
        'p_value': adf_result[1],
        'spread': spread,
        'is_cointegrated': adf_result[1] < 0.05
    }

# Example: testing Goldman Sachs (GS) vs JPMorgan (JPM)
result = test_cointegration(gs_prices, jpm_prices)
if result['is_cointegrated']:
    print(f"Cointegrated: β = {result['beta']:.3f}, p = {result['p_value']:.3f}")
```

#### Step 2: The Trading Rule

Once the spread $S(t) = P_A(t) - \beta \times P_B(t)$ is identified, the trading rule is based on z-scores of the spread:

$$z(t) = \frac{S(t) - \mu_S}{\sigma_S}$$

where $\mu_S$ and $\sigma_S$ are estimated over a rolling lookback window (typically 60–120 days).

**Entry, exit, and stop:**

| Signal | Rule | Position |
|---|---|---|
| $z(t) > +2$ | Spread too wide | Short $A$, Long $B \times \beta$ |
| $z(t) < -2$ | Spread too narrow | Long $A$, Short $B \times \beta$ |
| $|z(t)| < 0.5$ | Spread near mean | Close position (take profit) |
| $|z(t)| > 3$ | Spread diverging | Close position (stop-loss) |

The threshold of $\pm 2\sigma$ for entry and $0.5\sigma$ for exit is the standard (Gatev-Goetzmann-Rouwenhorst parameterisation). The $3\sigma$ stop-loss acknowledges that sometimes the spread diverges permanently because the structural relationship has broken down.

#### Complete Pairs Trading Backtest

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.regression.linear_model import OLS
import matplotlib.pyplot as plt

class PairsTradingBacktest:
    """
    A complete pairs trading backtest with Engle-Granger cointegration.
    
    Parameters
    ----------
    formation_period : int
        Days to estimate beta and spread statistics (default: 252)
    entry_z : float
        Z-score threshold for entering a trade (default: 2.0)
    exit_z : float
        Z-score threshold for exiting profitably (default: 0.5)
    stop_z : float
        Z-score threshold for stop-loss exit (default: 3.0)
    transaction_cost_bps : float
        Round-trip transaction cost in basis points (default: 2 bps)
    """
    def __init__(self, formation_period=252, entry_z=2.0, 
                 exit_z=0.5, stop_z=3.0, transaction_cost_bps=2.0):
        self.formation_period = formation_period
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
        self.tc = transaction_cost_bps / 10000
    
    def compute_spread(self, prices_a: pd.Series, 
                       prices_b: pd.Series, 
                       lookback: int) -> tuple:
        """
        Rolling OLS to estimate dynamic beta and compute spread z-score.
        """
        n = len(prices_a)
        z_scores = pd.Series(index=prices_a.index, dtype=float)
        betas = pd.Series(index=prices_a.index, dtype=float)
        
        for i in range(lookback, n):
            window_a = prices_a.iloc[i-lookback:i]
            window_b = prices_b.iloc[i-lookback:i]
            
            # Estimate beta via OLS in the formation window
            beta = OLS(window_a, window_b).fit().params[0]
            betas.iloc[i] = beta
            
            # Spread in the formation window
            spread = window_a - beta * window_b
            mu = spread.mean()
            sigma = spread.std()
            
            # Current spread z-score
            current_spread = prices_a.iloc[i] - beta * prices_b.iloc[i]
            z_scores.iloc[i] = (current_spread - mu) / (sigma + 1e-8)
        
        return z_scores, betas
    
    def run(self, prices_a: pd.Series, prices_b: pd.Series) -> pd.DataFrame:
        """
        Execute the pairs trading strategy and return daily P&L.
        """
        z_scores, betas = self.compute_spread(
            prices_a, prices_b, self.formation_period
        )
        
        positions = pd.Series(0, index=prices_a.index)  # +1 long spread, -1 short spread, 0 flat
        daily_pnl = pd.Series(0.0, index=prices_a.index)
        
        returns_a = prices_a.pct_change()
        returns_b = prices_b.pct_change()
        
        for i in range(self.formation_period + 1, len(prices_a)):
            z = z_scores.iloc[i]
            beta = betas.iloc[i]
            current_pos = positions.iloc[i-1]
            
            if np.isnan(z):
                positions.iloc[i] = 0
                continue
            
            # Entry logic
            if current_pos == 0:
                if z > self.entry_z:
                    positions.iloc[i] = -1   # Short spread (short A, long B)
                    daily_pnl.iloc[i] -= self.tc  # Transaction cost
                elif z < -self.entry_z:
                    positions.iloc[i] = +1   # Long spread (long A, short B)
                    daily_pnl.iloc[i] -= self.tc
                else:
                    positions.iloc[i] = 0
            
            # Exit logic
            elif current_pos != 0:
                # Profit-taking exit
                if abs(z) < self.exit_z:
                    positions.iloc[i] = 0
                    daily_pnl.iloc[i] -= self.tc
                # Stop-loss exit
                elif abs(z) > self.stop_z:
                    positions.iloc[i] = 0
                    daily_pnl.iloc[i] -= self.tc
                else:
                    positions.iloc[i] = current_pos
            
            # P&L from current position
            r_a = returns_a.iloc[i]
            r_b = returns_b.iloc[i]
            spread_return = r_a - beta * r_b
            daily_pnl.iloc[i] += current_pos * spread_return
        
        # Summary statistics
        ann_return = daily_pnl.mean() * 252
        ann_vol = daily_pnl.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        
        return pd.DataFrame({
            'z_score': z_scores,
            'position': positions,
            'daily_pnl': daily_pnl,
            'cumulative_pnl': daily_pnl.cumsum()
        }), {'sharpe': sharpe, 'ann_return': ann_return, 'ann_vol': ann_vol}
```

#### Step 3: Why Classic Pairs Trading Has Decayed

Gatev-Goetzmann-Rouwenhorst documented 11% annual returns for 1962–2002. By the mid-2000s, this had decayed significantly. Academic estimates for more recent periods (2005–2020) show returns of 3–5% annualised, often below transaction costs for retail-sized trades.

**Reasons for decay:**
1. **Publication effect**: once published, the strategy attracts capital, which arbitrages the deviation faster.
2. **HFT competition**: high-frequency traders now eliminate obvious mispricing within minutes, not days.
3. **Model risk**: pairs can permanently diverge (regulatory change, earnings shock, sector rotation), making the $3\sigma$ stop-loss expensive in crowded regimes.

### 3.3 More Robust Alternatives: Factor-Neutral Relative Value

Modern institutional stat arb has evolved beyond pairs. The approach is:

1. Build a multi-factor model that explains stock returns (market, sector, industry, size, value, momentum).
2. Strip all factor exposures from each position.
3. Trade only the **idiosyncratic** residual return — the part unexplained by factors.

This is called **factor-neutral relative value** or **alpha-only stat arb**. It avoids the crowded-pairs problem because you are not relying on stable pairwise relationships — you are relying on the factor model being complete.

**Mathematical framework:**

$$r_i = \sum_{k=1}^{K} \beta_{ik} f_k + \epsilon_i$$

You want to trade $\epsilon_i$ (the idiosyncratic component), not $r_i$. If $\epsilon_i$ is mean-reverting (as it is for many stocks due to sector rotation, analyst coverage cycles, and short-term liquidity), you have a stat arb signal.

### 3.4 Spread Construction Methods

| Type | Formula | Use Case |
|---|---|---|
| Level spread | $P_A - \beta \cdot P_B$ | Cointegrated stocks, ETF pairs |
| Ratio spread | $P_A / P_B$ | FX crosses, commodity ratios |
| Return spread | $r_A - r_B$ | Factor-neutralised relative value |
| Log-price spread | $\log P_A - \beta \log P_B$ | Better when prices have large ranges |

### 3.5 Kalman Filter Estimation of the Hedge Ratio

A key weakness of static OLS-estimated $\beta$ is that the true hedge ratio changes over time. The Kalman filter treats $\beta(t)$ as a latent state variable that evolves according to a random walk, and updates it each period as new observations arrive.

**State space representation:**

$$P_A(t) = \beta(t) \cdot P_B(t) + \epsilon_t, \quad \epsilon_t \sim N(0, R)$$
$$\beta(t) = \beta(t-1) + \delta_t, \quad \delta_t \sim N(0, Q)$$

where $R$ is the observation noise variance and $Q$ is the state transition variance. The ratio $Q/R$ controls how quickly $\beta$ adapts: higher $Q/R$ means faster adaptation (more responsive but noisier).

**Advantages of Kalman beta:**
- Adapts to structural breaks in the relationship.
- Provides a smoother and more continuously updated hedge ratio.
- Naturally incorporates uncertainty about the hedge ratio.

```python
from pykalman import KalmanFilter
import numpy as np

def kalman_hedge_ratio(prices_a: np.ndarray, prices_b: np.ndarray,
                       delta: float = 1e-4) -> np.ndarray:
    """
    Estimate dynamic hedge ratio using Kalman filter.
    
    Parameters
    ----------
    delta : float
        Variance of state transition noise (controls speed of adaptation).
                Lower delta = slower adaptation.
    """
    n = len(prices_a)
    
    # Kalman filter setup
    # State: [beta, intercept]
    # Observation: price_a = beta * price_b + intercept + noise
    
    obs_mat = np.array([[prices_b[i], 1.0] for i in range(n)])
    obs_mat = obs_mat[:, np.newaxis, :]  # Shape: (n, 1, 2)
    
    kf = KalmanFilter(
        n_dim_obs=1,
        n_dim_state=2,
        initial_state_mean=[0, 0],
        initial_state_covariance=np.eye(2),
        transition_matrices=np.eye(2),
        observation_matrices=obs_mat,
        observation_covariance=[[1.0]],
        transition_covariance=delta * np.eye(2)
    )
    
    state_means, _ = kf.filter(prices_a.reshape(-1, 1))
    return state_means[:, 0]  # Return beta estimates

# Usage:
# beta_dynamic = kalman_hedge_ratio(gs_prices.values, jpm_prices.values)
# spread = gs_prices.values - beta_dynamic * jpm_prices.values
```

### 3.6 FX Statistical Arbitrage

FX markets offer several stat arb opportunities beyond simple pair trades:

**Triangular consistency:** The exchange rate cross $EURGBP$ should equal $EURUSD / GBPUSD$. Any deviation is a pure arbitrage at HFT frequency, but the reversion from small systematic biases in the triangle can be exploited at MFT frequency.

**Cross-currency basis trading:** Covered Interest Parity (CIP) states that the return from borrowing in dollars, converting to euros, investing in euro rates, and hedging back with an FX forward should exactly equal the dollar interest rate. Post-2008, this parity has persistently failed (Avdjiev et al., BIS 2019), creating the cross-currency basis — an apparent arbitrage.

However, the basis reflects real constraints (bank balance sheet limits, counterparty credit risk, regulatory capital requirements), not a free lunch. For MFT purposes, mean-reversion in the basis at the 5–20 day horizon is a genuine signal: when the EUR/USD basis widens beyond its typical range, it tends to narrow over the next 1–3 weeks.

**Carry spread convergence:** When the carry spread between two currency pairs diverges anomalously — e.g., EURUSD carry suddenly yields 50 bps more than GBPUSD carry relative to its historical relationship — there is a statistical expectation of convergence. This is a cross-currency relative value trade at 5–15 day frequency.

---

<a name="section-4"></a>
## Section 4: Event-Driven MFT Strategies

### 4.1 Central Bank Events — The Most Important for FX MFT

No event in systematic macro trading generates as much FX alpha as central bank meetings. They occur at predictable times, produce discrete and quantifiable surprises, and generate price dynamics that persist for days.

#### The Central Bank Calendar

| Central Bank | Currency | Meetings/Year | Key Release | Time (Local) |
|---|---|---|---|---|
| Federal Reserve (FOMC) | USD | 8 | Statement + press conf. | 2:00 PM ET |
| European Central Bank (ECB) | EUR | 8 | Statement + press conf. | 1:45 PM CET |
| Bank of England (BoE) | GBP | 8 | Statement + MPC minutes | 12:00 PM GMT |
| Bank of Japan (BoJ) | JPY | 8 | Statement | Variable |
| Reserve Bank of Australia (RBA) | AUD | 11 | Statement | 2:30 PM AEST |
| Bank of Canada (BoC) | CAD | 8 | Statement | 10:00 AM ET |
| Swiss National Bank (SNB) | CHF | 4 | Statement | 9:30 AM CET |
| Reserve Bank of New Zealand (RBNZ) | NZD | 7 | Statement | 2:00 PM NZST |
| Riksbank (Sweden) | SEK | 6 | Statement | 9:30 AM CET |
| Norges Bank (Norway) | NOK | 8 | Statement | 10:00 AM CET |

Total: approximately 82 scheduled central bank events across G10 currencies per year, each a potential MFT signal.

#### Measuring Monetary Policy Surprises

The standard methodology uses OIS (Overnight Index Swap) rates to measure market expectations:

$$\text{Surprise}_{t} = \Delta r_{\text{policy}} - \Delta r_{\text{OIS,implied}}$$

where $\Delta r_{\text{policy}}$ is the actual rate change announced at time $t$, and $\Delta r_{\text{OIS,implied}}$ is the rate change that OIS rates implied 30–60 minutes before the announcement.

**In practice:**
- For the Fed: read the 30-day Fed Funds Futures contract immediately before the FOMC statement.
- The meeting's "priced-in" rate change = (current contract rate - prior month's settlement rate).
- Surprise = actual change - priced-in change.

This methodology is formalised in the FRBSF Monetary Policy Surprise dataset, available free at the San Francisco Fed website, covering Fed meetings from 1994 to the present.

#### Price Dynamics Around Central Bank Events

The price dynamics unfold in three phases that an MFT strategy must model separately:

**Phase 1 — Immediate spike (0–30 minutes):** HFT and fast-money accounts execute in milliseconds. The initial price response is roughly proportional to the surprise magnitude. A 25 bps surprise hike (vs. no change expected) typically moves EURUSD by 80–150 pips immediately.

**Phase 2 — Secondary drift (1–3 days):** After the initial reaction, the market continues to digest the statement, the press conference, and the implications for future meetings. This drift is the MFT opportunity. Nakamura and Steinsson (2018, QJE) documented that monetary policy announcements move not just policy rates but also long-term real rates and output growth expectations — a multi-day repricing process.

**Phase 3 — Mean reversion (3–5 days):** Particularly for large surprises, the initial move often partially reverts as the market reassesses. The "information effect" identified by Nakamura-Steinsson is key here: sometimes a surprise rate hike actually causes yields to fall and currencies to weaken, because the hike signals that the central bank has *positive* private information about economic strength. This is the opposite of the naive prediction.

**The "information effect" (Nakamura-Steinsson):**

When the Fed unexpectedly hikes rates, two competing signals are sent:
1. Higher rates → capital inflow → USD appreciation (the standard channel).
2. Fed must know something about the economy that is positive → output growth will be higher → this is actually a dovish signal for future inflation expectations.

The net effect depends on which channel dominates, which varies across regimes. In 2022, the standard channel dominated (aggressive hiking → USD strengthened). In early 2019, the information effect was more important.

**MFT strategy implementation:**

```python
def central_bank_signal(surprise: float, days_post_event: int,
                        regime: str = 'standard') -> float:
    """
    Signal for FX position after central bank event.
    
    Parameters
    ----------
    surprise : float
        Rate surprise in basis points (positive = hawkish surprise)
    days_post_event : int
        Days elapsed since the event
    regime : str
        'standard' (rate shock dominates) or 'information' (private info dominates)
    
    Returns
    -------
    float
        Signal for the domestic currency (positive = buy domestic)
    """
    if days_post_event == 0:
        return 0  # Let HFT execute the initial spike; don't trade immediately
    
    # Decay function: full signal on days 1-3, then rapid decay
    if days_post_event <= 3:
        decay = 1.0
    elif days_post_event <= 5:
        decay = 0.5
    else:
        decay = 0.0
    
    # Direction depends on regime
    if regime == 'standard':
        direction = np.sign(surprise)  # Hawkish = buy domestic currency
    else:  # Information effect
        direction = -np.sign(surprise)  # Hawkish = sell domestic (dovish signal)
    
    return direction * abs(surprise) * decay / 25.0  # Normalise by 25 bps
```

**Practical rule for FX MFT:**
- Enter position 2 hours after the event (after initial volatility subsides).
- Target holding period: 3 days.
- Maximum stop: 1.5× the expected daily move for the currency pair.
- Exit: after 3 days or when z-score of price move exceeds 2.5σ (mean reversion signal).

### 4.2 Macro Data Releases

US Non-Farm Payrolls (NFP) is the single most market-moving monthly data release for G10 FX. Released on the first Friday of each month at 8:30 AM ET. The consensus forecast (Bloomberg median) is widely watched; deviations from consensus drive immediate and multi-day FX moves.

**Andersen et al. (2003) findings for NFP:**
- A 100,000-person surprise above consensus drives approximately 60–80 pip move in EURUSD (in 2002 dollars; the impact has compressed as more capital competes to trade it).
- The response is fastest for USD-centric pairs (EURUSD, USDJPY) and slower for commodity currencies.
- Significant drift persists for 1–3 days, especially when the surprise confirms a trend (e.g., consistently strong payrolls reinforce a rate-hiking cycle).

**Multi-country surprise index for FX crosses:**

Rather than just using the US data, build a relative surprise signal across G10:

$$\text{CrossSignal}_{A/B} = \text{CPI Surprise}_A - \text{CPI Surprise}_B$$

A country that surprises to the upside on CPI tends to see its currency appreciate over the next 5–10 days (central bank expected to hike more aggressively). A country that surprises to the downside sees depreciation.

**Key data releases by importance for G10 FX:**

| Release | Country | Frequency | FX Impact (1–3 day) |
|---|---|---|---|
| Non-Farm Payrolls | US | Monthly | Very high |
| CPI | US, EU, UK, AU | Monthly | High |
| FOMC/ECB/BoE decisions | US, EU, UK | 8×/year | Very high |
| GDP (advance estimate) | US | Quarterly | Medium-high |
| Retail Sales | US | Monthly | Medium |
| PMI (Manufacturing, Services) | G10 | Monthly | Medium |
| Unemployment Rate | EU, UK, AU | Monthly | Medium |
| Trade Balance | US, China | Monthly | Low-medium |

### 4.3 Index Rebalancing Events

Index rebalancing creates predictable, price-sensitive flows that MFT strategies can exploit.

**MSCI Quarterly Rebalancing:**

MSCI announces constituent changes approximately 2 weeks before the effective date (quarterly in February, May, August, November). Academic evidence (Hrazdil and Scott 2009; studies on MSCI-Canada index by Greenwood 2005) shows:

- Stocks being added to the index experience price pressure of approximately 4% over the 20 trading days before the effective date (as index-tracking funds pre-position).
- The price effect partially reverses after the effective date (approximately -5.7% in the following month).
- The announcement-date-to-effective-date window is the primary MFT opportunity.

**Strategy:**
- On announcement date: buy additions at close price.
- Hold for 15–18 trading days (stop 2 days before effective date to avoid crowded-exit risk).
- Expected return: 3–5% over holding period (net of borrow costs for short/delta hedge).

**S&P 500 Rebalancing:**

Similar mechanism but faster to arbitrage. The window has compressed from 20 days to approximately 5–10 days in recent years as the strategy has attracted more capital.

**Free data:** S&P announces changes via press release; MSCI publishes changes on their website 2 weeks before effective date.

### 4.4 Corporate Events (Equity-Focused MFT)

| Event | Signal Direction | Expected Holding |
|---|---|---|
| Earnings beat (SUE > 1σ) | Long | 5–20 days (PEAD) |
| Guidance raise | Long | 3–10 days |
| Analyst upgrade | Long | 3–7 days |
| Analyst initiation (Buy) | Long | 3–5 days |
| M&A target announcement | Long (target) | Until deal close / arb entry |
| IPO lockup expiration (Day 180) | Short (anticipated selling) | −5 to +5 days |
| Index deletion announcement | Short | 5–15 days |

---

<a name="section-5"></a>
## Section 5: Momentum at MFT Frequency — The Evidence

### 5.1 Short-Term Reversal (1–5 Days)

Jegadeesh (1990, JF) was the first to document that 1-month stock returns negatively predict the next 1-month return in the cross-section — a reversal effect. The magnitude: approximately 1.7% monthly spread between the bottom decile and top decile of 1-month lagged returns.

**Mechanism:** Short-term reversals are driven by:
1. **Market-maker inventory management**: After a large order, market-makers are long/short inventory and need to unwind. This creates temporary price impact that reverts.
2. **Bid-ask bounce**: Buy orders execute at the ask; sell orders at the bid. A sequence of buys shows a price run-up that reverses when the directional flow stops.
3. **Noise trader activity**: Retail investors chase recent winners, creating short-term price momentum that institutional arbitrageurs exploit via contrarian trades.

**Practical implications for MFT:**
- The reversal effect works best in **illiquid stocks** (large bid-ask spreads, more inventory risk for market-makers).
- It breaks down in **trending markets** and **around earnings announcements** (when the price move is fundamental, not flow-driven).
- For G10 FX, the reversal effect is weak because market-makers are more sophisticated and liquidity is deep. FX reversal signals are most useful at very short horizons (intraday) — not the MFT sweet spot.

### 5.2 Medium-Term Continuation (5–20 Days)

**The Gutierrez-Kelley finding:**

Gutierrez and Kelley (2008, JF, "The Long-Lasting Momentum in Weekly Returns") showed that weekly returns have a specific temporal structure:
1. Formation week: positive return.
2. Weeks 1–2 after formation: brief reversal (short-term reversal effect).
3. Weeks 3–52: sustained momentum continuation.

The full-year return is positive (momentum dominates), but the first 2-week period is negative (reversal). For an MFT strategy entering on day 3–5 (after the initial reversal), the signal-to-noise ratio improves substantially.

**Post-Earnings Analyst Revision Drift:**

After an earnings surprise, sell-side analysts are slow to fully revise their estimates. Evidence shows:
- Analysts revise estimates in multiple steps over 4–8 weeks.
- Each revision step is correlated with future price appreciation.
- The combined "earnings + revision" signal has higher Sharpe than either alone over the 10–20 day horizon.

This is particularly robust in US equities and has been documented in European and Asian markets as well (Hvidkjaer 2006; Liu et al. 2014).

### 5.3 Time-Series Momentum at Weekly Frequency

Moskowitz, Ooi, and Pedersen (2012, JFE, "Time Series Momentum") examined 58 diverse futures and forward contracts over 25 years. Their findings:

- Significant time-series momentum exists in all asset classes: equities, fixed income, currencies, commodities.
- The 12-month lookback with 1-month skip is the standard specification.
- A diversified TSMOM portfolio with this specification achieved a Sharpe ratio exceeding 1.20.
- The strategy performed best during extreme markets (both bull and bear extremes) — the "crisis alpha" property that makes it valuable for portfolio construction.

**AQR's practical implementation** (from AQR dataset and paper appendix):

```python
def time_series_momentum_signal(returns: pd.DataFrame, 
                                 lookback: int = 252,
                                 skip: int = 21) -> pd.DataFrame:
    """
    Moskowitz-Ooi-Pedersen TSMOM signal.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Daily returns, columns = instruments
    lookback : int
        Lookback period in trading days (default: 252 = 12 months)
    skip : int
        Skip period in days (default: 21 = 1 month)
    
    Returns
    -------
    pd.DataFrame
        Daily signal for each instrument: +1 (long) or -1 (short)
    """
    # Cumulative return over [t-lookback, t-skip]
    cum_returns = (1 + returns).rolling(lookback).apply(
        lambda x: x.prod(), raw=True
    ).shift(skip) - 1
    
    # Signal: sign of past return
    signal = np.sign(cum_returns)
    
    return signal

def vol_scaled_tsmom(returns: pd.DataFrame, 
                      signal: pd.DataFrame,
                      target_vol: float = 0.40,
                      vol_lookback: int = 60) -> pd.DataFrame:
    """
    Volatility-scaled TSMOM positions.
    Scale each instrument to target 40% annual volatility before
    combining into equal-risk portfolio.
    """
    # Annualised realised volatility
    ann_vol = returns.rolling(vol_lookback).std() * np.sqrt(252)
    
    # Position: (target_vol / instrument_vol) × signal
    positions = (target_vol / ann_vol) * signal
    
    return positions
```

**Weekly rebalancing of TSMOM:**

Rebalancing TSMOM weekly (instead of monthly) slightly improves the Sharpe ratio (approximately +0.05 to +0.10) but increases annual transaction costs by roughly 30–50 bps. The net benefit depends on the instrument's bid-ask spread. For G10 FX futures (tight spreads), weekly rebalancing is worth it. For less liquid instruments, monthly rebalancing is more cost-efficient.

**Optimal lookback for MFT:**

The evidence suggests combining multiple lookback windows improves performance:

| Lookback | Signal Horizon | Sharpe (standalone) | Mechanism |
|---|---|---|---|
| 1 week | 1–3 days | ~0.3 | Gap effects, short-term flow |
| 1 month | 5–15 days | ~0.5 | News under-reaction |
| 3 months | 15–45 days | ~0.7 | Analyst revision cycles |
| 12 months (skip 1M) | 30–90 days | ~1.0 | Full momentum effect |

A composite signal combining all four lookbacks (equal-weighted z-scores) typically achieves a Sharpe of 1.2–1.5 depending on the asset class and sample period.

---

<a name="section-6"></a>
## Section 6: Risk Management at MFT Frequency

### 6.1 The Signal-to-Noise Challenge

Shorter holding periods have a fundamental problem: the signal-to-noise ratio per trade is lower. Consider:

- A low-frequency strategy (12-month momentum) has a holding period of 252 days. The signal drives returns over 252 daily returns, smoothing out the noise.
- An MFT strategy (5-day holding) has only 5 daily returns to express the signal. The noise dominates in any single trade.

The solution is not to improve the signal — it is to **increase breadth dramatically**. At 20 instruments × 252 trading days × 5-day rebalancing, you generate approximately 1,000 independent bets per year. This is why Grinold-Kahn applies so powerfully to MFT.

### 6.2 Position Sizing: Volatility Targeting

The standard institutional approach:

$$\text{Position}_i = \frac{\sigma_{\text{target,daily}}}{\hat{\sigma}_{i,\text{daily}}} \times z_{i,t}$$

where:
- $\sigma_{\text{target,daily}}$ = target daily portfolio volatility (e.g., 0.5% = 8% annual)
- $\hat{\sigma}_{i,\text{daily}}$ = estimated daily volatility of instrument $i$ (typically from a 20-day exponentially weighted moving average)
- $z_{i,t}$ = z-scored signal for instrument $i$ on day $t$, bounded to $[-3, +3]$

**Why daily vol targeting, not annual?** At MFT frequency, volatility regimes change quickly. Annual volatility estimates are stale by the time they're useful. A 20-day EWMA of daily squared returns provides an appropriately responsive (but not noise-reactive) volatility estimate.

```python
def vol_target_position(signals: pd.DataFrame, 
                         prices: pd.DataFrame,
                         daily_vol_target: float = 0.005,  # 0.5% daily = ~8% annual
                         ewma_halflife: int = 20,
                         max_position_size: float = 3.0) -> pd.DataFrame:
    """
    Volatility-targeted position sizing for MFT strategies.
    """
    # Compute daily returns
    returns = prices.pct_change()
    
    # EWMA volatility (annualised, then convert to daily)
    ewma_vol = returns.ewm(halflife=ewma_halflife).std()
    daily_vol = ewma_vol  # Already daily from daily returns
    
    # Clip signals to [-3, 3] z-score range
    clipped_signals = signals.clip(-max_position_size, max_position_size)
    
    # Position in fraction of portfolio notional
    positions = (daily_vol_target / (daily_vol + 1e-8)) * clipped_signals
    
    # Normalise: ensure portfolio vol = target even with multiple positions
    n_instruments = signals.shape[1]
    positions = positions / np.sqrt(n_instruments)  # Approximate diversification
    
    return positions
```

### 6.3 Drawdown Control Mechanisms

**Rolling drawdown control (5-day):**

```python
def apply_drawdown_filter(positions: pd.DataFrame, 
                           returns: pd.Series,
                           lookback: int = 5,
                           threshold: float = -0.02) -> pd.DataFrame:
    """
    Scale back positions when recent P&L is negative.
    
    Parameters
    ----------
    threshold : float
        5-day cumulative P&L threshold for position reduction (default: -2%)
    """
    rolling_pnl = returns.rolling(lookback).sum()
    
    # Scale factor: 1.0 when P&L > 0; reduce linearly to 0.2 at -4%
    scale = (rolling_pnl - threshold) / abs(threshold)
    scale = scale.clip(0.2, 1.0)  # Never reduce by more than 80%
    
    return positions.multiply(scale, axis=0)
```

**Pod-level drawdown limits (Millennium-style):**

The industry standard, codified by Millennium's pod structure:
- 5% drawdown from peak → capital cut by 50% immediately.
- 7.5% drawdown from peak → PM removed from trading.
- These limits are enforced by the central risk team, not the PM.

The key insight: **early, mechanical risk cuts prevent the "doubling-down" behaviour that destroys pods**. The hardest thing for a PM is to reduce risk when they believe the signal is correct but the market hasn't moved in their favour yet. Hard rules make this automatic.

### 6.4 Factor Exposure Management

MFT strategies that trade many instruments simultaneously accumulate unintended factor exposures. A strategy designed to capture PEAD in individual stocks might inadvertently be long value and short momentum at the portfolio level — exposing it to macro factor risk that has nothing to do with its intended signal.

**Daily factor neutralisation:**

```python
def neutralise_factor_exposure(positions: pd.Series, 
                                factor_loadings: pd.DataFrame) -> pd.Series:
    """
    Remove factor exposures from a portfolio of positions.
    
    Parameters
    ----------
    positions : pd.Series
        Raw positions (index = instruments)
    factor_loadings : pd.DataFrame
        Factor exposures (rows = instruments, columns = factors)
    
    Returns
    -------
    pd.Series
        Factor-neutralised positions
    """
    # Portfolio's aggregate factor exposure
    port_factor_exposure = factor_loadings.T @ positions
    
    # Hedges: positions that offset each factor exposure
    # Solve: B.T @ h = B.T @ p (cancel out factor exposure)
    B = factor_loadings.values
    h = np.linalg.lstsq(B.T @ B, B.T @ positions.values, rcond=None)[0]
    
    # Factor-neutralised position
    neutralised = positions - pd.Series(B @ h, index=positions.index)
    
    return neutralised
```

**Common factors to neutralise in equity MFT:**
- Market beta (most important)
- Sector exposure
- Size (market cap)
- Momentum exposure (to avoid doubling up on trend)
- Low volatility / beta exposure

**For FX MFT:**
- Dollar index exposure (when running multiple USD pairs simultaneously)
- Commodity currency basket (AUD, CAD, NZD tend to move together)
- Safe haven exposure (JPY, CHF tend to move together)

### 6.5 VIX Filter for MFT

Multiple studies confirm that MFT strategies perform worse during high-volatility regimes. The mechanism: in high-VIX environments, noise-to-signal ratios increase, correlations across instruments spike (a "everything sells off" dynamic), and mean-reversion signals fail because fundamental relationships are overwhelmed by panic flows.

**VIX scaling rule:**

$$\text{Scale}(VIX) = \max\left(0, 1 - \frac{VIX - 20}{20}\right)$$

This produces:
- VIX ≤ 20: full position (scale = 1.0)
- VIX = 25: 75% position (scale = 0.75)
- VIX = 30: 50% position (scale = 0.50)
- VIX ≥ 40: zero position (scale = 0.0)

The VIX threshold of 20 and the scaling rate are calibrated to historical data; the specific parameters should be validated on your own signals.

### 6.6 Stop-Losses for MFT

The optimal stop-loss design depends on the signal type:

| Signal Type | Best Stop Type | Rationale |
|---|---|---|
| Mean reversion (stat arb) | **Signal-flip stop**: exit if signal reverses | If the spread widens further, the model is wrong about the regime |
| Momentum (trend following) | **P&L stop**: exit at −50% of expected gain | Trend can persist; time-based stops destroy Sharpe |
| Event-driven (CB surprise) | **Time-based stop**: exit after 3–5 days | Signal has natural expiry (the event's information decays) |
| Macro data surprise | **P&L stop**: exit at −1× expected daily move | News can be persistent; don't cut winners short |

**Evidence:** For momentum strategies, stop-losses that exit based on time (rather than price level) have been shown to reduce the Sharpe ratio because they exit at the wrong times — trend signals can take time to manifest. For mean-reversion, the opposite is true: waiting too long after a signal reversal is costly.

### 6.7 Overnight Risk in MFT

MFT strategies that hold positions overnight face gap risk — particularly around scheduled macro events. The largest overnight gaps in G10 FX occur:
1. Around central bank decisions (scheduled; can be avoided).
2. Around major macro releases (scheduled; can be avoided).
3. During geopolitical events (unscheduled; cannot be fully avoided).

**Practical overlay:**

```python
def apply_event_overlay(positions: pd.DataFrame,
                         event_calendar: pd.DataFrame,
                         scale_factor: float = 0.3) -> pd.DataFrame:
    """
    Reduce overnight positions before scheduled macro events.
    
    Parameters
    ----------
    event_calendar : pd.DataFrame
        Columns: ['date', 'currency', 'importance']
                 importance: 1=low, 2=medium, 3=high
    scale_factor : float
        Fraction to reduce position before high-importance events
    """
    modified_positions = positions.copy()
    
    high_importance_events = event_calendar[event_calendar['importance'] == 3]
    
    for _, event in high_importance_events.iterrows():
        event_date = event['date']
        currency = event['currency']
        
        # Reduce positions in affected pairs one day before event
        pre_event_date = event_date - pd.Timedelta(days=1)
        
        # Identify columns (FX pairs) affected by this currency
        affected_pairs = [col for col in positions.columns 
                          if currency in col]
        
        if pre_event_date in modified_positions.index:
            modified_positions.loc[pre_event_date, affected_pairs] *= scale_factor
    
    return modified_positions
```

---

<a name="section-7"></a>
## Section 7: How Top MFT Funds Actually Work

### 7.1 Millennium Management: The Pod Model in Detail

Millennium's operating model is the most studied and most imitated in the industry. Understanding it is essential for anyone building MFT infrastructure.

**Pod structure:**

Each pod consists of:
- 1 Portfolio Manager (PM): sole decision-maker; responsible for all signals, positions, and P&L.
- 2–6 analysts: research support, model maintenance, alternative data processing.
- 1 risk specialist (may be shared across pods): risk limit monitoring.
- 1 trader/execution specialist: optimal execution, TCA analysis.

The PM is allocated capital by Millennium's central allocation committee. Capital ranges from $100M to $5B+ depending on the PM's track record and strategy capacity.

**Pod economics:**

- PM typically earns a "pass-through" of approximately 20–25% of their pod's net P&L.
- Millennium charges a significant "platform fee" to LPs (2.5–3% management fee equivalent in recent years, covering the infrastructure).
- The PM's compensation is entirely performance-based — no base salary in most cases.

**Typical pod strategy architecture:**

A 5-20 day holding equity stat arb pod at Millennium typically runs:
- Universe: 500–2,000 liquid US equities (typically S&P 1500 + Russell 2000 components)
- Signals (ranked by typical weight):
  1. Earnings revision momentum (analyst estimate changes, 5-day change): ~25% weight
  2. PEAD (SUE signal, decayed by days since announcement): ~20% weight
  3. Sector-relative price momentum (5-day, 21-day, 63-day): ~20% weight
  4. Short interest change: ~10% weight
  5. Valuation (P/E relative to sector): ~15% weight
  6. Quality (ROE, gross margin): ~10% weight
- Portfolio: 100–300 positions, sector-neutral (zero net sector exposure), dollar-neutral

**Central risk management:**

Millennium's central risk team performs daily:
- Factor exposure aggregation across all 330 pods.
- If aggregate market beta deviates from target → force pods to hedge.
- If any single sector or factor dominates firm-wide exposure → allocate capital away from overexposed pods.
- Correlation monitoring: if two pods' P&L streams become highly correlated, one is forced to diversify signals.

**Target Sharpe ratios:**

- Pod target (gross): 1.5–2.5 (stated in interviews with former PMs)
- After pod fees (20% performance): net to LP is approximately 1.0–1.5
- Firm-level Sharpe (diversification benefit across 330 pods): approximately 2.5–3.0

### 7.2 Citadel: Multi-Strategy with MFT Embedded

**Global Fixed Income (GFI) Division:**

The GFI business trades rates relative value at 5–20 day horizons:
- **Swap spreads**: When the spread between the 10-year interest rate swap and the 10-year Treasury deviates from its historical mean, a convergence position is established.
- **Cross-country yield curve relative value**: e.g., when the US 2s10s curve is steeper than the German 2s10s curve by more than 1 historical standard deviation, trade the convergence.
- **CIP deviations**: Cross-currency basis positions with 5–15 day horizon.

The key competitive advantage: Citadel runs a quantitative macro model for each major economy (US, Eurozone, UK, Japan, Australia, Canada) that integrates economic data, central bank communication, and market pricing to identify when curves or spreads are mispriced relative to fundamental expectations.

**Global Equities Division:**

"Quantamental" is the operative word — fundamental equity research translated into systematic position signals:
- PM identifies a sector or stock theme (e.g., "energy sector is pricing in too-low oil prices").
- The position is constructed as a factor-neutral, sector-neutral portfolio (not a directional bet on oil).
- Entry, sizing, and exit are governed by systematic rules.
- Holding periods: 5–30 days for most equity positions.

### 7.3 Balyasny Asset Management: The Quantamental Middle Ground

Balyasny explicitly occupies the space between pure quant (Two Sigma, D.E. Shaw) and discretionary (Tiger Global, Point72's fundamental books). Their stated philosophy:

- Fundamental analysts identify investment themes and specific catalysts.
- Systematic execution infrastructure implements the position with optimal sizing and timing.
- Risk management is systematic (pod-level drawdown rules) but the initial signal is human-generated.

This hybrid model has several advantages:
1. **Alternative data integration**: Fundamental analysts know which alternative data sources are relevant for their sector; they can reject false positives that pure models would accept.
2. **Catalyst timing**: Humans are better at assessing whether a catalyst is 3 weeks away or 3 months away — timing matters enormously at MFT frequency.
3. **Regime awareness**: Humans can recognise when a fundamental thesis is being overwhelmed by macro flows (risk-off, factor rotation) and scale back before the model catches up.

**Scale (2025):** 29B AUM, ~125 pods. Holding periods: 5–30 days for equity pods, 1–10 days for macro pods.

### 7.4 Two Sigma: Algorithmic MFT at Scale

Two Sigma represents the pure-algorithmic end of MFT:

- Every trading decision is made by algorithms. No human overrides.
- Signal types: ML models trained on alternative data (satellite imagery of retail parking lots → consumer spending → retail stock returns; credit card data → company-level revenue → earnings beats).
- Holding periods: 1–7 days for Spectrum fund.
- $5.8B in Spectrum alone; returned 10.9% net in 2024 and 14.3% in their Absolute Return Enhanced strategy.

**Alternative data integration:** Two Sigma reportedly spends $100M+ per year on data acquisition. The signal half-life from a novel alternative data source is typically 12–24 months before it becomes commoditised and decays. This creates a "data treadmill" where new data sources must constantly replace decaying ones.

**Infrastructure:** Centralised factor model; all signal outputs are adjusted for factor exposure before combination. This means no single signal can inadvertently bet on the market or on a sector.

---

<a name="section-8"></a>
## Section 8: Building an MFT Strategy for FX and Macro

This section is a practical construction guide for a G10 FX MFT strategy.

### 8.1 Step 1: Define Your Signal Universe

For G10 FX, five signal categories cover most of the alpha:

| Signal Category | Data Source | Construction | Expected Holding |
|---|---|---|---|
| Rate differential change | FRED (daily 2Y yields) | Δ(r_US - r_eur) z-scored over 60 days | 1–5 days |
| Central bank surprise | FRBSF dataset; OIS rates | Actual - OIS-implied, z-scored | 1–3 days |
| Macro data surprise | Bloomberg/Econoday/ForexFactory | (Actual - Consensus) / Hist σ | 3–5 days |
| COT positioning change | CFTC.gov (free, weekly) | Δ(Net Non-Commercial) z-scored | 5–10 days |
| Cross-asset signal | Yahoo Finance (equities, commodities) | Equity market return → correlated FX | 1–3 days |

**For each signal, specify:**
1. The exact data source and update frequency.
2. The transformation (z-score, sign, normalised).
3. The expected holding period and decay function.
4. The universe of currency pairs for which the signal is relevant.

### 8.2 Step 2: Choose Your Instruments

| Pair | Daily Range (bps) | Round-Trip Cost (bps) | Capacity |
|---|---|---|---|
| EURUSD | 50–80 | 0.5–1.0 | Very High |
| GBPUSD | 60–100 | 0.5–1.0 | High |
| USDJPY | 50–80 | 0.5–1.0 | High |
| USDCAD | 50–90 | 0.5–1.0 | High |
| AUDUSD | 60–100 | 0.5–1.5 | High |
| NZDUSD | 70–110 | 1.0–2.0 | Medium |
| EURGBP | 30–60 | 0.5–1.0 | Medium |
| EURJPY | 60–100 | 0.5–1.0 | Medium |
| GBPJPY | 80–130 | 1.0–2.0 | Medium |
| AUDJPY | 70–110 | 1.0–2.0 | Medium |

The six majors (EURUSD, GBPUSD, USDJPY, USDCAD, AUDUSD, NZDUSD) provide sufficient breadth for most MFT approaches while keeping transaction costs low. Adding the four crosses above increases breadth without a significant increase in correlation.

### 8.3 Step 3: Signal Combination

The AQR standard for signal combination: equal-weight cross-sectional z-scores.

```python
def combine_signals(signal_dict: dict, 
                     weights: dict = None) -> pd.DataFrame:
    """
    Combine multiple signals into a composite MFT signal.
    
    Parameters
    ----------
    signal_dict : dict
        Keys = signal names; values = pd.DataFrame (dates × instruments)
    weights : dict
        Optional signal weights (default: equal weights)
    
    Returns
    -------
    pd.DataFrame
        Composite signal (dates × instruments), z-scored
    """
    if weights is None:
        weights = {name: 1.0 for name in signal_dict}
    
    # Normalise weights to sum to 1
    total_w = sum(weights.values())
    weights = {k: v / total_w for k, v in weights.items()}
    
    # Z-score each signal cross-sectionally (across instruments, on each date)
    z_signals = {}
    for name, df in signal_dict.items():
        z_signals[name] = df.apply(
            lambda row: (row - row.mean()) / (row.std() + 1e-8), axis=1
        )
    
    # Weighted combination
    composite = sum(
        weights[name] * z_signals[name] 
        for name in signal_dict
    )
    
    # Final z-score of composite
    composite = composite.apply(
        lambda row: (row - row.mean()) / (row.std() + 1e-8), axis=1
    )
    
    return composite


def build_fx_mft_signals(data: dict) -> pd.DataFrame:
    """
    Full FX MFT signal construction pipeline.
    
    data : dict with keys:
        'us_2y', 'eur_2y', 'gbp_2y', 'jpy_2y', 'aud_2y', 'cad_2y', 'nzd_2y'
        'cot_eur', 'cot_gbp', 'cot_jpy', 'cot_aud', 'cot_cad', 'cot_nzd'
        'cb_surprise_fed', 'cb_surprise_ecb', ...
        'macro_surprise_us', 'macro_surprise_eur', ...
    """
    signals = {}
    
    # 1. Rate differential change signals
    # For each USD pair: Δ(US_2Y - Foreign_2Y)
    for ccy in ['eur', 'gbp', 'jpy', 'aud', 'cad', 'nzd']:
        pair = f'usd{ccy}' if ccy != 'eur' else 'eurusd'
        spread = data['us_2y'] - data[f'{ccy}_2y']
        delta_spread = spread.diff(1)
        signals[f'rate_diff_{pair}'] = delta_spread.rolling(60).apply(
            lambda x: (x[-1] - x.mean()) / (x.std() + 1e-8), raw=True
        )
    
    # 2. COT positioning change signals
    for ccy in ['eur', 'gbp', 'jpy', 'aud', 'cad', 'nzd']:
        cot = data[f'cot_{ccy}']
        # Weekly data; forward-fill to daily
        cot_daily = cot.resample('D').ffill()
        cot_change = cot_daily.diff(5)  # 5-day change (one COT cycle)
        signals[f'cot_{ccy}'] = (cot_change - cot_change.rolling(52*5).mean()) / \
                                  (cot_change.rolling(52*5).std() + 1e-8)
    
    # 3. Central bank surprise signals (sparse; only on event days)
    for event, col in [('fed', 'eurusd'), ('ecb', 'eurusd')]:
        surprise_signal = pd.Series(0.0, index=data[f'cb_surprise_{event}'].index)
        surprise_dates = data[f'cb_surprise_{event}'].dropna().index
        for date in surprise_dates:
            surprise_val = data[f'cb_surprise_{event}'].loc[date]
            # Decay over 3 days
            for d in range(1, 4):
                future_date = date + pd.Timedelta(days=d)
                if future_date in surprise_signal.index:
                    surprise_signal[future_date] += surprise_val * (1 - d/4)
        signals[f'cb_{event}'] = surprise_signal
    
    # Combine into a composite signal per currency pair
    pair_signals = {}
    for pair in ['eurusd', 'gbpusd', 'usdjpy', 'usdcad', 'audusd', 'nzdusd']:
        relevant = {k: v for k, v in signals.items() if pair[:3] in k or pair[3:] in k}
        if relevant:
            pair_signals[pair] = pd.concat(relevant, axis=1).mean(axis=1)
    
    return pd.DataFrame(pair_signals)
```

### 8.4 Step 4: Position Sizing

```python
def fx_mft_position_sizing(composite_signal: pd.DataFrame,
                             fx_daily_vol: pd.DataFrame,
                             daily_vol_target: float = 0.005,
                             max_position_pct: float = 0.03) -> pd.DataFrame:
    """
    Position sizing for FX MFT strategy.
    
    Positions are expressed as fraction of total portfolio notional.
    
    Parameters
    ----------
    composite_signal : pd.DataFrame
        Combined signal, z-scored (dates × pairs)
    fx_daily_vol : pd.DataFrame
        Estimated daily volatility for each FX pair (dates × pairs)
    daily_vol_target : float
        Target daily portfolio volatility (0.5% = 8% annual)
    max_position_pct : float
        Maximum position per pair as fraction of notional (3%)
    """
    # Raw position: scale signal by vol target
    n_pairs = composite_signal.shape[1]
    raw_position = (daily_vol_target / np.sqrt(n_pairs)) / fx_daily_vol
    raw_position = raw_position * composite_signal
    
    # Clip to maximum position
    positions = raw_position.clip(-max_position_pct, max_position_pct)
    
    return positions
```

**Worked example:**

Suppose EURUSD has:
- Daily vol: 0.6% (approximately 60 pips)
- Composite signal z-score: +1.5 (moderately bullish EUR)
- Number of pairs: 6

Position = (0.5% / √6) / 0.6% × 1.5 = 0.204% / 0.6% × 1.5 = 0.51

This means 0.51% of portfolio notional in EURUSD (long EUR, short USD). For a $10M portfolio, this is $51,000 notional — entirely manageable for G10 FX liquidity.

### 8.5 Step 5: Risk Management Overlay

```python
def apply_full_risk_overlay(positions: pd.DataFrame,
                              portfolio_returns: pd.Series,
                              vix: pd.Series,
                              correlation_threshold: float = 0.7,
                              daily_dd_limit: float = -0.01) -> pd.DataFrame:
    """
    Apply the full risk management overlay to raw positions.
    
    1. VIX scaling
    2. Rolling drawdown control
    3. Daily drawdown stop
    4. Correlation cap
    """
    modified = positions.copy()
    
    # 1. VIX scaling
    vix_scale = (1 - (vix - 20) / 20).clip(0, 1)
    modified = modified.multiply(vix_scale, axis=0)
    
    # 2. Rolling 5-day P&L control
    rolling_pnl = portfolio_returns.rolling(5).sum()
    pnl_scale = ((rolling_pnl + 0.02) / 0.02).clip(0.2, 1.0)
    modified = modified.multiply(pnl_scale, axis=0)
    
    # 3. Daily drawdown stop
    for date in modified.index:
        if date in portfolio_returns.index and portfolio_returns[date] < daily_dd_limit:
            # Set all positions to zero for the rest of the day
            # (In live trading: stop all trading; in backtest: set next day to 0)
            idx = modified.index.get_loc(date)
            if idx + 1 < len(modified):
                modified.iloc[idx + 1] = 0
    
    # 4. Correlation cap
    # If any two positions have rolling 5-day correlation > 0.7, reduce the later one
    pair_returns = positions.multiply(
        portfolio_returns.shift(1).rename('port'), axis=0
    )
    rolling_corr = pair_returns.rolling(5).corr()
    # (Simplified: in practice, compute pairwise correlation matrix)
    
    return modified
```

### 8.6 Step 6: Transaction Cost Model

Transaction costs are the most common killer of MFT strategies in backtesting. If you model zero or naive costs, your backtest will show spectacular Sharpe ratios that collapse in live trading.

**Institutional FX round-trip cost structure:**

| Cost Component | G10 Major (bps) | G10 Cross (bps) | EM Pair (bps) |
|---|---|---|---|
| Bid-ask spread (quoted) | 0.2–0.5 | 0.5–1.0 | 5–20 |
| Market impact (at scale) | 0.2–0.5 | 0.5–1.0 | 2–10 |
| Financing (overnight) | 0–0.5/day | 0–0.5/day | 0.5–2/day |
| **Total round-trip** | **0.5–1.5** | **1.0–2.0** | **7–30** |

For a daily-rebalancing strategy with average 20% of positions changing daily:
- Annual turnover ≈ 52× notional (20% × 252 days)
- Annual cost ≈ 52 × 1.0 bps = 52 bps (for G10 majors)

**Minimum IC requirement:**

To cover 52 bps/year in transaction costs, the signal needs to generate:
- At daily breadth of ~5,040 bets/year: IC × √5,040 > 0.52 / annual_vol
- For a 8% annual vol target: 0.52/8 = 0.065 minimum IR → minimum IC ≈ 0.065 / √5,040 ≈ 0.001

This seems low, but remember: you need IC > 0.001 **per trade** — and any model that delivers IC = 0.001 consistently over thousands of trades is already impressive. More practically, you want IC > 0.03 to have a comfortable buffer above transaction costs.

```python
def estimate_annual_transaction_costs(positions: pd.DataFrame,
                                       prices: pd.DataFrame,
                                       rt_cost_bps: float = 1.0) -> pd.Series:
    """
    Estimate daily and annual transaction costs.
    
    Parameters
    ----------
    positions : pd.DataFrame
        Daily positions as fraction of notional
    rt_cost_bps : float
        Round-trip cost in basis points
    """
    rt_cost = rt_cost_bps / 10000
    
    # Position changes (turnover)
    position_changes = positions.diff().abs()
    daily_cost = position_changes * rt_cost / 2  # one-way cost per direction change
    total_daily_cost = daily_cost.sum(axis=1)
    
    annual_cost_estimate = total_daily_cost.mean() * 252
    
    print(f"Average daily cost: {total_daily_cost.mean()*100:.3f}%")
    print(f"Estimated annual cost: {annual_cost_estimate*100:.2f}%")
    
    return total_daily_cost
```

---

<a name="section-9"></a>
## Section 9: MFT vs. Other Strategy Types — Comparative Analysis

### 9.1 The Full Landscape

| Dimension | HFT | MFT (this document) | Low-Frequency Systematic | Discretionary Macro |
|---|---|---|---|---|
| **Holding period** | Microseconds–minutes | 1–20 days | Weekly–quarterly | Days–months |
| **Signal type** | Order flow, latency, microstructure | Price, macro, events, positioning | Factor tilts, valuation | Economic views, policy, flows |
| **Infrastructure** | Co-location, FPGA, nanosecond | Standard API, daily data | Standard execution | Bloomberg terminal |
| **Competitive intensity** | Extreme (winner-take-all) | High but not winner-take-all | Moderate (crowded factors) | Lower (judgment-driven) |
| **Capacity** | Very low ($1M–$50M) | Medium ($100M–$5B) | Very high ($10B+) | Variable |
| **Typical net Sharpe** | 2–5 (profitable few) | 1.0–2.5 | 0.5–1.0 | 0.3–1.5 (wide variance) |
| **Signal decay risk** | High (but abundant new signals) | High-medium | Low-medium | Low (views evolve slowly) |
| **Data advantage importance** | Extreme | High | Medium | Low |
| **Team size (typical)** | 5–100 engineers | 3–30 researchers | 5–50 researchers | 1–10 PMs |
| **Technology barrier** | Very high | Medium | Low-medium | Low |
| **Skill transferred from discretionary** | Low | High | Medium | Full |

### 9.2 Why MFT Is the Natural Transition for Discretionary Macro

A discretionary macro trader's core competencies map directly to MFT:

1. **Understanding central bank reaction functions** → Central bank surprise signals (Section 4.1)
2. **Reading macro data releases** → Macro surprise signals (Section 4.2)
3. **Positioning analysis (COT, flow data)** → COT and ETF flow signals (Section 2.3)
4. **Cross-asset relationships** → Statistical arbitrage across FX and rates (Section 3)
5. **Event calendar management** → Event-driven MFT (Section 4)

The key gap: discretionary traders do not systematically track their IC (the correlation between their forecasts and outcomes). MFT forces you to build this infrastructure. The payoff: once you can measure IC, you can improve it — something impossible when trades are ad hoc.

### 9.3 Capacity Constraints by Strategy Type

Capacity is a function of how much alpha decays as AUM increases. At each frequency:

- **HFT**: capacity of $10–100M per strategy. Market impact is immediate at scale.
- **MFT**: capacity of $100M–$5B per strategy. A pod with $1B AUM can trade $100M/day in G10 FX without meaningful market impact. Beyond $5B for a single strategy, impact starts to matter.
- **Low-frequency**: virtually unlimited for the very largest factor funds (AQR manages $140B+ and still generates factor returns, though at compressing Sharpe ratios).

For a practitioner managing $10–500M, MFT is the natural frequency: signal-based, implementable at scale, with sufficient breadth to generate statistical power.

### 9.4 When Each Frequency Works Best

**HFT works best when:**
- Markets are in a clear microstructure equilibrium (normal market conditions, not around macro events).
- Order flow is predictable (e.g., end-of-month fixing flows in FX).
- Technology infrastructure is maintained at cutting edge.

**MFT works best when:**
- Information is released at discrete points (earnings, central bank meetings, data releases).
- Signals have persistent half-lives of days (not seconds).
- Volatility is moderate (VIX 15–25); high volatility destroys signal-to-noise; low volatility compresses returns.

**Low-frequency works best when:**
- Factor premia are wide (after a factor has underperformed and become cheaper).
- Market structure is stable (no regime changes in correlations or factor loadings).
- Long-only or constrained mandates prevent short-selling of overpriced assets.

---

<a name="section-10"></a>
## Section 10: Practical Roadmap — From Discretionary Macro to MFT

### 10.1 Phase 1 (Months 1–3): Documentation and Hypothesis Formation

**The trade journal discipline:**

Every discretionary trader believes they have edge. Systematising requires proving it. The first step is building a rigorous retrospective trade database. For every trade in the last 3 years, record:

| Field | Example |
|---|---|
| Entry date | 2023-11-01 |
| Exit date | 2023-11-07 |
| Instrument | EURUSD |
| Direction | Long EUR |
| Rationale category | Rate differential (ECB hawkish surprise) |
| Signal strength at entry (1–5) | 4 |
| Outcome | +0.8% |
| Was signal right? | Yes (EUR appreciated) |
| Was size appropriate? | Medium (should have been larger) |

After 30–50 trades, you can begin computing:
- **Hit rate** by category: % of trades where direction was correct.
- **Average return** by category.
- **Signal IC**: correlation between your "strength rating" and actual return.

**Hypothesis formation from your own data:**

Look for categories where:
1. Hit rate > 55% (above 50% suggests genuine edge).
2. Average winner > average loser × 1.2 (positive expected value per trade).
3. Hit rate is consistent across different market regimes (not just during one trending period).

This is the seed of your systematic signal. You are not inventing a new signal — you are systematising a signal you already use.

**Build a daily signal tracking spreadsheet:**

Before any backtesting, start tracking your signals live with daily updates:
- Day 1: record signal strength (−2 to +2).
- Day 5: record actual return over the holding period.
- After 3 months: compute rolling IC on 60-day window.

A live IC of 0.04–0.08 over 60 observations is consistent with a Sharpe > 1.0 at scale.

### 10.2 Phase 2 (Months 3–6): First Systematic Backtest

**Step 1: Data sourcing**

Free, high-quality data sources:
- **FRED (Federal Reserve Economic Data)**: US and international yield data, macro releases (fredapi Python library for programmatic access)
- **Yahoo Finance (yfinance)**: FX daily spot rates going back 20+ years
- **CFTC.gov**: COT positioning data (free download)
- **Quandl/Nasdaq Data Link**: macro data (some free tiers)
- **ForexFactory.com**: macro event calendar (free, community-maintained)
- **FRBSF**: Monetary Policy Surprise dataset (free)

```python
import yfinance as yf
import pandas_datareader as pdr
from fredapi import Fred

# G10 FX spot rates
pairs = ['EURUSD=X', 'GBPUSD=X', 'JPY=X', 'CADUSD=X', 'AUDUSD=X', 'NZDUSD=X']
fx_data = yf.download(pairs, start='2005-01-01', end='2025-12-31')['Close']
fx_data.columns = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD']

# 2Y yields from FRED
fred = Fred(api_key='YOUR_FREE_FRED_API_KEY')  # Register at fred.stlouisfed.org
us_2y = fred.get_series('DGS2')       # US 2Y constant maturity yield
de_2y = fred.get_series('IRLTST01DEM156N')  # German 2Y yield (ECB)
```

**Step 2: Simple backtest architecture**

```python
import numpy as np
import pandas as pd
from scipy import stats

def simple_backtest(signal: pd.Series, 
                     returns: pd.Series,
                     holding_period: int = 5,
                     transaction_cost_bps: float = 1.0) -> dict:
    """
    Simple backtest for a single signal on a single instrument.
    
    Parameters
    ----------
    signal : pd.Series
        Daily signal (positive = long, negative = short, 0 = flat)
    returns : pd.Series
        Daily returns of the instrument
    holding_period : int
        Target holding period in days
    """
    tc = transaction_cost_bps / 10000
    
    # Position: sign of signal (binary long/short)
    position = np.sign(signal).shift(1)  # Shift to avoid lookahead bias
    
    # Transaction cost: applied when position changes
    position_changes = position.diff().abs()
    
    # Daily P&L
    gross_pnl = position * returns
    cost_pnl = -position_changes * tc / 2  # Half round-trip per direction change
    net_pnl = gross_pnl + cost_pnl
    
    # Performance metrics
    ann_return = net_pnl.mean() * 252
    ann_vol = net_pnl.std() * np.sqrt(252)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    
    # IC (Information Coefficient)
    ic = signal.shift(1).corr(returns)
    
    # Maximum drawdown
    cumulative = (1 + net_pnl).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    # Deflated Sharpe Ratio (Bailey-López de Prado 2014)
    n = len(net_pnl.dropna())
    sharpe_skew = net_pnl.skew()
    sharpe_kurt = net_pnl.kurtosis()
    
    # Minimum acceptable Sharpe (adjusted for higher moments)
    sr_star = np.sqrt(1/n) * (1 - sharpe_skew * sharpe + 
                               (sharpe_kurt - 1) / 4 * sharpe**2)
    p_value = 1 - stats.norm.cdf(
        (sharpe - sr_star) / np.sqrt(1/n)
    )
    
    return {
        'ann_return': ann_return,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'ic': ic,
        'n_observations': n,
        'deflated_p_value': p_value,
        'net_pnl': net_pnl,
        'cumulative_pnl': cumulative
    }
```

**Step 3: Validating your signal**

Apply the Deflated Sharpe Ratio (DSR) test (Bailey and López de Prado, 2014) to correct for multiple-testing bias. If you tested 10 variations of your signal and report the best one, you need a much higher Sharpe to claim it is truly significant.

Rule of thumb:
- If you ran 1 backtest: Sharpe > 1.0 and DSR p-value < 0.05 is acceptable.
- If you ran 5–10 backtests and report the best: Sharpe > 1.5 required.
- If you ran 20+ backtests: Sharpe > 2.0, and OOS (out-of-sample) validation is mandatory.

**Walk-forward validation:**

```python
def walk_forward_backtest(signal_fn, 
                           price_data: pd.DataFrame,
                           train_years: int = 5,
                           test_years: int = 1) -> pd.DataFrame:
    """
    Walk-forward validation: train on 5 years, test on 1, roll forward.
    
    Parameters
    ----------
    signal_fn : callable
        Function that takes price_data and returns a signal Series
    """
    results = []
    
    total_years = (price_data.index[-1] - price_data.index[0]).days / 365.25
    n_folds = int((total_years - train_years) / test_years)
    
    for fold in range(n_folds):
        # Training window
        train_start = price_data.index[0] + pd.DateOffset(years=fold * test_years)
        train_end = train_start + pd.DateOffset(years=train_years)
        
        # Testing window
        test_start = train_end
        test_end = test_start + pd.DateOffset(years=test_years)
        
        # Estimate parameters on training data
        train_data = price_data.loc[train_start:train_end]
        
        # Generate signal on test data using parameters from training
        test_data = price_data.loc[test_start:test_end]
        signal = signal_fn(train_data, test_data)
        
        results.append({
            'fold': fold,
            'period': f"{test_start.date()} to {test_end.date()}",
            'sharpe': signal['sharpe'],
            'max_dd': signal['max_drawdown'],
            'ic': signal['ic']
        })
    
    return pd.DataFrame(results)
```

**Decision criteria after Phase 2:**
- Proceed if: DSR > 0.5 AND Sharpe > 1.0 in OOS periods AND IC is positive in at least 60% of OOS windows.
- Stop if: OOS Sharpe < 0.5 OR IC is negative in majority of OOS windows. (Backtest Sharpe of 3.0 with OOS Sharpe of 0.3 is a common and painful experience.)

### 10.3 Phase 3 (Months 6–12): Signal Combination and Portfolio Construction

**Diversification across signals:**

Add 2–3 more signals that are:
1. **Logically distinct**: rate differential change, COT positioning, central bank surprise — these have different generating mechanisms and should be less than perfectly correlated.
2. **Empirically uncorrelated**: measure the correlation of the signals' **daily P&L** (not the signals themselves) over the training period. Target pairwise correlation < 0.3.
3. **Covering different instruments**: a signal that works on EURUSD but not USDJPY, combined with one that works on USDJPY but not EURUSD, provides genuine diversification.

**Portfolio-level walk-forward test:**

Now run the full portfolio backtest with signal combination, position sizing, and risk overlay. Key targets:
- Combined Sharpe > 1.5
- Maximum drawdown < 20%
- Annual transaction costs modelled explicitly (not assumed away)
- OOS Sharpe within 80% of in-sample Sharpe (OOS / IS Sharpe ratio > 0.8)

If the OOS Sharpe is less than 60% of the in-sample Sharpe, the signal is likely overfit. Return to Step 2.

### 10.4 Phase 4 (Months 12–24): Live Trading and Monitoring

**Starting size discipline:**

Begin at 5–10% of your usual discretionary trading size. The purpose is not to make money in this phase — it is to identify implementation gaps between backtest and live:
- Does the signal compute correctly in real time from the same data sources?
- Is execution at the assumed costs achievable?
- Is the P&L correlation with the backtest sufficient (> 0.7 rolling monthly)?

**Live monitoring dashboard — build this before Day 1:**

```python
class MFTMonitor:
    """
    Daily monitoring for live MFT strategy.
    """
    def __init__(self, backtest_ic: float, backtest_sharpe: float):
        self.backtest_ic = backtest_ic
        self.backtest_sharpe = backtest_sharpe
        self.live_signals = []
        self.live_returns = []
        self.live_pnl = []
    
    def daily_update(self, signal: float, return_realised: float, pnl: float):
        self.live_signals.append(signal)
        self.live_returns.append(return_realised)
        self.live_pnl.append(pnl)
    
    def compute_live_ic(self, window: int = 60) -> float:
        if len(self.live_signals) < window:
            return None
        signals = np.array(self.live_signals[-window:])
        returns = np.array(self.live_returns[-window:])
        return np.corrcoef(signals[:-1], returns[1:])[0, 1]
    
    def signal_health_check(self) -> dict:
        live_ic = self.compute_live_ic()
        if live_ic is None:
            return {'status': 'insufficient_data'}
        
        ic_ratio = live_ic / self.backtest_ic
        live_sharpe = (np.mean(self.live_pnl) * 252) / (np.std(self.live_pnl) * np.sqrt(252) + 1e-8)
        sharpe_ratio = live_sharpe / self.backtest_sharpe
        
        status = 'healthy'
        if ic_ratio < 0.5:
            status = 'degraded_ic'  # Signal has decayed significantly
        if ic_ratio < 0:
            status = 'signal_broken'  # Signal is generating negative IC live
        if sharpe_ratio < 0.4:
            status = 'underperforming'
        
        return {
            'live_ic': live_ic,
            'backtest_ic': self.backtest_ic,
            'ic_ratio': ic_ratio,
            'live_sharpe': live_sharpe,
            'sharpe_ratio': sharpe_ratio,
            'status': status,
            'observations': len(self.live_signals)
        }
```

**Key metrics to track daily:**
1. **Rolling 60-day live IC vs. backtest IC**: the most important health indicator.
2. **Daily drawdown vs. maximum drawdown from backtest**: if live drawdown exceeds 1.5× the historical max drawdown, investigate before adding size.
3. **Signal auto-correlation**: if the signal's daily changes become highly autocorrelated (> 0.5), it may be fitting to recent noise.
4. **P&L attribution**: break down daily P&L by signal and by instrument. If all P&L is coming from one instrument and one signal, the strategy is not as diversified as you thought.

**The discretionary override protocol:**

Even in a systematic strategy, extreme macro events can make purely mechanical execution reckless. Build an explicit protocol for overrides:

- **Acceptable overrides**: reducing size before a scheduled high-impact event (e.g., reducing USDJPY position by 50% before an unscheduled BoJ meeting).
- **Unacceptable overrides**: adding size because you have a "strong view." Overriding to add risk defeats the purpose of systematic risk management.
- **Record all overrides**: note the date, the decision, and the reason. After 6 months, evaluate whether your overrides added or subtracted value. Evidence from discretionary traders running systematic overlays is mixed — overrides often hurt.

---

## Appendix A: Key Academic Papers Reference

| Paper | Authors | Journal | Year | Key Finding | Relevance to MFT |
|---|---|---|---|---|---|
| Returns to Buying Winners and Selling Losers | Jegadeesh, Titman | JF | 1993 | 3–12 month momentum; 1-month skip for reversal | Foundation of momentum signals |
| Co-integration and Error Correction | Engle, Granger | Econometrica | 1987 | Formal cointegration framework | Foundation of stat arb |
| Pairs Trading: Relative-Value Arbitrage | Gatev, Goetzmann, Rouwenhorst | RFS | 2006 | Distance method; 11% excess returns 1962–2002 | Classic pairs strategy reference |
| Post-Earnings-Announcement Drift | Bernard, Thomas | JAR | 1989 | 18% annualised from SUE portfolios | PEAD signal |
| Micro Effects of Macro Announcements | Andersen, Bollerslev, Diebold, Vega | AER | 2003 | FX price discovery around macro releases | Macro surprise signal timing |
| Time Series Momentum | Moskowitz, Ooi, Pedersen | JFE | 2012 | TSMOM across 58 futures; Sharpe > 1.2 | Weekly TSMOM implementation |
| Long-Lasting Momentum in Weekly Returns | Gutierrez, Kelley | JF | 2008 | Brief reversal followed by sustained continuation | MFT entry timing |
| Monetary Non-Neutrality: Information Effect | Nakamura, Steinsson | QJE | 2018 | CB hikes can be dovish via information channel | Central bank event trading |
| A Tug of War: Overnight vs. Intraday Returns | Lou, Polk, Skouras | JFE | 2019 | Overnight vs intraday return decomposition | Gap signal construction |
| Fundamental Law of Active Management | Grinold, Kahn | Book | 2000 | IR = IC × √BR | MFT breadth argument |

---

## Appendix B: Free Data Sources for MFT Research

| Data Type | Source | URL | Update Frequency |
|---|---|---|---|
| G10 FX spot rates | Yahoo Finance (yfinance) | finance.yahoo.com | Daily |
| US Treasury yields (2Y, 5Y, 10Y) | FRED | fred.stlouisfed.org | Daily |
| Euro area yields | FRED / ECB Statistical Warehouse | sdw.ecb.europa.eu | Daily |
| Fed monetary policy surprises | FRBSF | frbsf.org/economic-research | Per FOMC meeting |
| CFTC COT data | CFTC.gov | cftc.gov/MarketReports | Weekly (released Fri) |
| Macro event calendar | ForexFactory | forexfactory.com/calendar | Daily |
| US macro releases | FRED | fred.stlouisfed.org | As released |
| US equity prices | Yahoo Finance / yfinance | — | Daily |
| VIX data | Yahoo Finance (^VIX) | — | Daily |
| S&P 500 earnings | Compustat / free alternative: Macrotrends.net | macrotrends.net | Quarterly |
| MSCI rebalancing announcements | MSCI.com | msci.com | Quarterly |

---

## Appendix C: Glossary

**Breadth (BR):** Number of independent investment bets per year. In Grinold-Kahn, IR = IC × √BR.

**Deflated Sharpe Ratio (DSR):** Sharpe ratio adjusted for the number of strategies tested and non-normality of returns. Used to assess whether a backtest result is statistically significant.

**Half-life of a signal:** The time horizon over which a signal's predictive power decays to 50% of its initial value. At MFT, half-lives range from 1 to 20 trading days.

**IC (Information Coefficient):** Spearman or Pearson correlation between today's signal and tomorrow's (or next-period's) actual return. The primary measure of signal quality.

**Information Ratio (IR):** Annualised active return divided by annualised active risk. Equivalent to Sharpe ratio for a market-neutral strategy.

**MFT (Medium Frequency Trading):** Systematic strategies with holding periods of 1–20 trading days. Distinct from HFT (sub-minute) and low-frequency systematic (monthly/quarterly).

**OIS (Overnight Index Swap):** Interest rate swap where the floating leg is linked to the overnight rate. OIS rates are used to derive market expectations for future central bank policy rates.

**PEAD (Post-Earnings-Announcement Drift):** The empirical tendency for stock prices to continue drifting in the direction of an earnings surprise for 30–60 trading days.

**Pod:** An autonomous P&L unit within a multi-strategy hedge fund (Millennium, Balyasny, Citadel). Each pod is an independent team with its own capital allocation, strategy, and P&L tracking.

**Stat Arb (Statistical Arbitrage):** Trading strategies that exploit mean-reverting deviations from historical or structural relationships between assets. Not true arbitrage (involves risk).

**SUE (Standardised Unexpected Earnings):** The earnings surprise divided by its historical standard deviation, allowing comparison across companies and reporting periods.

**TSMOM (Time-Series Momentum):** The tendency for an asset with positive returns over the past 12 months to continue generating positive returns (and vice versa). Documented by Moskowitz-Ooi-Pedersen (2012).

**UIP (Uncovered Interest Rate Parity):** The theory that high-rate currencies should depreciate by exactly the rate differential. Empirically fails in the short run — this failure is the basis of the carry trade.

**VIX:** The CBOE Volatility Index; measures the market's expectation of 30-day S&P 500 volatility implied by options prices. Used as a risk-on/risk-off filter.

**Z-Score:** Standardised deviation from mean: (value − mean) / standard deviation. The universal normalisation for combining signals from different instruments and different economic environments.

---

*This document is intended as a private research and learning resource. All trading involves risk. Past academic findings do not guarantee future performance.*

*Prepared for NotebookLM ingestion — June 2026.*
