# Statistical Toolkit for the Transitioning Discretionary Trader
## A Complete Reference: From Hypothesis Testing to Machine Learning

*Target reader: An experienced discretionary FX/macro trader with strong market intuition and no formal statistics background, moving toward systematic quantitative trading.*

---

## Table of Contents

1. Statistical Foundations for Trading
2. Regression Analysis for Signal Testing
3. Time Series Analysis — ARIMA, GARCH, VAR
4. Cointegration and Pairs Trading
5. Bayesian Methods for Systematic Traders
6. Machine Learning Essentials for Finance
7. Signal Construction — A Complete Toolkit
8. Backtesting Framework — Building It Right
9. Performance Measurement and Monitoring
10. Python Learning Path — A 6-Month Curriculum

---

## Section 1: Statistical Foundations for Trading

### 1.1 Why Statistics Instead of Intuition?

A discretionary trader who has been right 60% of the time over 100 trades has a strong intuition. But here is the mathematical problem: if the true win rate is 50% (pure luck), there is a 5.7% chance of achieving 60%+ in 100 trades just by chance. That is not comforting — roughly 1 in 17 traders who are picking randomly will look like they have genuine edge.

Statistics exists to distinguish signal from noise. In systematic trading, this distinction is the entire job.

The core question you must answer about every strategy: **"What is the probability that this result occurred by luck?"**

### 1.2 Probability Distributions — What You Need to Know

**The Normal (Gaussian) distribution:**
- The bell curve. Symmetric, fully described by mean (μ) and standard deviation (σ).
- The assumption underlying most statistical tests.
- Daily stock and FX returns are *approximately* normal but with *fat tails*.

**Fat tails (leptokurtosis):**
- Financial returns have more extreme events than the normal distribution predicts.
- Kurtosis measures the "heaviness" of tails. Normal distribution has kurtosis = 3. FX daily returns typically have kurtosis of 5–8.
- Practical implication: your VaR (Value at Risk) based on normality will underestimate losses. The 2008 crisis, the 2015 SNB event, the 2020 COVID crash — all were "impossible" under normality.
- The Student's t-distribution with 3–5 degrees of freedom fits FX returns better than the normal.

**Skewness:**
- Asymmetry of a distribution. Carry trade returns are *negatively skewed*: many small positive returns (earned premium), occasionally large losses (carry unwind).
- Negative skewness means the Sharpe ratio overstates the true risk-adjusted attractiveness. A strategy with SR = 1.5 and skewness = -1.5 is less attractive than SR = 1.0 and skewness = 0.
- Always report skewness alongside Sharpe.

**Log-normal distribution:**
- Prices (not returns) follow a log-normal distribution — prices can't go negative, and compounding creates asymmetry.
- For multi-period analysis: use log returns = ln(P_t / P_{t-1}), not simple returns.
- Log returns are additive: total log return over 10 days = sum of 10 daily log returns.

**What distribution do G10 FX returns actually follow?**

| Pair | Excess Kurtosis | Skewness | Best Fit |
|---|---|---|---|
| EURUSD | 3.2 – 5.0 | -0.1 to -0.3 | t(4–5 df) |
| USDJPY | 4.0 – 6.5 | 0.1 to 0.5 | t(3–4 df) |
| GBPUSD | 5.0 – 8.0 | -0.2 to -0.8 | t(3–4 df) |
| AUDUSD | 3.0 – 4.5 | -0.2 to 0.2 | t(5 df) |

### 1.3 Hypothesis Testing — The Core Framework

Every time you test a trading strategy, you are running a hypothesis test. Understanding it deeply is essential.

**The null hypothesis in trading:**
> H₀: This signal has no predictive power (expected return = 0, or IC = 0)
> H₁: This signal has positive predictive power

**The t-statistic:**
```
t = (mean_return) / (standard_error_of_mean_return)
  = (mean_return × √N) / standard_deviation_of_returns
```

Where N is the number of observations. For an annualised Sharpe ratio S with N annual observations:
```
t = S × √N
```

A Sharpe ratio of 1.0 over 10 years (N=10) has t = 3.16 — barely significant at 5% level with multiple testing.

**The p-value:**
- The probability that you would observe a t-statistic this large if H₀ were true.
- p < 0.05: result is unlikely by chance alone (conventional threshold).
- p < 0.01: result is very unlikely by chance.
- In trading with multiple strategies tested: p < 0.003 (t > 3.0) is the minimum — this is Harvey, Liu & Zhu (2016)'s finding.

**Why p < 0.05 is not enough for trading:**

Harvey, Liu & Zhu (2016, Review of Financial Studies) catalogued 316+ factors published in finance journals. They show that with this many tests, the expected number of "significant" false discoveries at p < 0.05 is enormous. Their recommendation: require t > 3.0 (p < 0.0026) for new factor claims.

This is sobering: a strategy showing t = 2.5 in a 10-year backtest has a meaningful probability of being random noise.

**Statistical power:**
Power = probability of detecting a real effect given that it exists.

