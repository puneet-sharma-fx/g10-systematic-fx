"""
Shared backtest engine for the technical-strategy exploration.

Each signal function returns a daily position series in {−1, 0, +1}.
The engine handles: held-position lag, FX return, cost on turnover, metrics.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

TRADING_DAYS = 252
DEFAULT_COST_PIPS = 5.0


def pip_size(pair: str) -> float:
    return 0.01 if "JPY" in pair else 0.0001


def stats(returns: pd.Series) -> dict:
    if len(returns) < 5 or returns.std() == 0:
        return dict(ann_ret=0.0, ann_vol=0.0, sharpe=0.0,
                    max_dd=0.0, hit=0.0, cum=0.0)
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve = (1 + returns).cumprod()
    max_dd = float(((curve / curve.cummax()) - 1).min())
    hit = float((returns > 0).mean())
    cum = float(curve.iloc[-1] - 1)
    return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                max_dd=max_dd, hit=hit, cum=cum)


def backtest(
    price: pd.Series,
    signal_fn: Callable[[pd.Series], pd.Series],
    pair: str,
    cost_round_trip_pips: float = DEFAULT_COST_PIPS,
) -> dict:
    """
    Run a single-pair backtest of a signal function.

    Returns a dict with:
      position    : daily position series (decision at end-of-day t)
      gross_ret   : daily strategy gross return (position[t-1] × FX return[t])
      cost        : daily transaction cost
      net_ret     : daily net return
      gross_stats : stats on gross series
      net_stats   : stats on net series
      curve_net   : cumulative net equity curve
      n_trades    : number of position changes
    """
    pos = signal_fn(price).reindex(price.index).fillna(0)
    held = pos.shift(1).fillna(0)
    fx_ret = price.pct_change()

    cost_unit = (cost_round_trip_pips / 2.0) * pip_size(pair)
    turnover = pos.diff().abs().fillna(0)
    cost = turnover * cost_unit / price

    gross_ret = (held * fx_ret).dropna()
    net_ret = (held * fx_ret - cost).dropna()

    return dict(
        position=pos,
        held=held,
        gross_ret=gross_ret,
        net_ret=net_ret,
        cost=cost,
        gross_stats=stats(gross_ret),
        net_stats=stats(net_ret),
        curve_net=(1 + net_ret).cumprod(),
        curve_gross=(1 + gross_ret).cumprod(),
        n_trades=int((turnover > 0).sum()),
        turnover=float(turnover.sum()),
    )
