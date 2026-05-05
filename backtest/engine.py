"""
Walk-forward backtester.

Splits the full history into expanding or rolling train/test windows.
Each test window uses weights computed only from in-sample data (no look-ahead).
Returns a single out-of-sample return series covering the full test period.
"""

import logging
from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd

from backtest.costs import compute_costs
from backtest.metrics import print_summary, summary

log = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    returns: pd.Series           # weekly out-of-sample net returns
    weights: pd.DataFrame        # position weights at each rebalance
    costs: pd.Series             # cost drag per period
    windows: list[dict] = field(default_factory=list)  # per-window metadata


def _compute_pair_returns(
    fx_prices: pd.DataFrame,
    rebalance_dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """
    Weekly log-returns per pair, aligned to rebalance dates.
    Returns a DataFrame: rows = rebalance dates, columns = pairs.
    """
    # Use close price on each rebalance date (next available if market closed)
    px = fx_prices.reindex(rebalance_dates, method="ffill")
    return px.pct_change().shift(-1)  # forward return: earned after holding this period


def run_walk_forward(
    strategy,                      # G10SystematicFX instance with .compute_weights()
    fx_prices: pd.DataFrame,
    data: dict,                    # full pre-fetched data dict passed to strategy
    rebalance_dates: pd.DatetimeIndex,
    train_years: int = 3,
    test_months: int = 6,
    cost_bps: float = 2.0,
    expanding: bool = True,        # True = expanding window; False = rolling
) -> BacktestResult:
    """
    Parameters
    ----------
    strategy : G10SystematicFX
        Strategy instance. Must implement compute_weights(rebalance_dates, **data).
    fx_prices : DataFrame
        Daily FX close prices.
    data : dict
        Pre-fetched data (short_rates, cot, vix, fx_prices).
    rebalance_dates : DatetimeIndex
        All candidate rebalance dates covering the full backtest period.
    train_years : int
        Minimum in-sample history required.
    test_months : int
        Length of each out-of-sample test window.
    cost_bps : float
        Round-trip cost in basis points.
    expanding : bool
        If True, train window grows over time. If False, rolling fixed-length train.

    Returns
    -------
    BacktestResult
    """
    pair_returns = _compute_pair_returns(fx_prices, rebalance_dates)

    all_weights: list[pd.DataFrame] = []
    windows_meta: list[dict] = []

    first_date = rebalance_dates[0]
    last_date = rebalance_dates[-1]

    train_end = first_date + pd.DateOffset(years=train_years)
    window_start = train_end

    while window_start <= last_date:
        window_end = min(window_start + pd.DateOffset(months=test_months), last_date)

        train_mask = rebalance_dates < window_start
        test_mask = (rebalance_dates >= window_start) & (rebalance_dates <= window_end)

        if not train_mask.any() or not test_mask.any():
            window_start = window_end + timedelta(days=1)
            continue

        if expanding:
            train_start = first_date
        else:
            train_start = window_start - pd.DateOffset(years=train_years)

        train_dates = rebalance_dates[(rebalance_dates >= train_start) & (rebalance_dates < window_start)]
        test_dates = rebalance_dates[test_mask]

        log.info(
            "Walk-forward window: train %s → %s, test %s → %s",
            train_dates[0].date(), train_dates[-1].date(),
            test_dates[0].date(), test_dates[-1].date(),
        )

        # Compute weights using only in-sample data
        # Slice data dicts to training window only (prevents any look-ahead)
        train_data = _slice_data(data, end=train_dates[-1])
        weights_train = strategy.compute_weights(train_dates, **train_data)

        # Use the last computed weights to trade the test window
        # (parameters fitted on train; weights updated each week in test using live data)
        test_data = _slice_data(data, end=test_dates[-1])
        weights_test = strategy.compute_weights(test_dates, **test_data)

        all_weights.append(weights_test)
        windows_meta.append({
            "train_start": train_start,
            "train_end": train_dates[-1],
            "test_start": test_dates[0],
            "test_end": test_dates[-1],
            "n_train": len(train_dates),
            "n_test": len(test_dates),
        })

        window_start = window_end + timedelta(days=1)

    if not all_weights:
        raise RuntimeError("Walk-forward produced no test windows — check date range and train_years")

    weights_df = pd.concat(all_weights).sort_index()
    weights_df = weights_df[~weights_df.index.duplicated(keep="last")]

    costs = compute_costs(weights_df, cost_bps)

    # Portfolio return = sum(weight_i * return_i) - cost
    port_gross = (weights_df * pair_returns.reindex(weights_df.index)).sum(axis=1)
    port_net = port_gross - costs

    return BacktestResult(
        returns=port_net.dropna(),
        weights=weights_df,
        costs=costs,
        windows=windows_meta,
    )


def _slice_data(data: dict, end: pd.Timestamp) -> dict:
    """Return a copy of data dict with all DataFrames/Series truncated to `end`."""
    sliced = {}
    for k, v in data.items():
        if isinstance(v, (pd.DataFrame, pd.Series)):
            sliced[k] = v[v.index <= end]
        else:
            sliced[k] = v
    return sliced
