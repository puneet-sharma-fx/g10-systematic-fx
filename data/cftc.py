"""
CFTC Commitments of Traders — legacy futures-only report.
Downloads annual zip files from cftc.gov and extracts non-commercial net positioning
for G10 FX futures traded on the CME.
"""

import io
import logging
import zipfile
from datetime import datetime

import pandas as pd
import requests

from config import COT_MARKETS, CFTC_HIST_URL, CFTC_CURRENT_URL

log = logging.getLogger(__name__)

_COT_COLS = [
    "Market_and_Exchange_Names",
    "As_of_Date_In_Form_YYMMDD",
    "Open_Interest_All",
    "NonComm_Positions_Long_All",
    "NonComm_Positions_Short_All",
    "NonComm_Postions_Spread_All",  # CFTC typo in source — preserved
]

_TIMEOUT = 30  # seconds


def _download_cot_year(year: int) -> pd.DataFrame:
    url = CFTC_HIST_URL.format(year=year) if year < datetime.now().year else CFTC_CURRENT_URL
    log.info("Downloading CFTC COT: %s", url)
    resp = requests.get(url, timeout=_TIMEOUT)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        csv_name = next(n for n in zf.namelist() if n.endswith(".txt") or n.endswith(".csv"))
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, usecols=lambda c: c in _COT_COLS, low_memory=False)

    return df


def fetch_cot(start: str, end: str) -> pd.DataFrame:
    """
    Returns a weekly DataFrame of net-speculative positioning ratio per currency.

    Net ratio = (NonComm_Long - NonComm_Short) / Open_Interest

    Columns: one per currency in COT_MARKETS (e.g. 'EUR', 'GBP', ...).
    Index: weekly dates (Tuesday report date, parsed from As_of_Date_In_Form_YYMMDD).
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
        raise RuntimeError("Could not download any CFTC COT data")

    raw = pd.concat(frames, ignore_index=True)

    # Parse date: YYMMDD → datetime
    raw["date"] = pd.to_datetime(raw["As_of_Date_In_Form_YYMMDD"].astype(str), format="%y%m%d")
    raw = raw[(raw["date"] >= start) & (raw["date"] <= end)]

    records: dict[str, pd.Series] = {}
    for ccy, market_substr in COT_MARKETS.items():
        mask = raw["Market_and_Exchange_Names"].str.contains(market_substr, case=False, na=False)
        sub = raw[mask].copy()
        if sub.empty:
            log.warning("No COT data found for %s ('%s')", ccy, market_substr)
            continue

        sub = sub.drop_duplicates("date").set_index("date").sort_index()
        net_long = sub["NonComm_Positions_Long_All"] - sub["NonComm_Positions_Short_All"]
        oi = sub["Open_Interest_All"].replace(0, float("nan"))
        records[ccy] = (net_long / oi).rename(ccy)

    df = pd.DataFrame(records)
    df.index = pd.to_datetime(df.index)
    log.info("CFTC COT: %s weeks, %s currencies", len(df), df.shape[1])
    return df
