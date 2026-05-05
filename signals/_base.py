"""
BaseSignal: contract all signal classes must satisfy.

Every signal returns a DataFrame of the same shape as the rebalance index:
  - index: DatetimeIndex (rebalance dates)
  - columns: pair names matching config.G10_PAIRS
  - values: cross-sectionally z-scored floats (mean≈0, std≈1)
    NaN is acceptable where data is unavailable.

Signals are combined in strategy.py via weighted average of z-scores.
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseSignal(ABC):
    @abstractmethod
    def compute(
        self,
        rebalance_dates: pd.DatetimeIndex,
        **data,
    ) -> pd.DataFrame:
        """
        Parameters
        ----------
        rebalance_dates : DatetimeIndex
            Dates at which the strategy rebalances.
        **data : keyword arguments carrying pre-fetched DataFrames
            (fx_prices, short_rates, cot, vix, ...).

        Returns
        -------
        pd.DataFrame
            Rows = rebalance_dates, columns = pair names, values = z-scores.
        """

    @staticmethod
    def cross_section_zscore(df: pd.DataFrame) -> pd.DataFrame:
        """Z-score across pairs on each date (row-wise)."""
        mu = df.mean(axis=1)
        sigma = df.std(axis=1).replace(0, float("nan"))
        return df.sub(mu, axis=0).div(sigma, axis=0)
