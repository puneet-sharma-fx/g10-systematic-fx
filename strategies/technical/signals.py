"""
The 15 signal functions for the technical-strategy comparison.

Each takes a price Series and returns a daily position series in {-1, 0, +1}.

Conventions:
- Mean-reversion strategies: enter at extremes, exit in neutral zone (pos can go to 0)
- Trend strategies: position is always +1 or -1 (never 0); flips on signal change
- Oscillators: enter at extremes, exit when crossing back to neutral
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── Indicator helpers ────────────────────────────────────────────────────────
def _rsi(price: pd.Series, period: int = 14) -> pd.Series:
    delta = price.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """ATR; for FX daily close-only data we approximate with abs(close.diff)."""
    return close.diff().abs().rolling(period).mean()


def _atr_from_close(close: pd.Series, period: int = 14) -> pd.Series:
    """Pure close-to-close volatility proxy for ATR."""
    return close.diff().abs().rolling(period).mean()


def _ema(price: pd.Series, period: int) -> pd.Series:
    return price.ewm(span=period, adjust=False).mean()


# ── 1. RSI mean-reversion (14, 30/70) ──────────────────────────────────────
def sig_rsi(price: pd.Series, period: int = 14,
            oversold: float = 30, overbought: float = 70) -> pd.Series:
    rsi = _rsi(price, period)
    pos = pd.Series(0.0, index=price.index)
    pos[rsi < oversold]  = +1.0
    pos[rsi > overbought] = -1.0
    return pos


# ── 2. Bollinger Bands fade (20, 2σ) ────────────────────────────────────────
def sig_bollinger_fade(price: pd.Series, period: int = 20, n_std: float = 2.0) -> pd.Series:
    ma = price.rolling(period).mean()
    sd = price.rolling(period).std()
    upper = ma + n_std * sd
    lower = ma - n_std * sd
    pos = pd.Series(0.0, index=price.index)
    pos[price < lower] = +1.0
    pos[price > upper] = -1.0
    return pos


# ── 3. Z-score reversion (20-day, ±2) ───────────────────────────────────────
def sig_zscore(price: pd.Series, period: int = 20, threshold: float = 2.0) -> pd.Series:
    ma = price.rolling(period).mean()
    sd = price.rolling(period).std()
    z = (price - ma) / sd
    pos = pd.Series(0.0, index=price.index)
    pos[z < -threshold] = +1.0
    pos[z >  threshold] = -1.0
    return pos


# ── 4. CCI mean reversion (20, ±100) ────────────────────────────────────────
def sig_cci(price: pd.Series, period: int = 20, threshold: float = 100.0) -> pd.Series:
    """CCI computed on close only (typical price collapses to close for daily FX)."""
    ma = price.rolling(period).mean()
    md = (price - ma).abs().rolling(period).mean()
    cci = (price - ma) / (0.015 * md.replace(0, np.nan))
    pos = pd.Series(0.0, index=price.index)
    pos[cci < -threshold] = +1.0
    pos[cci >  threshold] = -1.0
    return pos


# ── 5. SMA Crossover (50/200) ───────────────────────────────────────────────
def sig_sma_cross(price: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    fast_ma = price.rolling(fast).mean()
    slow_ma = price.rolling(slow).mean()
    pos = pd.Series(np.nan, index=price.index)
    pos[fast_ma > slow_ma] = +1.0
    pos[fast_ma < slow_ma] = -1.0
    return pos.ffill().fillna(0)


# ── 6. EMA Crossover (12/26) ────────────────────────────────────────────────
def sig_ema_cross(price: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
    fast_ma = _ema(price, fast)
    slow_ma = _ema(price, slow)
    pos = pd.Series(np.nan, index=price.index)
    pos[fast_ma > slow_ma] = +1.0
    pos[fast_ma < slow_ma] = -1.0
    return pos.ffill().fillna(0)


# ── 7. MACD signal-line crossover (12/26/9) ─────────────────────────────────
def sig_macd(price: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    macd_line = _ema(price, fast) - _ema(price, slow)
    sig_line = _ema(macd_line, signal)
    pos = pd.Series(np.nan, index=price.index)
    pos[macd_line > sig_line] = +1.0
    pos[macd_line < sig_line] = -1.0
    return pos.ffill().fillna(0)


# ── 8. Donchian breakout (20-day) ───────────────────────────────────────────
def sig_donchian(price: pd.Series, period: int = 20) -> pd.Series:
    upper = price.rolling(period).max()
    lower = price.rolling(period).min()
    pos = pd.Series(np.nan, index=price.index)
    # On daily close-only data: signal flips when close = period high/low
    pos[price >= upper] = +1.0
    pos[price <= lower] = -1.0
    return pos.ffill().fillna(0)


# ── 9. Ichimoku Tenkan/Kijun crossover (9/26) ──────────────────────────────
def sig_ichimoku(price: pd.Series, tenkan: int = 9, kijun: int = 26) -> pd.Series:
    """Simplified Ichimoku: long when Tenkan > Kijun, short otherwise."""
    t = (price.rolling(tenkan).max() + price.rolling(tenkan).min()) / 2
    k = (price.rolling(kijun).max()  + price.rolling(kijun).min())  / 2
    pos = pd.Series(np.nan, index=price.index)
    pos[t > k] = +1.0
    pos[t < k] = -1.0
    return pos.ffill().fillna(0)


# ── 10. Stochastic %K/%D (14, 3) ───────────────────────────────────────────
def sig_stochastic(price: pd.Series, period: int = 14, smooth: int = 3,
                   oversold: float = 20, overbought: float = 80) -> pd.Series:
    lo = price.rolling(period).min()
    hi = price.rolling(period).max()
    k = 100 * (price - lo) / (hi - lo).replace(0, np.nan)
    d = k.rolling(smooth).mean()
    pos = pd.Series(0.0, index=price.index)
    pos[d < oversold]   = +1.0
    pos[d > overbought] = -1.0
    return pos


# ── 11. Williams %R (14, -80/-20) ──────────────────────────────────────────
def sig_williams_r(price: pd.Series, period: int = 14,
                   oversold: float = -80, overbought: float = -20) -> pd.Series:
    hi = price.rolling(period).max()
    lo = price.rolling(period).min()
    wr = -100 * (hi - price) / (hi - lo).replace(0, np.nan)
    pos = pd.Series(0.0, index=price.index)
    pos[wr < oversold]   = +1.0
    pos[wr > overbought] = -1.0
    return pos


# ── 12. ROC (Rate of Change, 20-day) momentum ──────────────────────────────
def sig_roc(price: pd.Series, period: int = 20) -> pd.Series:
    """Sign of N-day return."""
    roc = price / price.shift(period) - 1
    pos = pd.Series(np.nan, index=price.index)
    pos[roc > 0] = +1.0
    pos[roc < 0] = -1.0
    return pos.ffill().fillna(0)


# ── 13. Keltner Channel breakout (20 EMA + 1.5×ATR) ────────────────────────
def sig_keltner(price: pd.Series, period: int = 20, atr_mult: float = 1.5) -> pd.Series:
    mid = _ema(price, period)
    atr = _atr_from_close(price, period)
    upper = mid + atr_mult * atr
    lower = mid - atr_mult * atr
    pos = pd.Series(np.nan, index=price.index)
    pos[price > upper] = +1.0
    pos[price < lower] = -1.0
    return pos.ffill().fillna(0)


# ── 14. ATR-trailing trend (close above SMA20 + 0.5×ATR → long) ────────────
def sig_atr_trend(price: pd.Series, ma_period: int = 20,
                  atr_period: int = 14, atr_mult: float = 0.5) -> pd.Series:
    ma = price.rolling(ma_period).mean()
    atr = _atr_from_close(price, atr_period)
    pos = pd.Series(np.nan, index=price.index)
    pos[price > ma + atr_mult * atr] = +1.0
    pos[price < ma - atr_mult * atr] = -1.0
    return pos.ffill().fillna(0)


# ── 15. TRIX (15-day triple-smoothed EMA) momentum ─────────────────────────
def sig_trix(price: pd.Series, period: int = 15) -> pd.Series:
    e1 = _ema(price, period)
    e2 = _ema(e1, period)
    e3 = _ema(e2, period)
    trix = e3.pct_change()
    pos = pd.Series(np.nan, index=price.index)
    pos[trix > 0] = +1.0
    pos[trix < 0] = -1.0
    return pos.ffill().fillna(0)


# ── Registry ────────────────────────────────────────────────────────────────
STRATEGIES = [
    ("RSI(14)",         "Mean Rev",   sig_rsi),
    ("Bollinger(20,2)", "Mean Rev",   sig_bollinger_fade),
    ("Z-score(20,2)",   "Mean Rev",   sig_zscore),
    ("CCI(20,100)",     "Mean Rev",   sig_cci),
    ("SMA Cross(50/200)","Trend",     sig_sma_cross),
    ("EMA Cross(12/26)","Trend",      sig_ema_cross),
    ("MACD(12,26,9)",   "Trend",      sig_macd),
    ("Donchian(20)",    "Trend",      sig_donchian),
    ("Ichimoku(9/26)",  "Trend",      sig_ichimoku),
    ("Stochastic(14,3)","Oscillator", sig_stochastic),
    ("Williams %R(14)", "Oscillator", sig_williams_r),
    ("ROC(20)",         "Momentum",   sig_roc),
    ("Keltner(20,1.5)", "Volatility", sig_keltner),
    ("ATR Trend(0.5)",  "Volatility", sig_atr_trend),
    ("TRIX(15)",        "Momentum",   sig_trix),
]
