"""
Strategy #14 — Calibrated rate-diff portfolio with 50-DMA trend confirmation overlay

Strategy #12 (the leverage-calibrated rate-diff portfolio) with one additional rule:
each pair's position is only retained if its sign agrees with the pair's 50-DMA
trend direction. Signal-but-against-trend setups are dropped (weight set to 0
for that day-pair cell).

Hypothesis:
    The rate-diff signal already works. A trend-confirmation overlay should
    further reduce drawdowns by avoiding "right signal, wrong regime" trades —
    e.g. d_diff says long EURUSD but EURUSD is in a sustained downtrend.

Rule (per pair, per day):
    keep weight if sign(weight) × sign(close − 50-DMA) ≥ 0
    drop to 0 otherwise

The leverage scalar is re-calibrated against the *filtered* unlevered returns,
so the strategy still targets 10% portfolio vol regardless of how many signals
the trend filter removes.

Identical to #12 in every other respect (universe, signal, cost, sizing).
"""
from __future__ import annotations

from pathlib import Path

from strat_10_g10_rate_diff_portfolio import run

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TRACK = REPO / "live" / "track_record"


if __name__ == "__main__":
    run(
        strategy_number=14,
        universe_name="core4",
        calibrate_leverage=True,
        calibration_window=63,
        max_leverage_scalar=3.0,
        max_per_pair_levered=0.60,
        trend_filter=True,
        trend_ma_period=50,
        csv_out=TRACK / "strategy_14_portfolio_trend_filtered_track_record.csv",
    )
