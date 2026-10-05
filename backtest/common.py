"""
Shared harness for numbered strategies (strategies/strat_NN_*.py).

One place for: data loading (with the Yahoo FX timestamp fix), cost model,
performance stats, benchmark comparison, sub-period and hold-out reporting,
pre-registered pass criteria, and artefact output.

Yahoo FX timestamp fix (see notebooks/fx_timestamp_audit.py)
------------------------------------------------------------
Yahoo's daily FX bar dated D closes at ~00:00 UTC *at the start* of D — i.e.
it is the NY-evening price of D-1. Pairing that series with anything that
closes during day D (yields, VIX, oil, equities) is a 1-day look-ahead.
`fetch_fx()` re-dates the series so that close[D] ≈ 00:00 UTC D+1, which is
after every G10 2Y yield close on D. The re-dating is only valid from 2011
(2008–2010 Yahoo used a different convention), so aligned FX starts there.

Pure FX-price strategies (momentum, TA) are unaffected — they only compare
FX to itself.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

logging.getLogger("yfinance").setLevel(logging.ERROR)

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "reports"
TRACK = REPO / "live" / "track_record"
CACHE = REPO / "data" / "cache" / "yf"
YIELDS_CSV = REPO / "data" / "raw" / "tvc_2y_yields.csv"

TRADING_DAYS = 252

# Research window: pre-registered verdicts use IN-SAMPLE only; HOLDOUT is
# reported separately and never used to choose parameters.
START = "2011-01-01"
IN_SAMPLE_END = "2024-12-31"
HOLDOUT_START = "2025-01-01"

ALIGNED_FX_VALID_FROM = pd.Timestamp("2011-01-01")

# Round-trip cost in bps of notional, per pair. Conservative retail/small-fund
# levels (EURUSD 4 bps ≈ the old 5-pip assumption). Replaces the fixed-pip
# model, which made USDSEK/USDNOK ~20x too cheap.
FX_COST_BPS_RT = {
    "EURUSD": 4.0, "USDJPY": 4.0, "GBPUSD": 5.0, "USDCHF": 5.0,
    "AUDUSD": 5.0, "USDCAD": 5.0, "NZDUSD": 6.0,
    "USDSEK": 10.0, "USDNOK": 10.0,
}

SUBPERIODS = {
    "2011-15 ZIRP":       ("2011-01-01", "2015-12-31"),
    "2016-19 Divergence": ("2016-01-01", "2019-12-31"),
    "2020-21 COVID":      ("2020-01-01", "2021-12-31"),
    "2022-24 Hiking":     ("2022-01-01", "2024-12-31"),
}


# ── Data ────────────────────────────────────────────────────────────────────

def fetch_close(ticker: str, start: str = "2000-01-01", end: str | None = None,
                refresh: bool = False) -> pd.Series:
    """Daily close from yfinance, cached to data/cache/yf/ (gitignored)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{ticker.replace('^', '_').replace('=', '_')}.csv"
    if path.exists() and not refresh:
        s = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
    else:
        df = yf.download(ticker, start="2000-01-01", auto_adjust=True, progress=False)
        if df is None or df.empty:
            raise RuntimeError(f"yfinance returned no data for {ticker}")
        s = df["Close"].squeeze().dropna()
        s.to_frame(ticker).to_csv(path)
    s.name = ticker
    s.index = pd.to_datetime(s.index)
    return s.loc[start:end] if end else s.loc[start:]


def despike(px: pd.Series, z: float = 6.0, window: int = 60) -> pd.Series:
    """
    Drop bad single-day ticks: a move > z·σ that the next day reverses by > z·σ
    (Yahoo USDNOK has +28%/−52% in Mar-2020 and year-end spikes). Genuine
    jumps that stick (SNB Jan-2015, Brexit) are kept.
    """
    px = px.copy()
    for _ in range(3):
        r = np.log(px).diff()
        sigma = r.abs().rolling(window, min_periods=20).median().shift(1) * 1.4826
        big = r.abs() > z * sigma
        bad = big & big.shift(-1, fill_value=False) & (np.sign(r) != np.sign(r.shift(-1)))
        if not bad.any():
            break
        px[bad] = np.nan
        px = px.ffill()
    return px


def fetch_fx(pair: str, start: str = START, end: str | None = None,
             aligned: bool = True) -> pd.Series:
    """
    Yahoo FX close for `pair` (e.g. "EURUSD").

    aligned=True re-dates each bar one trading day earlier so close[D] is the
    price at ~00:00 UTC D+1 (see module docstring). Use aligned=False only to
    reproduce legacy results.
    """
    raw = despike(fetch_close(f"{pair}=X"))
    if aligned:
        raw = raw.shift(-1).dropna()
        raw = raw[raw.index >= ALIGNED_FX_VALID_FROM]
    raw.name = pair
    return raw.loc[start:end] if end else raw.loc[start:]


