"""
Strategy #7 — Δ(US 2Y − CH 2Y) → next-day USDCHF
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=7,
        pair="USDCHF",
        base_ccy="US",
        quote_ccy="CH",
    )
