"""
Strategy #34 — Faber's Global Tactical Asset Allocation (5-asset, done correctly)

The correct implementation of Faber (2007), "A Quantitative Approach to
Tactical Asset Allocation" (SSRN 962461, ~3,000 citations). Strategy #33
tested the SPY-only version and found the timing rule barely beat buy-
and-hold — because SPY B&H is a demanding benchmark and the rule's edge
comes from ASSET-CLASS DIVERSIFICATION, not from timing SPY specifically.

Faber's original 5-asset universe:
  US equity   : SPY  (S&P 500 ETF)
  Foreign eq  : EFA  (iShares MSCI EAFE — developed international)
  US bonds    : AGG  (iShares Core US Aggregate Bond)
  Real estate : VNQ  (Vanguard Real Estate ETF)
  Commodities : GLD  (SPDR Gold Shares — proxy for broad commodities)

Rule per asset:
  Long  (weight = 0.20) when close[t] > 200-day SMA[t]
  Flat  (weight = 0.00) when close[t] <= 200-day SMA[t]

Portfolio: sum of active per-asset weights (0.0 to 1.0 total).
Any capital "in cash" earns 0% (conservative — Faber used T-bills).

Signal: 200-day SMA of the closing price (Faber's spec was 10-month SMA
on monthly data ≈ 210 trading days; the daily version is same signal at
higher resolution).

Cost: 5 bps round-trip per position flip. Applied per-asset on turnover.

Benchmarks:
  1. SPY buy-and-hold — the tough passive benchmark from #33
  2. 60/40 portfolio (60% SPY, 40% AGG, daily rebalanced)
  3. Equal-weight passive 5-asset portfolio (20% each, daily rebalanced)

The claim to test: does the diversified timing rule improve on ALL THREE
benchmarks? Or specifically:
  - Higher risk-adjusted return than SPY?
  - Higher risk-adjusted return than 60/40 (the standard institutional
    passive)?
  - Lower drawdown than either?

Period: 2010-01 → 2024-12 (matches #33 and rest of repo).
Note: VNQ and AGG both have data from ~2003; EFA from 2001; GLD from 2004.
All 5 have full coverage over the backtest window.
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

# ── Strategy parameters ──────────────────────────────────────────────────────
MA_DAYS                = 200
COST_ROUND_TRIP_BPS    = 5.0
TRADING_DAYS           = 252
START                  = "2010-01-04"
END                    = "2024-12-31"

# Faber's 5-asset universe, equal 20% target weight per asset
UNIVERSE = ["SPY", "EFA", "AGG", "VNQ", "GLD"]
LABELS = {
    "SPY": "US equity (SPY)",
    "EFA": "Intl developed (EFA)",
    "AGG": "US bonds (AGG)",
    "VNQ": "US REITs (VNQ)",
    "GLD": "Gold (GLD)",
}
PER_ASSET_WEIGHT = 1.0 / len(UNIVERSE)


def _fetch(ticker: str) -> pd.Series:
    df = yf.download(ticker, start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze().dropna()
    s.index = pd.to_datetime(s.index)
    s.name = ticker
    return s


def _stats(returns: pd.Series) -> dict:
    returns = returns.dropna()
    if len(returns) == 0:
        return dict(n_days=0, ann_ret=0.0, ann_vol=0.0, sharpe=0.0,
                    sortino=0.0, max_dd=0.0, hit=0.0, skew=0.0, cum=0.0)
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew()) if returns.std() > 0 else 0.0
    dvol    = float(returns[returns < 0].std() * np.sqrt(TRADING_DAYS))
    sortino = ann_ret / dvol if dvol > 0 else 0.0
    return dict(n_days=len(returns), ann_ret=ann_ret, ann_vol=ann_vol,
                sharpe=sharpe, sortino=sortino, max_dd=max_dd, hit=hit,
                skew=skew, cum=float(curve.iloc[-1] - 1))


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #34 — Faber 5-asset GTAA (correct Faber 2007 spec)")
    print(f"  Universe    : {', '.join(UNIVERSE)}")
    print(f"  Signal      : per-asset {MA_DAYS}-day SMA (long above, flat below)")
    print(f"  Weight      : {PER_ASSET_WEIGHT:.0%} per active asset (cash 0% on flat)")
    print(f"  Cost        : {COST_ROUND_TRIP_BPS:.1f} bps RT per flip")
    print(f"  Period      : {START} → {END}\n")

    # ── Fetch all 5 ETFs ──────────────────────────────────────────────────
    print("Fetching 5-asset universe from yfinance...")
    px = {}
    for t in UNIVERSE:
        px[t] = _fetch(t)
        print(f"  {t}: {len(px[t])} rows, {px[t].index[0].date()} → {px[t].index[-1].date()}")

    idx = pd.bdate_range(start=START, end=END)
    close_df = pd.DataFrame({t: px[t].reindex(idx).ffill() for t in UNIVERSE})

    # ── Per-asset signal and position ─────────────────────────────────────
    signal = pd.DataFrame(0.0, index=idx, columns=UNIVERSE)
    ma_df = pd.DataFrame(index=idx, columns=UNIVERSE, dtype=float)
    for t in UNIVERSE:
        ma_df[t] = close_df[t].rolling(MA_DAYS, min_periods=MA_DAYS).mean()
        signal[t] = (close_df[t] > ma_df[t]).astype(float) * PER_ASSET_WEIGHT
        signal[t] = signal[t].where(ma_df[t].notna(), 0.0)

    # 1-day execution lag
    weights_lag = signal.shift(1).fillna(0.0)

    # ── P&L ────────────────────────────────────────────────────────────────
    ret_df = close_df.pct_change()
    gross_pair = weights_lag * ret_df
    gross_port = gross_pair.sum(axis=1)

    # Cost: per-asset turnover × 5 bps
    turnover = weights_lag.diff().abs().fillna(0)
    cost_pair = turnover * (COST_ROUND_TRIP_BPS / 10000.0)
    cost_total = cost_pair.sum(axis=1)

    net_port = (gross_port - cost_total).dropna()

    # ── Benchmarks ────────────────────────────────────────────────────────
    spy_ret     = ret_df["SPY"].loc[net_port.index]
    # 60/40 = 60% SPY + 40% AGG, daily rebalanced (no cost — pure passive baseline)
    p60_40      = 0.60 * ret_df["SPY"] + 0.40 * ret_df["AGG"]
    p60_40      = p60_40.loc[net_port.index]
    # Equal-weight 5-asset passive (20% each daily rebalance)
    ew_passive  = ret_df[UNIVERSE].mean(axis=1).loc[net_port.index]

    # ── Metrics ────────────────────────────────────────────────────────────
    s_strat   = _stats(net_port)
    s_spy     = _stats(spy_ret)
    s_60_40   = _stats(p60_40)
    s_ew5     = _stats(ew_passive)
    calmar    = lambda s: s["ann_ret"] / abs(s["max_dd"]) if s["max_dd"] else float("nan")

    # Per-asset time-in-market
    time_in = (weights_lag > 0).mean() * 100

    # Total flips per asset
    flips_per_asset = (turnover > 0).sum()

    print()
    print("=" * 100)
    print("  Strategy #34 — Faber 5-asset GTAA vs three benchmarks")
    print("=" * 100)
    print(f"  {'METRIC':<20} {'#34 GTAA':>12} {'SPY B&H':>12} {'60/40':>12} {'EW-5 passive':>14}")
    print(f"  {'Net Sharpe':<20} {s_strat['sharpe']:>12.2f} {s_spy['sharpe']:>12.2f} {s_60_40['sharpe']:>12.2f} {s_ew5['sharpe']:>14.2f}")
    print(f"  {'Sortino':<20} {s_strat['sortino']:>12.2f} {s_spy['sortino']:>12.2f} {s_60_40['sortino']:>12.2f} {s_ew5['sortino']:>14.2f}")
    print(f"  {'Ann. Return':<20} {s_strat['ann_ret']*100:>11.2f}% {s_spy['ann_ret']*100:>11.2f}% {s_60_40['ann_ret']*100:>11.2f}% {s_ew5['ann_ret']*100:>13.2f}%")
    print(f"  {'Ann. Vol':<20} {s_strat['ann_vol']*100:>11.2f}% {s_spy['ann_vol']*100:>11.2f}% {s_60_40['ann_vol']*100:>11.2f}% {s_ew5['ann_vol']*100:>13.2f}%")
    print(f"  {'Max Drawdown':<20} {s_strat['max_dd']*100:>11.2f}% {s_spy['max_dd']*100:>11.2f}% {s_60_40['max_dd']*100:>11.2f}% {s_ew5['max_dd']*100:>13.2f}%")
    print(f"  {'Calmar':<20} {calmar(s_strat):>12.2f} {calmar(s_spy):>12.2f} {calmar(s_60_40):>12.2f} {calmar(s_ew5):>14.2f}")
    print(f"  {'Daily Skew':<20} {s_strat['skew']:>12.2f} {s_spy['skew']:>12.2f} {s_60_40['skew']:>12.2f} {s_ew5['skew']:>14.2f}")
    print(f"  {'Cumulative':<20} {s_strat['cum']*100:>11.2f}% {s_spy['cum']*100:>11.2f}% {s_60_40['cum']*100:>11.2f}% {s_ew5['cum']*100:>13.2f}%")
    print("=" * 100)

    print()
    print("Per-asset time-in-market and flips (2010-2024):")
    print(f"  {'Ticker':<8} {'Label':<24} {'Time long':>12} {'# flips':>10}")
    for t in UNIVERSE:
        print(f"  {t:<8} {LABELS[t]:<24} {time_in[t]:>11.1f}% {int(flips_per_asset[t]):>10}")
    print()

    # ── Conditional Sharpe test ───────────────────────────────────────────
    # Compare strategy Sharpe vs EW-5 passive on days when the strategy is
    # ≤50% invested (partial "risk-off" position)
    gross_expo = weights_lag.sum(axis=1).loc[net_port.index]
    risk_off_mask = (gross_expo <= 0.50)
    n_risk_off = int(risk_off_mask.sum())
    if n_risk_off > 30:
        strat_risk_off = net_port[risk_off_mask]
        ew5_risk_off = ew_passive[risk_off_mask]
        strat_ro_sharpe = float(strat_risk_off.mean() * TRADING_DAYS /
                                 (strat_risk_off.std() * np.sqrt(TRADING_DAYS))) if strat_risk_off.std() > 0 else 0.0
        ew5_ro_sharpe = float(ew5_risk_off.mean() * TRADING_DAYS /
                               (ew5_risk_off.std() * np.sqrt(TRADING_DAYS))) if ew5_risk_off.std() > 0 else 0.0
        print(f"Conditional Sharpe when strategy is <= 50% invested ({n_risk_off} days, "
              f"{n_risk_off/len(net_port)*100:.1f}% of sample):")
        print(f"  #34 GTAA        : {strat_ro_sharpe:+.2f}")
        print(f"  EW-5 passive    : {ew5_ro_sharpe:+.2f}")
        good_gate = strat_ro_sharpe > ew5_ro_sharpe
        print(f"  → {'YES — timing filter beats passive during risk-off' if good_gate else 'NO — filter underperforms passive during risk-off'}")

    print()
    print(f"Sharpe deltas vs benchmarks:")
    print(f"  #34 vs SPY B&H       : {s_strat['sharpe']-s_spy['sharpe']:+.2f}")
    print(f"  #34 vs 60/40         : {s_strat['sharpe']-s_60_40['sharpe']:+.2f}")
    print(f"  #34 vs EW-5 passive  : {s_strat['sharpe']-s_ew5['sharpe']:+.2f}")

    n_wins = sum(1 for s_bench in (s_spy, s_60_40, s_ew5) if s_strat["sharpe"] > s_bench["sharpe"])
    if n_wins >= 2:
        print(f"  ▶︎ ✅ Beats {n_wins}/3 benchmarks on Sharpe — Faber 5-asset GTAA works as advertised.")
    elif n_wins == 1:
        print(f"  ▶︎ ⚠️  Beats only 1/3 benchmarks — partial confirmation.")
    else:
        print(f"  ▶︎ ❌ Loses to all 3 benchmarks — Faber's edge does not survive on this sample.")

    # ── Plot ───────────────────────────────────────────────────────────────
    strat_curve = (1 + net_port).cumprod()
    spy_curve   = (1 + spy_ret).cumprod()
    p6040_curve = (1 + p60_40).cumprod()
    ew5_curve   = (1 + ew_passive).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(strat_curve.index, strat_curve.values, color="#2ca02c", lw=2,
            label=f"#34 Faber 5-asset (Sharpe {s_strat['sharpe']:.2f}, MaxDD {s_strat['max_dd']*100:.1f}%)")
    ax.plot(spy_curve.index, spy_curve.values, color="#1f77b4", lw=1.4, alpha=0.7,
            label=f"SPY B&H (Sharpe {s_spy['sharpe']:.2f}, MaxDD {s_spy['max_dd']*100:.1f}%)")
    ax.plot(p6040_curve.index, p6040_curve.values, color="#ff7f0e", lw=1.4, alpha=0.7,
            label=f"60/40 (Sharpe {s_60_40['sharpe']:.2f}, MaxDD {s_60_40['max_dd']*100:.1f}%)")
    ax.plot(ew5_curve.index, ew5_curve.values, color="#9467bd", lw=1.4, alpha=0.7, ls="--",
            label=f"EW-5 passive (Sharpe {s_ew5['sharpe']:.2f}, MaxDD {s_ew5['max_dd']*100:.1f}%)")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #34 — Faber 2007 GTAA (5-asset done correctly)\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"200-day SMA per-asset timing  ·  20% weight per active leg  ·  5 bps RT"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    strat_dd = (strat_curve / strat_curve.cummax()) - 1
    spy_dd = (spy_curve / spy_curve.cummax()) - 1
    ax.fill_between(spy_dd.index, spy_dd.values, 0, color="#1f77b4", alpha=0.30, label="SPY B&H DD")
    ax.fill_between(strat_dd.index, strat_dd.values, 0, color="#2ca02c", alpha=0.50, label="#34 DD")
    ax.set_ylabel("Drawdown")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.plot(gross_expo.index, gross_expo.values, color="#d62728", lw=0.5)
    ax.fill_between(gross_expo.index, gross_expo.values, 0, color="#d62728", alpha=0.25)
    ax.set_ylabel("Gross exposure")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_34_faber_gtaa_5asset.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"]    = gross_port.loc[net_port.index]
        out_df["cost"]            = cost_total.loc[net_port.index]
        out_df["net_return"]      = net_port
        out_df["gross_exposure"]  = gross_expo
        for t in UNIVERSE:
            out_df[f"weight_{t}"] = weights_lag[t].loc[net_port.index]
        out_df["bench_SPY"]       = spy_ret
        out_df["bench_6040"]      = p60_40
        out_df["bench_EW5"]       = ew_passive
        out_df["cum_strategy"]    = strat_curve
        out_df["cum_SPY"]         = spy_curve
        out_df["cum_6040"]        = p6040_curve
        out_df["cum_EW5"]         = ew5_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved: {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(
        strategy=s_strat, spy=s_spy, p60_40=s_60_40, ew5=s_ew5,
        calmar_strat=calmar(s_strat), calmar_spy=calmar(s_spy),
        calmar_6040=calmar(s_60_40), calmar_ew5=calmar(s_ew5),
        n_wins=n_wins,
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_34_faber_gtaa_5asset_track_record.csv")
