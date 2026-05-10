"""
CFTC Commitments of Traders — Traders in Financial Futures (TFF) report.

Downloads annual zip files from cftc.gov and extracts the Leveraged Money
(hedge-fund / CTA) net positioning for G10 FX futures traded on the CME.

Leveraged Money is the cleanest publicly available proxy for speculator flow:
it isolates hedge funds and managed futures from real-money allocators
(Asset Managers), sell-side dealers, and small accounts.
"""
from __future__ import annotations

import io
import logging
import zipfile

import pandas as pd
import requests

from config import COT_MARKETS, CFTC_HIST_URL

log = logging.getLogger(__name__)

# Columns we keep from the TFF report
_COT_COLS = [
    "Market_and_Exchange_Names",
    "Report_Date_as_YYYY-MM-DD",
    "Open_Interest_All",
    "Lev_Money_Positions_Long_All",
    "Lev_Money_Positions_Short_All",
]

_TIMEOUT = 30  # seconds


def _download_cot_year(year: int) -> pd.DataFrame:
    url = CFTC_HIST_URL.format(year=year)
    log.info("Downloading CFTC TFF: %s", url)
    resp = requests.get(url, timeout=_TIMEOUT)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        # The TFF zip contains a single .txt file (e.g. FinFutYY.txt)
        text_name = next(n for n in zf.namelist() if n.lower().endswith(".txt"))
        with zf.open(text_name) as f:
            df = pd.read_csv(f, usecols=lambda c: c in _COT_COLS, low_memory=False)
    return df


def fetch_cot(start: str, end: str) -> pd.DataFrame:
    """
    Returns a weekly DataFrame of Leveraged-Money net-positioning ratio per currency.

    Net ratio = (Lev_Money_Long - Lev_Money_Short) / Open_Interest

    Columns: one per currency in COT_MARKETS (e.g. 'EUR', 'GBP', ...).
    Index: weekly dates (Tuesday report date).
    """
    start_year = pd.Timestamp(start).year
    end_year = pd.Timestamp(end).year

    frames = []
    for yr in range(start_year, end_year + 1):
        try:
            frames.append(_download_cot_year(yr))
        except Exception as exc:
            log.warning("CFTC download failed for %s: %s", yr, exc)

    if not frames:
        raise RuntimeError("Could not download any CFTC TFF data")

    raw = pd.concat(frames, ignore_index=True)

    raw["date"] = pd.to_datetime(raw["Report_Date_as_YYYY-MM-DD"], errors="coerce")
    raw = raw.dropna(subset=["date"])
    raw = raw[(raw["date"] >= start) & (raw["date"] <= end)]

    records: dict[str, pd.Series] = {}
    for ccy, market_substr in COT_MARKETS.items():
        mask = raw["Market_and_Exchange_Names"].str.contains(market_substr, case=False, na=False)
        sub = raw[mask].copy()
        if sub.empty:
            log.warning("No TFF data found for %s ('%s')", ccy, market_substr)
            continue

        sub = sub.drop_duplicates("date").set_index("date").sort_index()
        net_long = sub["Lev_Money_Positions_Long_All"] - sub["Lev_Money_Positions_Short_All"]
        oi = sub["Open_Interest_All"].replace(0, float("nan"))
        records[ccy] = (net_long / oi).rename(ccy)

    df = pd.DataFrame(records)
    df.index = pd.to_datetime(df.index)
    log.info("CFTC TFF: %s weeks, %s currencies", len(df), df.shape[1])
    return df
