"""
Vol-regime filter: scales all position sizes by a VIX-based scalar.

  VIX <= elevated_threshold  -> scalar = 1.0  (full exposure)
  VIX >  elevated_threshold  -> scalar = elevated_scale (e.g. 0.5)
  VIX >  crisis_threshold    -> scalar = crisis_scale   (e.g. 0.0)

Returns a scalar Series indexed by rebalance_dates, NOT a z-scored signal.
Applied multiplicatively to the composite score in strategy.py.
"""
from __future__ import annotations

import pandas as pd

from config import VOL_REGIME


class VolRegimeFilter:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or VOL_REGIME

    def compute(self, rebalance_dates: pd.DatetimeIndex, **data) -> pd.Series:
        """Returns a Series of floats in [0, 1] indexed by rebalance_dates."""
        vix: pd.Series = data["vix"]

        smoothed = vix.rolling(int(self.cfg["smoothing_days"]), min_periods=1).mean()
        smoothed = smoothed.reindex(rebalance_dates, method="ffill")

        elev_thr = float(self.cfg["elevated_threshold"])
        crisis_thr = float(self.cfg["crisis_threshold"])
        elev_scale = float(self.cfg["elevated_scale"])
        crisis_scale = float(self.cfg["crisis_scale"])

        scalar = pd.Series(1.0, index=rebalance_dates, dtype=float)
        scalar[smoothed > elev_thr] = elev_scale
        scalar[smoothed > crisis_thr] = crisis_scale

        return scalar