For IC = 0.03 (a modest but real signal):
- N = 100 observations: power ≈ 17% (you'll miss the real signal 83% of the time)
- N = 500 observations: power ≈ 53%
- N = 1000 observations: power ≈ 78%
- N = 2000 observations: power ≈ 96%

This explains why daily signals (252 obs/year) are statistically more tractable than monthly signals (12 obs/year). You need 10+ years of monthly data to have confidence in a monthly signal.

### 1.4 The Information Coefficient (IC)

The IC is the standard measure of signal quality used throughout the quant industry.

```
IC = Spearman rank correlation(signal[t], return[t+1])
```

Using Spearman rank correlation rather than Pearson is standard because:
1. Ranks are robust to outlier returns.
2. We care about monotonic, not linear, relationships.

**Interpreting IC values:**

| IC | Quality | Context |
|---|---|---|
| < 0.01 | Noise / reject | Not worth pursuing |
| 0.01 – 0.03 | Weak but possibly real | Need very large N to confirm |
| 0.03 – 0.05 | Moderate — typical live signals | Institutional funds work with these |
| 0.05 – 0.10 | Strong signal | Rare; often decays post-discovery |
| > 0.10 | Exceptional | Suspect look-ahead bias; verify carefully |

**A daily IC of 0.03 is considered good.** A signal with IC = 0.05 is exceptional. The rate-differential-change signal in this repository (Strategy #1) has measured IC in the range that produces its observed Sharpe of 2.75 — though this needs the timestamp-alignment verification noted in RESEARCH.md.

```python
import pandas as pd
from scipy.stats import spearmanr

def compute_ic(signal: pd.Series, returns: pd.Series, lag: int = 1) -> float:
    """Spearman IC between signal and future returns."""
    aligned = pd.DataFrame({'signal': signal, 'fwd_return': returns.shift(-lag)}).dropna()
    ic, pvalue = spearmanr(aligned['signal'], aligned['fwd_return'])
    return ic, pvalue

# Monthly rolling IC
def rolling_ic(signal, returns, window=63):
    """Rolling 63-day IC to monitor signal health over time."""
    ics = []
    for i in range(window, len(signal)):
        s = signal.iloc[i-window:i]
        r = returns.iloc[i-window:i]
        ic, _ = spearmanr(s, r)
        ics.append({'date': signal.index[i], 'ic': ic})
    return pd.DataFrame(ics).set_index('date')
```

### 1.5 ICIR — The Consistency Measure

```
ICIR = mean(IC) / std(IC)
```

The ICIR (IC Information Ratio) measures how *consistently* the signal works, not just its average strength.

- ICIR > 0.5: signal is stable enough for IC-weighted combination with other signals
- ICIR < 0.5: signal is inconsistent — use equal weighting or do not include
- ICIR > 1.0: exceptional consistency; rare

A signal with IC = 0.05 but ICIR = 0.2 (highly inconsistent) is less useful than a signal with IC = 0.03 and ICIR = 0.8 (very consistent). Consistency is what creates reliable P&L streams.

### 1.6 The Grinold-Kahn Fundamental Law of Active Management

The most important equation in quantitative portfolio management:

```
IR ≈ IC × √BR
```

Where:
- **IR** = Information Ratio (annualised α / annualised tracking error)
- **IC** = Information Coefficient (signal-to-return correlation)
- **BR** = Breadth (number of independent forecasts per year)

**Applied to this repository's rate-differential signal:**
- IC ≈ 0.05 (estimated from Sharpe and holding period)
- BR = 9 pairs × 252 signals/year ≈ 2,268 (but autocorrelation reduces effective BR to ~48)
- IR ≈ 0.05 × √48 ≈ 0.35 per unit — consistent with the observed performance when combined

**The key insight:** You can have a *weak* signal (IC = 0.02) and still produce excellent returns if you trade it across *many* instruments (high breadth). Conversely, a strong signal (IC = 0.10) applied to only one instrument gives limited IR.

This is why diversification across currency pairs matters: more breadth, same IC, higher IR.

---

## Section 2: Regression Analysis for Signal Testing

### 2.1 Simple Linear Regression

The workhorse of signal testing. Given a signal x and returns y:

```
y_t = α + β × x_t + ε_t
```

In trading terms:
- y = next-period FX return
- x = today's signal (e.g., rate differential change)
- α = intercept (constant drift — usually close to zero for FX)
- β = slope coefficient: for every 1-unit increase in x, expected return changes by β
- ε = residual error (the part of return not explained by x)

**R-squared interpretation:**
R² measures what fraction of return variation is explained by the signal.

In FX and other financial markets, R² of 1–7% is considered **good**. This sounds low, but it means:
- 93–99% of daily return variation is unexplained by any single signal.
- That 1–7% of predictability, consistently captured, is what generates alpha.

Do not be discouraged by low R². Professional models with R² of 3% have produced careers.

**Statistical significance of β:**
The t-statistic for β = β̂ / se(β̂). If t > 2, β is statistically distinguishable from zero at conventional thresholds.

### 2.2 Newey-West Standard Errors — Why You Must Use Them

**The problem:** Standard OLS assumes errors (ε_t) are independent and identically distributed (i.i.d.). Financial returns violate this — they exhibit:
1. **Serial correlation**: Today's return partially predicts tomorrow's (even if small).
2. **Heteroskedasticity**: Variance of returns changes over time (high-vol regimes vs. calm periods).

Using standard OLS standard errors when errors are autocorrelated produces standard errors that are *too small*, making your signal look more significant than it is. This is a common source of false alphas.

**The fix:** Newey-West (1987) standard errors are robust to both autocorrelation and heteroskedasticity.

```python
import statsmodels.api as sm
import numpy as np

def test_signal_significance(signal: pd.Series, returns: pd.Series, lags: int = 5):
    """
    Test signal predictive power with Newey-West standard errors.
    
    Parameters
    ----------
    signal : lagged signal (already shifted so signal[t] predicts returns[t])
    returns : forward returns
    lags : number of lags for Newey-West correction (rule of thumb: 4 × (T/100)^(2/9))
    """
    X = sm.add_constant(signal.dropna())
    y = returns.reindex(X.index)
    mask = X.notna().all(axis=1) & y.notna()
    X, y = X[mask], y[mask]
    
    # OLS with Newey-West HAC standard errors
    model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    
    print(f"β coefficient: {model.params.iloc[1]:.6f}")
    print(f"t-statistic (NW): {model.tvalues.iloc[1]:.2f}")
    print(f"p-value: {model.pvalues.iloc[1]:.4f}")
    print(f"R-squared: {model.rsquared:.4f}")
    print(f"N observations: {len(y)}")
    
    return model
```

### 2.3 The Fama-MacBeth Cross-Sectional Regression

When you have a signal measured across multiple instruments (e.g., rate differential for 9 G10 pairs) and want to test its cross-sectional predictive power, the Fama-MacBeth (1973) procedure is the industry standard.

**Procedure:**
1. For each time period t, run a cross-sectional regression: return_i,t = α_t + β_t × signal_i,t + ε_i,t
2. Collect the time series of β_t coefficients (one per period).
3. Test whether the mean β is significantly different from zero using a standard t-test.

This approach automatically handles:
- Cross-sectional correlation between instruments.
- Time-varying risk premiums.

```python
def fama_macbeth(signals_panel: pd.DataFrame, returns_panel: pd.DataFrame):
    """
    Fama-MacBeth cross-sectional regression.
    
    Parameters
    ----------
    signals_panel : DataFrame, index=dates, columns=currency pairs
    returns_panel : DataFrame of next-period returns, same shape
    
    Returns
    -------
    Mean β and t-statistic across periods
    """
    betas = []
    
    for date in signals_panel.index:
        x = signals_panel.loc[date].dropna()
        y = returns_panel.loc[date].reindex(x.index).dropna()
        x = x.reindex(y.index)
        
        if len(x) < 3:
            continue
        
        # Cross-sectional regression
        X = sm.add_constant(x)
        beta = np.linalg.lstsq(X, y, rcond=None)[0][1]
        betas.append(beta)
    
    betas = pd.Series(betas)
    mean_beta = betas.mean()
    t_stat = mean_beta / (betas.std() / np.sqrt(len(betas)))
    
    print(f"Mean β: {mean_beta:.6f}")
    print(f"t-statistic: {t_stat:.2f}")
    print(f"Observations (periods): {len(betas)}")
    
    return mean_beta, t_stat, betas
```

### 2.4 Multiple Regression and Controlling for Risk Factors

A signal that appears to predict returns might do so because it loads on a known risk factor (carry, momentum, dollar factor). To test whether your signal has *incremental* value:

```python
def test_incremental_alpha(new_signal, existing_signals, returns):
    """
    Test whether new_signal adds alpha beyond existing systematic signals.
    The t-stat on new_signal's coefficient is the key output.
    """
    X = pd.concat([existing_signals, new_signal], axis=1).dropna()
    y = returns.reindex(X.index).dropna()
    X = X.reindex(y.index)
    
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    
    # Key: t-stat on new_signal column
    print(model.summary())
    return model
```

**Multicollinearity:**
When two signals are highly correlated (e.g., 2Y rate differential level and 2Y rate differential change), the individual coefficients become unreliable. Check the Variance Inflation Factor (VIF):

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

def check_vif(X: pd.DataFrame):
    """VIF > 10 indicates problematic multicollinearity."""
    vifs = pd.Series(
        {col: variance_inflation_factor(X.values, i) for i, col in enumerate(X.columns)}
    )
    print("Variance Inflation Factors:")
    print(vifs.to_string())
    return vifs
```

If VIF > 10, consider orthogonalising signals or dropping the most correlated one.

---

## Section 3: Time Series Analysis

### 3.1 Stationarity — The Foundation

A time series is **stationary** if its statistical properties (mean, variance, autocorrelation structure) do not change over time.

**Why it matters:** Statistical models estimate parameters (mean, variance, etc.) assuming they are stable. If a series is non-stationary, these estimates are meaningless — you are fitting parameters to a moving target.

**Common cases:**
- Price levels (e.g., EURUSD spot rate): **non-stationary** (trending, drifting)
- Price returns (EURUSD daily % change): **approximately stationary**
- Interest rate *levels*: **non-stationary** (trending with policy cycles)
- Interest rate *changes*: **stationary**
- Rate *differentials* (2Y US – 2Y Germany): **approximately stationary** but slow-moving

This is the key insight behind Strategy #1 in this repository: taking *changes* in the rate differential (Δ(2Y spread)) produces a stationary signal from non-stationary interest rate levels.

**Formal test — Augmented Dickey-Fuller (ADF):**

```python
from statsmodels.tsa.stattools import adfuller

def test_stationarity(series: pd.Series, name: str = 'series'):
    """
    ADF test for unit root (non-stationarity).
    H0: Series has a unit root (non-stationary)
    H1: Series is stationary
    Reject H0 if p-value < 0.05.
    """
    result = adfuller(series.dropna(), autolag='AIC')
    print(f"\n{name} — ADF Test:")
    print(f"  ADF Statistic: {result[0]:.4f}")
    print(f"  p-value: {result[1]:.4f}")
    print(f"  Stationary: {'YES (p < 0.05)' if result[1] < 0.05 else 'NO (non-stationary)'}")
    
    for key, val in result[4].items():
        print(f"  Critical value ({key}): {val:.4f}")
```

Rule: if p-value < 0.05, reject the null → series is stationary.

### 3.2 Autocorrelation

**Autocorrelation** is the correlation of a series with its own past values:

```
ACF(k) = Corr(x_t, x_{t-k})
```

**For FX returns:** Autocorrelation is typically near zero (near-random walk), which is why pure price prediction is hard.

**For FX volatility:** Highly positive autocorrelation at many lags — this is the famous "volatility clustering" phenomenon and what GARCH models capture.

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_ljungbox
import matplotlib.pyplot as plt

def analyze_autocorrelation(series: pd.Series, lags: int = 20):
    """Check autocorrelation structure of a return series."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(series.dropna(), lags=lags, ax=axes[0])
    plot_pacf(series.dropna(), lags=lags, ax=axes[1])
    axes[0].set_title('ACF')
    axes[1].set_title('Partial ACF')
    plt.tight_layout()
    plt.show()
    
    # Ljung-Box test for significant autocorrelation
    lb_test = acorr_ljungbox(series.dropna(), lags=[5, 10, 20], return_df=True)
    print("\nLjung-Box Test (H0: no autocorrelation):")
    print(lb_test.to_string())
    
    # Durbin-Watson (2.0 = no autocorrelation)
    dw = durbin_watson(series.dropna())
    print(f"\nDurbin-Watson statistic: {dw:.3f} (2.0 = no autocorrelation)")
```

### 3.3 ARIMA Models

**ARIMA(p, d, q)** = AutoRegressive Integrated Moving Average.

- **AR(p):** current value depends on p lagged values: x_t = φ₁x_{t-1} + ... + φ_p x_{t-p} + ε_t
- **I(d):** differencing d times to achieve stationarity
- **MA(q):** current value depends on q lagged errors: x_t = ε_t + θ₁ε_{t-1} + ... + θ_q ε_{t-q}

**When ARIMA is useful for traders:**
- Interest rate forecasting (rates have meaningful autocorrelation)
- Inflation series (slow-moving, autocorrelated)
- Industrial production (cyclical, autocorrelated)
- **Not for FX returns** — they are too close to a random walk

```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import auto_arima  # via pmdarima

def fit_arima(series: pd.Series, order=(1, 1, 1)):
    """
    Fit ARIMA model. Use for macro series (rates, CPI), not for returns.
    Use pmdarima.auto_arima() to select optimal (p,d,q) automatically.
    """
    model = ARIMA(series.dropna(), order=order)
    result = model.fit()
    print(result.summary())
    
    # Forecast next 3 periods
    forecast = result.forecast(steps=3)
    print(f"\n3-period forecast: {forecast.values}")
    return result

# Automatic order selection
import pmdarima as pm
def auto_fit_arima(series):
    model = pm.auto_arima(series.dropna(), start_p=0, start_q=0, 
                          max_p=5, max_q=5, d=None, 
                          stepwise=True, information_criterion='aic')
    print(model.summary())
    return model
```

### 3.4 GARCH Models — Volatility Forecasting

**GARCH(1,1)** is the most important model for financial volatility. It captures the fact that large moves tend to follow large moves (volatility clustering).

```
σ²_t = ω + α × ε²_{t-1} + β × σ²_{t-1}
```

Where:
- σ²_t = conditional variance at time t (what we want to forecast)
- ω = long-run variance floor (intercept)
- α = "ARCH" coefficient: how much yesterday's shock affects today's variance
- β = "GARCH" coefficient: how much yesterday's variance estimate persists
- α + β < 1 for stationarity (typically α ≈ 0.05, β ≈ 0.93 for FX)

**Long-run variance:** σ²_∞ = ω / (1 - α - β)

**What GARCH is used for in systematic trading:**

1. **Volatility forecasting for position sizing:**
   - Size position based on GARCH-forecasted σ rather than realised σ
   - Reduces position size as volatility rises — equivalent to vol-targeting but forward-looking

2. **VRP (Volatility Risk Premium) signal:**
   - VRP = IV (implied vol from options) - GARCH (realised/expected vol)
   - When VRP > threshold, sell volatility
   - Applied to Nifty options in India, VIX vs GARCH for equity strategies

3. **Regime detection:**
   - High GARCH vol → risk-off regime → reduce carry positions
   - Low GARCH vol → risk-on → carry works well

```python
from arch import arch_model
import numpy as np

def fit_garch(returns: pd.Series, p: int = 1, q: int = 1):
    """
    Fit GARCH(1,1) to daily return series.
    Returns: fitted model with daily conditional volatility forecasts.
    """
    # Scale to percentage returns for numerical stability
    r = returns.dropna() * 100
    
    model = arch_model(r, vol='Garch', p=p, q=q, dist='t')  # t-distribution for fat tails
    result = model.fit(disp='off')
    
    print(result.summary())
    
    # Extract conditional volatility (annualised)
    cond_vol_annual = result.conditional_volatility / 100 * np.sqrt(252)
    
    # 1-step-ahead forecast
    forecast = result.forecast(horizon=1)
    next_day_vol = np.sqrt(forecast.variance.iloc[-1, 0]) / 100 * np.sqrt(252)
    print(f"\n1-day-ahead annualised vol forecast: {next_day_vol:.2%}")
    
    return result, cond_vol_annual

def garch_position_sizing(returns: pd.Series, target_annual_vol: float = 0.10):
    """
    GARCH-based position sizing. Scale position to target annual vol.
    """
    _, cond_vol_annual = fit_garch(returns)
    
    # Position size: target_vol / current_vol
    sizing = target_annual_vol / cond_vol_annual.clip(lower=0.02)
    sizing = sizing.clip(upper=3.0)  # cap at 3× to avoid extreme sizes
    
    return sizing
```

### 3.5 VAR (Vector Autoregression)

VAR extends AR to multiple variables simultaneously — each variable depends on lagged values of *all* variables in the system.

```
[x1_t]   [A11 A12] [x1_{t-1}]   [ε1_t]
[x2_t] = [A21 A22] [x2_{t-1}] + [ε2_t]
```

**Trading applications:**
- Multi-currency systems where EUR and GBP rates influence each other
- Oil price and CAD/NOD interaction dynamics
- Yield curve dynamics (2Y, 5Y, 10Y as a VAR system)

**Granger causality test:**
"Does x1 Granger-cause x2?" = "Do lagged values of x1 improve the forecast of x2 beyond x2's own lags?"

```python
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.stattools import grangercausalitytests

def test_granger_causality(x: pd.Series, y: pd.Series, max_lags: int = 5):
    """
    Test if x Granger-causes y.
    H0: x does not Granger-cause y.
    Reject H0 (p < 0.05) → x helps predict y beyond y's own history.
    """
    data = pd.concat([y, x], axis=1).dropna()
    results = grangercausalitytests(data, max_lag=max_lags, verbose=False)
    
    print("Granger causality: does X help predict Y?")
    for lag, result in results.items():
        p = result[0]['ssr_chi2test'][1]
        print(f"  Lag {lag}: p-value = {p:.4f} {'*SIGNIFICANT*' if p < 0.05 else ''}")

def fit_var_system(data: pd.DataFrame, max_lags: int = 10):
    """
    Fit VAR system and compute impulse response functions.
    data: DataFrame with stationary series (use returns or differences)
    """
    model = VAR(data.dropna())
    
    # Select lag order by AIC
    lag_order = model.select_order(max_lags)
    print(lag_order.summary())
    
    optimal_lag = lag_order.aic
    result = model.fit(optimal_lag)
    
    # Impulse response: shock to column 0 propagates to all variables
    irf = result.irf(10)
    irf.plot(orth=False)
    
    return result
```

---

## Section 4: Cointegration and Pairs Trading

### 4.1 The Concept of Cointegration

Two non-stationary series X and Y are **cointegrated** if there exists a linear combination:

```
Z_t = X_t - β × Y_t
```

such that Z_t is stationary (mean-reverting). Even though X and Y individually drift, they stay "stuck together" in the long run — whenever they diverge, they eventually converge back.

**Classic examples:**
- Spot price and futures price (same underlying, different settlement)
- Two shares of the same company on different exchanges (ADR arbitrage)
- Oil price (WTI) and USD/CAD exchange rate (structural link via oil exports)
- EUR/USD × GBP/USD and EUR/GBP — triangular relationship

**Trading the cointegrated spread:**
When Z_t is far above its mean → the spread is "rich" → short the overperforming, long the underperforming.
When Z_t is far below its mean → the spread is "cheap" → long the overperforming, short the underperforming.

### 4.2 Testing for Cointegration

**Engle-Granger two-step test (1987):**
1. Regress X on Y: X_t = α + β × Y_t + Z_t
2. Test Z_t for stationarity using ADF.
3. If Z_t is stationary → cointegrated.

```python
from statsmodels.tsa.stattools import coint, adfuller
import statsmodels.api as sm

def test_cointegration(price_a: pd.Series, price_b: pd.Series):
    """
    Engle-Granger cointegration test.
    Returns: t-stat, p-value, β hedge ratio
    """
    # Step 1: regression to find hedge ratio β
    X = sm.add_constant(price_b.dropna())
    y = price_a.reindex(X.index).dropna()
    X = X.reindex(y.index)
    
    reg = sm.OLS(y, X).fit()
    beta = reg.params.iloc[1]
    
    # Step 2: ADF test on residuals
    residuals = reg.resid
    adf_result = adfuller(residuals, maxlags=5)
    
    print(f"Hedge ratio β: {beta:.4f}")
    print(f"ADF t-statistic: {adf_result[0]:.4f}")
    print(f"p-value: {adf_result[1]:.4f}")
    print(f"Cointegrated: {'YES' if adf_result[1] < 0.05 else 'NO'}")
    
    # Using statsmodels coint function directly
    t_stat, p_val, crit_vals = coint(price_a, price_b)
    print(f"\nDirect coint test p-value: {p_val:.4f}")
    
    return beta, residuals, adf_result[1]
```

**Johansen test** (better for multiple cointegrating relationships):

```python
from statsmodels.tsa.vector_ar.vecm import coint_johansen

def johansen_test(data: pd.DataFrame):
    """
    Johansen cointegration test for multiple series.
    Works well for 3+ series (e.g., EURUSD, GBPUSD, EURGBP triangle).
    """
    result = coint_johansen(data.dropna(), det_order=0, k_ar_diff=1)
    
    print("Trace Statistics vs Critical Values (90%, 95%, 99%):")
    for i, (trace, cv) in enumerate(zip(result.lr1, result.cvt)):
        print(f"  r ≤ {i}: trace = {trace:.2f}, CV(95%) = {cv[1]:.2f} "
              f"{'*REJECT*' if trace > cv[1] else ''}")
    
    # The cointegrating vectors
    print(f"\nCointegrating vectors:\n{pd.DataFrame(result.evec)}")
    return result
```

### 4.3 Building a Pairs Trading Strategy

```python
class PairsTradingStrategy:
    """
    Complete pairs trading strategy using cointegration.
    Entry: z-score > ±2σ
    Exit: z-score returns to ±0.5σ
    Stop: z-score exceeds ±3σ (spread diverging)
    """
    
    def __init__(self, entry_z=2.0, exit_z=0.5, stop_z=3.0, lookback=252):
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
        self.lookback = lookback
    
    def compute_spread(self, price_a, price_b, beta):
        return price_a - beta * price_b
    
    def compute_zscore(self, spread):
        rolling_mean = spread.rolling(self.lookback).mean()
        rolling_std = spread.rolling(self.lookback).std()
        return (spread - rolling_mean) / rolling_std
    
    def generate_signals(self, price_a, price_b, beta):
        spread = self.compute_spread(price_a, price_b, beta)
        z = self.compute_zscore(spread)
        
        position = pd.Series(0, index=z.index)
        current_pos = 0
        
        for i in range(1, len(z)):
            zi = z.iloc[i]
            
            if current_pos == 0:
                # Entry
                if zi > self.entry_z:
                    current_pos = -1   # short spread: short A, long β×B
                elif zi < -self.entry_z:
                    current_pos = 1    # long spread: long A, short β×B
                    
            elif current_pos == 1:
                # Exit long spread
                if zi > self.exit_z or zi < -self.stop_z:
                    current_pos = 0
                    
            elif current_pos == -1:
                # Exit short spread
                if zi < -self.exit_z or zi > self.stop_z:
                    current_pos = 0
            
            position.iloc[i] = current_pos
        
        return position, z
    
    def backtest(self, price_a, price_b, beta, ret_a, ret_b, cost_bps=2):
        """
        Run backtest. Return series = position × (ret_a - beta×ret_b) - costs.
        """
        position, z_score = self.generate_signals(price_a, price_b, beta)
        
        spread_returns = ret_a - beta * ret_b
        gross_returns = position.shift(1) * spread_returns
        
        # Transaction costs on position changes
        position_changes = position.diff().abs()
        costs = position_changes * (cost_bps / 10000)
        
        net_returns = gross_returns - costs
        
        sharpe = net_returns.mean() / net_returns.std() * np.sqrt(252)
        print(f"Pairs Trading Results:")
        print(f"  Net Sharpe: {sharpe:.2f}")
        print(f"  Annual Return: {net_returns.mean() * 252:.2%}")
        print(f"  Max Drawdown: {self._max_dd(net_returns):.2%}")
        
        return net_returns, z_score
    
    def _max_dd(self, returns):
        cum = (1 + returns).cumprod()
        return ((cum - cum.expanding().max()) / cum.expanding().max()).min()
```

### 4.4 Dynamic Hedge Ratio with Kalman Filter

The static hedge ratio β from OLS assumes the relationship between X and Y is constant. In reality, cointegrating relationships shift gradually over time. The **Kalman filter** estimates a time-varying β that adapts as the relationship evolves.

The Kalman filter treats β as an unobserved state that evolves according to:
```
State (transition): β_t = β_{t-1} + η_t     (η ~ N(0, Q))
Observation:        x_t = β_t × y_t + ε_t   (ε ~ N(0, R))
```

Q (transition noise) controls how fast β can change. R (observation noise) controls how noisy the spread is.

```python
import numpy as np

class KalmanPairFilter:
    """Dynamic hedge ratio estimation using Kalman filter."""
    
    def __init__(self, delta=1e-4, Vt=1e-3):
        # delta: transition noise variance (how fast β can change)
        # Vt: observation noise variance
        self.delta = delta
        self.Vt = Vt
    
    def estimate_hedge_ratio(self, price_a: np.ndarray, price_b: np.ndarray):
        """
        Returns time-varying hedge ratio β and Kalman spread.
        """
        n = len(price_a)
        beta = np.zeros(n)
        P = np.zeros(n)   # state variance
        
        # Initialise
        beta[0] = price_a[0] / price_b[0]
        P[0] = 1.0
        
        Q = self.delta  # process noise covariance
        R = self.Vt     # observation noise covariance
        
        spreads = np.zeros(n)
        
        for t in range(1, n):
            # Predict step
            beta_pred = beta[t-1]
            P_pred = P[t-1] + Q
            
            # Observation: how well does predicted β explain the price ratio?
            y_pred = beta_pred * price_b[t]
            innovation = price_a[t] - y_pred
            S = price_b[t]**2 * P_pred + R  # innovation variance
            
            # Update step
            K = P_pred * price_b[t] / S      # Kalman gain
            beta[t] = beta_pred + K * innovation
            P[t] = (1 - K * price_b[t]) * P_pred
            
            spreads[t] = price_a[t] - beta[t] * price_b[t]
        
        return beta, spreads
```

The Kalman spread is then z-scored and traded identically to the static pairs trade, but with the hedge ratio adapting over time — reducing the risk of "false divergence" signals when the fundamental relationship has shifted.

---

## Section 5: Bayesian Methods for Systematic Traders

### 5.1 Why Bayesian Thinking Is Natural for Macro Traders

A discretionary macro trader already thinks Bayesian. When a central bank meeting surprises markets:
- **Prior belief**: "The ECB will hold rates, 70% confident."
- **New evidence**: Hotter-than-expected CPI data, ECB sources cited saying hike possible.
- **Updated belief** (posterior): "ECB will hike, now 80% confident."

Bayes' theorem formalises this:

```
P(H | data) ∝ P(data | H) × P(H)

Posterior ∝ Likelihood × Prior
```

The posterior is your updated belief after seeing the data. The likelihood is how probable the data was given hypothesis H. The prior is your belief before seeing the data.

Systematic trading is essentially a continuous Bayesian updating process as new data arrives.

### 5.2 Bayesian Parameter Estimation

Instead of a single estimate of a parameter (e.g., the true Sharpe ratio of a strategy), Bayesian estimation gives you a **distribution** over all plausible values.

**Example: What is the true Sharpe ratio of a strategy?**

With only 2 years of data (504 trading days), a measured Sharpe of 1.5 has enormous uncertainty. The Bayesian posterior over the true Sharpe ratio:
- 90% credible interval: approximately [0.5, 2.5]
- This means you cannot be confident the true Sharpe exceeds 1.0

This is why the Probabilistic Sharpe Ratio (PSR) matters — it is essentially Bayesian thinking applied to Sharpe ratio uncertainty.

```python
import pymc as pm  # PyMC v4+
import numpy as np
import arviz as az

def bayesian_sharpe_estimation(returns: pd.Series):
    """
    Estimate true Sharpe ratio with full uncertainty quantification.
    Uses PyMC to build posterior over mean and volatility.
    """
    r = returns.dropna().values
    
    with pm.Model() as model:
        # Priors — weakly informative
        mu = pm.Normal('mu', mu=0, sigma=0.005)          # daily mean return
        sigma = pm.HalfNormal('sigma', sigma=0.02)        # daily volatility
        
        # Likelihood
        obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=r)
        
        # Derived quantity: annualised Sharpe
        sharpe = pm.Deterministic('sharpe', mu / sigma * np.sqrt(252))
        
        # Sample from posterior
        trace = pm.sample(2000, tune=1000, return_inferencedata=True, progressbar=False)
    
    # Summarise
    az.plot_posterior(trace, var_names=['sharpe'])
    summary = az.summary(trace, var_names=['sharpe'])
    
    print(f"\nTrue Sharpe posterior (from {len(r)} observations):")
    print(summary[['mean', 'sd', 'hdi_3%', 'hdi_97%']].to_string())
    
    return trace
```

### 5.3 The Black-Litterman Model — Applied Bayesian Inference

The Black-Litterman (1990) model is one of the most widely used applications of Bayesian inference in portfolio management. It solves a practical problem: **how do you combine your discretionary macro views with a systematic equilibrium starting point?**

**The components:**
1. **Prior** (Π): Market-implied equilibrium returns = λ × Σ × w_market
   - λ = risk aversion coefficient (typically 2.5)
   - Σ = covariance matrix of returns
   - w_market = market-cap weights (or vol-parity weights for FX)
2. **Views** (Q, P, Ω): Your discretionary/systematic signal expressed as expected returns
   - Q = vector of expected returns for each view
   - P = matrix mapping views to assets
   - Ω = diagonal matrix of view uncertainty
3. **Posterior** (μ_BL): The optimal blended expected return vector

```python
import numpy as np

def black_litterman(Sigma, w_market, views, view_assets, view_confidence,
                    risk_aversion=2.5, tau=0.05):
    """
    Black-Litterman model.
    
    Parameters
    ----------
    Sigma : (N×N) covariance matrix
    w_market : (N,) market cap / reference weights  
    views : list of (view_value, sign) e.g. [(0.03, 'long_A'), (-0.02, 'long_B_short_C')]
    view_assets : P matrix (K×N) mapping K views to N assets
    view_confidence : (K,) confidence for each view (0 to 1)
    """
    N = len(w_market)
    
    # Step 1: Implied equilibrium returns
    Pi = risk_aversion * Sigma @ w_market
    
    # Step 2: Views
    P = np.array(view_assets)   # K×N
    Q = np.array(views)          # K
    
    # Omega: view uncertainty (inversely proportional to confidence)
    omega_diag = [(1 - c) / c * tau for c in view_confidence]
    Omega = np.diag(omega_diag)
    
    # Step 3: Black-Litterman posterior
    tSigma = tau * Sigma
    
    BL_posterior_cov = np.linalg.inv(np.linalg.inv(tSigma) + P.T @ np.linalg.inv(Omega) @ P)
    BL_posterior_mean = BL_posterior_cov @ (np.linalg.inv(tSigma) @ Pi + P.T @ np.linalg.inv(Omega) @ Q)
    
    return BL_posterior_mean, BL_posterior_cov
```

**How a discretionary trader uses BL:**
- Your carry signal gives a view: "AUDUSD will return +3% over next month" (confidence: 60%)
- Your momentum signal gives another view: "EURUSD will return -2% over next month" (confidence: 40%)
- BL blends these with the equilibrium (historical returns) to produce optimal expected returns.
- You then run a portfolio optimiser on those expected returns.

This is exactly how quantamental funds like Man Numeric and AQR incorporate discretionary views into systematic portfolios.

### 5.4 Bayesian Signal Combination

For combining multiple signals, a Bayesian approach weights each signal by its posterior confidence:

```python
def bayesian_signal_combination(signals: dict, ics: dict, ic_stds: dict):
    """
    Weight signals by posterior IC confidence.
    
    signals: {name: signal_series}
    ics: {name: estimated_IC}
    ic_stds: {name: std_of_IC_estimates}
    """
    # Bayesian estimate of true IC for each signal
    # Prior: IC ~ Normal(0, 0.05)  — weakly informative
    prior_mean = 0.0
    prior_var = 0.05**2
    
    posterior_weights = {}
    for name in signals:
        obs_ic = ics[name]
        obs_var = ic_stds[name]**2
        
        # Posterior mean IC
        posterior_ic = (prior_mean / prior_var + obs_ic / obs_var) / (1/prior_var + 1/obs_var)
        posterior_weights[name] = max(0, posterior_ic)  # only use positive IC signals
    
    # Normalise weights
    total = sum(posterior_weights.values())
    if total > 0:
        posterior_weights = {k: v/total for k, v in posterior_weights.items()}
    
    # Compute weighted composite signal
    composite = sum(posterior_weights[name] * signals[name] for name in signals)
    
    return composite, posterior_weights
```

---

## Section 6: Machine Learning Essentials for Finance

### 6.1 Why ML Is Powerful and Dangerous in Finance

ML can detect non-linear, high-dimensional patterns that linear models miss. But finance is a hostile environment for ML:

1. **Low signal-to-noise ratio**: daily returns are 95%+ noise.
2. **Non-stationarity**: relationships change over time (regime shifts).
3. **Limited data**: even 20 years of daily data is only 5,000 observations.
4. **Adaptive adversaries**: once a pattern is exploited, it becomes crowded.

The cardinal rule: **never let ML see your test data during training**. In standard ML, random train-test splits are fine. In financial time series, they guarantee look-ahead bias.

### 6.2 The Bias-Variance Trade-Off

- **Bias**: error from oversimplifying assumptions. Linear regression on a non-linear relationship.
- **Variance**: error from overfitting to training data noise. A 100-parameter model on 500 observations.
- **Trade-off**: complex models reduce bias but increase variance. Simple models have high bias but low variance.
- **The sweet spot**: regularisation controls model complexity and balances the trade-off.

### 6.3 Linear Models with Regularisation

**Ridge Regression (L2 penalty):**
Minimise: Σ(y_i - β'x_i)² + λ Σβ_j²

Shrinks all coefficients toward zero. Works well when many signals are relevant.

**LASSO (L1 penalty):**
Minimise: Σ(y_i - β'x_i)² + λ Σ|β_j|

Produces sparse solutions (many coefficients exactly zero). Works well for feature selection.

**Elastic Net (L1 + L2):**
Best of both — sparsity from L1, stability from L2. The standard for systematic trading.

```python
from sklearn.linear_model import ElasticNetCV, RidgeCV, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

def fit_elastic_net_signal(features: pd.DataFrame, returns: pd.Series, 
                            n_splits: int = 5, test_size: int = 63):
    """
    Elastic net for return prediction using time-series cross-validation.
    
    CRITICAL: Uses TimeSeriesSplit, not random split.
    """
    from sklearn.model_selection import TimeSeriesSplit
    
    X = features.dropna()
    y = returns.reindex(X.index).dropna()
    X = X.reindex(y.index)
    
    # Time-series cross-validation: always train on past, test on future
    tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', ElasticNetCV(
            l1_ratio=[0.1, 0.5, 0.7, 0.9, 0.95, 1.0],
            cv=tscv,
            max_iter=5000
        ))
    ])
    
    pipeline.fit(X, y)
    
    model = pipeline.named_steps['model']
    print(f"Best l1_ratio: {model.l1_ratio_:.2f}")
    print(f"Best alpha: {model.alpha_:.6f}")
    
    feature_importance = pd.Series(
        model.coef_, 
        index=features.columns
    ).sort_values(key=abs, ascending=False)
    
    print("\nTop feature importances:")
    print(feature_importance.head(10).to_string())
    
    return pipeline, feature_importance
```

### 6.4 Gradient Boosting — LightGBM for Return Prediction

LightGBM is the industry workhorse for tabular financial data. It builds decision trees sequentially, each correcting the errors of the previous one.

**Why it beats neural networks for most financial ML problems:**
- Handles missing values natively.
- Works well on small-to-medium datasets.
- Explicit feature importance — you can understand what the model is doing.
- Fast training and hyperparameter tuning.

```python
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

def fit_lgbm_signal(features: pd.DataFrame, returns: pd.Series):
    """
    LightGBM for return prediction with time-series validation.
    """
    X = features.dropna()
    y = returns.reindex(X.index).dropna()
    X = X.reindex(y.index)
    
    # Walk-forward split
    n = len(X)
    train_end = int(n * 0.7)
    
    X_train, X_test = X.iloc[:train_end], X.iloc[train_end:]
    y_train, y_test = y.iloc[:train_end], y.iloc[train_end:]
    
    # LightGBM parameters (conservative to avoid overfitting)
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'num_leaves': 15,        # keep small to prevent overfitting
        'max_depth': 4,
        'learning_rate': 0.05,
        'n_estimators': 500,
        'min_child_samples': 50, # need meaningful number of samples per leaf
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 0.1,
        'verbose': -1
    }
    
    model = lgb.LGBMRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)]
    )
    
    # OOS predictions
    predictions = pd.Series(model.predict(X_test), index=X_test.index)
    
    # IC on OOS predictions
    from scipy.stats import spearmanr
    ic, _ = spearmanr(predictions, y_test)
    print(f"\nOOS IC: {ic:.4f}")
    
    # Feature importance
    importance = pd.Series(
        model.feature_importances_, 
        index=features.columns
    ).sort_values(ascending=False)
    print("\nTop features:")
    print(importance.head(10).to_string())
    
    return model, predictions, importance
```

### 6.5 Purged Cross-Validation — The Critical Safeguard

Standard k-fold cross-validation randomly splits data into folds. For time series, this introduces look-ahead bias because training data from the "future" bleeds into test data from the "past."

**López de Prado's solution:** Purge observations near the train-test boundary, and add an embargo period after each test fold.

```python
from sklearn.model_selection import KFold
import numpy as np

class PurgedKFold:
    """
    Purged K-Fold cross-validation for time series.
    Removes training samples whose labels overlap with test period.
    Adds embargo after each test fold.
    
    Based on: López de Prado (2018), Advances in Financial Machine Learning
    """
    
    def __init__(self, n_splits=5, purge_window=5, embargo_pct=0.01):
        self.n_splits = n_splits
        self.purge_window = purge_window  # days to purge around boundary
        self.embargo_pct = embargo_pct    # fraction of dataset as embargo
    
    def split(self, X, y=None, groups=None):
        n = len(X)
        indices = np.arange(n)
        fold_size = n // self.n_splits
        embargo = int(n * self.embargo_pct)
        
        for k in range(self.n_splits):
            test_start = k * fold_size
            test_end = test_start + fold_size if k < self.n_splits - 1 else n
            
            test_idx = indices[test_start:test_end]
            
            # Training: exclude purge window around test period and embargo
            train_idx = np.concatenate([
                indices[:max(0, test_start - self.purge_window)],
                indices[min(n, test_end + embargo):]
            ])
            
            if len(train_idx) > 0 and len(test_idx) > 0:
                yield train_idx, test_idx
```

**This is the single most important ML concept for finance.** Without purging, virtually any ML model will show spuriously good in-sample results that evaporate out-of-sample.

---

## Section 7: Signal Construction — A Complete Toolkit

### 7.1 The Signal Pipeline

Every systematic signal goes through the same pipeline:

```
Raw Data → Feature Engineering → Signal Construction → Normalisation → Combination → Position Sizing
```

```python
import pandas as pd
import numpy as np

class SignalPipeline:
    """End-to-end signal construction for G10 FX systematic strategy."""
    
    def __init__(self, lookback_z: int = 252):
        self.lookback_z = lookback_z
    
    def z_score(self, series: pd.Series) -> pd.Series:
        """Cross-time z-score (signal normalisation)."""
        return ((series - series.rolling(self.lookback_z).mean()) /
                series.rolling(self.lookback_z).std())
    
    def cross_sectional_z(self, panel: pd.DataFrame) -> pd.DataFrame:
        """Cross-sectional z-score across instruments at each time step."""
        return panel.sub(panel.mean(axis=1), axis=0).div(panel.std(axis=1), axis=0)
    
    def build_carry_signal(self, rate_base: pd.Series, rate_quote: pd.Series) -> pd.Series:
        """Carry: level of rate differential."""
        carry = rate_base - rate_quote
        return self.z_score(carry)
    
    def build_carry_change_signal(self, rate_base: pd.Series, rate_quote: pd.Series) -> pd.Series:
        """Change-in-carry: daily change in rate differential (Strategy #1 type)."""
        carry_change = (rate_base - rate_quote).diff()
        return np.sign(carry_change)  # pure direction signal
    
    def build_momentum_signal(self, fx_returns: pd.Series, 
                               lookback: int = 252, skip: int = 21) -> pd.Series:
        """12-1 skip-last-month momentum."""
        total = fx_returns.rolling(lookback).sum()
        recent = fx_returns.rolling(skip).sum()
        momentum = total - recent
        return self.z_score(momentum)
    
    def build_vol_normalised_carry(self, carry: pd.Series, 
                                    vol: pd.Series) -> pd.Series:
        """Dupuy (2021): carry divided by realised vol. SR improves from 0.76 to 1.07."""
        vn_carry = carry / vol.clip(lower=0.02)
        return self.z_score(vn_carry)
    
    def build_cot_signal(self, net_spec: pd.Series, window: int = 104) -> pd.Series:
        """CFTC COT contrarian signal: z-score of net speculative positioning."""
        z = ((net_spec - net_spec.rolling(window).mean()) /
              net_spec.rolling(window).std())
        # Contrarian: only signal when extreme
        return -z * (z.abs() > 1.5)
    
    def build_vix_scaled_signal(self, signal: pd.Series, vix: pd.Series,
                                 vix_cap: float = 40.0) -> pd.Series:
        """Scale signal down in high-vol regimes."""
        scale = (1 - (vix - 15) / (vix_cap - 15)).clip(0, 1)
        return signal * scale
    
    def combine_signals(self, signals: dict, weights: dict = None) -> pd.Series:
        """
        Combine multiple signals.
        Default: equal weighting. Pass weights dict for IC-weighted combination.
        """
        df = pd.DataFrame(signals)
        z_df = df.apply(lambda col: self.z_score(col))
        
        if weights is None:
            return z_df.mean(axis=1)
        else:
            w = pd.Series(weights)
            w = w / w.sum()
            return (z_df * w).sum(axis=1)
```

### 7.2 IC Decay Analysis — Understanding Your Signal's Half-Life

How long does your signal remain informative? The answer determines the optimal holding period.

```python
def compute_ic_decay(signal: pd.Series, returns: pd.Series, 
                      horizons: list = [1, 3, 5, 10, 21, 42, 63],
                      method: str = 'spearman') -> pd.DataFrame:
    """
    Compute IC at multiple forward horizons to measure signal decay.
    
    Returns: DataFrame with IC, t-stat, and n for each horizon.
    """
    from scipy.stats import spearmanr, pearsonr
    
    results = []
    for h in horizons:
        # Compound returns over h periods
        fwd_return = returns.rolling(h).sum().shift(-h)
        
        aligned = pd.DataFrame({
            'signal': signal,
            'fwd': fwd_return
        }).dropna()
        
        if method == 'spearman':
            ic, pval = spearmanr(aligned['signal'], aligned['fwd'])
        else:
            ic, pval = pearsonr(aligned['signal'], aligned['fwd'])
        
        n = len(aligned)
        t_stat = ic * np.sqrt(n) / np.sqrt(1 - ic**2)
        
        results.append({
            'horizon_days': h,
            'IC': round(ic, 4),
            't_stat': round(t_stat, 2),
            'p_value': round(pval, 4),
            'n_obs': n
        })
    
    df = pd.DataFrame(results).set_index('horizon_days')
    print("IC Decay Analysis:")
    print(df.to_string())
    
    # Fit exponential decay: IC(t) = IC(0) × exp(-λt)
    from scipy.optimize import curve_fit
    
    valid = df[df['IC'] > 0]
    if len(valid) > 2:
        def exp_decay(t, ic0, lam):
            return ic0 * np.exp(-lam * t)
        
        popt, _ = curve_fit(exp_decay, valid.index, valid['IC'], 
                              p0=[0.03, 0.1], maxfev=1000)
        half_life = np.log(2) / popt[1]
        print(f"\nEstimated IC half-life: {half_life:.1f} days")
        print(f"IC(0) estimate: {popt[0]:.4f}")
    
    return df
```

---

## Section 8: Backtesting Framework — Building It Right

### 8.1 The Seven Deadly Sins of Backtesting

Understanding these is more important than any technique:

| Sin | Description | Consequence | Fix |
|---|---|---|---|
| 1. Survivorship bias | Testing only current constituents | Strategy looks better than it is | Include delisted instruments |
| 2. Look-ahead bias | Using tomorrow's data today | False alpha | Strict timestamp discipline; shift signals by 1 |
| 3. Timestamp misalignment | Signal and return dates don't match | Can be positive or negative; either way, wrong | Verify alignment explicitly |
| 4. Transaction cost blindness | Ignoring realistic costs | Overestimated net returns | Use 5-pip RT for G10 FX minimum |
| 5. Data mining | Testing 50 versions, reporting best | The Sharpe you see is inflated by selection | Use Deflated Sharpe Ratio |
| 6. Non-stationarity blindness | Assuming relationships are constant | Backtest from 2010 may fail in 2020 | Sub-period analysis; regime testing |
| 7. Sample size insufficiency | Reporting 18-month results | t-stat is meaningless | Minimum 5 years daily or 10+ years for monthly |

### 8.2 The Walk-Forward Backtest — The Gold Standard

```python
class WalkForwardBacktest:
    """
    Walk-forward backtesting engine with proper data isolation.
    No information from the future leaks into historical decisions.
    """
    
    def __init__(self, train_window: int = 252, test_window: int = 63,
                 transaction_cost_bps: float = 5.0, vol_target: float = 0.10):
        self.train_window = train_window
        self.test_window = test_window
        self.cost_bps = transaction_cost_bps / 10000
        self.vol_target = vol_target
    
    def run(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.Series:
        """
        Run walk-forward backtest.
        
        Parameters
        ----------
        signals : pre-computed raw signals (not z-scored; z-scoring happens inside each fold)
        returns : next-period returns
        
        Returns
        -------
        out_of_sample_returns : daily P&L series
        """
        all_returns = []
        all_dates = []
        
        for start in range(self.train_window, len(signals) - self.test_window, 
                            self.test_window):
            
            # CRITICAL: z-score parameters computed from training data ONLY
            train_signals = signals.iloc[:start]
            
            train_mean = train_signals.mean()
            train_std = train_signals.std().replace(0, np.nan)
            
            # Apply to test period
            test_signals = signals.iloc[start:start + self.test_window]
            test_returns = returns.iloc[start:start + self.test_window]
            
            # Normalise using TRAINING statistics only
            z_signals = (test_signals - train_mean) / train_std
            z_signals = z_signals.clip(-3, 3)   # winsorise
            
            # Vol-targeted positions
            # Estimate vol from training data
            train_vol = returns.iloc[:start].std() * np.sqrt(252)
            scale = self.vol_target / train_vol.replace(0, np.nan).fillna(self.vol_target)
            
            positions = z_signals * scale
            positions = positions.clip(-2, 2)   # position limits
            
            # P&L
            daily_pnl = (positions.shift(1) * test_returns).sum(axis=1)
            
            # Transaction costs on position changes
            pos_changes = positions.diff().abs().sum(axis=1)
            costs = pos_changes * self.cost_bps
            
            net_pnl = daily_pnl - costs
            
            all_returns.extend(net_pnl.values)
            all_dates.extend(net_pnl.index.tolist())
        
        return pd.Series(all_returns, index=all_dates)
```

### 8.3 Sub-Period Analysis — Detecting Regime Dependence

```python
def sub_period_analysis(returns: pd.Series, periods: dict = None) -> pd.DataFrame:
    """
    Break backtest results into sub-periods to test stability.
    
    periods: dict of {label: (start_date, end_date)}
    """
    if periods is None:
        # Default: split into thirds
        n = len(returns)
        dates = returns.index
        periods = {
            'Early': (dates[0], dates[n//3]),
            'Middle': (dates[n//3], dates[2*n//3]),
            'Late': (dates[2*n//3], dates[-1]),
            # Specific market regimes
            'GFC (2008-2009)': ('2008-01-01', '2009-12-31'),
            'ZIRP (2010-2015)': ('2010-01-01', '2015-12-31'),
            'Taper/Hike (2022-2023)': ('2022-01-01', '2023-12-31'),
        }
    
    results = []
    for label, (start, end) in periods.items():
        sub = returns.loc[start:end]
        if len(sub) < 50:
            continue
        
        ann_return = sub.mean() * 252
        ann_vol = sub.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        cum = (1 + sub).cumprod()
        max_dd = ((cum - cum.expanding().max()) / cum.expanding().max()).min()
        
        results.append({
            'Period': label,
            'Start': str(start)[:10],
            'End': str(end)[:10],
            'N_days': len(sub),
            'Ann_Return%': round(ann_return * 100, 1),
            'Ann_Vol%': round(ann_vol * 100, 1),
            'Sharpe': round(sharpe, 2),
            'Max_DD%': round(max_dd * 100, 1)
        })
    
    df = pd.DataFrame(results)
    print("Sub-Period Analysis:")
    print(df.to_string(index=False))
    return df
```

---

## Section 9: Performance Measurement and Monitoring

### 9.1 Core Metrics

```python
def full_strategy_metrics(returns: pd.Series, risk_free: float = 0.0,
                           n_trials: int = 1) -> dict:
    """
    Complete performance metrics suite for a strategy.
    
    Parameters
    ----------
    returns : daily return series
    risk_free : daily risk-free rate (annualised / 252)
    n_trials : number of strategy versions tried (for Deflated Sharpe Ratio)
    """
    r = returns.dropna()
    excess = r - risk_free / 252
    
    # Basic metrics
    ann_return = r.mean() * 252
    ann_vol = r.std() * np.sqrt(252)
    sharpe = (ann_return - risk_free) / ann_vol if ann_vol > 0 else 0
    
    # Sortino (downside deviation)
    downside = r[r < 0].std() * np.sqrt(252)
    sortino = (ann_return - risk_free) / downside if downside > 0 else 0
    
    # Drawdown metrics
    cumulative = (1 + r).cumprod()
    rolling_max = cumulative.expanding().max()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    # Recovery time
    in_drawdown = (drawdown < 0)
    if in_drawdown.any():
        dd_periods = in_drawdown.astype(int).groupby((~in_drawdown).cumsum()).sum()
        max_recovery_days = dd_periods.max()
    else:
        max_recovery_days = 0
    
    calmar = ann_return / abs(max_dd) if max_dd < 0 else np.inf
    
    # Distribution stats
    skewness = float(r.skew())
    kurtosis = float(r.kurtosis())  # excess kurtosis
    
    # Hit rate and profit factor
    hit_rate = (r > 0).mean()
    avg_win = r[r > 0].mean() if (r > 0).any() else 0
    avg_loss = r[r < 0].mean() if (r < 0).any() else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else np.inf
    
    # Probabilistic Sharpe Ratio (PSR)
    # P(true SR > 0 | observed SR, N, skew, kurt)
    import scipy.stats as stats
    n = len(r)
    sr_se = np.sqrt((1 + (1/2) * sharpe**2 - skewness * sharpe + 
                     ((kurtosis + 2) / 4) * sharpe**2) / n)
    psr = stats.norm.cdf(sharpe / sr_se) if sr_se > 0 else 0.5
    
    # Deflated Sharpe Ratio (DSR) — adjusts for multiple testing
    if n_trials > 1:
        # Expected maximum SR from n_trials independent random strategies
        euler_gamma = 0.5772156649
        e_max_sr = ((1 - euler_gamma) * stats.norm.ppf(1 - 1/n_trials) +
                    euler_gamma * stats.norm.ppf(1 - 1/(n_trials * np.e)))
        dsr = stats.norm.cdf((sharpe - e_max_sr) / sr_se) if sr_se > 0 else 0
    else:
        dsr = psr
    
    metrics = {
        'Annual Return': f"{ann_return:.2%}",
        'Annual Vol': f"{ann_vol:.2%}",
        'Sharpe Ratio': f"{sharpe:.2f}",
        'Sortino Ratio': f"{sortino:.2f}",
        'Calmar Ratio': f"{calmar:.2f}",
        'Max Drawdown': f"{max_dd:.2%}",
        'Max Recovery (days)': int(max_recovery_days),
        'Hit Rate': f"{hit_rate:.2%}",
        'Profit Factor': f"{profit_factor:.2f}",
        'Skewness': f"{skewness:.2f}",
        'Excess Kurtosis': f"{kurtosis:.2f}",
        'PSR (SR > 0)': f"{psr:.2%}",
        f'DSR ({n_trials} trials)': f"{dsr:.2%}",
        'N Observations': n,
    }
    
    for k, v in metrics.items():
        print(f"  {k:30s}: {v}")
    
    return metrics
```

### 9.2 Live Signal Monitoring — The Health Dashboard

After deployment, monitor these metrics daily:

```python
class SignalHealthMonitor:
    """Real-time signal health monitoring dashboard."""
    
    def __init__(self, ic_warning: float = 0.01, sr_warning: float = 0.5,
                 lookback: int = 63):
        self.ic_warning = ic_warning
        self.sr_warning = sr_warning
        self.lookback = lookback
    
    def daily_health_check(self, signal_history: pd.Series, 
                             return_history: pd.Series,
                             pnl_history: pd.Series) -> dict:
        """Run daily health check on a live signal."""
        from scipy.stats import spearmanr
        
        # Rolling IC (last lookback days)
        recent_signal = signal_history.iloc[-self.lookback:]
        recent_returns = return_history.iloc[-self.lookback:]
        rolling_ic, _ = spearmanr(recent_signal, recent_returns)
        
        # Rolling Sharpe
        recent_pnl = pnl_history.iloc[-self.lookback:]
        rolling_sr = recent_pnl.mean() / recent_pnl.std() * np.sqrt(252) if recent_pnl.std() > 0 else 0
        
        # Drawdown from peak
        cumulative = (1 + pnl_history).cumprod()
        current_dd = (cumulative.iloc[-1] / cumulative.max() - 1)
        
        # Status
        ic_status = 'GREEN' if rolling_ic > 0.04 else ('AMBER' if rolling_ic > self.ic_warning else 'RED')
        sr_status = 'GREEN' if rolling_sr > 1.0 else ('AMBER' if rolling_sr > self.sr_warning else 'RED')
        dd_status = 'GREEN' if current_dd > -0.05 else ('AMBER' if current_dd > -0.10 else 'RED')
        
        health = {
            f'Rolling {self.lookback}d IC': round(rolling_ic, 4),
            f'Rolling {self.lookback}d Sharpe': round(rolling_sr, 2),
            'Current Drawdown': f"{current_dd:.2%}",
            'IC Status': ic_status,
            'SR Status': sr_status,
            'DD Status': dd_status,
            'Overall': 'RED' if 'RED' in [ic_status, sr_status, dd_status] else
                       ('AMBER' if 'AMBER' in [ic_status, sr_status, dd_status] else 'GREEN')
        }
        
        for k, v in health.items():
            flag = ' ⚠' if str(v) in ['RED', 'AMBER'] else ''
            print(f"  {k:30s}: {v}{flag}")
        
        return health
```

### 9.3 What to Do When a Signal Turns Red

The traffic light system:

| Status | IC | Sharpe | Action |
|---|---|---|---|
| GREEN | > 0.04 | > 1.0 | Full size, monitor weekly |
| AMBER | 0.01 – 0.04 | 0.5 – 1.0 | Reduce to 50% size, investigate regime |
| RED | < 0.01 | < 0.5 | Reduce to 0% or 25%, root cause analysis |

**Root cause analysis for signal deterioration:**
1. **Regime change?** Is VIX elevated? Is the yield curve inverted? Check if the signal historically underperforms in this regime — if yes, reduce; do not kill.
2. **Crowding?** Has the signal been widely published? McLean-Pontiff (2016) show 26% decay before publication, 58% after. If signal was in a 2023 paper, it may already be crowded.
3. **Structural break?** Did something permanent change (e.g., ZIRP killing carry, SNB peg break, COVID)? If yes, the historical calibration may no longer apply.
4. **Data issue?** Is your data feed broken? Has a series changed definition? Check raw data before assuming signal failure.

---

## Section 10: Python Learning Path — A 6-Month Curriculum

### Month 1: Data Handling Foundation

```python
# Week 1: pandas core operations
import pandas as pd

# Read FRED data
from fredapi import Fred
fred = Fred(api_key='your_key_here')  # Free at fred.stlouisfed.org
us_2y = fred.get_series('DGS2', observation_start='2000-01-01')
de_2y = fred.get_series('IRLTLT01DEM156N', observation_start='2000-01-01')

# Alignment and forward-fill
data = pd.DataFrame({'US_2Y': us_2y, 'DE_2Y': de_2y}).ffill()

# Date manipulation
data.index = pd.to_datetime(data.index)
data_monthly = data.resample('ME').last()

# Week 2: Computing signals from data
rate_diff = data['US_2Y'] - data['DE_2Y']
rate_diff_change = rate_diff.diff()

# Week 3: CFTC COT data
# Download from: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
import requests
cot_url = "https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"

# Week 4: Yahoo Finance for FX rates
import yfinance as yf
eurusd = yf.download('EURUSD=X', start='2000-01-01', auto_adjust=True)['Close']
```

### Month 2: Signal Construction

```python
# Week 5: numpy and scipy fundamentals
import numpy as np
from scipy import stats

# Z-score function
def z_score(series, window=252):
    return (series - series.rolling(window).mean()) / series.rolling(window).std()

# IC computation
def compute_ic(signal, returns, lag=1, method='spearman'):
    s = signal.shift(lag)
    aligned = pd.DataFrame({'s': s, 'r': returns}).dropna()
    if method == 'spearman':
        return stats.spearmanr(aligned['s'], aligned['r'])
    return stats.pearsonr(aligned['s'], aligned['r'])

# Week 6: full signal library (carry, momentum, COT, cross-asset)
# Build and test each signal independently before combining
```

### Month 3: Backtest Framework

```python
# Week 7-8: Build the walk-forward backtest from Section 8
# Start simple: one signal, one pair, daily rebalancing
# Add complexity gradually: multiple pairs, multiple signals, transaction costs

# Common timestamp error to avoid:
# WRONG:
positions = np.sign(signal)         # today's signal → today's return (look-ahead!)
pnl = positions * returns

# CORRECT:
positions = np.sign(signal).shift(1)  # today's signal → tomorrow's return
pnl = positions * returns
```

### Month 4: Statistical Testing

```python
# Week 9-10: statsmodels for regression
import statsmodels.api as sm

# Test whether rate-diff-change predicts next-day EURUSD return
X = sm.add_constant(rate_diff_change.shift(1).dropna())
y = eurusd_returns.reindex(X.index).dropna()
X = X.reindex(y.index)

model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
print(model.summary())

# Week 11-12: hypothesis testing
from scipy.stats import t as t_dist

# Is our strategy's Sharpe ratio statistically significant?
n = len(pnl)
sharpe = pnl.mean() / pnl.std() * np.sqrt(252)
t_stat = sharpe / np.sqrt(252 / n)
p_value = 1 - t_dist.cdf(t_stat, df=n-1)
print(f"Sharpe: {sharpe:.2f}, t-stat: {t_stat:.2f}, p-value: {p_value:.4f}")
```

### Month 5: Portfolio Construction

```python
# Week 13-14: Ledoit-Wolf covariance and risk parity
from sklearn.covariance import LedoitWolf

def risk_parity_weights(returns_matrix: pd.DataFrame) -> pd.Series:
    """Equal risk contribution weights."""
    lw = LedoitWolf().fit(returns_matrix.dropna())
    Sigma = lw.covariance_
    
    # Simple risk parity: weight ∝ 1/vol
    vols = np.sqrt(np.diag(Sigma))
    weights = (1 / vols) / (1 / vols).sum()
    return pd.Series(weights, index=returns_matrix.columns)

# Week 15-16: Black-Litterman (from Section 5.3)
# Apply views from your signals; combine with equilibrium
```

### Month 6: ML Introduction

```python
# Week 17-18: Elastic Net with time-series CV
from sklearn.linear_model import ElasticNetCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

feature_cols = ['carry_z', 'momentum_z', 'cot_z', 'vol_z']
X = signals[feature_cols].dropna()
y = returns.reindex(X.index).dropna()
X = X.reindex(y.index)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', ElasticNetCV(cv=TimeSeriesSplit(5), max_iter=5000))
])
pipeline.fit(X, y)

# Week 19-20: LightGBM with feature importance
# Use purged CV from Section 6.5
import lightgbm as lgb
```

### Key Library Reference

| Library | Purpose | Install |
|---|---|---|
| `pandas` | Data manipulation, time series | `pip install pandas` |
| `numpy` | Numerical computation | `pip install numpy` |
| `scipy` | Statistics, optimisation | `pip install scipy` |
| `statsmodels` | Regression, time series models | `pip install statsmodels` |
| `fredapi` | FRED data API | `pip install fredapi` |
| `yfinance` | Yahoo Finance data | `pip install yfinance` |
| `scikit-learn` | ML models, cross-validation | `pip install scikit-learn` |
| `lightgbm` | Gradient boosting | `pip install lightgbm` |
| `arch` | GARCH models | `pip install arch` |
| `pykalman` | Kalman filter | `pip install pykalman` |
| `pymc` | Bayesian inference | `pip install pymc` |
| `matplotlib` | Plotting | `pip install matplotlib` |
| `seaborn` | Statistical plots | `pip install seaborn` |
| `pmdarima` | Auto ARIMA | `pip install pmdarima` |

### Free Data Sources

| Data | Source | Coverage |
|---|---|---|
| US/G10 macro | FRED (`fred.stlouisfed.org`) | All G10 rate, CPI, IP, GDP data |
| FX rates | Yahoo Finance (`yfinance`) | Daily OHLCV, G10 pairs |
| COT positioning | CFTC (`cftc.gov`) | Weekly, CME FX futures, all G10 pairs |
| OECD CLIs | FRED (`LORSGPNO`, `OECDLOLIVO`, etc.) | Monthly, all G10 countries |
| NY Fed Nowcast | `newyorkfed.org/research/policy/nowcast` | Weekly US GDP estimate |
| FRBSF Fed surprises | `frbsf.org` | FOMC surprises 1994-present |
| PPP data | OECD stats (`stats.oecd.org`) | Annual, all G10 |
| BIS REER | BIS (`bis.org/statistics/eer`) | Monthly, all major currencies |
| ETF flows | ETF.com | Daily with 1-day lag |

---

## Appendix A: Key Academic Citations

| Paper | Journal | Key Finding |
|---|---|---|
| Harvey, Liu & Zhu (2016) | Review of Financial Studies | t > 3.0 required for new factors; 316+ factors tested |
| McLean & Pontiff (2016) | Journal of Finance | 26% alpha decay pre-publication; 58% post-publication |
| Bailey & López de Prado (2014) | JPM | Deflated Sharpe Ratio corrects for multiple testing |
| Newey & West (1987) | Econometrica | HAC standard errors for autocorrelated residuals |
| Engle & Granger (1987) | Econometrica | Cointegration test; two-step procedure |
| Fama (1984) | Journal of Monetary Economics | Forward premium puzzle; UIP fails; β ≈ -0.88 |
| Grinold & Kahn (2000) | Book | Fundamental Law: IR = IC × √BR |
| López de Prado (2018) | Book | Purged cross-validation; combinatorial CPCV |
| Engle (1982) | Econometrica | ARCH model; volatility clustering |
| Black & Litterman (1990) | Goldman Sachs | Bayesian portfolio optimisation with views |

---

## Appendix B: The Minimum Viable Systematic Strategy — Checklist

Before declaring a strategy ready for live trading, verify each item:

- [ ] Signal has t-statistic > 3.0 on the primary metric (Sharpe, IC)
- [ ] Walk-forward backtest shows consistent performance across sub-periods
- [ ] All cost estimates are realistic (at least 5 bps RT for G10 FX)
- [ ] No look-ahead bias: timestamps explicitly verified
- [ ] Deflated Sharpe Ratio > 0.5 (accounting for number of strategies tested)
- [ ] IC decay analysis shows meaningful predictive power at intended holding period
- [ ] Sub-period analysis: no single 12-month period drives all the P&L
- [ ] VIX regime analysis: strategy survives (or at least doesn't blow up) in stress periods
- [ ] Maximum drawdown within acceptable bounds for your capital and risk tolerance
- [ ] Live monitoring framework in place (rolling IC, rolling Sharpe, drawdown alerts)
- [ ] Clear decision rules for when to reduce or stop trading the strategy

---

*This document is part of the g10-systematic-fx research library. Related documents: `discretionary_to_systematic_bridge.md` (mindset and translation), `mft_comprehensive_reference.md` (medium-frequency strategies), `systematic_macro_models_reference.md` (macro signal construction), `quant_reference_master.md` (portfolio optimisation and factor models).*
