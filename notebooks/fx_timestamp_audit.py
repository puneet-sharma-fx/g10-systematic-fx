"""
FX timestamp audit — resolves the rate-diff question left open by Strategy #21.

Three pieces of evidence:
  1. Yahoo daily FX close vs Yahoo hourly snapshots (last ~700 days): which
     UTC hour does the daily "Close" dated D actually represent?
  2. Yahoo daily FX returns vs FRED H.10 noon-NY fixings, year by year
     2008–2024: does the timestamp convention hold over the backtest period?
  3. The full rate-diff family (#1–#8 pairs + #18 core-4 equal-weight
     portfolio) re-run on legacy (misdated) vs aligned FX.

Finding: Yahoo FX close[D] ≈ 00:00 UTC on D, i.e. NY evening of D-1. The
legacy rate-diff backtests therefore traded the SAME-DAY co-move of yields
and FX (look-ahead), not next-day prediction.

Run:  python notebooks/fx_timestamp_audit.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import (FX_COST_BPS_RT, IN_SAMPLE_END, REPORTS, START,  # noqa: E402
                             fetch_fx, load_2y_yields, split, stats, turnover_cost)

# pair → (base yield, quote yield)
RATE_DIFF_PAIRS = {
    "EURUSD": ("EU", "US"), "GBPUSD": ("GB", "US"), "AUDUSD": ("AU", "US"),
    "NZDUSD": ("NZ", "US"), "USDJPY": ("US", "JP"), "USDCAD": ("US", "CA"),
    "USDCHF": ("US", "CH"), "USDSEK": ("US", "SE"),
}
CORE4 = ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD"]
# FRED H.10 noon-NY fixings, same orientation as the Yahoo pair
FRED_NOON = {"EURUSD": "DEXUSEU", "GBPUSD": "DEXUSUK", "USDJPY": "DEXJPUS"}


# ── 1. Hourly snapshot profile ──────────────────────────────────────────────

def hourly_profile(pair: str) -> pd.Series:
    d = yf.download(f"{pair}=X", period="700d", interval="1d", progress=False, auto_adjust=True)["Close"].squeeze()
    h = yf.download(f"{pair}=X", period="700d", interval="1h", progress=False, auto_adjust=True)["Close"].squeeze()
    dr = np.log(d).diff().dropna()
    out = {}
    for off in range(-24, 25):
        snaps = {}
        for day in d.index:
            t = pd.Timestamp(day, tz="UTC") + pd.Timedelta(hours=off)
            s = h[:t]
            if len(s) and (t - s.index[-1]) < pd.Timedelta(hours=2):
                snaps[day] = s.iloc[-1]
        sr = np.log(pd.Series(snaps)).diff()
        out[off] = pd.concat([dr, sr], axis=1).dropna().corr().iloc[0, 1]
    return pd.Series(out)


# ── 2. Yahoo vs FRED noon by year ───────────────────────────────────────────

def fred_csv(series_id: str) -> pd.Series:
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", timeout=60)
    s = pd.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True).iloc[:, 0]
    return pd.to_numeric(s, errors="coerce").dropna()


def noon_check(pair: str) -> pd.DataFrame:
    noon = np.log(fred_csv(FRED_NOON[pair])).diff()
    yh = np.log(yf.download(f"{pair}=X", start="2008-01-01", progress=False,
                            auto_adjust=True)["Close"].squeeze()).diff()
    rows = []
    for yr in range(2008, 2025):
        row = {"year": yr}
        for lag, name in ((-1, "noon D-1"), (0, "noon D")):
            j = pd.concat([yh, noon.shift(-lag)], axis=1).dropna()
            j = j[j.index.year == yr]
            row[name] = j.corr().iloc[0, 1]
        rows.append(row)
    return pd.DataFrame(rows).set_index("year")


# ── 3. Rate-diff family re-run ──────────────────────────────────────────────

def rate_diff_returns(pair: str, aligned: bool) -> tuple[pd.Series, pd.Series]:
    """(net, position). pos[D] = sign(Δdiff[D]) held from close[D] to close[D+1]."""
    base, quote = RATE_DIFF_PAIRS[pair]
    y = load_2y_yields()
    fx = fetch_fx(pair, start=START, end=IN_SAMPLE_END, aligned=aligned)
    idx = fx.index
    diff = (y[base] - y[quote]).reindex(idx).ffill()
    signal = np.sign(diff.diff())
    pos = signal.shift(1).fillna(0)                 # earns close[D-1]→close[D]
    ret = fx.pct_change().fillna(0)
    net = pos * ret - turnover_cost(pos, FX_COST_BPS_RT[pair])
    first = max(y[base].first_valid_index(), y[quote].first_valid_index())
    return net[net.index > first], pos


def main() -> None:
    print("1. Which UTC hour is Yahoo's daily FX close? (corr of daily ret vs hourly-snapshot ret)")
    prof = {p: hourly_profile(p) for p in ("EURUSD", "USDJPY", "AUDUSD")}
    for p, s in prof.items():
        print(f"   {p}: best offset {s.idxmax():+d}h from 00:00 UTC on D (corr {s.max():.2f}); "
              f"at +20h (≈ NY close D): {s[20]:.2f}")

    print("\n2. Yahoo return on D vs FRED noon-NY return (D-1 vs D), by year")
    noon = {p: noon_check(p) for p in FRED_NOON}
    print(pd.concat(noon, axis=1).round(2).to_string())

    print("\n3. Rate-diff family, in-sample 2011–2024, net of per-pair bps costs")
    rows, legacy_nets, aligned_nets = [], {}, {}
    for pair in RATE_DIFF_PAIRS:
        leg, _ = rate_diff_returns(pair, aligned=False)
        ali, _ = rate_diff_returns(pair, aligned=True)
        legacy_nets[pair], aligned_nets[pair] = leg, ali
        rows.append({"pair": pair, "legacy SR": stats(leg)["sharpe"], "aligned SR": stats(ali)["sharpe"],
                     "aligned ann ret": stats(ali)["ann_ret"]})
    ew_leg = pd.concat([legacy_nets[p] for p in CORE4], axis=1).fillna(0).mean(axis=1)
    ew_ali = pd.concat([aligned_nets[p] for p in CORE4], axis=1).fillna(0).mean(axis=1)
    rows.append({"pair": "#18 core-4 EW", "legacy SR": stats(ew_leg)["sharpe"],
                 "aligned SR": stats(ew_ali)["sharpe"], "aligned ann ret": stats(ew_ali)["ann_ret"]})
    table = pd.DataFrame(rows).set_index("pair")
    print(table.to_string(float_format=lambda x: f"{x:+.2f}"))

    # Figure
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    for p, s in prof.items():
        axes[0].plot(s.index, s.values, label=p)
    axes[0].axvline(0, color="k", lw=0.6)
    axes[0].axvline(20, color="grey", ls="--", lw=0.8)
    axes[0].text(20, 0.05, " NY close\n of D", fontsize=8)
    axes[0].set(title="Yahoo daily close[D] ≈ price at 00:00 UTC on D",
                xlabel="snapshot hour offset from 00:00 UTC on D", ylabel="corr with daily return")
    axes[0].legend(fontsize=8)
    n = pd.concat(noon, axis=1)
    for p in FRED_NOON:
        axes[1].plot(n.index, n[(p, "noon D-1")], label=f"{p} vs noon D-1")
        axes[1].plot(n.index, n[(p, "noon D")], ls="--", label=f"{p} vs noon D")
    axes[1].set(title="Holds across the backtest (2011+)", xlabel="year", ylabel="corr")
    axes[1].legend(fontsize=7)
    table[["legacy SR", "aligned SR"]].plot.bar(ax=axes[2])
    axes[2].axhline(0, color="k", lw=0.6)
    axes[2].set(title="Rate-diff family: legacy vs aligned FX (net SR)", ylabel="Sharpe")
    axes[2].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    out = REPORTS / "fx_timestamp_audit.png"
    fig.savefig(out, dpi=120)
    print(f"\n  chart → {out.relative_to(REPORTS.parent)}")


if __name__ == "__main__":
    main()