def fetch_fred(series_id: str, refresh: bool = False) -> pd.Series:
    """FRED series via the public CSV endpoint (no API key), cached."""
    import io
    import requests

    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"fred_{series_id}.csv"
    if path.exists() and not refresh:
        s = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
    else:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", timeout=60)
        r.raise_for_status()
        s = pd.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True).iloc[:, 0]
        s = pd.to_numeric(s, errors="coerce").dropna()
        s.to_frame(series_id).to_csv(path)
    s.name = series_id
    return s


# ccy → OECD 3M interbank rate on FRED (monthly average, percent)
SHORT_RATE_SERIES = {
    "USD": "IR3TIB01USM156N", "EUR": "IR3TIB01EZM156N", "GBP": "IR3TIB01GBM156N",
    "AUD": "IR3TIB01AUM156N", "NZD": "IR3TIB01NZM156N", "JPY": "IR3TIB01JPM156N",
    "CAD": "IR3TIB01CAM156N", "CHF": "IR3TIB01CHM156N", "SEK": "IR3TIB01SEM156N",
    "NOK": "IR3TIB01NOM156N",
}


def short_rates(index: pd.DatetimeIndex, point_in_time: bool = True) -> pd.DataFrame:
    """
    Daily 3M rates (percent) on `index`, columns = ccy.
    point_in_time=True: month M's average is usable only from the end of M+1
    (OECD publication lag) — use for SIGNALS. False: contemporaneous — use
    for carry ACCRUAL (what the forward points actually paid).
    """
    cols = {}
    for ccy, sid in SHORT_RATE_SERIES.items():
        s = fetch_fred(sid)
        s.index = s.index + (pd.offsets.MonthEnd(2) if point_in_time else pd.offsets.MonthBegin(0))
        cols[ccy] = s
    df = pd.DataFrame(cols).sort_index()
    return df.reindex(df.index.union(index)).ffill().reindex(index)


def carry_accrual(pair: str, index: pd.DatetimeIndex) -> pd.Series:
    """Daily return from holding +1 of `pair` (e.g. AUDUSD): (r_base − r_quote)/252."""
    r = short_rates(index, point_in_time=False)
    return (r[pair[:3]] - r[pair[3:]]) / 100 / TRADING_DAYS


def load_2y_yields() -> pd.DataFrame:
    """TVC 2Y yields (percent), columns = ccy codes. Closes fall 17:30–23:00 UTC on D."""
    if not YIELDS_CSV.exists():
        raise FileNotFoundError(f"{YIELDS_CSV} missing — run strategies/_fetch_yields.py")
    return pd.read_csv(YIELDS_CSV, index_col=0, parse_dates=True)


# ── Costs ───────────────────────────────────────────────────────────────────

G10_VS_USD = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCAD", "USDCHF", "USDSEK", "USDNOK"]


def foreign_vs_usd_returns(pairs: list[str] = G10_VS_USD, start: str = START,
                           end: str | None = None, with_carry: bool = True) -> pd.DataFrame:
    """
    Daily total return of being LONG each foreign ccy vs USD (USDxxx inverted),
    columns = foreign ccy code. Aligned FX; carry accrual included by default.
    """
    out = {}
    for pair in pairs:
        px = fetch_fx(pair, start=start, end=end)
        ret = px.pct_change()
        if with_carry:
            ret = ret + carry_accrual(pair, px.index)
        if pair.startswith("USD"):
            out[pair[3:]] = -ret
        else:
            out[pair[:3]] = ret
    return pd.DataFrame(out).dropna(how="all").iloc[1:]


def turnover_cost(weights: pd.Series | pd.DataFrame,
                  cost_bps_rt: float | dict[str, float]) -> pd.Series:
    """
    Cost drag in return units. Each unit of |Δweight| pays half the round-trip.
    `cost_bps_rt` is a scalar or a {column: bps} dict for DataFrames.
    """
    dw = weights.diff().abs()
    dw.iloc[0] = weights.iloc[0].abs() if isinstance(weights, pd.DataFrame) else abs(weights.iloc[0])
    if isinstance(weights, pd.Series):
        return dw * (cost_bps_rt / 2 / 1e4)
    bps = pd.Series(cost_bps_rt) if isinstance(cost_bps_rt, dict) else pd.Series(cost_bps_rt, index=weights.columns)
    return (dw * (bps.reindex(weights.columns) / 2 / 1e4)).sum(axis=1)


# ── Stats ───────────────────────────────────────────────────────────────────

def stats(returns: pd.Series, periods: int = TRADING_DAYS) -> dict:
    r = returns.dropna()
    if len(r) < 2 or r.std() == 0:
        return dict(sharpe=0.0, ann_ret=0.0, ann_vol=0.0, max_dd=0.0, sortino=0.0,
                    calmar=0.0, hit=0.0, skew=0.0, n=len(r))
    ann_ret = float(r.mean() * periods)
    ann_vol = float(r.std() * np.sqrt(periods))
    curve = (1 + r).cumprod()
    max_dd = float((curve / curve.cummax() - 1).min())
    dvol = float(r[r < 0].std() * np.sqrt(periods))
    return dict(
        sharpe=ann_ret / ann_vol,
        ann_ret=ann_ret,
        ann_vol=ann_vol,
        max_dd=max_dd,
        sortino=ann_ret / dvol if dvol > 0 else 0.0,
        calmar=ann_ret / abs(max_dd) if max_dd < 0 else 0.0,
        hit=float((r[r != 0] > 0).mean()) if (r != 0).any() else 0.0,
        skew=float(r.skew()),
        n=len(r),
    )


