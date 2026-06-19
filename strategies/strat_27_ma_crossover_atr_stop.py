"""
Strategy #27 — 20/50 DMA crossover with 1 ATR stop (G10 core4 FX portfolio)

The most textbook trend-following spec there is. Per the user request:

  - Entry  : 20-day SMA crosses above 50-day SMA → LONG ("golden cross")
             20-day SMA crosses below 50-day SMA → SHORT ("death cross")
  - Stop   : 1 × ATR(14) BELOW the 20-day SMA for longs
             1 × ATR(14) ABOVE the 20-day SMA for shorts
             Recomputed DAILY (stop level moves with the 20-DMA — non-ratchet,
             matches user spec "keep the stop 1 ATR below the 20 DMA")
  - Reverse: An opposite crossover while in position triggers an exit AND a
             reversal entry on the same day (one round-trip of turnover, one
             new position opened).
  - One position at a time per pair. Decision at close[t], execution lagged 1 day.

This is the simplest moving-average system in trading — taught in every retail
course and built into every charting package. Question: does it survive 5 pips
round-trip cost on G10 core 4 (EURUSD, GBPUSD, AUDUSD, USDCAD)?

Prior in this repo:
  #23 — 60-day Donchian + ATR breakout : Sharpe −0.18 (rejected)
  #24a — Turtle 20/10 with filter      : Sharpe −0.01 (filter dead-lock)
  #24b — Turtle 20/10 no filter        : Sharpe −0.28 (whipsaw graveyard)

If the 20/50 crossover joins the same rejection family, that's a 4th independent
TA-in-FX confirmation. If it differs materially, the 20/50 MA pair has something
the 60-day Donchian and 20/10 breakout don't.

Reports trade-level metrics in print output: # trades per pair, long/short
split, win rate, profit factor, avg/max win/loss, avg duration, exit-reason
decomposition (stop vs crossover-reversal), time-in-market.

Universe: G10 majors, 2010-2024, 5 pips RT cost.
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
FAST_MA_DAYS         = 20       # fast SMA
SLOW_MA_DAYS         = 50       # slow SMA
ATR_PERIOD           = 14       # canonical ATR window
STOP_ATR_MULT        = 1.0      # 1 ATR offset from the fast MA
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS         = 252
START                = "2010-01-04"
END                  = "2024-12-31"

UNIVERSE = [
    ("EURUSD", 0.0001),
    ("GBPUSD", 0.0001),
    ("AUDUSD", 0.0001),
    ("USDCAD", 0.0001),
]


def _fetch_fx_ohlc(pair: str) -> pd.DataFrame:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    df.index = pd.to_datetime(df.index)
    df.columns = ["open", "high", "low", "close"]
    return df.sort_index()


def _compute_atr(high: pd.Series, low: pd.Series, close: pd.Series,
                 period: int = ATR_PERIOD) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def _compute_ma_crossover_positions(ohlc: pd.DataFrame, pair: str) -> tuple[pd.Series, list[dict]]:
    """
    Compute the daily position (+1/-1/0) and the list of completed trades for
    one pair using 20/50 SMA crossover entries and a 1×ATR stop below the
    fast SMA (above, for shorts).
    """
    close = ohlc["close"]
    high  = ohlc["high"]
    low   = ohlc["low"]

    ma_fast = close.rolling(FAST_MA_DAYS, min_periods=FAST_MA_DAYS).mean()
    ma_slow = close.rolling(SLOW_MA_DAYS, min_periods=SLOW_MA_DAYS).mean()
    atr     = _compute_atr(high, low, close)

    # Crossover events fire only on the day the sign of (ma_fast - ma_slow) flips
    diff      = ma_fast - ma_slow
    diff_prev = diff.shift(1)
    golden_x  = (diff_prev <= 0) & (diff > 0)
    death_x   = (diff_prev >= 0) & (diff < 0)

    positions = pd.Series(0, index=close.index, dtype=int)
    trades: list[dict] = []
    position = 0
    entry_close: float | None = None
    entry_date:  pd.Timestamp | None = None

    for t, date in enumerate(close.index):
        c  = float(close.iloc[t])
        mf = float(ma_fast.iloc[t]) if not pd.isna(ma_fast.iloc[t]) else np.nan
        a  = float(atr.iloc[t])     if not pd.isna(atr.iloc[t])     else np.nan
        gx = bool(golden_x.iloc[t]) if not pd.isna(golden_x.iloc[t]) else False
        dx = bool(death_x.iloc[t])  if not pd.isna(death_x.iloc[t])  else False

        if np.isnan(mf) or np.isnan(a):
            positions.iloc[t] = position
            continue

        if position == 0:
            if gx:
                position = +1
                entry_close = c
                entry_date  = date
            elif dx:
                position = -1
                entry_close = c
                entry_date  = date
        elif position == +1:
            assert entry_close is not None and entry_date is not None
            stop_level = mf - STOP_ATR_MULT * a   # daily, non-ratchet
            stopped = c < stop_level
            reversed = dx
            if stopped or reversed:
                trades.append({
                    "pair": pair, "side": "long",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": (c - entry_close) / entry_close,
                    "duration_days": int((date - entry_date).days),
                    "exit_reason": "stop" if stopped else "reversal",
                })
                if reversed:
                    position = -1
                    entry_close = c
                    entry_date  = date
                else:
                    position = 0
                    entry_close = None
                    entry_date  = None
        elif position == -1:
            assert entry_close is not None and entry_date is not None
            stop_level = mf + STOP_ATR_MULT * a   # 1 ATR above MA20 for shorts
            stopped = c > stop_level
            reversed = gx
            if stopped or reversed:
                trades.append({
                    "pair": pair, "side": "short",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": (entry_close - c) / entry_close,
                    "duration_days": int((date - entry_date).days),
                    "exit_reason": "stop" if stopped else "reversal",
                })
                if reversed:
                    position = +1
                    entry_close = c
                    entry_date  = date
                else:
                    position = 0
                    entry_close = None
                    entry_date  = None

        positions.iloc[t] = position

    return positions, trades


def _stats(returns: pd.Series) -> dict:
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew()) if returns.std() > 0 else 0.0
    downside_vol = float(returns[returns < 0].std() * np.sqrt(TRADING_DAYS))
    sortino = ann_ret / downside_vol if downside_vol > 0 else 0.0
    return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe, sortino=sortino,
                max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1))


def _trade_stats(trades: list[dict]) -> dict:
    if not trades:
        return dict(n=0)
    df = pd.DataFrame(trades)
    wins   = df[df["pnl_pct"] > 0]
    losses = df[df["pnl_pct"] <= 0]
    profit_factor = (wins["pnl_pct"].sum() / abs(losses["pnl_pct"].sum())) if not losses.empty and losses["pnl_pct"].sum() != 0 else float("inf")
    exits_by_reason = df["exit_reason"].value_counts().to_dict() if "exit_reason" in df.columns else {}
    return dict(
        n            = int(len(df)),
        n_long       = int((df["side"] == "long").sum()),
        n_short      = int((df["side"] == "short").sum()),
        win_rate     = float(len(wins) / len(df)),
        avg_win_pct  = float(wins["pnl_pct"].mean()) if not wins.empty else 0.0,
        avg_loss_pct = float(losses["pnl_pct"].mean()) if not losses.empty else 0.0,
        max_win_pct  = float(df["pnl_pct"].max()),
        max_loss_pct = float(df["pnl_pct"].min()),
        avg_duration_d = float(df["duration_days"].mean()),
        med_duration_d = float(df["duration_days"].median()),
        profit_factor = float(profit_factor),
        avg_long_pct  = float(df[df["side"] == "long"]["pnl_pct"].mean())  if (df["side"] == "long").any()  else 0.0,
        avg_short_pct = float(df[df["side"] == "short"]["pnl_pct"].mean()) if (df["side"] == "short").any() else 0.0,
        n_stop_exits      = int(exits_by_reason.get("stop", 0)),
        n_reversal_exits  = int(exits_by_reason.get("reversal", 0)),
    )


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #27 — 20/50 DMA crossover with 1 ATR stop (core4 G10 FX)")
    print(f"  Fast MA               : {FAST_MA_DAYS} days")
    print(f"  Slow MA               : {SLOW_MA_DAYS} days")
    print(f"  ATR period            : {ATR_PERIOD} days")
    print(f"  Stop offset from MA20 : ±{STOP_ATR_MULT} × ATR (non-ratchet, daily)")
    print(f"  Crossover reversal    : ON (golden/death cross while in position flips)")
    print(f"  Cost                  : {COST_ROUND_TRIP_PIPS} pips round-trip")
    print(f"  Sizing                : equal-weight ±1/N per active pair")
    print()

    pair_names = [p[0] for p in UNIVERSE]
    pip_by_pair = {p[0]: p[1] for p in UNIVERSE}

    print(f"  Fetching OHLC for {len(UNIVERSE)} pairs...")
    ohlc_by_pair = {name: _fetch_fx_ohlc(name) for name, _ in UNIVERSE}
    for name, df in ohlc_by_pair.items():
        print(f"    {name}: {len(df)} rows, {df.index[0].date()} → {df.index[-1].date()}")

    idx = pd.bdate_range(start=START, end=END)
    positions_df = pd.DataFrame(0, index=idx, columns=pair_names, dtype=float)
    close_df     = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    trades_all: list[dict] = []
    trades_by_pair: dict[str, list[dict]] = {}

    for name, _ in UNIVERSE:
        ohlc = ohlc_by_pair[name].reindex(idx).ffill()
        pos, trades = _compute_ma_crossover_positions(ohlc, name)
        positions_df[name] = pos.reindex(idx).fillna(0).astype(float)
        close_df[name]     = ohlc["close"]
        trades_all.extend(trades)
        trades_by_pair[name] = trades

    weights = (positions_df / len(UNIVERSE)).fillna(0)
    weights_lag = weights.shift(1).fillna(0)

    fx_ret = close_df.pct_change()
    gross_pair = weights_lag * fx_ret
    gross_port = gross_pair.sum(axis=1)

    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    turnover = weights_lag.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    for name in pair_names:
        cost_per_pair[name] = turnover[name] * (cost_per_unit_pips * pip_by_pair[name]) / close_df[name]
    cost_total = cost_per_pair.sum(axis=1)

    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    in_market = (positions_df.abs() > 0).mean()
    avg_gross_exposure = weights_lag.abs().sum(axis=1).mean()

    print()
    print("=" * 78)
    print(f"  Strategy #27 — 20/50 DMA crossover portfolio (core4)")
    print("=" * 78)
    print(f"  Sample                   : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Observations             : {len(net_port):,}")
    print(f"  Avg portfolio gross expo : {avg_gross_exposure*100:5.1f}%")
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
    print("Trade-level breakdown by pair:")
    print(f"  {'Pair':<8} {'N':>4} {'L':>4} {'S':>4} {'Win%':>6} {'AvgWin':>8} {'AvgLoss':>9} {'MaxWin':>8} {'MaxLoss':>9} {'PF':>6} {'AvgDur':>7} {'Stop':>5} {'Revrt':>6} {'%TIM':>6}")
    for name in pair_names:
        ts = _trade_stats(trades_by_pair[name])
        tim = in_market[name] * 100
        if ts["n"] == 0:
            print(f"  {name:<8}  no completed trades")
            continue
        pf_str = f"{ts['profit_factor']:.2f}" if np.isfinite(ts['profit_factor']) else "inf"
        print(f"  {name:<8} {ts['n']:>4} {ts['n_long']:>4} {ts['n_short']:>4} "
              f"{ts['win_rate']*100:>5.1f}% {ts['avg_win_pct']*100:>7.2f}% {ts['avg_loss_pct']*100:>8.2f}% "
              f"{ts['max_win_pct']*100:>7.2f}% {ts['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts['avg_duration_d']:>6.0f}d {ts['n_stop_exits']:>5} {ts['n_reversal_exits']:>6} {tim:>5.1f}%")
    print()
    ts_all = _trade_stats(trades_all)
    if ts_all["n"] > 0:
        pf_str = f"{ts_all['profit_factor']:.2f}" if np.isfinite(ts_all['profit_factor']) else "inf"
        per_year_per_pair = ts_all["n"] / (len(UNIVERSE) * (len(net_port) / TRADING_DAYS))
        print(f"  ALL      {ts_all['n']:>4} {ts_all['n_long']:>4} {ts_all['n_short']:>4} "
              f"{ts_all['win_rate']*100:>5.1f}% {ts_all['avg_win_pct']*100:>7.2f}% {ts_all['avg_loss_pct']*100:>8.2f}% "
              f"{ts_all['max_win_pct']*100:>7.2f}% {ts_all['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts_all['avg_duration_d']:>6.0f}d {ts_all['n_stop_exits']:>5} {ts_all['n_reversal_exits']:>6}")
        print(f"  Average trades per pair per year      : {per_year_per_pair:.2f}")
        print(f"  Exit decomposition: {ts_all['n_stop_exits']} on stop, "
              f"{ts_all['n_reversal_exits']} on opposite crossover reversal")
        print(f"  Long avg PnL : {ts_all['avg_long_pct']*100:+.2f}%  ·  Short avg PnL: {ts_all['avg_short_pct']*100:+.2f}%")

    # ── Plot ───────────────────────────────────────────────────────────────
    net_curve = (1 + net_port).cumprod()
    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    gross_curve = (1 + gross_port.loc[net_port.index]).cumprod()
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #27 — 20/50 DMA crossover with 1 ATR stop (core4 FX)\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"{ts_all['n']} trades  ·  "
        f"net Sharpe {s_net['sharpe']:.2f}, MaxDD {s_net['max_dd']*100:.1f}%, Calmar {calmar:.2f}"
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
    ax.plot(gross_exposure.index, gross_exposure.values, color="#d62728", lw=0.7)
    ax.fill_between(gross_exposure.index, gross_exposure.values, 0, color="#d62728", alpha=0.25)
    ax.set_ylabel("Gross exposure")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_27_ma_crossover_atr_stop.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["gross_exposure"] = weights_lag.abs().sum(axis=1).loc[net_port.index]
        for name in pair_names:
            out_df[f"position_{name}"] = positions_df[name].loc[net_port.index]
            out_df[f"weight_{name}"]   = weights_lag[name].loc[net_port.index]
        out_df["cum_gross"] = (1 + gross_port.loc[net_port.index]).cumprod()
        out_df["cum_net"]   = net_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV (daily) : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

        if trades_all:
            trades_df = pd.DataFrame(trades_all)
            trades_csv = csv_out.with_name(csv_out.stem + "_trades.csv")
            trades_df.to_csv(trades_csv, index=False, float_format="%.6f")
            print(f"CSV (trades): {trades_csv.relative_to(REPO)}  ({len(trades_df)} trades)")

    return dict(
        net=s_net, gross=s_gross, calmar=calmar,
        trades_total=ts_all if trades_all else dict(n=0),
        trades_per_pair={p: _trade_stats(trades_by_pair[p]) for p in pair_names},
        time_in_market={p: float(in_market[p]) for p in pair_names},
        avg_gross_exposure=float(avg_gross_exposure),
        n_obs=len(net_port),
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_27_ma_crossover_atr_stop_track_record.csv")
