"""
Strategy #3 — Δ(AU 2Y − US 2Y) → next-day AUDUSD
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=3,
        pair="AUDUSD",
        base_ccy="AU",
        quote_ccy="US",
    )
