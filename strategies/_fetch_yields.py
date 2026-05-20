"""
One-time fetch of daily 2Y yield data from TradingView (TVC:XX02Y).

Saves to data/raw/tvc_2y_yields.csv  (gitignored — do not redistribute).

Run once to populate the local cache:
    python strategies/_fetch_yields.py

Re-run periodically to refresh.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from tvDatafeed import Interval, TvDatafeed

logging.basicConfig(level=logging.WARNING)
logging.getLogger("tvDatafeed").setLevel(logging.WARNING)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RAW = REPO / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
OUT = RAW / "tvc_2y_yields.csv"

TICKERS = {
    "US": "US02Y",
    "EU": "DE02Y",   # German 2Y as the EUR benchmark
    "GB": "GB02Y",
    "AU": "AU02Y",
    "NZ": "NZ02Y",
    "JP": "JP02Y",
    "CA": "CA02Y",
    "CH": "CH02Y",
    "SE": "SE02Y",
    # NOK skipped — TradingView returns empty for NO02Y
}


def main() -> None:
    tv = TvDatafeed()   # anonymous mode

    series: dict[str, pd.Series] = {}
    for ccy, ticker in TICKERS.items():
        print(f"  Fetching TVC:{ticker} ...", end=" ", flush=True)
        try:
            df = tv.get_hist(symbol=ticker, exchange="TVC",
                             interval=Interval.in_daily, n_bars=5000)
            if df is None or len(df) == 0:
                print("EMPTY")
                continue
            s = df["close"].copy()
            s.index = pd.to_datetime(s.index).normalize()
            s.name = ccy
            series[ccy] = s
            print(f"OK ({len(s)} obs, {s.index[0].date()} → {s.index[-1].date()})")
        except Exception as exc:
            print(f"FAIL: {exc}")

    if not series:
        raise RuntimeError("No yield series fetched")

    df = pd.DataFrame(series).sort_index()
    df.to_csv(OUT, float_format="%.6f")
    print(f"\nSaved {len(df)} rows × {df.shape[1]} cols → {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
