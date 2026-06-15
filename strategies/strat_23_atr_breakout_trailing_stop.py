"""
Strategy #23 — Donchian / ATR breakout with trailing stop (G10 core4 FX portfolio)

Classic trend-following breakout strategy of the kind any discretionary
chartist or systematic CTA would recognise. Enter on a clean break of a
multi-month high (or low) by a meaningful ATR margin, then ride the trade
with a wide ATR trailing stop until the trend exhausts.

Per-pair rules:
  - ATR period: 14 days (simple rolling mean of true range)
  - Resistance: 60-day rolling MAX of close (lagged 1 day, excludes today)
    Support   : 60-day rolling MIN of close (lagged 1 day, excludes today)
  - Long entry  : close[t] > resistance[t]  + 1.5 × ATR[t]
    Short entry : close[t] < support[t]     − 1.5 × ATR[t]
  - Trailing stop (ratchet, no look-back):
      Long  : stop[t] = max(stop[t−1], close[t] − 2.5 × ATR[t])
      Short : stop[t] = min(stop[t−1], close[t] + 2.5 × ATR[t])
    Exit when close crosses the stop level.
  - One position at a time per pair (long XOR short XOR flat).
  - Decision at close[t], execution lagged 1 day (position.shift(1)).

The 60-day lookback for resistance/support is calibrated so a fresh break
is uncommon — typically 2-4 entries per pair per year as the user requested
("price peaks 2-3 times a year"). The 1.5 ATR buffer filters whipsaw entries;
the 2.5 ATR trailing stop is wide enough to let trends run for weeks or months.

Portfolio: equal-weight (1/N) per active pair across {EURUSD, GBPUSD, AUDUSD,
USDCAD}. Max gross exposure is 1.0 when all 4 pairs are simultaneously in a
trade; typical gross is 0.25-0.50 (1-2 active pairs at any time).

Universe: G10 majors, 2010-2024, 5 pips RT cost.

This is the first NON-rate-diff directional strategy in the repo. It uses ONLY
FX price data (no rates, no VIX, no positioning data) and is therefore
structurally immune to the timing-leakage artefact that flagged the entire
rate-diff family in Strategy #21. Whatever Sharpe this produces is genuine
predictive content from price patterns alone.
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
ATR_PERIOD          = 14         # 14-day true-range window (canonical)
DONCHIAN_LOOKBACK   = 60         # 60-day resistance/support window
BREAKOUT_ATR_MULT   = 1.5        # entry buffer above resistance / below support
TRAIL_STOP_ATR_MULT = 2.5        # trailing stop distance from close
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS        = 252
START               = "2010-01-04"
END                 = "2024-12-31"

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
    """Average True Range — simple rolling mean of true range."""
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def _compute_breakout_positions(ohlc: pd.DataFrame, pair: str) -> tuple[pd.Series, list[dict]]:
    """
    Compute the daily position signal (+1 long, −1 short, 0 flat) and the
    list of completed trades for one pair using ATR-breakout + trailing stop.
    """
    close = ohlc["close"]
    high  = ohlc["high"]
    low   = ohlc["low"]

    atr  = _compute_atr(high, low, close)
    # Lag the rolling high/low by 1 day so today's close compares against the
    # 60-day range that ENDS YESTERDAY (no use of today's high in the test).
    resistance = close.rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).max().shift(1)
    support    = close.rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).min().shift(1)

    positions = pd.Series(0, index=close.index, dtype=int)
    trades: list[dict] = []
    position = 0
    stop: float | None = None
    entry_close: float | None = None
    entry_date: pd.Timestamp | None = None

    for t, date in enumerate(close.index):
        c = float(close.iloc[t])
        a = float(atr.iloc[t]) if not pd.isna(atr.iloc[t]) else np.nan
        r = float(resistance.iloc[t]) if not pd.isna(resistance.iloc[t]) else np.nan
        s = float(support.iloc[t])    if not pd.isna(support.iloc[t])    else np.nan

        if np.isnan(a) or np.isnan(r) or np.isnan(s):
            positions.iloc[t] = position
            continue

        if position == 0:
            # Entry test
            if c > r + BREAKOUT_ATR_MULT * a:
                position = +1
                stop = c - TRAIL_STOP_ATR_MULT * a
                entry_close = c
                entry_date = date
            elif c < s - BREAKOUT_ATR_MULT * a:
                position = -1
                stop = c + TRAIL_STOP_ATR_MULT * a
                entry_close = c
                entry_date = date
        elif position == +1:
            assert stop is not None and entry_close is not None and entry_date is not None
            new_stop = c - TRAIL_STOP_ATR_MULT * a
            if new_stop > stop:
                stop = new_stop
            if c < stop:
                trades.append({
                    "pair": pair, "side": "long",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": (c - entry_close) / entry_close,
                    "duration_days": int((date - entry_date).days),
                })
                position = 0
                stop = None
                entry_close = None
                entry_date = None
        elif position == -1:
            assert stop is not None and entry_close is not None and entry_date is not None
            new_stop = c + TRAIL_STOP_ATR_MULT * a
            if new_stop < stop:
                stop = new_stop
            if c > stop:
                trades.append({
                    "pair": pair, "side": "short",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": (entry_close - c) / entry_close,
                    "duration_days": int((date - entry_date).days),
                })
                position = 0
                stop = None
                entry_close = None
                entry_date = None

        positions.iloc[t] = position

    return positions, trades


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
    )


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #23 — Donchian/ATR breakout with trailing stop (core4 G10 FX portfolio)")
    print(f"  ATR period                : {ATR_PERIOD} days")
    print(f"  Resistance/support lookback: {DONCHIAN_LOOKBACK} days")
    print(f"  Breakout buffer           : ±{BREAKOUT_ATR_MULT} × ATR")
    print(f"  Trailing stop distance    : {TRAIL_STOP_ATR_MULT} × ATR")
    print(f"  Cost                      : {COST_ROUND_TRIP_PIPS} pips round-trip")
    print(f"  Sizing                    : equal-weight ±1/N per active pair (max gross = 1.0)")
    print()

    pair_names = [p[0] for p in UNIVERSE]
    pip_by_pair = {p[0]: p[1] for p in UNIVERSE}

    print(f"  Fetching OHLC for {len(UNIVERSE)} pairs...")
    ohlc_by_pair = {name: _fetch_fx_ohlc(name) for name, _ in UNIVERSE}
    for name, df in ohlc_by_pair.items():
        print(f"    {name}: {len(df)} rows, {df.index[0].date()} → {df.index[-1].date()}")

    # ── Per-pair positions and trades ──────────────────────────────────────
    idx = pd.bdate_range(start=START, end=END)
    positions_df = pd.DataFrame(0, index=idx, columns=pair_names, dtype=float)
    close_df     = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    trades_all: list[dict] = []
    trades_by_pair: dict[str, list[dict]] = {}

    for name, _ in UNIVERSE:
        ohlc = ohlc_by_pair[name].reindex(idx).ffill()
        pos, trades = _compute_breakout_positions(ohlc, name)
        positions_df[name] = pos.reindex(idx).fillna(0).astype(float)
        close_df[name]     = ohlc["close"]
        trades_all.extend(trades)
        trades_by_pair[name] = trades

    # ── Portfolio construction (equal-weight per active pair) ──────────────
    weights = (positions_df / len(UNIVERSE)).fillna(0)
    weights_lag = weights.shift(1).fillna(0)

    fx_ret = close_df.pct_change()
    gross_pair = weights_lag * fx_ret
    gross_port = gross_pair.sum(axis=1)

    # Cost: turnover × half-spread / spot per pair
    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    turnover = weights_lag.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    for name in pair_names:
        cost_per_pair[name] = turnover[name] * (cost_per_unit_pips * pip_by_pair[name]) / close_df[name]
    cost_total = cost_per_pair.sum(axis=1)

    net_port = (gross_port - cost_total).dropna()

    # ── Metrics ────────────────────────────────────────────────────────────
    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    # Time-in-market per pair
    in_market = (positions_df.abs() > 0).mean()

    # Average gross exposure
    avg_gross_exposure = weights_lag.abs().sum(axis=1).mean()

    # ── Print ──────────────────────────────────────────────────────────────
    print()
    print("=" * 78)
    print(f"  Strategy #23 — Donchian/ATR breakout portfolio (core4)")
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

    # ── Per-pair trade-level breakdown ─────────────────────────────────────
    print()
    print("Trade-level breakdown by pair:")
    print(f"  {'Pair':<8} {'N':>4} {'L':>4} {'S':>4} {'Win%':>6} {'AvgWin':>8} {'AvgLoss':>9} {'MaxWin':>8} {'MaxLoss':>9} {'PF':>6} {'AvgDur':>7} {'MedDur':>7} {'%TIM':>6}")
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
              f"{ts['avg_duration_d']:>6.0f}d {ts['med_duration_d']:>6.0f}d {tim:>5.1f}%")
    print()
    ts_all = _trade_stats(trades_all)
    if ts_all["n"] > 0:
        pf_str = f"{ts_all['profit_factor']:.2f}" if np.isfinite(ts_all['profit_factor']) else "inf"
        per_year_per_pair = ts_all["n"] / (len(UNIVERSE) * (len(net_port) / TRADING_DAYS))
        print(f"  ALL      {ts_all['n']:>4} {ts_all['n_long']:>4} {ts_all['n_short']:>4} "
              f"{ts_all['win_rate']*100:>5.1f}% {ts_all['avg_win_pct']*100:>7.2f}% {ts_all['avg_loss_pct']*100:>8.2f}% "
              f"{ts_all['max_win_pct']*100:>7.2f}% {ts_all['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts_all['avg_duration_d']:>6.0f}d {ts_all['med_duration_d']:>6.0f}d")
        print(f"  Average trades per pair per year: {per_year_per_pair:.2f}")
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
        f"Strategy #23 — Donchian/ATR breakout (core4 FX portfolio)\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"{ts_all['n']} trades, {per_year_per_pair:.1f} per pair per year  ·  "
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
    out = REPORTS / "strategy_23_atr_breakout_trailing_stop.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # ── CSV outputs ────────────────────────────────────────────────────────
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

        # Trade-level CSV
        if trades_all:
            trades_df = pd.DataFrame(trades_all)
            trades_df["pnl_pct"] = trades_df["pnl_pct"].astype(float)
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
    run(csv_out=TRACK / "strategy_23_atr_breakout_track_record.csv")
