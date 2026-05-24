"""
Export daily track-record CSVs for the three cleanest strategies:
  - Strategy #1  EURUSD   (FRED + ECB SDW + yfinance)
  - Strategy #2  GBPUSD   (TVC + yfinance)
  - Strategy #6  USDCAD   (TVC + yfinance)

Each CSV contains the full daily time series:
    date, base_2y_pct, quote_2y_pct, rate_diff_pp, d_diff_pp,
    <pair>_close, <pair>_return, position,
    gross_return, cost, net_return, cum_gross, cum_net

Auditable track record — recruiters can re-derive Sharpe / DD / hit-rate from the CSV.

Run:
    python strategies/_export_csvs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

REPO = HERE.parent
TRACK = REPO / "live" / "track_record"
TRACK.mkdir(parents=True, exist_ok=True)


def main() -> None:
    from strat_01_eu_us_2y_diff_eurusd import run as run_01
    from _rate_diff_strategy import run_rate_diff_strategy

    print("=" * 60)
    print("  Exporting daily track-record CSVs for Strategies #1, #2, #6")
    print("=" * 60)

    # ── #1 EURUSD ──────────────────────────────────────────────────────────
    run_01(csv_out=TRACK / "strategy_01_eurusd_track_record.csv")

    # ── #2 GBPUSD ──────────────────────────────────────────────────────────
    run_rate_diff_strategy(
        number=2, pair="GBPUSD", base_ccy="GB", quote_ccy="US",
        csv_out=TRACK / "strategy_02_gbpusd_track_record.csv",
    )

    # ── #6 USDCAD ──────────────────────────────────────────────────────────
    run_rate_diff_strategy(
        number=6, pair="USDCAD", base_ccy="US", quote_ccy="CA",
        csv_out=TRACK / "strategy_06_usdcad_track_record.csv",
    )

    print("\n" + "=" * 60)
    print("  All 3 CSVs exported to live/track_record/")
    print("=" * 60)


if __name__ == "__main__":
    main()
