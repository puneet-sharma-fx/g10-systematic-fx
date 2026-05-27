"""
Strategy #11 — Cross-sectional momentum portfolio (G10, weekly rebalance)

Signal:
    ret_21d[pair, t] = (price[t] / price[t-21]) - 1
    Computed on each Friday close.

Trading rule:
    Every Friday at close:
      - Rank all 8 G10 pairs by their trailing 21-day return
      - LONG the top 2 with weight +0.25 each   (+0.50 gross long)
      - SHORT the bottom 2 with weight -0.25 each (-0.50 gross short)
      - Other 4 pairs not held
    Hold the resulting weights until next Friday close (1 trading week).

Sizing convention:
    Each leg ±0.25, total gross exposure = 1.0, net = 0 (dollar-neutral).
    No vol-targeting (clean v1; can add later).

Cost:
    5 pips total round-trip, charged as 2.5 pips per unit of |Δweight|.

Universe:
    All 8 G10 pairs that have FX data on yfinance:
      EURUSD, GBPUSD, AUDUSD, NZDUSD, USDJPY, USDCAD, USDCHF, USDSEK
    (No exclusions — momentum may work where rate-diff failed.)
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

HERE = Path(__file__).resolve().parent      # strategies/rejected/
REPO = HERE.parent.parent                   # repo root
REPORTS = REPO / "reports" / "rejected"
TRACK = REPO / "live" / "track_record" / "rejected"

# ── Strategy parameters ──────────────────────────────────────────────────────
START               = "2010-01-04"
END                 = "2024-12-31"
LOOKBACK_DAYS       = 21       # ≈ 1 trading month — standard short-window momentum
N_LONG              = 2        # long top-2 pairs
N_SHORT             = 2        # short bottom-2 pairs
LEG_WEIGHT          = 0.25     # ±0.25 per leg → gross 1.0, net 0
COST_ROUND_TRIP_PIPS = 5.0
WEEKLY_PERIODS_PER_YEAR = 52

# Universe: (pair, pip_size)
PAIRS = [
    ("EURUSD", 0.0001),
    ("GBPUSD", 0.0001),
    ("AUDUSD", 0.0001),
    ("NZDUSD", 0.0001),
    ("USDJPY", 0.01),    # JPY pairs quoted to 2 decimals
    ("USDCAD", 0.0001),
    ("USDCHF", 0.0001),
    ("USDSEK", 0.0001),
]


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    s.name = pair
    return s.dropna()


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #11 — Cross-sectional momentum portfolio")
    print(f"  Period      : {START} → {END}")
    print(f"  Signal      : {LOOKBACK_DAYS}-day trailing return")
    print(f"  Rebalance   : weekly (Friday close)")
    print(f"  Position    : long top-{N_LONG}, short bottom-{N_SHORT}, ±{LEG_WEIGHT:.2f} each")
    print(f"  Cost        : {COST_ROUND_TRIP_PIPS} pips round-trip\n")

    pair_names = [p[0] for p in PAIRS]
    pip_by_pair = {p[0]: p[1] for p in PAIRS}

    print("Fetching FX prices...")
    px_dict = {name: _fetch_fx(name) for name in pair_names}

    # Daily aligned price frame
    idx_daily = pd.bdate_range(start=START, end=END)
    px_daily = pd.DataFrame({name: px_dict[name].reindex(idx_daily).ffill()
                             for name in pair_names})
    print(f"  Daily price frame: {px_daily.shape}\n")

    # 21-day trailing return per pair (daily series)
    ret_21d = px_daily.pct_change(periods=LOOKBACK_DAYS)

    # Resample to weekly Friday close — keep last available value of each week
    px_weekly = px_daily.resample("W-FRI").last()
    ret_21d_weekly = ret_21d.resample("W-FRI").last()

    # Cross-section ranking on each Friday → weights
    weights_weekly = pd.DataFrame(0.0, index=px_weekly.index, columns=pair_names)

    for dt in ret_21d_weekly.index:
        row = ret_21d_weekly.loc[dt].dropna()
        if len(row) < N_LONG + N_SHORT:
            continue   # not enough data this week (early period)
        ranked = row.sort_values(ascending=False)
        for p in ranked.head(N_LONG).index:
            weights_weekly.loc[dt, p] = +LEG_WEIGHT
        for p in ranked.tail(N_SHORT).index:
            weights_weekly.loc[dt, p] = -LEG_WEIGHT

    # Weekly pair returns (Friday-close to Friday-close)
    pair_ret_weekly = px_weekly.pct_change()

    # Positions decided on day t apply to next-week return (t+1)
    positions = weights_weekly.shift(1).fillna(0)

    # Gross P&L per pair per week
    gross_per_pair_weekly = positions * pair_ret_weekly

    # Cost on rebalance: |Δweight| × (2.5 pips / spot) per pair
    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    turnover_weekly = weights_weekly.diff().abs().fillna(0)
    cost_per_pair_weekly = pd.DataFrame(index=weights_weekly.index, columns=pair_names, dtype=float)
    for name in pair_names:
        cost_per_pair_weekly[name] = turnover_weekly[name] * \
            (cost_per_unit_pips * pip_by_pair[name]) / px_weekly[name]

    gross_port = gross_per_pair_weekly.sum(axis=1)
    cost_total = cost_per_pair_weekly.sum(axis=1)
    net_port = (gross_port - cost_total).dropna()

    # Drop early period before signal is valid
    first_valid = ret_21d_weekly.dropna(how="all").index.min() + pd.Timedelta(days=7)
    net_port = net_port[net_port.index >= first_valid]
    gross_port = gross_port.reindex(net_port.index)
    cost_total = cost_total.reindex(net_port.index)

    # ── Metrics (annualised on 52-week basis) ───────────────────────────────
    def stats(returns: pd.Series) -> dict:
        ann_ret = returns.mean() * WEEKLY_PERIODS_PER_YEAR
        ann_vol = returns.std() * np.sqrt(WEEKLY_PERIODS_PER_YEAR)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve = (1 + returns).cumprod()
        max_dd = float(((curve / curve.cummax()) - 1).min())
        hit = float((returns > 0).mean())
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=float(curve.iloc[-1] - 1))

    s_gross = stats(gross_port)
    s_net = stats(net_port)
    calmar = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] != 0 else float("nan")

    avg_weekly_turnover = turnover_weekly.sum(axis=1).mean()
    n_rebalances = int((turnover_weekly.sum(axis=1) > 0).sum())
    cum_cost_drag = float(cost_total.sum())

    # ── Print summary ──────────────────────────────────────────────────────
    print("=" * 65)
    print(f"  Strategy #11 — Cross-sectional momentum (weekly, top-{N_LONG} / bottom-{N_SHORT})")
    print("=" * 65)
    print(f"  Universe             : {', '.join(pair_names)}")
    print(f"  Weekly observations  : {len(net_port):,}")
    print(f"  Rebalances           : {n_rebalances:,}")
    print(f"  Avg weekly Σ|Δw|     : {avg_weekly_turnover:.3f}")
    print(f"  Cumulative cost drag : {cum_cost_drag*100:.1f}%")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}%")
    print(f"  {'Hit Rate':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}%")
    print(f"  {'Calmar (net)':<18} {' ':>10} {calmar:>10.2f}")
    print("=" * 65)

    # ── Plot ───────────────────────────────────────────────────────────────
    gross_curve = (1 + gross_port).cumprod()
    net_curve = (1 + net_port).cumprod()
    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f}, vol {s_gross['ann_vol']*100:.1f}%)")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f}, vol {s_net['ann_vol']*100:.1f}%)")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #11 — Cross-sectional momentum portfolio (G10, weekly)\n"
        f"{net_port.index[0].strftime('%Y-%m-%d')} to {END}  ·  "
        f"{len(net_port):,} weekly obs  ·  long top-{N_LONG} / short bottom-{N_SHORT} "
        f"by {LOOKBACK_DAYS}d return, net of {COST_ROUND_TRIP_PIPS:.0f} pips RT"
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
    plot_out = REPORTS / "strategy_11_g10_momentum_portfolio.png"
    plt.savefig(plot_out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_out.relative_to(REPO)}")

    # ── Optional CSV ───────────────────────────────────────────────────────
    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port
        out_df["cost"] = cost_total
        out_df["net_return"] = net_port
        out_df["cum_gross"] = gross_curve
        out_df["cum_net"] = net_curve
        for name in pair_names:
            out_df[f"weight_{name}"] = weights_weekly[name].reindex(net_port.index)
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(
        net=s_net, gross=s_gross, calmar=calmar,
        n_rebalances=n_rebalances, cost_drag=cum_cost_drag,
        n_obs=len(net_port),
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_11_momentum_portfolio_track_record.csv")
