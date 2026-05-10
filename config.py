"""
Central configuration for the G10 Systematic FX strategy.
All pairs, data series, signal parameters, and backtest settings live here.
"""
from __future__ import annotations

# ── Universe ──────────────────────────────────────────────────────────────────
# Expressed as base/quote vs USD. Direction convention:
#   positive signal → long the pair as listed (e.g. long EURUSD = long EUR short USD)
G10_PAIRS: dict[str, dict] = {
    "EURUSD": {"base": "EUR", "quote": "USD", "yf_ticker": "EURUSD=X"},
    "GBPUSD": {"base": "GBP", "quote": "USD", "yf_ticker": "GBPUSD=X"},
    "AUDUSD": {"base": "AUD", "quote": "USD", "yf_ticker": "AUDUSD=X"},
    "NZDUSD": {"base": "NZD", "quote": "USD", "yf_ticker": "NZDUSD=X"},
    "USDJPY": {"base": "USD", "quote": "JPY", "yf_ticker": "USDJPY=X"},
    "USDCAD": {"base": "USD", "quote": "CAD", "yf_ticker": "USDCAD=X"},
    "USDCHF": {"base": "USD", "quote": "CHF", "yf_ticker": "USDCHF=X"},
    "USDSEK": {"base": "USD", "quote": "SEK", "yf_ticker": "USDSEK=X"},
    "USDNOK": {"base": "USD", "quote": "NOK", "yf_ticker": "USDNOK=X"},
}

CURRENCIES = ["USD", "EUR", "GBP", "AUD", "NZD", "JPY", "CAD", "CHF", "SEK", "NOK"]

# ── FRED short-rate series (annualised %, daily or monthly) ───────────────────
# All freely available. Monthly OECD series resampled to daily via ffill.
RATE_SERIES: dict[str, str] = {
    "USD": "DFF",                  # Fed Funds effective (daily)
    "EUR": "ECBDFR",               # ECB deposit facility rate (daily)
    "GBP": "IUDSOIA",              # BoE SONIA overnight (daily)
    "AUD": "IRSTCI01AUM156N",      # OECD Australia 3m (monthly)
    "NZD": "IRSTCI01NZM156N",      # OECD New Zealand 3m (monthly)
    "JPY": "IRSTCI01JPM156N",      # OECD Japan 3m (monthly)
    "CAD": "IRSTCI01CAM156N",      # OECD Canada 3m (monthly)
    "CHF": "IRSTCI01CHM156N",      # OECD Switzerland 3m (monthly)
    "SEK": "IRSTCI01SEM156N",      # OECD Sweden 3m (monthly)
    "NOK": "IRSTCI01NOM156N",      # OECD Norway 3m (monthly)
}

# ── Signal parameters ─────────────────────────────────────────────────────────
SIGNAL_PARAMS: dict[str, dict] = {
    "carry": {
        "smoothing_days": 20,
        "weight": 0.40,
    },
    "momentum": {
        "fast_days": 21,     # ~1 month
        "slow_days": 63,     # ~3 months
        "weight": 0.35,
    },
    "cot": {
        "smoothing_weeks": 4,
        "weight": 0.25,
    },
}

# ── Vol-regime filter (VIX-based) ─────────────────────────────────────────────
VOL_REGIME: dict[str, float | str] = {
    "vix_fred_series": "VIXCLS",
    "vix_yf_ticker": "^VIX",
    "smoothing_days": 5,
    "elevated_threshold": 25.0,   # scale exposure to `elevated_scale`
    "crisis_threshold": 35.0,     # scale exposure to `crisis_scale`
    "elevated_scale": 0.50,
    "crisis_scale": 0.00,
}

# ── Backtest ──────────────────────────────────────────────────────────────────
BACKTEST: dict = {
    "start": "2010-01-01",
    "end": "2024-12-31",
    "rebalance_freq": "W-FRI",   # weekly, Friday close
    "n_long": 3,                 # top-N pairs to go long
    "n_short": 3,                # bottom-N pairs to go short
    "target_ann_vol": 0.10,      # 10% annualised target vol
    "realised_vol_window": 21,   # days for realised-vol estimate
    "cost_bps_roundtrip": 2.0,   # realistic G10 spot spread + commission
    "walk_forward": {
        "train_years": 3,
        "test_months": 6,
    },
}

# ── CFTC COT (Traders in Financial Futures — TFF report) ─────────────────────
# Leveraged Money (hedge-fund / CTA) net positioning from the CFTC TFF report.
# Key = currency, value = exact prefix to match in Market_and_Exchange_Names.
# SEK and NOK are not traded on CME, so they are omitted (signal falls through).
COT_MARKETS: dict[str, str] = {
    "EUR": "EURO FX",
    "GBP": "BRITISH POUND",
    "AUD": "AUSTRALIAN DOLLAR",
    "NZD": "NZ DOLLAR",
    "JPY": "JAPANESE YEN",
    "CAD": "CANADIAN DOLLAR",
    "CHF": "SWISS FRANC",
}
# Annual TFF zip pattern (text format, ~30KB per year compressed)
CFTC_HIST_URL = "https://www.cftc.gov/files/dea/history/fut_fin_txt_{year}.zip"
