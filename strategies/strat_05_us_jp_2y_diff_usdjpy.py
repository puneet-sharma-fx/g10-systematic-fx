"""
Strategy #5 — Δ(US 2Y − JP 2Y) → next-day USDJPY

USDJPY is quoted base=USD / quote=JPY, so the signal uses US − JP rates.
JPY pip size = 0.01 (handled automatically by _rate_diff_strategy).
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=5,
        pair="USDJPY",
        base_ccy="US",
        quote_ccy="JP",
    )
