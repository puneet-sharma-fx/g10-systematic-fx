"""Unit tests for performance metrics."""

import numpy as np
import pandas as pd
import pytest

from backtest.metrics import sharpe, sortino, max_drawdown, calmar, annualised_return


def flat_returns(n: int = 104, weekly_return: float = 0.001) -> pd.Series:
    dates = pd.date_range("2018-01-05", periods=n, freq="W-FRI")
    return pd.Series(weekly_return, index=dates)


class TestMetrics:
    def test_sharpe_positive_returns(self):
        r = flat_returns(weekly_return=0.002)
        assert sharpe(r) > 0

    def test_sharpe_zero_returns(self):
        r = flat_returns(weekly_return=0.0)
        assert sharpe(r) == 0.0

    def test_max_drawdown_negative(self):
        r = flat_returns()
        # Inject a drawdown
        r.iloc[50] = -0.10
        assert max_drawdown(r) < 0

    def test_max_drawdown_all_positive(self):
        r = flat_returns(weekly_return=0.001)
        assert max_drawdown(r) <= 0  # could be exactly 0 if always going up

    def test_annualised_return_known(self):
        # 1% per week for 52 weeks → (1.01^52 - 1) ≈ 0.6777
        r = flat_returns(n=52, weekly_return=0.01)
        ann = annualised_return(r)
        assert abs(ann - (1.01**52 - 1)) < 1e-6

    def test_calmar_positive(self):
        r = flat_returns()
        r.iloc[20] = -0.05
        assert calmar(r) > 0
