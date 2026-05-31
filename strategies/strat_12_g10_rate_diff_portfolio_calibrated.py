"""
Strategy #12 — Leverage-calibrated G10 rate-differential portfolio (core 4)

Strategy #10's realised vol came in at 5% despite a 10% target. The uncorrelated-
pairs sizing formula under-shoots because the long/short z-score structure
diversifies further than the formula predicts.

This strategy fixes the calibration via an ex-ante rolling-vol scalar:

  rolling_vol[t]      = 63-day annualised vol of Strategy #10's unlevered net return
  leverage_scalar[t]  = clip(TARGET_VOL / rolling_vol[t-1], 0, 3.0)
  weights_levered[t]  = clip(weights_unlevered[t] * leverage_scalar[t], ±0.60)

Identical signal, identical universe (EURUSD/GBPUSD/AUDUSD/USDCAD) — only the
leverage scaling is different. Lag of 1 day on the scalar prevents look-ahead.
"""
from __future__ import annotations

from pathlib import Path

from strat_10_g10_rate_diff_portfolio import run

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TRACK = REPO / "live" / "track_record"


if __name__ == "__main__":
    run(
        strategy_number=12,
        universe_name="core4",
        calibrate_leverage=True,
        calibration_window=63,
        max_leverage_scalar=3.0,
        max_per_pair_levered=0.60,
        csv_out=TRACK / "strategy_12_portfolio_calibrated_track_record.csv",
    )
