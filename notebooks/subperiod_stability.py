"""
Sub-period stability of the rate-differential signal.

The headline result on this repo is that Δ(2Y rate differential) predicts next-day
FX across most of G10. The natural rigour question: is the edge stable across macro
regimes, or concentrated in one period (i.e. a 2010-2024 fluke)?

This script re-runs each rate-diff strategy (#1-#8 single-pair + #10 portfolio),
captures the daily net-return series, and slices it two ways:
  1. Per calendar year   → heatmap of annualised Sharpe (strategy × year)
  2. Per macro regime    → table of Sharpe across 4 rate-environment eras

Macro regimes (chosen by rate-environment, which is what a rate-diff signal cares about):
  - ZIRP / post-GFC   2010-2015  (zero rates, QE, low rate-vol)
  - Divergence        2016-2019  (Fed normalisation, policy divergence)
  - COVID             2020-2021  (pandemic shock, emergency easing, reflation)
  - Hiking cycle      2022-2024  (aggressive global tightening, high rate-vol)

Output:
  - reports/subperiod_stability.png   (Sharpe heatmap + regime bar chart)
  - tables printed to stdout

Requires FRED_API_KEY (for Strategy #1's EUR/US legs).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.WARNING)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"
sys.path.insert(0, str(REPO / "strategies"))

TRADING_DAYS = 252

REGIMES = {
    "ZIRP 2010-15":      ("2010-01-01", "2015-12-31"),
    "Divergence 2016-19":("2016-01-01", "2019-12-31"),
    "COVID 2020-21":     ("2020-01-01", "2021-12-31"),
    "Hiking 2022-24":    ("2022-01-01", "2024-12-31"),
}


def _sharpe(returns: pd.Series) -> float:
    if len(returns) < 20 or returns.std() == 0:
        return np.nan
    return float(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS))


def collect_return_series() -> dict[str, pd.Series]:
    """Run each strategy, return {label: daily_net_return_series}."""
    from strat_01_eu_us_2y_diff_eurusd import run as run_01
    from strat_10_g10_rate_diff_portfolio import run as run_10
    from _rate_diff_strategy import run_rate_diff_strategy

    series: dict[str, pd.Series] = {}

    print("Running Strategy #1 (EURUSD)...")
    series["#1 EURUSD"] = run_01()["net_ret_series"]

    specs = [
        (2, "GBPUSD", "GB", "US"), (3, "AUDUSD", "AU", "US"),
        (4, "NZDUSD", "NZ", "US"), (5, "USDJPY", "US", "JP"),
        (6, "USDCAD", "US", "CA"), (7, "USDCHF", "US", "CH"),
        (8, "USDSEK", "US", "SE"),
    ]
    for num, pair, base, quote in specs:
        print(f"Running Strategy #{num} ({pair})...")
        r = run_rate_diff_strategy(number=num, pair=pair, base_ccy=base, quote_ccy=quote)
        series[f"#{num} {pair}"] = r["net_ret_series"]

    print("Running Strategy #10 (portfolio)...")
    series["#10 Portfolio"] = run_10()["net_ret_series"]

    return series


def main() -> None:
    series = collect_return_series()
    labels = list(series.keys())
    years = list(range(2010, 2025))

    # ── Per-year Sharpe matrix ──────────────────────────────────────────────
    yr_sharpe = pd.DataFrame(index=labels, columns=years, dtype=float)
    for label, ret in series.items():
        for yr in years:
            yr_sharpe.loc[label, yr] = _sharpe(ret[ret.index.year == yr])

    # ── Per-regime Sharpe table ─────────────────────────────────────────────
    reg_sharpe = pd.DataFrame(index=labels, columns=list(REGIMES.keys()), dtype=float)
    for label, ret in series.items():
        for rname, (start, end) in REGIMES.items():
            seg = ret[(ret.index >= start) & (ret.index <= end)]
            reg_sharpe.loc[label, rname] = _sharpe(seg)

    # ── Print tables ────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("  Per-regime annualised Sharpe")
    print("=" * 78)
    print(reg_sharpe.round(2).to_string())
    print("\n  Full-period Sharpe (for reference):")
    for label, ret in series.items():
        print(f"    {label:<16} {_sharpe(ret):+.2f}")

    # ── Plot: heatmap + regime bars ─────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(20, 8),
                             gridspec_kw={"width_ratios": [3, 1.4]})

    # Left: year × strategy Sharpe heatmap
    ax = axes[0]
    data = yr_sharpe.astype(float).values
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", vmin=-2, vmax=2)
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Annualised Sharpe by calendar year", fontsize=12, fontweight="bold")
    for i in range(len(labels)):
        for j in range(len(years)):
            v = data[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontsize=7, color="black")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="Sharpe")

    # Right: per-regime mean Sharpe across the rate-diff strategies (exclude CHF, the known fail)
    ax = axes[1]
    rate_diff_labels = [l for l in labels if l != "#7 USDCHF"]
    regime_means = reg_sharpe.loc[rate_diff_labels].astype(float).mean()
    colors = ["#2ca02c" if v > 0 else "#d62728" for v in regime_means]
    ax.bar(range(len(regime_means)), regime_means.values, color=colors)
    ax.set_xticks(range(len(regime_means)))
    ax.set_xticklabels(regime_means.index, rotation=30, ha="right", fontsize=9)
    ax.axhline(0, color="k", lw=0.5)
    ax.axhline(1.0, color="gray", ls="--", lw=0.8)
    ax.set_ylabel("Mean Sharpe (rate-diff strategies, ex-CHF)")
    ax.set_title("Signal strength by macro regime", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    plt.suptitle("Rate-differential signal — sub-period stability (2010-2024)",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = REPORTS / "subperiod_stability.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
