"""
Strategy #4 — Δ(NZ 2Y − US 2Y) → next-day NZDUSD

Note: NZ 2Y data on TVC starts 2016-04-27, so this backtest is shorter than #1-#3.
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=4,
        pair="NZDUSD",
        base_ccy="NZ",
        quote_ccy="US",
    )
