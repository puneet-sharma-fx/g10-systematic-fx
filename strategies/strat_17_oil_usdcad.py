"""
Strategy #17 — Oil → next-day USDCAD (cross-asset macro signal)

Hypothesis:
    Canada is one of the world's largest oil exporters. When WTI crude rises,
    the CAD strengthens against the USD (USDCAD falls). When oil falls, the
    CAD weakens (USDCAD rises). This relationship is one of the most documented
    in the FX–commodities literature (Chen-Rogoff 2003, Cayen et al 2010).

Signal:
    oil_return[t] = (CL=F[t] / CL=F[t−1]) − 1
    position[t+1] = −sign(oil_return[t])

    Oil up today (positive return) → short USDCAD tomorrow (= long CAD)
    Oil down today (negative return) → long USDCAD tomorrow

Held for 1 trading day, then re-evaluated. Same structural template as Strategy #1.

Universe: USDCAD only.
Cost: 5 pips round-trip per unit of turnover (2.5 pips per unit of |Δposition|).
Data: WTI from yfinance `CL=F`. USDCAD from yfinance `USDCAD=X`.
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
TRACK = REPO / "live" / "track_record"

# ── Parameters ───────────────────────────────────────────────────────────────
START               = "2010-01-04"
END                 = "2024-12-31"
ROUND_TRIP_PIPS     = 5.0
COST_PER_UNIT_PIPS  = ROUND_TRIP_PIPS / 2.0
PIP_SIZE            = 0.0001
TRADING_DAYS        = 252


def _fetch(ticker: str) -> pd.Series:
    df = yf.download(ticker, start=START, end=END, auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    return s.dropna()


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #17 — Oil (WTI) → next-day USDCAD")
    print(f"  Signal : pos[t+1] = −sign(oil_return[t])")
    print(f"  Cost   : {ROUND_TRIP_PIPS} pips round-trip ({COST_PER_UNIT_PIPS} pips/unit traded)\n")

    print("Fetching data...")
    oil = _fetch("CL=F")
    fx  = _fetch("USDCAD=X")
    print(f"  WTI    : {len(oil)} daily obs")
    print(f"  USDCAD : {len(fx)} daily obs\n")

    idx = pd.bdate_range(start=START, end=END)
    oil = oil.reindex(idx).ffill()
    fx  = fx.reindex(idx).ffill()

    oil_ret = oil.pct_change()
    fx_ret  = fx.pct_change()

    # Signal: position decided end-of-t, applied at t+1
    raw_signal = -np.sign(oil_ret)             # short USDCAD when oil rose
    position   = raw_signal.shift(1).fillna(0) # tomorrow's position

    gross_ret = position * fx_ret

    # Cost: |Δposition| × (2.5 pips / spot)
    pos_change      = position.diff().abs().fillna(0)
    cost_in_returns = pos_change * (COST_PER_UNIT_PIPS * PIP_SIZE) / fx
    net_ret         = (gross_ret - cost_in_returns).dropna()

    benchmark_ret = fx_ret.dropna()

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

    n_trades      = int((pos_change > 0).sum())
    avg_turnover  = float(pos_change.mean())
    cost_drag_pct = float(cost_in_returns.sum())

    # Quick signal-IC regression (oil_return → next-day USDCAD return)
    df_reg = pd.concat([oil_ret.rename("oil_ret"),
                        fx_ret.shift(-1).rename("fx_fwd_ret")], axis=1).dropna()
    if len(df_reg) > 10:
        beta = float(np.polyfit(df_reg["oil_ret"], df_reg["fx_fwd_ret"], 1)[0])
        corr = float(df_reg["oil_ret"].corr(df_reg["fx_fwd_ret"]))
    else:
        beta = corr = float("nan")

    print("=" * 65)
    print(f"  Strategy #17 — Oil (WTI) → USDCAD next-day")
    print("=" * 65)
    print(f"  Observations         : {len(net_ret):,}")
    print(f"  Position flips       : {n_trades:,}  ({n_trades/len(net_ret)*100:.1f}% of days)")
    print(f"  Avg daily |Δpos|     : {avg_turnover:.3f}")
    print(f"  Cumulative cost drag : {cost_drag_pct*100:.1f}%")
    print(f"  Signal regression    : β={beta:+.4f}, corr={corr:+.4f}")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10} {'Passive USDCAD':>17}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}% {s_bench['ann_ret']*100:>16.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}% {s_bench['ann_vol']*100:>16.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f} {s_bench['sharpe']:>17.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}% {s_bench['max_dd']*100:>16.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}% {s_bench['cum']*100:>16.2f}%")
    print(f"  {'Hit Rate':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}% {s_bench['hit']*100:>16.2f}%")
    print("=" * 65)

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
            label=f"Passive long USDCAD (Sharpe {s_bench['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #17 — Oil (WTI) → next-day USDCAD\n"
        f"{START} to {END}  ·  {len(net_ret):,} daily obs  ·  "
        f"signal β={beta:+.4f}, corr={corr:+.4f}  ·  net of {ROUND_TRIP_PIPS:.0f} pips RT"
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
    out = REPORTS / "strategy_17_oil_usdcad.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame({
            "wti_close": oil,
            "wti_return": oil_ret,
            "usdcad_close": fx,
            "usdcad_return": fx_ret,
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
    run(csv_out=TRACK / "strategy_17_oil_usdcad_track_record.csv")
