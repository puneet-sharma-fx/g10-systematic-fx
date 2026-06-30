"""
Strategy #33 — SPY 200-DMA tactical allocation (Faber 2007)

The first US-equity strategy in the repo. Opens a new asset class beyond
G10 FX, commodities, and crypto. Tests the most-cited tactical-allocation
spec in retail systematic literature: long SPY when its price is above the
200-day simple moving average, flat (cash, 0%) when below.

Per Mebane Faber (2007), "A Quantitative Approach to Tactical Asset
Allocation" (SSRN 962461, ~3,000 citations) — applied to a 5-asset
universe (US equity, international equity, US bonds, REITs, commodities)
the timing rule produced ~10% annualized return with ~50% lower max
drawdown vs buy-and-hold. The SPY-only single-asset version is the
educational entry point.

Spec:
  - Asset       : SPY (S&P 500 ETF, total-return-adjusted via auto_adjust)
  - Signal      : SPY close vs 200-day simple moving average
  - Position    : Long SPY (weight = 1) when close[t] > MA200[t]
                  Flat (weight = 0, earning 0%) when close[t] <= MA200[t]
  - Decision    : End-of-day, executed next day (1-day lag — no look-ahead)
  - Cost        : 5 bps round-trip on every position flip
                  Conservative for SPY (real spreads ~0.3 bps)
  - Period      : 2010-01 → 2024-12 (matches other repo strategies)

The published Faber spec uses a 10-month SMA (= 210 trading days, very
close to 200) on monthly data. The 200-day daily version is the same
signal at higher resolution — more responsive but otherwise equivalent.

The natural benchmark is **SPY buy-and-hold**. The honest question is:
  - Does the timing rule clear the bar of just-buy-and-hold?
  - Specifically: lower drawdown? Higher Sharpe? Or just lower return?

Expected outcomes per the literature:
  - Annualized return     : ~equal or slightly lower than SPY (B&H)
  - Annualized vol        : ~25-35% lower than SPY
  - Max drawdown          : ~50% smaller than SPY
  - Sharpe                : higher than B&H by ~0.1-0.2
  - Daily skew            : less negative than B&H (avoids the worst left tail)

The strategy is long-only, so it WILL underperform buy-and-hold during
sustained bull markets (the 2010-2020 stretch). It earns its keep during
drawdowns — the test is whether the risk-adjusted return wins net of
cost on the full sample.
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
MA_DAYS               = 200      # Faber's 10-month SMA ≈ 210 trading days
COST_ROUND_TRIP_BPS   = 5.0      # 5 bps RT — conservative for SPY
TRADING_DAYS          = 252
START                 = "2010-01-04"
END                   = "2024-12-31"
TICKER                = "SPY"


def _fetch_spy() -> pd.Series:
    df = yf.download(TICKER, start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze().dropna()
    s.index = pd.to_datetime(s.index)
    s.name = TICKER
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


def _drawdown_durations(returns: pd.Series) -> dict:
    curve = (1 + returns.fillna(0)).cumprod()
    peak  = curve.cummax()
    in_dd = (curve < peak).astype(int)
    spells = []
    cur = 0
    for v in in_dd:
        if v == 1:
            cur += 1
        else:
            if cur > 0:
                spells.append(cur)
            cur = 0
    if cur > 0:
        spells.append(cur)
    if not spells:
        return dict(median_dd_days=0, max_dd_days=0, pct_underwater=0.0)
    return dict(
        median_dd_days = int(np.median(spells)),
        max_dd_days    = int(np.max(spells)),
        pct_underwater = float(in_dd.mean()),
    )


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #33 — SPY 200-DMA tactical allocation (Faber 2007)")
    print(f"  Asset       : {TICKER}")
    print(f"  Signal      : close > {MA_DAYS}-day SMA → long; else flat (cash 0%)")
    print(f"  Cost        : {COST_ROUND_TRIP_BPS:.1f} bps RT on each flip")
    print(f"  Period      : {START} → {END}\n")

    print(f"Fetching {TICKER} (yfinance, auto_adjust=True)...")
    spy = _fetch_spy()
    print(f"  {len(spy)} daily rows, {spy.index[0].date()} → {spy.index[-1].date()}")

    # ── Signal: SMA and binary position ────────────────────────────────────
    ma = spy.rolling(MA_DAYS, min_periods=MA_DAYS).mean()
    position = (spy > ma).astype(int)
    position = position.where(ma.notna(), 0)  # before MA defined, stay flat
    position_lag = position.shift(1).fillna(0)

    # ── Returns ────────────────────────────────────────────────────────────
    spy_ret = spy.pct_change()
    gross_ret = position_lag * spy_ret

    # Cost: 5 bps on each round trip; turnover = |Δposition| (0 or 1 per flip)
    turnover = position_lag.diff().abs().fillna(0)
    cost = turnover * (COST_ROUND_TRIP_BPS / 10000.0)
    net_ret = (gross_ret - cost).dropna()

    # Benchmark: SPY buy-and-hold over the same start date
    bench = spy_ret.loc[net_ret.index]

    # ── Stats ──────────────────────────────────────────────────────────────
    s_strat  = _stats(net_ret)
    s_bench  = _stats(bench)
    calmar_strat = s_strat["ann_ret"] / abs(s_strat["max_dd"]) if s_strat["max_dd"] else float("nan")
    calmar_bench = s_bench["ann_ret"] / abs(s_bench["max_dd"]) if s_bench["max_dd"] else float("nan")

    n_flips = int((turnover > 0).sum())
    pct_time_in_market = float(position_lag.mean() * 100)

    dd_strat = _drawdown_durations(net_ret)
    dd_bench = _drawdown_durations(bench)

    # Conditional Sharpe — when filter is binding (out of market)
    out_of_market_mask = (position_lag == 0).loc[net_ret.index]
    strat_oom = net_ret[out_of_market_mask]
    bench_oom = bench[out_of_market_mask]
    if len(bench_oom) > 10:
        cond_bench_sharpe = float(bench_oom.mean() * TRADING_DAYS /
                                  (bench_oom.std() * np.sqrt(TRADING_DAYS))) if bench_oom.std() > 0 else 0.0
        cond_strat_sharpe = 0.0  # we're in cash earning nothing
    else:
        cond_bench_sharpe = cond_strat_sharpe = float("nan")

    # ── Print ──────────────────────────────────────────────────────────────
    print()
    print("=" * 90)
    print("  Strategy #33 — SPY 200-DMA tactical vs SPY buy-and-hold")
    print("=" * 90)
    print(f"  {'METRIC':<22} {'#33 timing':>14} {'SPY B&H':>14} {'Δ':>12}")
    print(f"  {'Net Sharpe':<22} {s_strat['sharpe']:>14.2f} {s_bench['sharpe']:>14.2f} {s_strat['sharpe']-s_bench['sharpe']:>+12.2f}")
    print(f"  {'Sortino':<22} {s_strat['sortino']:>14.2f} {s_bench['sortino']:>14.2f} {s_strat['sortino']-s_bench['sortino']:>+12.2f}")
    print(f"  {'Ann. Return':<22} {s_strat['ann_ret']*100:>13.2f}% {s_bench['ann_ret']*100:>13.2f}% {(s_strat['ann_ret']-s_bench['ann_ret'])*100:>+11.2f}%")
    print(f"  {'Ann. Vol':<22} {s_strat['ann_vol']*100:>13.2f}% {s_bench['ann_vol']*100:>13.2f}% {(s_strat['ann_vol']-s_bench['ann_vol'])*100:>+11.2f}%")
    print(f"  {'Max Drawdown':<22} {s_strat['max_dd']*100:>13.2f}% {s_bench['max_dd']*100:>13.2f}% {(s_strat['max_dd']-s_bench['max_dd'])*100:>+11.2f}%")
    print(f"  {'Calmar':<22} {calmar_strat:>14.2f} {calmar_bench:>14.2f} {calmar_strat-calmar_bench:>+12.2f}")
    print(f"  {'Daily Skew':<22} {s_strat['skew']:>14.2f} {s_bench['skew']:>14.2f} {s_strat['skew']-s_bench['skew']:>+12.2f}")
    print(f"  {'Daily Hit Rate':<22} {s_strat['hit']*100:>13.2f}% {s_bench['hit']*100:>13.2f}% {(s_strat['hit']-s_bench['hit'])*100:>+11.2f}%")
    print(f"  {'Cumulative':<22} {s_strat['cum']*100:>13.2f}% {s_bench['cum']*100:>13.2f}% {(s_strat['cum']-s_bench['cum'])*100:>+11.2f}%")
    print("=" * 90)

    print()
    print(f"Strategy diagnostics:")
    print(f"  Time in market               : {pct_time_in_market:.1f}% of days")
    print(f"  Total position flips         : {n_flips:,}")
    print(f"  Total cost drag (15y)        : {(cost.sum()*100):.2f}%")
    print()
    print(f"Drawdown duration:")
    print(f"  {'':<22} {'#33 timing':>14} {'SPY B&H':>14}")
    print(f"  {'Median DD spell (days)':<22} {dd_strat['median_dd_days']:>14} {dd_bench['median_dd_days']:>14}")
    print(f"  {'Max DD spell (days)':<22} {dd_strat['max_dd_days']:>14} {dd_bench['max_dd_days']:>14}")
    print(f"  {'% of days underwater':<22} {dd_strat['pct_underwater']*100:>13.1f}% {dd_bench['pct_underwater']*100:>13.1f}%")
    print()
    if not np.isnan(cond_bench_sharpe):
        print(f"Conditional benchmark Sharpe when strategy is OUT of market:")
        print(f"  SPY B&H Sharpe on those days  : {cond_bench_sharpe:+.2f}")
        print(f"  Strategy was in cash (Sharpe=0 by construction)")
        print(f"  → {'YES — the timing rule sits out periods that are genuinely bad' if cond_bench_sharpe < 0.0 else 'NO — the rule sits out periods that would have been positive on average'}")

    # ── Plot ───────────────────────────────────────────────────────────────
    strat_curve = (1 + net_ret).cumprod()
    bench_curve = (1 + bench).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)

    ax = axes[0]
    ax.plot(bench_curve.index, bench_curve.values, color="#1f77b4", lw=1.4, alpha=0.85,
            label=f"SPY B&H (Sharpe {s_bench['sharpe']:.2f}, MaxDD {s_bench['max_dd']*100:.1f}%)")
    ax.plot(strat_curve.index, strat_curve.values, color="#2ca02c", lw=2,
            label=f"#33 200-DMA timing (Sharpe {s_strat['sharpe']:.2f}, MaxDD {s_strat['max_dd']*100:.1f}%)")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #33 — SPY 200-DMA tactical allocation (Faber 2007) vs SPY buy-and-hold\n"
        f"{net_ret.index[0].date()} → {net_ret.index[-1].date()}  ·  "
        f"5 bps RT cost  ·  {n_flips} flips over 15 years"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    dd_strat_series = (strat_curve / strat_curve.cummax()) - 1
    dd_bench_series = (bench_curve / bench_curve.cummax()) - 1
    ax.fill_between(dd_bench_series.index, dd_bench_series.values, 0, color="#1f77b4", alpha=0.35, label="SPY B&H DD")
    ax.fill_between(dd_strat_series.index, dd_strat_series.values, 0, color="#2ca02c", alpha=0.45, label="#33 DD")
    ax.set_ylabel("Drawdown")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    # Overlay SPY price and 200-DMA, color-shade position regime
    ax.plot(spy.index, spy.values, color="#1f77b4", lw=0.5, label="SPY close")
    ax.plot(ma.index, ma.values, color="#ff7f0e", lw=1.2, label=f"{MA_DAYS}-day SMA")
    # Highlight out-of-market periods
    flat_periods = (position_lag == 0)
    if flat_periods.any():
        ax.fill_between(spy.index, spy.min(), spy.max(),
                        where=flat_periods.values, color="red", alpha=0.07,
                        label="Out of market (flat)")
    ax.set_ylabel("SPY ($)")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_33_spy_200dma_tactical.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_ret.index)
        out_df["spy_close"]       = spy.loc[net_ret.index]
        out_df["ma200"]           = ma.loc[net_ret.index]
        out_df["position"]        = position_lag.loc[net_ret.index]
        out_df["bench_return"]    = bench
        out_df["gross_return"]    = gross_ret.loc[net_ret.index]
        out_df["cost"]            = cost.loc[net_ret.index]
        out_df["net_return"]      = net_ret
        out_df["cum_strategy"]    = strat_curve
        out_df["cum_benchmark"]   = bench_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved: {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(
        strategy=s_strat, benchmark=s_bench,
        calmar_strat=calmar_strat, calmar_bench=calmar_bench,
        n_flips=n_flips, pct_time_in_market=pct_time_in_market,
        dd_strat=dd_strat, dd_bench=dd_bench,
        cond_bench_sharpe=cond_bench_sharpe,
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_33_spy_200dma_tactical_track_record.csv")
