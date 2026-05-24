"""
Strategy #1 — Δ(EU 2Y − US 2Y) → next-day EURUSD

Hypothesis:
  When the 2Y rate differential moves in EU's favor today, EURUSD rises tomorrow.
  Exploration regression: β = +0.0335, R² = 7.5%, t-stat = +17.8, n = 3,910.
  (See notebooks/explore_2y_diff_vs_eurusd.py.)

Trading rule:
  Each business day at close, compute d_diff[t] = Δ(EU_2Y − US_2Y) on day t.
  position[t+1] = sign(d_diff[t])  ∈ {-1, 0, +1}
  Hold the position from t close to t+1 close, then re-evaluate.

Transaction cost:
  Round-trip cost = 5 pips total (2.5 pips buy + 2.5 pips sell).
  Charged as 2.5 pips per unit of |Δposition|:
    0 → +1     :  buy 1 unit  = 2.5 pips
    +1 → 0     :  sell 1 unit = 2.5 pips
    +1 → -1    :  sell 2 units = 5 pips  (full round-trip)

Data:
  US 2Y    — FRED `DGS2` (daily)
  EU 2Y    — ECB SDW `YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y` (daily, Euro-area AAA, ~Bund 2Y)
  EURUSD   — yfinance `EURUSD=X` (daily close)

Output:
  - reports/strategy_01_eu_us_2y_diff_eurusd.png   (equity curve + drawdown)
  - Summary printed to stdout
"""
from __future__ import annotations

import io
import logging
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from fredapi import Fred

logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"
REPORTS.mkdir(exist_ok=True)

# ── Parameters ───────────────────────────────────────────────────────────────
START               = "2010-01-04"
END                 = "2024-12-31"
ROUND_TRIP_PIPS     = 5      # total bid-ask round-trip cost (buy + sell)
COST_PER_UNIT_PIPS  = ROUND_TRIP_PIPS / 2   # = 2.5 pips per unit of |Δposition|
PIP_SIZE            = 0.0001 # EURUSD pip size in spot units
TRADING_DAYS        = 252


# ── Data fetchers ────────────────────────────────────────────────────────────
def fetch_us_2y() -> pd.Series:
    fred = Fred(api_key=os.environ["FRED_API_KEY"])
    s = fred.get_series("DGS2", observation_start=START, observation_end=END)
    s.index = pd.to_datetime(s.index)
    s.name = "US_2Y"
    return s.dropna()


