"""
Data fetching layer: FRED (rates, VIX) and yfinance (FX spot prices).
Requires FRED_API_KEY environment variable (free at fred.stlouisfed.org).
"""
from __future__ import annotations

import os
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

from config import G10_PAIRS, RATE_SERIES, VOL_REGIME

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

log = logging.getLogger(__name__)


def _fred_client():
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "FRED_API_KEY not set. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    from fredapi import Fred
    return Fred(api_key=api_key)


def fetch_fx_prices(
    start: str,
    end: str,
    pairs: dict | None = None,
    field: str = "Close",
) -> pd.DataFrame:
    """
    Returns a DataFrame of daily FX close prices indexed by date.
    Columns are pair names (e.g. 'EURUSD'). Prices are in quote-per-base terms
    as listed in config.G10_PAIRS.
    """
    if pairs is None:
        pairs = G10_PAIRS

    tickers = {name: meta["yf_ticker"] for name, meta in pairs.items()}
    raw = yf.download(
        list(tickers.values()),
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
    )

    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw[field]
        prices.columns = {v: k for k, v in tickers.items()}[c] if len(tickers) == 1 else [
            {v: k for k, v in tickers.items()}.get(c, c) for c in prices.columns
        ]
    else:
        # single ticker returned as flat DataFrame
        pair_name = list(tickers.keys())[0]
        prices = raw[[field]].rename(columns={field: pair_name})

    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index().ffill()
    log.info("Fetched FX prices: %s rows, %s pairs", len(prices), prices.shape[1])
    return prices


def fetch_short_rates(
    start: str,
    end: str,
    currencies: list[str] | None = None,
) -> pd.DataFrame:
    """
    Returns daily short-rate DataFrame (annualised %) indexed by date.
    Monthly OECD series are forward-filled to daily frequency.
    """
    fred = _fred_client()
    if currencies is None:
        currencies = list(RATE_SERIES.keys())

    frames: dict[str, pd.Series] = {}
    for ccy in currencies:
        series_id = RATE_SERIES[ccy]
        try:
            s = fred.get_series(series_id, observation_start=start, observation_end=end)
            s.name = ccy
            frames[ccy] = s
        except Exception as exc:
            log.warning("Could not fetch %s (%s): %s", ccy, series_id, exc)

    df = pd.DataFrame(frames)
    df.index = pd.to_datetime(df.index)

    # Resample to daily and forward-fill (handles monthly OECD series)
    daily_idx = pd.date_range(start=start, end=end, freq="B")
    df = df.reindex(daily_idx).ffill()
    log.info("Fetched short rates: %s rows, %s currencies", len(df), df.shape[1])
    return df


def fetch_vix(start: str, end: str) -> pd.Series:
    """
    Returns daily VIX close as a Series. Tries yfinance first, falls back to FRED.
    """
    try:
        raw = yf.download("^VIX", start=start, end=end, auto_adjust=True, progress=False)
        vix = raw["Close"].squeeze()
        vix.name = "VIX"
        vix.index = pd.to_datetime(vix.index)
        if len(vix) > 0:
            log.info("Fetched VIX from yfinance: %s rows", len(vix))
            return vix.sort_index().ffill()
    except Exception as exc:
        log.warning("yfinance VIX fetch failed (%s), trying FRED", exc)

    fred = _fred_client()
    s = fred.get_series(
        VOL_REGIME["vix_fred_series"],
        observation_start=start,
        observation_end=end,
    )
    s.name = "VIX"
    s.index = pd.to_datetime(s.index)
    daily_idx = pd.date_range(start=start, end=end, freq="B")
    s = s.reindex(daily_idx).ffill()
    log.info("Fetched VIX from FRED: %s rows", len(s))
    return s
