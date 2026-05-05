"""
Carry signal: annualised rate differential (base ccy rate - quote ccy rate).

For a pair like EURUSD: carry = EUR_rate - USD_rate.
For a pair like USDJPY: carry = USD_rate - JPY_rate.

Positive carry → positive signal (hold the pair as listed).
Output is cross-sectionally z-scored across the universe on each rebalance date.
"""
from __future__ import annotations

import pandas as pd

from config import G10_PAIRS, SIGNAL_PARAMS
from signals._base import BaseSignal


class CarrySignal(BaseSignal):
    def __init__(self, smoothing_days: int | None = None):
        cfg = SIGNAL_PARAMS["carry"]
        self.smoothing = smoothing_days or cfg["smoothing_days"]

    def compute(self, rebalance_dates: pd.DatetimeIndex, **data) -> pd.DataFrame:
        rates: pd.DataFrame = data["short_rates"]  # daily, annualised %, columns = currency

        raw_carry: dict[str, pd.Series] = {}
        for pair, meta in G10_PAIRS.items():
            base, quote = meta["base"], meta["quote"]
            if base not in rates.columns or quote not in rates.columns:
                continue
            # Smooth to reduce noise from rate-fixing lags
            diff = (rates[base] - rates[quote]).rolling(self.smoothing, min_periods=1).mean()
            raw_carry[pair] = diff

        carry_df = pd.DataFrame(raw_carry)

        # Align to rebalance dates (use last available value on or before each date)
        carry_rebal = carry_df.reindex(rebalance_dates, method="ffill")
        return self.cross_section_zscore(carry_rebal)
