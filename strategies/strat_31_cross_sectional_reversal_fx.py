"""
Strategy #31 — Cross-sectional short-term mean reversion on G10 FX

The direct mirror image of Strategy #11 (cross-sectional momentum portfolio,
rejected at Sharpe −0.34). If trend-following doesn't extract net edge from
G10 FX 2010-2024, the opposite mechanism — short-term overreaction-and-
reversion — should be a clean honest test of whether retail/algorithmic
overreaction creates mean-revertable signals at the weekly horizon.

Spec:
  - Universe   : 7 G10 pairs (EURUSD, GBPUSD, AUDUSD, NZDUSD, USDJPY,
                 USDCAD, USDCHF) — same as Strategy #20
  - Signal     : Trailing 5-day cumulative return per pair
  - Ranking    : Cross-sectional sort each Friday (weekly rebalance)
  - Positions  : LONG bottom 2 pairs (biggest losers over past 5 days)
                 SHORT top 2 pairs (biggest winners over past 5 days)
                 Equal weight ±0.25 per leg → 4 active positions, net 0
                 gross exposure 1.0 (market-neutral cross-sectional)
  - Hold       : 5 business days until next Friday rebalance
  - Cost       : 5 pips RT applied on actual turnover

Theory: Jegadeesh (1990) — "Evidence of Predictable Behavior of Security
Returns", JF — showed strong short-term reversal in US individual stocks
at 1-week horizon. The mechanism: liquidity-driven overreaction by
non-information traders that gets corrected when informed traders enter.

Whether it works in G10 FX depends on:
  - Is FX overreactive at 1-week horizon? (Vs. weak-form efficient, where
    even random short-term moves shouldn't mean-revert)
  - Do liquidity-driven flows in spot FX create exploitable mispricing?

Prior in this repo:
  - #11 cross-sectional momentum portfolio (21-day lookback, weekly):
    REJECTED at Sharpe −0.34. Suggested either FX is mean-reverting
    at multi-week horizons OR momentum has decayed.

This (#31) tests the second-derivative question: IF #11 lost because of
mean reversion, the OPPOSITE side (the reversal trade) should be a winner.
If #31 ALSO loses, then FX in 2010-2024 is noise at this horizon — neither
trending nor mean-reverting in a tradable way.

Universe: 7 G10 spot pairs, daily yfinance close. 2010-01 → 2024-12.
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
LOOKBACK_DAYS        = 5         # trailing window for cross-sectional sort
HOLD_DAYS            = 5         # weekly rebalance horizon
N_LONG               = 2         # long bottom-2 by trailing return (losers)
N_SHORT              = 2         # short top-2 by trailing return (winners)
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS         = 252
START                = "2010-01-04"
END                  = "2024-12-31"

# 7 G10 pairs (same universe as #20 — broad enough for cross-sectional rank)
UNIVERSE = [
    ("EURUSD", 0.0001),
    ("GBPUSD", 0.0001),
    ("AUDUSD", 0.0001),
    ("NZDUSD", 0.0001),
    ("USDJPY", 0.01),
    ("USDCAD", 0.0001),
    ("USDCHF", 0.0001),
]


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    s.name = pair
    return s.dropna()


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
                sharpe=sharpe, sortino=sortino, max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1))


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #31 — Cross-sectional 5-day MEAN REVERSION on G10 FX")
    print(f"  Universe   : {len(UNIVERSE)} pairs ({', '.join(p[0] for p in UNIVERSE)})")
    print(f"  Lookback   : {LOOKBACK_DAYS} days trailing return")
    print(f"  Hold       : {HOLD_DAYS} days (weekly rebalance, Fridays)")
    print(f"  Positions  : long bottom-{N_LONG} losers, short top-{N_SHORT} winners")
    print(f"  Sizing     : ±1/(N_long + N_short) = ±{1/(N_LONG+N_SHORT):.2f} per leg")
    print(f"  Cost       : {COST_ROUND_TRIP_PIPS} pips RT\n")

    pair_names = [p[0] for p in UNIVERSE]
    pip_by_pair = {p[0]: p[1] for p in UNIVERSE}

    print("Fetching FX closes...")
    fx_close = {}
    for pair, _ in UNIVERSE:
        fx_close[pair] = _fetch_fx(pair)
        print(f"  {pair}: {len(fx_close[pair])} rows")

    idx = pd.bdate_range(start=START, end=END)
    close_df = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    for pair in pair_names:
        close_df[pair] = fx_close[pair].reindex(idx).ffill()

    # Trailing 5-day return per pair
    trailing = close_df.pct_change(LOOKBACK_DAYS)

    # Friday rebalance dates only (where weekday == 4)
    rebalance_dates = idx[idx.weekday == 4]
    print(f"\nFriday rebalance dates: {len(rebalance_dates):,} (across {len(idx):,} business days)")

    # Build the weight series — on rebalance days, set new weights; else carry forward.
    weights = pd.DataFrame(0.0, index=idx, columns=pair_names)
    leg_weight = 1.0 / (N_LONG + N_SHORT)
    last_weights = pd.Series(0.0, index=pair_names)

    for date in idx:
        if date in rebalance_dates and not trailing.loc[date].isna().any():
            # Rank pairs by trailing N-day return — ascending
            ranking = trailing.loc[date].rank(method="first")
            new_w = pd.Series(0.0, index=pair_names)
            # Long the bottom N_LONG (smallest ranks = biggest losers)
            new_w[ranking <= N_LONG] = +leg_weight
            # Short the top N_SHORT (largest ranks = biggest winners)
            new_w[ranking >= len(pair_names) - N_SHORT + 1] = -leg_weight
            last_weights = new_w
        weights.loc[date] = last_weights

    # Apply 1-day execution lag (rebalance decisions on Friday → exposures starting Monday)
    weights_lag = weights.shift(1).fillna(0)

    # P&L
    pair_ret = close_df.pct_change()
    gross_pair = weights_lag * pair_ret
    gross_port = gross_pair.sum(axis=1)

    # Cost
    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    turnover = weights_lag.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    for pair in pair_names:
        cost_per_pair[pair] = turnover[pair] * (cost_per_unit_pips * pip_by_pair[pair]) / close_df[pair]
    cost_total = cost_per_pair.sum(axis=1)

    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    avg_gross_exposure = weights_lag.abs().sum(axis=1).mean()
    n_rebalances = len(rebalance_dates)

    # Per-pair time-in-market
    time_long  = ((weights_lag > 0).sum() / len(weights_lag)).to_dict()
    time_short = ((weights_lag < 0).sum() / len(weights_lag)).to_dict()

    print()
    print("=" * 78)
    print(f"  Strategy #31 — Cross-sectional 5-day MEAN REVERSION on G10 FX")
    print("=" * 78)
    print(f"  Sample                   : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Rebalances               : {n_rebalances:,} Fridays")
    print(f"  Avg portfolio gross expo : {avg_gross_exposure*100:5.1f}%  (target: 100% = ±25% × 4 legs)")
    print(f"  Cumulative cost drag     : {cost_total.sum()*100:5.2f}%")
    print()
    print(f"  {'':<22} {'GROSS':>12} {'NET':>12}")
    print(f"  {'Ann. Return':<22} {s_gross['ann_ret']*100:>11.2f}% {s_net['ann_ret']*100:>11.2f}%")
    print(f"  {'Ann. Vol':<22} {s_gross['ann_vol']*100:>11.2f}% {s_net['ann_vol']*100:>11.2f}%")
    print(f"  {'Sharpe':<22} {s_gross['sharpe']:>12.2f} {s_net['sharpe']:>12.2f}")
    print(f"  {'Sortino':<22} {s_gross['sortino']:>12.2f} {s_net['sortino']:>12.2f}")
    print(f"  {'Max Drawdown':<22} {s_gross['max_dd']*100:>11.2f}% {s_net['max_dd']*100:>11.2f}%")
    print(f"  {'Calmar (net)':<22} {' ':>12} {calmar:>12.2f}")
    print(f"  {'Daily Skew':<22} {s_gross['skew']:>12.2f} {s_net['skew']:>12.2f}")
    print(f"  {'Daily Hit Rate':<22} {s_gross['hit']*100:>11.2f}% {s_net['hit']*100:>11.2f}%")
    print(f"  {'Cumulative':<22} {s_gross['cum']*100:>11.2f}% {s_net['cum']*100:>11.2f}%")
    print("=" * 78)

    print()
    print(f"Per-pair time-in-market (fraction of days):")
    print(f"  {'Pair':<8} {'Long %':>8} {'Short %':>9} {'Active %':>10}")
    for pair in pair_names:
        active = (time_long[pair] + time_short[pair]) * 100
        print(f"  {pair:<8} {time_long[pair]*100:>7.1f}% {time_short[pair]*100:>8.1f}% {active:>9.1f}%")

    print()
    print(f"  COMPARISON — cross-sectional sorts on G10 FX:")
    print(f"    #11 momentum  (21-day lookback, long winners): Sharpe -0.34, REJECTED")
    print(f"    #31 reversal  ( 5-day lookback, long losers):  Sharpe {s_net['sharpe']:+.2f}")
    if s_net["sharpe"] > 0.3:
        print(f"  ▶︎ ✅ Material positive — short-term reversal is the right side of the trade.")
    elif s_net["sharpe"] > 0.0:
        print(f"  ▶︎ ⚠️  Mildly positive — reversal exists but barely overcomes cost.")
    elif s_net["sharpe"] > -0.2:
        print(f"  ▶︎ ⚠️  Essentially flat — neither trend nor reversal works at this horizon.")
    else:
        print(f"  ▶︎ ❌ Negative — even the opposite of momentum doesn't work. FX is noisy at this horizon.")

    # ── Plot ───────────────────────────────────────────────────────────────
    net_curve = (1 + net_port).cumprod()
    gross_curve = (1 + gross_port.loc[net_port.index]).cumprod()
    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #31 — Cross-sectional 5-day mean reversion on G10 FX (long losers / short winners)\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"weekly Friday rebalance  ·  net Sharpe {s_net['sharpe']:+.2f}, MaxDD {s_net['max_dd']*100:.1f}%"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    drawdown = (net_curve / net_curve.cummax()) - 1
    ax.fill_between(drawdown.index, drawdown.values, 0, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown (net)")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    gross_exposure = weights_lag.abs().sum(axis=1).loc[net_port.index]
    ax.plot(gross_exposure.index, gross_exposure.values, color="#d62728", lw=0.5)
    ax.fill_between(gross_exposure.index, gross_exposure.values, 0, color="#d62728", alpha=0.2)
    ax.set_ylabel("Gross exposure")
    ax.set_xlabel("Date")
    ax.set_ylim(0, 1.10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_31_cross_sectional_reversal_fx.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["gross_exposure"] = weights_lag.abs().sum(axis=1).loc[net_port.index]
        for pair in pair_names:
            out_df[f"weight_{pair}"] = weights_lag[pair].loc[net_port.index]
        out_df["cum_gross"] = (1 + gross_port.loc[net_port.index]).cumprod()
        out_df["cum_net"]   = net_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV (daily) : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(net=s_net, gross=s_gross, calmar=calmar,
                avg_gross_exposure=float(avg_gross_exposure),
                n_rebalances=n_rebalances, n_obs=len(net_port))


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_31_cross_sectional_reversal_fx_track_record.csv")
