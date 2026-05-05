"""
Momentum signal: dual time-series momentum (fast minus slow return).

Signal = fast_return - slow_return, where:
  fast_return  = (price_t / price_{t - fast_days}) - 1
  slow_return  = (price_t / price_{t - slow_days}) - 1

Positive value → recent outperformance → positive signal (long the pair).
Output is cross-sectionally z-scored.
"""
from __future__ import annotations

import pandas as pd

from config import G10_PAIRS, SIGNAL_PARAMS
from signals._base import BaseSignal


class MomentumSignal(BaseSignal):
    def __init__(self, fast_days: int | None = None, slow_days: int | None = None):
        cfg = SIGNAL_PARAMS["momentum"]
        self.fast = fast_days or cfg["fast_days"]
        self.slow = slow_days or cfg["slow_days"]

    def compute(self, rebalance_dates: pd.DatetimeIndex, **data) -> pd.DataFrame:
        prices: pd.DataFrame = data["fx_prices"]  # daily close, columns = pair names

        available = [p for p in G10_PAIRS if p in prices.columns]
        px = prices[available]

        fast_ret = px / px.shift(self.fast) - 1
        slow_ret = px / px.shift(self.slow) - 1
        signal = fast_ret - slow_ret

        signal_rebal = signal.reindex(rebalance_dates, method="ffill")
        return self.cross_section_zscore(signal_rebal)
