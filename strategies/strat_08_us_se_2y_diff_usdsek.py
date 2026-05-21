"""
Strategy #8 — Δ(US 2Y − SE 2Y) → next-day USDSEK

Note: SE 2Y data on TVC starts 2012-08-14, so backtest covers ~12 years.
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=8,
        pair="USDSEK",
        base_ccy="US",
        quote_ccy="SE",
    )
