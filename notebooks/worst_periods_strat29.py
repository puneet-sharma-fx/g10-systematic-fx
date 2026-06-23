"""
Worst-period / drawdown-shape analysis for Strategy #29 (crash filter on #28).

Yesterday's #29 result showed the crash filter overlay materially improves
ALL metrics on top of #28: Sharpe +0.09, MaxDD reduced 7.7pp, Sortino +0.11,
skew +0.12. The natural next defensive question is:

  Which SPECIFIC drawdowns did the overlay trim, and which did it miss?

This script answers that with three views, all driven off #29's own CSV
(which already contains both base and filtered daily returns plus the
crash scalar history — no refetch needed):

  1. Worst 15 CALENDAR MONTHS on the base #28, side-by-side with the
     filtered #29 result for the same month. Plus the mean filter scalar
     during that month — tells us whether the filter was active when it
     was needed.

  2. Top 5 PEAK-TO-TROUGH DRAWDOWN EPISODES on the base, with the
     corresponding filtered behaviour during the same date range.
     Episodes are identified by walking the cumulative equity curve and
     extracting consecutive underwater spells with their depth and
     duration. Tells us whether the filter trimmed the biggest cliff
     drops or just the small grinding losses.

  3. Daily return DISTRIBUTION (histogram + tail statistics): if the
     filter is genuinely cutting the left tail, the filtered distribution
     should be narrower in the left tail without sacrificing the right
     tail. Quantiles at 1%, 5%, 95%, 99% directly testable.

Plus a quick plot: worst-month bars + drawdown overlay + return histograms.

Output:
  - reports/worst_periods_strat29.png
  - tables printed to stdout
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.WARNING)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"
TRACK = REPO / "live" / "track_record"

CSV = TRACK / "strategy_29_crash_filter_on_28_track_record.csv"

TRADING_DAYS = 252
WORST_N_MONTHS = 15
TOP_N_DD_EPISODES = 5


def _dd_episodes(returns: pd.Series, top_n: int = TOP_N_DD_EPISODES) -> pd.DataFrame:
    """Walk the equity curve and return the deepest `top_n` peak-to-trough episodes."""
    curve = (1 + returns.fillna(0)).cumprod()
    peak = curve.cummax()
    in_dd = (curve < peak).values
    dates = curve.index

    episodes = []
    i = 0
    n = len(in_dd)
    while i < n:
        if not in_dd[i]:
            i += 1
            continue
        # Start of an underwater spell — peak was at i-1 (the last day curve == peak)
        peak_date = dates[i - 1] if i > 0 else dates[0]
        peak_val = curve.iloc[i - 1] if i > 0 else curve.iloc[0]
        # Walk forward to recovery (curve >= peak_val) or end of series
        j = i
        trough_val = curve.iloc[i]
        trough_idx = i
        while j < n and in_dd[j]:
            if curve.iloc[j] < trough_val:
                trough_val = curve.iloc[j]
                trough_idx = j
            j += 1
        trough_date = dates[trough_idx]
        end_date = dates[j - 1] if j > 0 else dates[i]
        depth = float(trough_val / peak_val - 1)
        episodes.append({
            "peak_date":   peak_date,
            "trough_date": trough_date,
            "end_date":    end_date,
            "depth":       depth,
            "days_to_trough": (trough_date - peak_date).days,
            "days_total":     (end_date - peak_date).days,
        })
        i = j

    df = pd.DataFrame(episodes)
    if df.empty:
        return df
    return df.sort_values("depth").head(top_n).reset_index(drop=True)


def main():
    print(f"\nReading #29 daily series from {CSV.relative_to(REPO)}")
    daily = pd.read_csv(CSV, parse_dates=["date"], index_col="date")
    print(f"  {len(daily):,} rows, {daily.index[0].date()} → {daily.index[-1].date()}")

    base = daily["base_net_return"].dropna()
    filt = daily["filt_net_return"].dropna()
    common = base.index.intersection(filt.index)
    base = base.loc[common]
    filt = filt.loc[common]
    scale = daily["scale"].loc[common]

    # ── (1) Worst CALENDAR MONTHS ──────────────────────────────────────────
    monthly_base = (1 + base).resample("ME").apply(lambda r: r.prod() - 1)
    monthly_filt = (1 + filt).resample("ME").apply(lambda r: r.prod() - 1)
    monthly_mean_scale = scale.resample("ME").mean()
    months = pd.DataFrame({
        "base":  monthly_base,
        "filt":  monthly_filt,
        "scale_mean": monthly_mean_scale,
    }).dropna()
    months["delta"] = months["filt"] - months["base"]
    worst = months.sort_values("base").head(WORST_N_MONTHS)

    print()
    print("=" * 100)
    print(f"  Worst {WORST_N_MONTHS} CALENDAR MONTHS for #28 base — and what #29 did instead")
    print("=" * 100)
    print(f"  {'Month':<10} {'#28 base':>9} {'#29 filt':>10} {'Δ (filt-base)':>15} {'Mean scale':>11} {'Verdict':<12}")
    print("-" * 100)
    n_helped = 0
    n_hurt   = 0
    total_base_loss = 0.0
    total_filt_loss = 0.0
    for date, row in worst.iterrows():
        verdict = "trimmed" if row["delta"] > 0.001 else ("missed" if row["delta"] < -0.001 else "flat")
        if verdict == "trimmed":
            n_helped += 1
        elif verdict == "missed":
            n_hurt += 1
        total_base_loss += row["base"]
        total_filt_loss += row["filt"]
        print(f"  {date.strftime('%Y-%m'):<10} "
              f"{row['base']*100:>+8.2f}% {row['filt']*100:>+9.2f}% "
              f"{row['delta']*100:>+14.2f}% "
              f"{row['scale_mean']:>10.2f} {verdict:<12}")
    print("-" * 100)
    print(f"  Sum of worst-{WORST_N_MONTHS} months : "
          f"base {total_base_loss*100:+6.1f}%   filtered {total_filt_loss*100:+6.1f}%   "
          f"saved {(total_filt_loss-total_base_loss)*100:+5.1f}pp")
    print(f"  Months where filter TRIMMED the loss : {n_helped}/{WORST_N_MONTHS}")
    print(f"  Months where filter MISSED (or made worse): {n_hurt}/{WORST_N_MONTHS}")
    print("=" * 100)

    # ── (2) Top peak-to-trough drawdown episodes ───────────────────────────
    dd_base = _dd_episodes(base, TOP_N_DD_EPISODES)
    dd_filt = _dd_episodes(filt, TOP_N_DD_EPISODES)

    print()
    print("=" * 100)
    print(f"  Top {TOP_N_DD_EPISODES} peak-to-trough DRAWDOWN EPISODES — #28 base")
    print("=" * 100)
    print(f"  {'Peak':<12} {'Trough':<12} {'End':<12} {'Depth':>9} {'To trough':>11} {'Total':>9}")
    for _, row in dd_base.iterrows():
        print(f"  {row['peak_date'].strftime('%Y-%m-%d'):<12} "
              f"{row['trough_date'].strftime('%Y-%m-%d'):<12} "
              f"{row['end_date'].strftime('%Y-%m-%d'):<12} "
              f"{row['depth']*100:>8.2f}% {row['days_to_trough']:>10}d {row['days_total']:>8}d")
    print()
    print(f"  Top {TOP_N_DD_EPISODES} peak-to-trough DRAWDOWN EPISODES — #29 filtered")
    print("-" * 100)
    print(f"  {'Peak':<12} {'Trough':<12} {'End':<12} {'Depth':>9} {'To trough':>11} {'Total':>9}")
    for _, row in dd_filt.iterrows():
        print(f"  {row['peak_date'].strftime('%Y-%m-%d'):<12} "
              f"{row['trough_date'].strftime('%Y-%m-%d'):<12} "
              f"{row['end_date'].strftime('%Y-%m-%d'):<12} "
              f"{row['depth']*100:>8.2f}% {row['days_to_trough']:>10}d {row['days_total']:>8}d")
    print("=" * 100)
    print(f"  Deepest base drawdown : {dd_base['depth'].iloc[0]*100:+.2f}%  "
          f"({dd_base['peak_date'].iloc[0].date()} → {dd_base['trough_date'].iloc[0].date()})")
    print(f"  Deepest filt drawdown : {dd_filt['depth'].iloc[0]*100:+.2f}%  "
          f"({dd_filt['peak_date'].iloc[0].date()} → {dd_filt['trough_date'].iloc[0].date()})")
    print(f"  Reduction in worst DD : {(dd_filt['depth'].iloc[0] - dd_base['depth'].iloc[0])*100:+.2f}pp")

    # ── (3) Return distribution tails ──────────────────────────────────────
    print()
    print("=" * 100)
    print("  Daily return distribution: tail quantiles (the filter should narrow the left tail)")
    print("=" * 100)
    quantiles = [0.005, 0.01, 0.025, 0.05, 0.10, 0.50, 0.90, 0.95, 0.975, 0.99, 0.995]
    qb = base.quantile(quantiles)
    qf = filt.quantile(quantiles)
    print(f"  {'Quantile':<10} {'#28 base':>12} {'#29 filt':>12} {'Δ':>10}")
    print("-" * 100)
    for q in quantiles:
        delta = qf[q] - qb[q]
        marker = ""
        if q < 0.10 and delta > 0:
            marker = "  ← left tail trimmed"
        elif q > 0.90 and delta < 0:
            marker = "  ← right tail clipped"
        print(f"  {q*100:>7.1f}%   {qb[q]*100:>+10.2f}% {qf[q]*100:>+11.2f}% "
              f"{delta*100:>+9.2f}%{marker}")
    print("=" * 100)

    # Tail-ratio metric (right tail / abs(left tail) at 5th/95th percentile)
    tail_base = abs(qb[0.95]) / abs(qb[0.05]) if qb[0.05] != 0 else float("nan")
    tail_filt = abs(qf[0.95]) / abs(qf[0.05]) if qf[0.05] != 0 else float("nan")
    print(f"  Tail ratio (95th / |5th|)  base: {tail_base:.2f}   filt: {tail_filt:.2f}   "
          f"Δ: {tail_filt-tail_base:+.2f}")

    # ── Plot ───────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(3, 1, figsize=(13, 12))

    # Panel 1: worst-month bars
    ax = axes[0]
    x = np.arange(len(worst))
    width = 0.4
    ax.bar(x - width/2, worst["base"] * 100, width=width, color="#1f77b4",
           edgecolor="black", linewidth=0.8, alpha=0.85, label="#28 base")
    ax.bar(x + width/2, worst["filt"] * 100, width=width, color="#2ca02c",
           edgecolor="black", linewidth=0.8, alpha=0.85, label="#29 filtered")
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%Y-%m") for d in worst.index], rotation=45, ha="right")
    ax.axhline(0, color="k", lw=0.7)
    ax.set_ylabel("Monthly return (%)")
    ax.set_title(f"Worst {WORST_N_MONTHS} calendar months for #28 base — filtered #29 same months")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 2: equity curves + DD episodes annotated
    ax = axes[1]
    base_curve = (1 + base).cumprod()
    filt_curve = (1 + filt).cumprod()
    ax.plot(base_curve.index, base_curve.values, color="#1f77b4", lw=1.4, alpha=0.85, label="#28 base")
    ax.plot(filt_curve.index, filt_curve.values, color="#2ca02c", lw=2, label="#29 filtered")
    for _, row in dd_base.iterrows():
        ax.axvspan(row["peak_date"], row["end_date"], color="#1f77b4", alpha=0.08)
        ax.scatter([row["trough_date"]],
                   [base_curve.loc[row["trough_date"]]],
                   color="#1f77b4", marker="v", s=60, zorder=5, edgecolor="black")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title("Equity curves — top 5 #28 drawdown episodes shaded; ▼ marks each trough")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    # Panel 3: histogram of daily returns
    ax = axes[2]
    bins = np.linspace(-0.06, 0.06, 60)
    ax.hist(base.values, bins=bins, alpha=0.55, color="#1f77b4", edgecolor="black", linewidth=0.5,
            label=f"#28 base (5th pct {qb[0.05]*100:+.2f}%, 95th {qb[0.95]*100:+.2f}%)")
    ax.hist(filt.values, bins=bins, alpha=0.55, color="#2ca02c", edgecolor="black", linewidth=0.5,
            label=f"#29 filtered (5th pct {qf[0.05]*100:+.2f}%, 95th {qf[0.95]*100:+.2f}%)")
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlabel("Daily return")
    ax.set_ylabel("Days")
    ax.set_title("Daily return distribution — filter should narrow the left tail without clipping the right")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "worst_periods_strat29.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
