"""
Strategy #2 — Δ(GB 2Y − US 2Y) → next-day GBPUSD

Same structure as Strategy #1, applied to GBPUSD.

Signal   : d_diff[t] = Δ(GB_2Y − US_2Y) on day t
Position : pos[t+1] = sign(d_diff[t])
Hold     : 1 trading day
Cost     : 5 pips round-trip
Data     : TVC:GB02Y, TVC:US02Y (via tvDatafeed), GBPUSD=X (yfinance)
"""
from __future__ import annotations

from _rate_diff_strategy import run_rate_diff_strategy

if __name__ == "__main__":
    run_rate_diff_strategy(
        number=2,
        pair="GBPUSD",
        base_ccy="GB",
        quote_ccy="US",
    )