def information_ratio(strat: pd.Series, bench: pd.Series, periods: int = TRADING_DAYS) -> float:
    active = (strat - bench).dropna()
    return float(active.mean() / active.std() * np.sqrt(periods)) if active.std() > 0 else 0.0


def subperiod_sharpes(returns: pd.Series, periods: int = TRADING_DAYS,
                      subperiods: dict[str, tuple[str, str]] | None = None) -> dict[str, float]:
    return {k: stats(returns.loc[a:b], periods)["sharpe"] for k, (a, b) in (subperiods or SUBPERIODS).items()}


def ins_start(returns: pd.Series) -> str:
    return str(returns.dropna().index.min().year)


def split(returns: pd.Series) -> tuple[pd.Series, pd.Series]:
    """(in-sample, hold-out)."""
    return returns.loc[:IN_SAMPLE_END], returns.loc[HOLDOUT_START:]


# ── Reporting ───────────────────────────────────────────────────────────────

@dataclass
class Result:
    number: int | str
    title: str
    net: pd.Series
    gross: pd.Series | None = None
    benchmarks: dict[str, pd.Series] | None = None
    periods: int = TRADING_DAYS
    subperiods: dict[str, tuple[str, str]] | None = None

    def summary(self) -> dict:
        ins, hold = split(self.net)
        out = {"in_sample": stats(ins, self.periods), "holdout": stats(hold, self.periods),
               "subperiods": subperiod_sharpes(ins, self.periods, self.subperiods)}
        if self.gross is not None:
            out["gross_in_sample"] = stats(split(self.gross)[0], self.periods)
        for name, b in (self.benchmarks or {}).items():
            b_ins = split(b)[0]
            out[f"bench:{name}"] = stats(b_ins, self.periods)
            out[f"ir_vs:{name}"] = information_ratio(ins, b_ins, self.periods)
        return out

    def print(self, criteria: dict[str, bool] | None = None) -> dict:
        s = self.summary()
        i, h = s["in_sample"], s["holdout"]
        print(f"\nStrategy #{self.number} — {self.title}")
        print(f"  In-sample {ins_start(self.net)}–{IN_SAMPLE_END[:4]}: SR {i['sharpe']:+.2f} | ret {i['ann_ret']:+.2%} "
              f"| vol {i['ann_vol']:.2%} | MaxDD {i['max_dd']:.1%} | skew {i['skew']:+.2f}")
        if "gross_in_sample" in s:
            print(f"  Gross in-sample SR: {s['gross_in_sample']['sharpe']:+.2f}")
        for k, v in s.items():
            if k.startswith("bench:"):
                name = k[6:]
                print(f"  vs {name}: bench SR {v['sharpe']:+.2f} | IR {s['ir_vs:' + name]:+.2f}")
        print("  Sub-periods: " + " | ".join(f"{k} {v:+.2f}" for k, v in s["subperiods"].items()))
        print(f"  Hold-out {HOLDOUT_START[:4]}+ ({h['n']} obs): SR {h['sharpe']:+.2f} | ret {h['ann_ret']:+.2%}")
        if criteria:
            passed = sum(criteria.values())
            print(f"  Pre-registered criteria: {passed}/{len(criteria)} pass")
            for name, ok in criteria.items():
                print(f"    {'✓' if ok else '✗'} {name}")
        return s

    def save(self, extra: pd.DataFrame | None = None, slug: str = "") -> Path:
        """Equity-curve PNG to reports/. Daily CSV only if `extra` is given."""
        import matplotlib.pyplot as plt

        slug = slug or f"strategy_{self.number}"
        fig, ax = plt.subplots(figsize=(11, 5))
        (1 + self.net).cumprod().plot(ax=ax, label="Strategy (net)", lw=1.6)
        for name, b in (self.benchmarks or {}).items():
            (1 + b.reindex(self.net.index).fillna(0)).cumprod().plot(ax=ax, label=name, lw=1, alpha=0.7)
        ax.axvline(pd.Timestamp(HOLDOUT_START), color="grey", ls="--", lw=0.8)
        ax.text(pd.Timestamp(HOLDOUT_START), ax.get_ylim()[1], " hold-out", va="top", fontsize=8, color="grey")
        ax.set_title(f"Strategy #{self.number} — {self.title}", fontsize=11)
        ax.set_ylabel("Growth of 1")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        path = REPORTS / f"{slug}.png"
        fig.savefig(path, dpi=120)
        plt.close(fig)
        if extra is not None:
            TRACK.mkdir(parents=True, exist_ok=True)
            extra.to_csv(TRACK / f"{slug}_track_record.csv")
        return path
