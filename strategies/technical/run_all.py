"""
Run all 15 technical strategies on EURUSD, GBPUSD, USDJPY.

Outputs:
  - reports/technical/comparison_<pair>.png   (overlaid equity curves per pair)
  - reports/technical/summary_heatmap.png     (Sharpe heatmap: strategy × pair)
  - reports/technical/summary_table.csv       (full metrics — gitignored locally)

Usage: python strategies/technical/run_all.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
REPORTS = REPO / "reports" / "technical"
REPORTS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE))
from _base import backtest
from signals import STRATEGIES

PAIRS = ["EURUSD", "GBPUSD", "USDJPY"]
START = "2010-01-04"
END   = "2024-12-31"


def fetch(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    return s.dropna()


def main() -> None:
    print(f"Running {len(STRATEGIES)} strategies × {len(PAIRS)} pairs "
          f"= {len(STRATEGIES) * len(PAIRS)} backtests")
    print(f"Period: {START} → {END}\n")

    print("Fetching FX prices...")
    px = {p: fetch(p) for p in PAIRS}
    print(f"  EURUSD: {len(px['EURUSD'])} days")
    print(f"  GBPUSD: {len(px['GBPUSD'])} days")
    print(f"  USDJPY: {len(px['USDJPY'])} days")

    # Run all backtests
    print("\nBacktesting...")
    results: dict[tuple[str, str], dict] = {}
    for pair in PAIRS:
        for name, family, fn in STRATEGIES:
            r = backtest(px[pair], fn, pair)
            results[(pair, name)] = dict(family=family, **r)

    # ── Per-pair comparison charts ──────────────────────────────────────────
    for pair in PAIRS:
        fig, ax = plt.subplots(figsize=(13, 7))
        for name, family, _fn in STRATEGIES:
            curve = results[(pair, name)]["curve_net"]
            sharpe = results[(pair, name)]["net_stats"]["sharpe"]
            ax.plot(curve.index, curve.values, lw=1.2, alpha=0.85,
                    label=f"{name}  (Sharpe {sharpe:+.2f})")
        ax.axhline(1.0, color="k", lw=0.5)
        ax.set_ylabel("Cumulative return (×)")
        ax.set_xlabel("Date")
        ax.set_title(f"Technical strategies on {pair}  ·  "
                     f"{START} to {END}  ·  net of 5 pips RT, daily rebalance")
        ax.legend(loc="upper left", fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        out = REPORTS / f"comparison_{pair.lower()}.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {out.relative_to(REPO)}")

    # ── Summary table (CSV — gitignored locally) ────────────────────────────
    rows = []
    for pair in PAIRS:
        for name, family, _fn in STRATEGIES:
            r = results[(pair, name)]
            ns = r["net_stats"]; gs = r["gross_stats"]
            rows.append(dict(
                pair=pair, strategy=name, family=family,
                net_sharpe=ns["sharpe"], net_ann_ret=ns["ann_ret"],
                net_ann_vol=ns["ann_vol"], net_max_dd=ns["max_dd"],
                net_hit=ns["hit"], net_cum=ns["cum"],
                gross_sharpe=gs["sharpe"], n_trades=r["n_trades"],
            ))
    summary = pd.DataFrame(rows)
    csv_out = REPORTS / "summary_table.csv"
    summary.to_csv(csv_out, float_format="%.4f", index=False)
    print(f"  Saved: {csv_out.relative_to(REPO)}")

    # ── Sharpe heatmap (strategy × pair) ────────────────────────────────────
    pivot = summary.pivot(index="strategy", columns="pair", values="net_sharpe")
    pivot = pivot[PAIRS]  # column order
    pivot = pivot.reindex([s[0] for s in STRATEGIES])  # row order matches STRATEGIES

    fig, ax = plt.subplots(figsize=(7, 9))
    vmax = float(np.abs(pivot.values).max()) if pivot.size else 1.0
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn",
                   vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = pivot.values[i, j]
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=9, color="black", fontweight="bold")
    ax.set_title("Net Sharpe by strategy × pair  (2010–2024, net of 5 pips RT)",
                 fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04, label="Net Sharpe")
    plt.tight_layout()
    out = REPORTS / "summary_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.relative_to(REPO)}")

    # ── Print summary table ────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("  Net Sharpe by strategy × pair")
    print("=" * 78)
    print(pivot.round(2).to_string())
    print("\n  Best per pair (net Sharpe):")
    for pair in PAIRS:
        s = pivot[pair].sort_values(ascending=False)
        print(f"    {pair}: {s.index[0]:<22}  {s.iloc[0]:+.2f}  "
              f"(2nd: {s.index[1]:<22} {s.iloc[1]:+.2f})")


if __name__ == "__main__":
    main()
