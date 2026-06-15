"""
Strategy #24 — Classic Turtle Trading System 1 (G10 core4 FX portfolio)

The original 1984 Dennis-Eckhardt system, by-the-book. System 1 uses faster
20-day breakouts with a 10-day reversion exit, plus the famous "last-trade
was a winner → skip" filter that defines the strategy's character.

Per-pair rules (System 1):
  - N = 20-day ATR (Wilder used a 20-day average, we follow that)
  - Long entry  : close[t] > 20-day high of closes (lagged 1d, excludes today)
    Short entry : close[t] < 20-day low  of closes (lagged 1d, excludes today)
  - Long exit   : close[t] < 10-day low  of closes (lagged 1d) — reversion exit
    Short exit  : close[t] > 10-day high of closes (lagged 1d)
  - Hard stop   : 2N below entry (long) or 2N above entry (short) — fixed
                  at entry, does NOT trail. Eckhardt called this the
                  "money management stop."
  - Filter      : If the LAST COMPLETED TRADE on this pair was a winner, SKIP
                  the next entry signal. Take it only if the last trade was a
                  loser (or no prior history). This is the canonical filter
                  that distinguishes Turtle System 1 from a naive breakout.
  - One position at a time per pair. Execution lagged 1 day.

Portfolio: equal-weight (1/N) per active pair across {EURUSD, GBPUSD,
AUDUSD, USDCAD}, max gross 100% when all 4 simultaneously in trade.

This is the most-documented breakout system in trading history. The 20/10
parameter pair has been published verbatim by Curtis Faith (one of the
original Turtles) in "Way of the Turtle" (2007). Any quant practitioner
will recognise these numbers.

Comparison vs Strategy #23:
  #23 — 60-day resistance, +1.5 ATR buffer, 2.5 ATR trailing stop, no filter
  #24 — 20-day resistance (no buffer), 10-day reversion exit, 2N hard stop, last-loser filter

Where #23 produced Sharpe −0.18 over 23 trades, this Turtle variant fires
much more often (20-day windows are 3× tighter than 60-day) and uses the
last-loser filter to weed out chop. We track both ACTUAL trades and
SKIPPED entries to expose the filter's contribution.

Universe: G10 majors, 2010–2024, 5 pips RT cost.
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

# ── Strategy parameters (Turtle System 1, canonical) ─────────────────────────
ATR_PERIOD            = 20         # N — Turtle's 20-day average true range
ENTRY_BREAKOUT_LOOKBACK = 20       # 20-day entry breakout
EXIT_REVERSION_LOOKBACK = 10       # 10-day reversion exit
HARD_STOP_ATR_MULT    = 2.0        # 2N below/above entry — money mgmt stop
USE_LAST_LOSER_FILTER = True       # canonical Turtle filter
COST_ROUND_TRIP_PIPS  = 5.0
TRADING_DAYS          = 252
START                 = "2010-01-04"
END                   = "2024-12-31"

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


def _compute_turtle_positions(ohlc: pd.DataFrame, pair: str,
                              use_filter: bool = USE_LAST_LOSER_FILTER) -> tuple[pd.Series, list[dict], int]:
    """
    Return (positions, completed_trades, n_skipped_entries) for one pair.
    """
    close = ohlc["close"]
    high  = ohlc["high"]
    low   = ohlc["low"]

    atr = _compute_atr(high, low, close)
    entry_high = close.rolling(ENTRY_BREAKOUT_LOOKBACK, min_periods=ENTRY_BREAKOUT_LOOKBACK).max().shift(1)
    entry_low  = close.rolling(ENTRY_BREAKOUT_LOOKBACK, min_periods=ENTRY_BREAKOUT_LOOKBACK).min().shift(1)
    exit_high  = close.rolling(EXIT_REVERSION_LOOKBACK,  min_periods=EXIT_REVERSION_LOOKBACK).max().shift(1)
    exit_low   = close.rolling(EXIT_REVERSION_LOOKBACK,  min_periods=EXIT_REVERSION_LOOKBACK).min().shift(1)

    positions = pd.Series(0, index=close.index, dtype=int)
    trades: list[dict] = []
    position = 0
    stop_level: float | None = None
    entry_close: float | None = None
    entry_atr: float | None = None
    entry_date: pd.Timestamp | None = None
    last_trade_won = False
    has_trade_history = False
    n_skipped = 0
    # Track if we were in signal state yesterday — only count NEW signal events
    in_signal_state_prev = False

    for t, date in enumerate(close.index):
        c = float(close.iloc[t])
        a = float(atr.iloc[t]) if not pd.isna(atr.iloc[t]) else np.nan
        eh = float(entry_high.iloc[t]) if not pd.isna(entry_high.iloc[t]) else np.nan
        el = float(entry_low.iloc[t])  if not pd.isna(entry_low.iloc[t])  else np.nan
        xh = float(exit_high.iloc[t])  if not pd.isna(exit_high.iloc[t])  else np.nan
        xl = float(exit_low.iloc[t])   if not pd.isna(exit_low.iloc[t])   else np.nan

        if np.isnan(a) or np.isnan(eh) or np.isnan(el) or np.isnan(xh) or np.isnan(xl):
            positions.iloc[t] = position
            continue

        if position == 0:
            long_signal  = (c > eh)
            short_signal = (c < el)
            new_signal_event = (long_signal or short_signal) and (not in_signal_state_prev)
            in_signal_state_prev = (long_signal or short_signal)

            if new_signal_event:
                # Apply the last-loser filter (Turtle System 1 canonical)
                take_trade = (not use_filter) or (not has_trade_history) or (not last_trade_won)
                if take_trade:
                    if long_signal:
                        position = +1
                        entry_close = c
                        entry_atr = a
                        entry_date = date
                        stop_level = c - HARD_STOP_ATR_MULT * a
                    else:
                        position = -1
                        entry_close = c
                        entry_atr = a
                        entry_date = date
                        stop_level = c + HARD_STOP_ATR_MULT * a
                else:
                    n_skipped += 1
        elif position == +1:
            # Reset signal-state tracker so a fresh breakout after we close
            # this position counts as a new event.
            in_signal_state_prev = False
            assert stop_level is not None and entry_close is not None
            # Long exits: 10-day reversion OR hard stop
            if c < xl or c < stop_level:
                pnl_pct = (c - entry_close) / entry_close
                exit_reason = "stop" if c < stop_level else "reversion"
                trades.append({
                    "pair": pair, "side": "long",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": pnl_pct,
                    "duration_days": int((date - entry_date).days),
                    "exit_reason": exit_reason,
                })
                last_trade_won = pnl_pct > 0
                has_trade_history = True
                position = 0
                stop_level = None
                entry_close = None
                entry_atr = None
                entry_date = None
        elif position == -1:
            in_signal_state_prev = False
            assert stop_level is not None and entry_close is not None
            if c > xh or c > stop_level:
                pnl_pct = (entry_close - c) / entry_close
                exit_reason = "stop" if c > stop_level else "reversion"
                trades.append({
                    "pair": pair, "side": "short",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": pnl_pct,
                    "duration_days": int((date - entry_date).days),
                    "exit_reason": exit_reason,
                })
                last_trade_won = pnl_pct > 0
                has_trade_history = True
                position = 0
                stop_level = None
                entry_close = None
                entry_atr = None
                entry_date = None

        positions.iloc[t] = position

    return positions, trades, n_skipped


def _stats(returns: pd.Series) -> dict:
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew())
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
        max_duration_d = int(df["duration_days"].max()),
        med_duration_d = float(df["duration_days"].median()),
        profit_factor = float(profit_factor),
        avg_long_pct = float(df[df["side"] == "long"]["pnl_pct"].mean())  if (df["side"] == "long").any()  else 0.0,
        avg_short_pct = float(df[df["side"] == "short"]["pnl_pct"].mean()) if (df["side"] == "short").any() else 0.0,
        sum_pnl_pct   = float(df["pnl_pct"].sum()),
        n_stop_exits  = int(exits_by_reason.get("stop", 0)),
        n_reversion_exits = int(exits_by_reason.get("reversion", 0)),
    )


def run(csv_out: Path | None = None, use_filter: bool = USE_LAST_LOSER_FILTER, label: str = "") -> dict:
    print(f"\nStrategy #24{label} — Classic Turtle Trading System 1 (core4 G10 FX portfolio)")
    print(f"  N (ATR period)              : {ATR_PERIOD} days")
    print(f"  Entry breakout              : {ENTRY_BREAKOUT_LOOKBACK}-day high/low")
    print(f"  Exit reversion              : {EXIT_REVERSION_LOOKBACK}-day low/high")
    print(f"  Hard stop                   : {HARD_STOP_ATR_MULT}N from entry (fixed)")
    print(f"  Last-trade-loser filter     : {'ON (canonical Turtle)' if use_filter else 'OFF (pure 20-day breakout)'}")
    print(f"  Cost                        : {COST_ROUND_TRIP_PIPS} pips round-trip")
    print(f"  Sizing                      : equal-weight ±1/N per active pair")
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
    skipped_by_pair: dict[str, int] = {}

    for name, _ in UNIVERSE:
        ohlc = ohlc_by_pair[name].reindex(idx).ffill()
        pos, trades, n_skipped = _compute_turtle_positions(ohlc, name, use_filter=use_filter)
        positions_df[name] = pos.reindex(idx).fillna(0).astype(float)
        close_df[name]     = ohlc["close"]
        trades_all.extend(trades)
        trades_by_pair[name] = trades
        skipped_by_pair[name] = n_skipped

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
    print(f"  Strategy #24{label} — Turtle System 1 portfolio (core4, filter {'ON' if use_filter else 'OFF'})")
    print("=" * 78)
    print(f"  Sample                   : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Observations             : {len(net_port):,}")
    print(f"  Avg portfolio gross expo : {avg_gross_exposure*100:5.1f}%  (max possible = 100%)")
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
    print(f"  {'Pair':<8} {'N':>4} {'L':>4} {'S':>4} {'Win%':>6} {'AvgWin':>8} {'AvgLoss':>9} {'MaxWin':>8} {'MaxLoss':>9} {'PF':>6} {'AvgDur':>7} {'Stop':>5} {'Revrt':>6} {'Skip':>5} {'%TIM':>6}")
    for name in pair_names:
        ts = _trade_stats(trades_by_pair[name])
        tim = in_market[name] * 100
        skipped = skipped_by_pair[name]
        if ts["n"] == 0:
            print(f"  {name:<8}  no completed trades  (skipped: {skipped})")
            continue
        pf_str = f"{ts['profit_factor']:.2f}" if np.isfinite(ts['profit_factor']) else "inf"
        print(f"  {name:<8} {ts['n']:>4} {ts['n_long']:>4} {ts['n_short']:>4} "
              f"{ts['win_rate']*100:>5.1f}% {ts['avg_win_pct']*100:>7.2f}% {ts['avg_loss_pct']*100:>8.2f}% "
              f"{ts['max_win_pct']*100:>7.2f}% {ts['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts['avg_duration_d']:>6.0f}d {ts['n_stop_exits']:>5} {ts['n_reversion_exits']:>6} {skipped:>5} {tim:>5.1f}%")
    print()
    ts_all = _trade_stats(trades_all)
    skipped_total = sum(skipped_by_pair.values())
    if ts_all["n"] > 0:
        pf_str = f"{ts_all['profit_factor']:.2f}" if np.isfinite(ts_all['profit_factor']) else "inf"
        per_year_per_pair = ts_all["n"] / (len(UNIVERSE) * (len(net_port) / TRADING_DAYS))
        print(f"  ALL      {ts_all['n']:>4} {ts_all['n_long']:>4} {ts_all['n_short']:>4} "
              f"{ts_all['win_rate']*100:>5.1f}% {ts_all['avg_win_pct']*100:>7.2f}% {ts_all['avg_loss_pct']*100:>8.2f}% "
              f"{ts_all['max_win_pct']*100:>7.2f}% {ts_all['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts_all['avg_duration_d']:>6.0f}d {ts_all['n_stop_exits']:>5} {ts_all['n_reversion_exits']:>6} {skipped_total:>5}")
        print(f"  Average trades per pair per year      : {per_year_per_pair:.2f}")
        print(f"  Total entry signals skipped by filter : {skipped_total} (vs {ts_all['n']} taken — {skipped_total/(ts_all['n']+skipped_total)*100:.0f}% rejection rate)")
        print(f"  Long avg PnL : {ts_all['avg_long_pct']*100:+.2f}%  ·  Short avg PnL: {ts_all['avg_short_pct']*100:+.2f}%")

    # Plot
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
        f"Strategy #24 — Turtle System 1 (core4 FX, 20-day entry / 10-day exit / 2N stop / last-loser filter)\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"{ts_all['n']} trades + {skipped_total} skipped  ·  "
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
    suffix = "_filter_on" if use_filter else "_filter_off"
    out = REPORTS / f"strategy_24_turtle_system1{suffix}.png"
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
        skipped_total=skipped_total,
        time_in_market={p: float(in_market[p]) for p in pair_names},
        avg_gross_exposure=float(avg_gross_exposure),
        n_obs=len(net_port),
    )


if __name__ == "__main__":
    # Variant A: canonical Turtle System 1 with last-loser filter ON
    res_on = run(
        csv_out=TRACK / "strategy_24a_turtle_system1_filter_on_track_record.csv",
        use_filter=True,
        label="a",
    )
    # Variant B: pure 20/10 breakout without the filter
    res_off = run(
        csv_out=TRACK / "strategy_24b_turtle_system1_filter_off_track_record.csv",
        use_filter=False,
        label="b",
    )

    print()
    print("=" * 78)
    print("  HEAD-TO-HEAD COMPARISON: filter ON vs OFF")
    print("=" * 78)
    print(f"  {'Metric':<22} {'Filter ON (#24a)':>18} {'Filter OFF (#24b)':>20}")
    print(f"  {'Net Sharpe':<22} {res_on['net']['sharpe']:>18.2f} {res_off['net']['sharpe']:>20.2f}")
    print(f"  {'Net Ann. Return':<22} {res_on['net']['ann_ret']*100:>17.2f}% {res_off['net']['ann_ret']*100:>19.2f}%")
    print(f"  {'Net Ann. Vol':<22} {res_on['net']['ann_vol']*100:>17.2f}% {res_off['net']['ann_vol']*100:>19.2f}%")
    print(f"  {'Max Drawdown':<22} {res_on['net']['max_dd']*100:>17.2f}% {res_off['net']['max_dd']*100:>19.2f}%")
    print(f"  {'Calmar (net)':<22} {res_on['calmar']:>18.2f} {res_off['calmar']:>20.2f}")
    print(f"  {'Daily Skew':<22} {res_on['net']['skew']:>18.2f} {res_off['net']['skew']:>20.2f}")
    print(f"  {'Total trades':<22} {res_on['trades_total']['n']:>18} {res_off['trades_total']['n']:>20}")
    print(f"  {'Trade win rate':<22} {res_on['trades_total']['win_rate']*100:>17.1f}% {res_off['trades_total']['win_rate']*100:>19.1f}%")
    print(f"  {'Profit factor':<22} {res_on['trades_total']['profit_factor']:>18.2f} {res_off['trades_total']['profit_factor']:>20.2f}")
    print(f"  {'Avg gross exposure':<22} {res_on['avg_gross_exposure']*100:>17.1f}% {res_off['avg_gross_exposure']*100:>19.1f}%")
    print("=" * 78)
