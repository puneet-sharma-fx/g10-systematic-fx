"""
Strategy #18 — Equal-weight rate-diff portfolio (diagnostic benchmark for #10/#12)

Same universe (core 4: EURUSD, GBPUSD, AUDUSD, USDCAD), same signal source
(d_diff = Δ(base_2Y − quote_2Y)), same leverage calibration (rolling-vol scalar
to hit 10% portfolio vol target) as Strategy #12.

The ONLY difference: position sizing.
    #12: cross-section z-score × inverse-vol × portfolio-vol scalar
    #18: sign(d_diff) × (1/N) per pair  (pure equal-weight, direction only)

This isolates the value of the z-score/inverse-vol/concentration-cap machinery.

Interpretation of the comparison:
    Sharpe(#18) ≈ Sharpe(#12)  → the sophistication adds no edge; direction is everything
    Sharpe(#18) < Sharpe(#12)  → the z-score/magnitude info genuinely adds value
    Sharpe(#18) > Sharpe(#12)  → we've been over-engineering; equal-weight is simpler and better
"""
from __future__ import annotations

from pathlib import Path

from strat_10_g10_rate_diff_portfolio import run

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TRACK = REPO / "live" / "track_record"


if __name__ == "__main__":
    run(
        strategy_number=18,
        universe_name="core4",
        calibrate_leverage=True,        # same vol-target framework as #12
        calibration_window=63,
        max_leverage_scalar=3.0,
        max_per_pair_levered=0.60,
        equal_weight=True,              # the only meaningful difference vs #12
        csv_out=TRACK / "strategy_18_portfolio_equal_weight_track_record.csv",
    )
