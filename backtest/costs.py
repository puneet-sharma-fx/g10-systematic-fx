"""
Transaction cost model for G10 FX spot.

Round-trip cost is expressed in basis points and applied on each turnover.
Turnover is computed as the absolute change in notional weight per pair per period.
"""

import pandas as pd


def compute_costs(
    weights: pd.DataFrame,
    cost_bps_roundtrip: float = 2.0,
) -> pd.Series:
    """
    Parameters
    ----------
    weights : DataFrame
        Rebalance-date × pair notional weights (can be negative for shorts).
    cost_bps_roundtrip : float
        Round-trip transaction cost in basis points (default 2 bps ≈ 0.4 pip on EURUSD).

    Returns
    -------
    pd.Series
        Cost drag per rebalance period, indexed by rebalance_dates.
        Units match weights (i.e. if weights sum to 1, cost is a fractional return).
    """
    cost_per_unit = cost_bps_roundtrip / 10_000

    # Turnover = half the sum of absolute weight changes (one-way)
    weight_change = weights.diff().abs().sum(axis=1)
    return weight_change * cost_per_unit
