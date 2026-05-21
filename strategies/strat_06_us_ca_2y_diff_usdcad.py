"""
Strategy #6 — Δ(US 2Y − CA 2Y) → next-day USDCAD
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=6,
        pair="USDCAD",
        base_ccy="US",
        quote_ccy="CA",
    )
