"""
Strategy #21 — EURUSD: Δ(EU 2Y − US 2Y) with 1-day extra lag (verification of #1)

Strategy #1's headline Sharpe of 2.75 may be partially inflated by an intraday
timing artefact, the same way Strategy #17's Sharpe was (verified by #19).

The structural concern: Yahoo's EURUSD daily "close" is at 5pm ET, US Treasury
rates close at NY end-of-day (~5pm ET), and ECB AAA yields close earlier at the
European session close (~12pm ET / 6pm CET). In the hours between the ECB yield
close and the EURUSD close, EURUSD may have already partially responded to the
European rate move. If so, what Strategy #1 records as "next-day predictive
content" is actually same-day contemporaneous response measured at a misaligned
timestamp — not a tradable edge for someone entering at 5pm EURUSD close.

The rigour check: shift the signal by one extra day, so by the time we hold
the position from t close to t+1 close, the rate-diff signal is more than
24 hours old. There's no plausible way the FX market wouldn't have already
priced it in.

    Strategy #1:   pos[t+1] = sign(d_diff[t])         ← signal at end-of-t
    Strategy #21:  pos[t+1] = sign(d_diff[t−1])       ← signal one full day older

Same in every other respect (data sources: FRED `DGS2` for US, ECB SDW for EU
AAA 2Y, yfinance `EURUSD=X`; full notional ±1; 5 pips RT cost; 2010–2024).

Interpretation:
    Sharpe stays positive (>1)   → #1 has genuine lagged predictive content;
                                   rate-diff family (#1–#10, #12, #18) is real
    Sharpe collapses to ~0 or −  → #1's edge was timing artefact; rate-diff
                                   family needs reassessment, possibly major
                                   downgrade of headline numbers

Requires FRED_API_KEY environment variable for the US 2Y fetch.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"
TRACK = REPO / "live" / "track_record"

# Reuse the data fetchers and parameters from Strategy #1
sys.path.insert(0, str(HERE))
from strat_01_eu_us_2y_diff_eurusd import (
    fetch_us_2y, fetch_eu_2y, fetch_eurusd,
    START, END,
    ROUND_TRIP_PIPS, COST_PER_UNIT_PIPS, PIP_SIZE, TRADING_DAYS,
)

EXTRA_LAG_DAYS = 1            # ← the only change vs Strategy #1


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #21 — EURUSD rate-diff with 1-day extra lag (verification of #1)")
    print(f"  Signal : pos[t+1] = sign(d_diff[t−{EXTRA_LAG_DAYS}])")
    print(f"  Cost   : {ROUND_TRIP_PIPS} pips round-trip ({COST_PER_UNIT_PIPS} pips/unit traded)\n")

    print("Fetching data (FRED US 2Y, ECB AAA 2Y, yfinance EURUSD)...")
    us = fetch_us_2y()
    eu = fetch_eu_2y()
    px = fetch_eurusd()

    idx = pd.bdate_range(start=START, end=END)
    us = us.reindex(idx).ffill()
    eu = eu.reindex(idx).ffill()
    px = px.reindex(idx).ffill()
    print(f"  Aligned to {len(idx)} business days\n")

    # ── Rate differential and its daily change ──────────────────────────────
    rate_diff = (eu - us).rename("rate_diff_pp")
    d_diff    = rate_diff.diff().rename("d_diff_pp")

    # ── The verification: signal is yesterday's d_diff, not today's ────────
    lagged_d_diff = d_diff.shift(EXTRA_LAG_DAYS)
    raw_signal    = np.sign(lagged_d_diff)
    position      = raw_signal.shift(1).fillna(0)   # tomorrow's position

    # ── Returns ─────────────────────────────────────────────────────────────
    spot_ret  = px.pct_change()
    gross_ret = position * spot_ret

    pos_change      = position.diff().abs().fillna(0)
    cost_in_returns = pos_change * (COST_PER_UNIT_PIPS * PIP_SIZE) / px
    net_ret         = (gross_ret - cost_in_returns).dropna()

    benchmark_ret = spot_ret.dropna()   # passive long EURUSD

    def stats(returns: pd.Series) -> dict:
        ann_ret = float(returns.mean() * TRADING_DAYS)
        ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
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

    # Signal-IC regression with the extra lag
    df_reg = pd.concat([lagged_d_diff.rename("d_diff_lag"),
                        spot_ret.shift(-1).rename("fx_fwd_ret")], axis=1).dropna()
    if len(df_reg) > 10:
        beta = float(np.polyfit(df_reg["d_diff_lag"], df_reg["fx_fwd_ret"], 1)[0])
        corr = float(df_reg["d_diff_lag"].corr(df_reg["fx_fwd_ret"]))
    else:
        beta = corr = float("nan")

    print("=" * 70)
    print(f"  Strategy #21 — EURUSD rate-diff with 1-day extra lag (verification)")
    print("=" * 70)
    print(f"  Observations         : {len(net_ret):,}")
    print(f"  Position flips       : {n_trades:,}  ({n_trades/len(net_ret)*100:.1f}% of days)")
    print(f"  Cumulative cost drag : {cost_drag_pct*100:.1f}%")
    print(f"  Signal regression    : β={beta:+.4f}, corr={corr:+.4f}")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10} {'Passive EURUSD':>17}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}% {s_bench['ann_ret']*100:>16.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}% {s_bench['ann_vol']*100:>16.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f} {s_bench['sharpe']:>17.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}% {s_bench['max_dd']*100:>16.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}% {s_bench['cum']*100:>16.2f}%")
    print(f"  {'Hit Rate':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}% {s_bench['hit']*100:>16.2f}%")
    print("=" * 70)
    print(f"\n  ▶︎ For comparison: Strategy #1 (no extra lag) had net Sharpe 2.75")
    print(f"  ▶︎ Strategy #1's signal: β=+0.0335, corr=+0.27, t-stat=+17.8")
    print(f"  ▶︎ This run (1-day extra lag) net Sharpe:  {s_net['sharpe']:+.2f}")
    print(f"  ▶︎ This run signal regression: β={beta:+.4f}, corr={corr:+.4f}")
    if s_net["sharpe"] > 1.0:
        print(f"  ▶︎ ✅ Edge survives the lag → genuine lagged predictive content. #1 (and rate-diff family) is real.")
    elif s_net["sharpe"] > 0:
        print(f"  ▶︎ ⚠️  Edge partially survives → some predictive content but inflated by timing.")
    else:
        print(f"  ▶︎ ❌ Edge collapses → #1's Sharpe was largely intraday timing artefact.")
        print(f"        Rate-diff family (#1–#10, #12, #18) needs major reassessment.")

    # Plot
    gross_curve = (1 + gross_ret.dropna()).cumprod()
    net_curve   = (1 + net_ret).cumprod()
    bench_curve = (1 + benchmark_ret).cumprod()

    fig, axes = plt.subplots(2, 1, figsize=(13, 8),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.3, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.plot(bench_curve.index, bench_curve.values, color="gray", ls="--", lw=1,
            label=f"Passive long EURUSD (Sharpe {s_bench['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #21 — EURUSD rate-diff with 1-day extra lag (verification of #1)\n"
        f"{START} to {END}  ·  signal β={beta:+.4f}, corr={corr:+.4f}  ·  "
        f"net Sharpe {s_net['sharpe']:+.2f} (vs #1's +2.75)"
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
    out = REPORTS / "strategy_21_eu_us_2y_diff_eurusd_lagged.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame({
            "eu_2y_pct": eu,
            "us_2y_pct": us,
            "rate_diff_pp": rate_diff,
            "d_diff_pp": d_diff,
            "d_diff_lagged_signal": lagged_d_diff,
            "eurusd_close": px,
            "eurusd_return": spot_ret,
            "position": position,
            "gross_return": gross_ret,
            "cost": cost_in_returns,
            "net_return": gross_ret - cost_in_returns,
            "cum_gross": (1 + gross_ret.fillna(0)).cumprod(),
            "cum_net": (1 + (gross_ret - cost_in_returns).fillna(0)).cumprod(),
        })
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(net=s_net, gross=s_gross, benchmark=s_bench,
                n_trades=n_trades, cost_drag=cost_drag_pct,
                beta=beta, corr=corr)


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_21_eurusd_lagged_track_record.csv")
