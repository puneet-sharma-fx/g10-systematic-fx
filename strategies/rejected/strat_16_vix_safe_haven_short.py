"""
Strategy #16 — VIX spike → safe-haven short (USDJPY + USDCHF)

Cross-asset macro signal — first one in the repo not based on rate differentials.

Hypothesis:
    When equity volatility spikes (carry-trade unwind risk rising), capital
    historically flows into the two textbook safe-haven currencies — JPY and
    CHF — causing them to appreciate against the USD. So a sharp VIX move
    should mean short USDJPY + short USDCHF (= long JPY + long CHF) for the
    duration of the stress regime.

Setup:
    vix_z[t] = (VIX[t] − rolling_mean[t]) / rolling_std[t]   over 252-day window
    "stress regime" = vix_z[t] > +1.0

Action:
    For each pair (USDJPY, USDCHF): position = −1 (short the pair)
    Hold: any day within HOLD_DAYS (10) of a stress trigger keeps us short.
          Sustained stress regime extends the holding window.

Realism:
    Signal computed end-of-day t (using close VIX), position applied to day t+1.
    No look-ahead.

Cost: 5 pips round-trip per pair per trade event.
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

HERE = Path(__file__).resolve().parent          # strategies/rejected/
REPO = HERE.parent.parent                       # repo root
REPORTS = REPO / "reports" / "rejected"
TRACK = REPO / "live" / "track_record" / "rejected"

# ── Parameters ───────────────────────────────────────────────────────────────
START                = "2010-01-04"
END                  = "2024-12-31"
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS         = 252

VIX_ZSCORE_WINDOW    = 252      # 1 year rolling window
VIX_THRESHOLD        = 1.0      # +1σ → stress regime
HOLD_DAYS            = 10       # hold each trigger for 10 trading days

PAIRS = [
    ("USDJPY", 0.01),
    ("USDCHF", 0.0001),
]
SIDE = -1   # short both pairs = long JPY + long CHF


def _fetch(ticker: str) -> pd.Series:
    df = yf.download(ticker, start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    return s.dropna()


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #16 — VIX spike → safe-haven short (USDJPY + USDCHF)")
    print(f"  Signal : VIX z-score > +{VIX_THRESHOLD}σ over {VIX_ZSCORE_WINDOW}-day window")
    print(f"  Action : short both pairs for {HOLD_DAYS} trading days from any trigger")
    print(f"  Cost   : {COST_ROUND_TRIP_PIPS} pips RT per pair per trade")
    print()

    print("Fetching VIX and FX prices...")
    idx = pd.bdate_range(start=START, end=END)
    vix = _fetch("^VIX").reindex(idx).ffill()
    fx_close = {}
    for pair, _pip in PAIRS:
        fx_close[pair] = _fetch(f"{pair}=X").reindex(idx).ffill()

    # VIX z-score
    vix_mean = vix.rolling(VIX_ZSCORE_WINDOW, min_periods=63).mean()
    vix_std  = vix.rolling(VIX_ZSCORE_WINDOW, min_periods=63).std()
    vix_z    = (vix - vix_mean) / vix_std

    # Stress regime + rolling holding window
    stress = (vix_z > VIX_THRESHOLD).fillna(False)
    in_trade = stress.rolling(HOLD_DAYS, min_periods=1).max().astype(bool)

    # Positions: −1 per pair, shifted 1 day (use yesterday's signal for today's hold)
    pair_names = [p[0] for p in PAIRS]
    positions = pd.DataFrame(0.0, index=idx, columns=pair_names)
    for pair, _pip in PAIRS:
        positions[pair] = SIDE * in_trade.shift(1).fillna(False).astype(float)

    # P&L per pair
    fx_ret = pd.DataFrame({pair: fx_close[pair].pct_change() for pair, _ in PAIRS})
    gross_pair_ret = positions * fx_ret

    # Cost per pair: |Δposition| × (pip_size × 2.5) / spot
    cost_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    cost_per_pair = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    for pair, pip in PAIRS:
        turn = positions[pair].diff().abs().fillna(0)
        cost_per_pair[pair] = turn * (cost_unit_pips * pip) / fx_close[pair]
    cost_total = cost_per_pair.sum(axis=1)

    gross_port = gross_pair_ret.sum(axis=1)
    net_port = (gross_port - cost_total).dropna()

    # Burn-in: drop pre-1y so z-score is well-formed
    burn_in_start = pd.Timestamp(START) + pd.DateOffset(years=1)
    net_port = net_port[net_port.index >= burn_in_start]
    gross_port = gross_port.reindex(net_port.index)
    cost_total = cost_total.reindex(net_port.index)
    in_trade_post = in_trade.reindex(net_port.index)

    # ── Metrics ────────────────────────────────────────────────────────────
    def stats(returns: pd.Series) -> dict:
        ann_ret = float(returns.mean() * TRADING_DAYS)
        ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve = (1 + returns).cumprod()
        max_dd = float(((curve / curve.cummax()) - 1).min())
        hit = float((returns > 0).mean())
        cum = float(curve.iloc[-1] - 1)
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=cum)

    s_gross = stats(gross_port)
    s_net = stats(net_port)
    calmar = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] != 0 else float("nan")

    # Counts
    n_trigger_days  = int(stress.reindex(net_port.index).sum())
    n_in_trade_days = int(in_trade_post.sum())
    pct_in_trade    = float(in_trade_post.mean())
    cum_cost_drag   = float(cost_total.sum())

    print("=" * 65)
    print(f"  Strategy #16 — VIX spike → safe-haven short")
    print("=" * 65)
    print(f"  VIX trigger days (z > +{VIX_THRESHOLD}) : {n_trigger_days:,}")
    print(f"  Days in trade (within {HOLD_DAYS}d window) : {n_in_trade_days:,}")
    print(f"  % time in trade : {pct_in_trade*100:.1f}%")
    print(f"  Cumulative cost drag : {cum_cost_drag*100:.2f}%")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}%")
    print(f"  {'Hit Rate (daily)':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}%")
    print(f"  {'Calmar (net)':<18} {' ':>10} {calmar:>10.2f}")
    print("=" * 65)

    # ── Plot ───────────────────────────────────────────────────────────────
    gross_curve = (1 + gross_port).cumprod()
    net_curve = (1 + net_port).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)

    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.3, alpha=0.6,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #16 — VIX spike → safe-haven short (USDJPY + USDCHF)\n"
        f"VIX z > +{VIX_THRESHOLD}σ ({VIX_ZSCORE_WINDOW}-day window), hold {HOLD_DAYS}d, "
        f"{n_trigger_days} trigger days, net of {COST_ROUND_TRIP_PIPS:.0f} pips RT"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    vix_z_plot = vix_z.reindex(net_port.index)
    ax.plot(vix_z_plot.index, vix_z_plot.values, color="orange", lw=0.7)
    ax.axhline(VIX_THRESHOLD, color="red", ls="--", lw=1, label=f"+{VIX_THRESHOLD}σ trigger")
    ax.axhline(0, color="gray", lw=0.3)
    ax.fill_between(in_trade_post.index, 0, in_trade_post.astype(int) * 4,
                    color="green", alpha=0.10, label="In trade")
    ax.set_ylabel("VIX z-score (252d)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    dd = (net_curve / net_curve.cummax()) - 1
    ax.fill_between(dd.index, dd.values, 0, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown (net)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_out = REPORTS / "strategy_16_vix_safe_haven.png"
    plt.savefig(plot_out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["vix_close"] = vix.reindex(net_port.index)
        out_df["vix_z"] = vix_z.reindex(net_port.index)
        out_df["in_trade"] = in_trade_post.astype(int)
        for pair, _ in PAIRS:
            out_df[f"position_{pair}"] = positions[pair].reindex(net_port.index)
            out_df[f"{pair}_close"] = fx_close[pair].reindex(net_port.index)
        out_df["gross_return"] = gross_port
        out_df["cost"] = cost_total
        out_df["net_return"] = net_port
        out_df["cum_net"] = net_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")

    return dict(net=s_net, gross=s_gross, calmar=calmar,
                pct_in_trade=pct_in_trade, n_obs=len(net_port))


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_16_vix_safe_haven_track_record.csv")
