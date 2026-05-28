"""
Sweep the cross-sectional momentum portfolio across lookback windows.

Strategy #11 used a 21-day lookback and printed net Sharpe −0.34. The momentum
literature favours longer windows (63d ≈ 3m, 252d ≈ 12m). This script re-runs the
same portfolio (8 G10 pairs, weekly rebalance, long top-2 / short bottom-2, 5 pips RT)
across {21, 63, 126, 252} day lookbacks to see whether a longer window rescues it.

Output:
  - reports/momentum_lookback_sweep.png   (overlaid equity curves)
  - comparison table printed to stdout
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"

START = "2010-01-04"
END   = "2024-12-31"
N_LONG = 2
N_SHORT = 2
LEG_WEIGHT = 0.25
COST_RT_PIPS = 5.0
WEEKS_PER_YEAR = 52
LOOKBACKS = [21, 63, 126, 252]

PAIRS = [
    ("EURUSD", 0.0001), ("GBPUSD", 0.0001), ("AUDUSD", 0.0001), ("NZDUSD", 0.0001),
    ("USDJPY", 0.01), ("USDCAD", 0.0001), ("USDCHF", 0.0001), ("USDSEK", 0.0001),
]


def _fetch(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END, auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    return s.dropna()


def run_one(px_daily: pd.DataFrame, lookback: int) -> tuple[dict, pd.Series]:
    pair_names = list(px_daily.columns)
    pip = {p[0]: p[1] for p in PAIRS}

    ret_lb = px_daily.pct_change(periods=lookback)
    px_w = px_daily.resample("W-FRI").last()
    ret_lb_w = ret_lb.resample("W-FRI").last()

    weights = pd.DataFrame(0.0, index=px_w.index, columns=pair_names)
    for dt in ret_lb_w.index:
        row = ret_lb_w.loc[dt].dropna()
        if len(row) < N_LONG + N_SHORT:
            continue
        ranked = row.sort_values(ascending=False)
        for p in ranked.head(N_LONG).index:
            weights.loc[dt, p] = +LEG_WEIGHT
        for p in ranked.tail(N_SHORT).index:
            weights.loc[dt, p] = -LEG_WEIGHT

    pair_ret_w = px_w.pct_change()
    positions = weights.shift(1).fillna(0)
    gross = (positions * pair_ret_w).sum(axis=1)

    cost_unit = COST_RT_PIPS / 2.0
    turn = weights.diff().abs().fillna(0)
    cost = sum(turn[n] * (cost_unit * pip[n]) / px_w[n] for n in pair_names)
    net = (gross - cost).dropna()

    first_valid = ret_lb_w.dropna(how="all").index.min() + pd.Timedelta(days=7)
    net = net[net.index >= first_valid]

    ann_ret = net.mean() * WEEKS_PER_YEAR
    ann_vol = net.std() * np.sqrt(WEEKS_PER_YEAR)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve = (1 + net).cumprod()
    max_dd = float(((curve / curve.cummax()) - 1).min())
    hit = float((net > 0).mean())
    stats = dict(lookback=lookback, ann_ret=ann_ret, ann_vol=ann_vol,
                 sharpe=sharpe, max_dd=max_dd, hit=hit,
                 cum=float(curve.iloc[-1] - 1), n=len(net))
    return stats, curve


def main() -> None:
    print("Fetching FX prices...")
    idx = pd.bdate_range(start=START, end=END)
    px_daily = pd.DataFrame({name: _fetch(name).reindex(idx).ffill() for name, _ in PAIRS})

    results = []
    curves = {}
    for lb in LOOKBACKS:
        stats, curve = run_one(px_daily, lb)
        results.append(stats)
        curves[lb] = curve
        print(f"  lookback {lb:>3}d → net Sharpe {stats['sharpe']:+.2f}, "
              f"ann {stats['ann_ret']*100:+.1f}%, maxDD {stats['max_dd']*100:.1f}%, "
              f"hit {stats['hit']*100:.1f}%")

    # Comparison table
    print()
    print("=" * 72)
    print(f"{'Lookback':>9}  {'Net Sharpe':>11}  {'Ann Ret':>9}  {'Ann Vol':>9}  {'Max DD':>9}  {'Hit':>7}")
    print("-" * 72)
    for r in results:
        print(f"{r['lookback']:>7}d  {r['sharpe']:>+11.2f}  {r['ann_ret']*100:>+8.1f}%  "
              f"{r['ann_vol']*100:>8.1f}%  {r['max_dd']*100:>+8.1f}%  {r['hit']*100:>6.1f}%")
    print("=" * 72)

    # Plot overlaid equity curves
    fig, ax = plt.subplots(figsize=(13, 7))
    colors = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd"]
    for lb, c in zip(LOOKBACKS, colors):
        s = next(r for r in results if r["lookback"] == lb)
        ax.plot(curves[lb].index, curves[lb].values, color=c, lw=1.6,
                label=f"{lb}d lookback (Sharpe {s['sharpe']:+.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_xlabel("Date")
    ax.set_title("Cross-sectional momentum portfolio — lookback sweep\n"
                 "8 G10 pairs, weekly, long top-2 / short bottom-2, net of 5 pips RT")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = REPORTS / "rejected" / "momentum_lookback_sweep.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