def fetch_eu_2y() -> pd.Series:
    url = (
        "https://data-api.ecb.europa.eu/service/data/YC/"
        "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y"
        f"?format=csvdata&startPeriod={START}&endPeriod={END}"
    )
    r = requests.get(url, headers={"Accept": "text/csv"}, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    s = pd.Series(df["OBS_VALUE"].values,
                  index=pd.to_datetime(df["TIME_PERIOD"]),
                  name="EU_2Y")
    return s.sort_index().dropna()


def fetch_eurusd() -> pd.Series:
    df = yf.download("EURUSD=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.name = "EURUSD"
    s.index = pd.to_datetime(s.index)
    return s.dropna()


# ── Strategy logic ───────────────────────────────────────────────────────────
def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #1 — Δ(EU 2Y − US 2Y) → next-day EURUSD")
    print(f"  Period   : {START} → {END}")
    print(f"  Cost     : {ROUND_TRIP_PIPS} pips round-trip ({COST_PER_UNIT_PIPS} pips/unit traded)\n")

    print("Fetching data…")
    us = fetch_us_2y()
    eu = fetch_eu_2y()
    px = fetch_eurusd()

    # Align all series on a common business-day index
    idx = pd.bdate_range(start=START, end=END)
    us = us.reindex(idx).ffill()
    eu = eu.reindex(idx).ffill()
    px = px.reindex(idx).ffill()
    print(f"  Aligned to {len(idx)} business days\n")

    # Rate differential and its daily change
    rate_diff = (eu - us).rename("rate_diff_pp")
    d_diff    = rate_diff.diff().rename("d_diff_pp")

    # Signal: position decided at end-of-day t, held t→t+1
    raw_signal = np.sign(d_diff)
    position   = raw_signal.shift(1).fillna(0)   # tomorrow's position

    # Returns
    spot_ret  = px.pct_change()
    gross_ret = position * spot_ret

    # Costs: |Δposition| × (2.5 pips / spot)
    pos_change       = position.diff().abs().fillna(0)
    cost_in_returns  = pos_change * (COST_PER_UNIT_PIPS * PIP_SIZE) / px
    net_ret          = (gross_ret - cost_in_returns).dropna()

    # Benchmarks
    benchmark_ret = spot_ret.dropna()   # passive long EURUSD

    # ── Metrics ─────────────────────────────────────────────────────────────
    def stats(returns: pd.Series) -> dict:
        ann_ret = returns.mean() * TRADING_DAYS
        ann_vol = returns.std() * np.sqrt(TRADING_DAYS)
        sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve   = (1 + returns).cumprod()
        max_dd  = float(((curve / curve.cummax()) - 1).min())
        hit     = float((returns > 0).mean())
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=float(curve.iloc[-1] - 1))

    s_gross = stats(gross_ret.dropna())
    s_net   = stats(net_ret)
    s_bench = stats(benchmark_ret)

    n_trades       = int((pos_change > 0).sum())
    avg_turnover   = float(pos_change.mean())
    cost_drag_pct  = float(cost_in_returns.sum())

    # ── Print summary ──────────────────────────────────────────────────────
    print("=" * 60)
    print(f"  Strategy #1 — Δ(EU 2Y − US 2Y) → EURUSD next-day")
    print("=" * 60)
    print(f"  Observations         : {len(net_ret):,}")
    print(f"  Position flips       : {n_trades:,}  ({n_trades/len(net_ret)*100:.1f}% of days)")
    print(f"  Avg daily |Δpos|     : {avg_turnover:.3f}")
    print(f"  Cumulative cost drag : {cost_drag_pct*100:.1f}%  over the whole period")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10} {'EURUSD passive':>16}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}% {s_bench['ann_ret']*100:>15.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}% {s_bench['ann_vol']*100:>15.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f} {s_bench['sharpe']:>16.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}% {s_bench['max_dd']*100:>15.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}% {s_bench['cum']*100:>15.2f}%")
    print(f"  {'Hit Rate':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}% {s_bench['hit']*100:>15.2f}%")
    print("=" * 60)

    # ── Plot ────────────────────────────────────────────────────────────────
    gross_curve = (1 + gross_ret.dropna()).cumprod()
    net_curve   = (1 + net_ret).cumprod()
    bench_curve = (1 + benchmark_ret).cumprod()

    fig, axes = plt.subplots(2, 1, figsize=(12, 8),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.3, alpha=0.6,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {ROUND_TRIP_PIPS} pips round-trip (Sharpe {s_net['sharpe']:.2f})")
    ax.plot(bench_curve.index, bench_curve.values, color="gray", ls="--", lw=1,
            label=f"Passive long EURUSD (Sharpe {s_bench['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #1 — Δ(EU 2Y − US 2Y) → next-day EURUSD\n"
        f"{START} to {END}  ·  {len(net_ret):,} daily obs  ·  net of {ROUND_TRIP_PIPS} pips round-trip"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    drawdown = (net_curve / net_curve.cummax()) - 1
    ax.fill_between(drawdown.index, drawdown.values, 0, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown (net)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_01_eu_us_2y_diff_eurusd.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # Optional CSV time-series export — full track record, daily
    if csv_out is not None:
        cum_gross_full = (1 + gross_ret.fillna(0)).cumprod()
        cum_net_full = (1 + (gross_ret - cost_in_returns).fillna(0)).cumprod()

        csv_df = pd.DataFrame({
            "eu_2y_pct": eu,
            "us_2y_pct": us,
            "rate_diff_pp": rate_diff,
            "d_diff_pp": d_diff,
            "eurusd_close": px,
            "eurusd_return": spot_ret,
            "position": position,
            "gross_return": gross_ret,
            "cost": cost_in_returns,
            "net_return": gross_ret - cost_in_returns,
            "cum_gross": cum_gross_full,
            "cum_net": cum_net_full,
        })
        csv_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        csv_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(csv_df):,} rows × {csv_df.shape[1]} cols)")

    return dict(net=s_net, gross=s_gross, benchmark=s_bench,
                n_trades=n_trades, cost_drag=cost_drag_pct)


if __name__ == "__main__":
    run()
