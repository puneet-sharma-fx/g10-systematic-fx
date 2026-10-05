"""Offline tests for backtest/common.py (synthetic data, no network)."""
import numpy as np
import pandas as pd

from backtest.common import despike, stats, turnover_cost


def _px(n=300, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.Series(10 * np.exp(np.cumsum(rng.normal(0, 0.005, n))), index=idx)


def test_despike_removes_reverting_tick():
    px = _px()
    px.iloc[150] *= 0.7                     # bad tick that reverts next day
    clean = despike(px)
    assert abs(np.log(clean).diff()).max() < 0.05


def test_despike_keeps_persistent_jump():
    px = _px()
    px.iloc[150:] *= 1.15                   # SNB-style jump that sticks
    clean = despike(px)
    assert clean.iloc[-1] == px.iloc[-1]


def test_turnover_cost_series_charges_half_round_trip_per_unit():
    w = pd.Series([0.0, 1.0, 1.0, -1.0])
    c = turnover_cost(w, 10.0)              # 10 bps RT → 5 bps per unit traded
    assert np.allclose(c.values, [0, 5e-4, 0, 10e-4])


def test_turnover_cost_frame_uses_per_column_bps():
    w = pd.DataFrame({"A": [1.0, 1.0], "B": [0.0, 1.0]})
    c = turnover_cost(w, {"A": 2.0, "B": 20.0})
    assert np.isclose(c.iloc[0], 1e-4) and np.isclose(c.iloc[1], 10e-4)


def test_stats_sharpe_sign_and_drawdown():
    r = pd.Series(np.r_[np.full(100, 0.001), np.full(10, -0.01)])
    s = stats(r)
    assert s["sharpe"] > 0 and s["max_dd"] < -0.09
