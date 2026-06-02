"""
Strategy #13 — CFTC positioning extreme + 21-DMA reversal (long AND short)

Two-sided mean-reversion strategy: catch positioning unwinds in both directions.
Earlier short-only version superseded by this two-sided one.

LONG SIDE
    Setup:    pair positioning z[t] < −2.0   (crowded SHORT → due for short squeeze)
    Trigger:  close[t]   > SMA21[t]
              close[t-1] > SMA21[t-1]
    Entry:    long the pair (+1 notional)
    Exit:     close[t] < SMA21[t] AND close[t-1] < SMA21[t-1],  OR  30-day time stop

SHORT SIDE  (identical to Strategy #13)
    Setup:    pair positioning z[t] > +2.0   (crowded LONG → due for unwind)
    Trigger:  close[t]   < SMA21[t]
              close[t-1] < SMA21[t-1]
    Entry:    short the pair (−1 notional)
    Exit:     close[t] > SMA21[t] AND close[t-1] > SMA21[t-1],  OR  30-day time stop

A pair can hold either a long or a short, never both simultaneously. After exit,
the strategy is flat in that pair until a new setup+trigger fires.

Realism (inherited from #13):
    CFTC TFF shifted +3 business days for publication lag → no look-ahead.
    Z-score computed over 260-week (5y) rolling window, sign-adjusted to pair direction.

Universe: 7 G10 pairs with CFTC TFF data.
Cost: 5 pips round-trip per trade.
"""
from __future__ import annotations

import logging
import sys
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
COT_CACHE = REPO / "data" / "raw" / "cftc_tff_cache.csv"

sys.path.insert(0, str(REPO))
from data.cftc import fetch_cot

# ── Parameters (mirror of #13) ───────────────────────────────────────────────
START                  = "2010-01-04"
END                    = "2024-12-31"
COST_ROUND_TRIP_PIPS   = 5.0
TRADING_DAYS           = 252

ZSCORE_WINDOW_WEEKS    = 260
ZSCORE_THRESHOLD       = 2.0
SMA_DAYS               = 21
CONSECUTIVE_DAYS       = 2
TIME_STOP_DAYS         = 30
COT_PUBLISH_LAG_BDAYS  = 3

PAIRS = [
    ("EURUSD", "EUR", +1, 0.0001),
    ("GBPUSD", "GBP", +1, 0.0001),
    ("AUDUSD", "AUD", +1, 0.0001),
    ("NZDUSD", "NZD", +1, 0.0001),
    ("USDJPY", "JPY", -1, 0.01),
    ("USDCAD", "CAD", -1, 0.0001),
    ("USDCHF", "CHF", -1, 0.0001),
]


def load_cot() -> pd.DataFrame:
    if COT_CACHE.exists():
        print(f"  Loading cached COT: {COT_CACHE.relative_to(REPO)}")
        return pd.read_csv(COT_CACHE, index_col=0, parse_dates=True)
    print("  No cache — fetching CFTC TFF zips...")
    df = fetch_cot(START, END)
    COT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(COT_CACHE)
    return df


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    return df["Close"].squeeze().dropna()


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #13 — CFTC positioning extreme + 21-DMA reversal (long + short)")
    print(f"  Setup     : |positioning z| > {ZSCORE_THRESHOLD}σ (over {ZSCORE_WINDOW_WEEKS}w)")
    print(f"  LONG trig : close > {SMA_DAYS}-DMA for {CONSECUTIVE_DAYS} consec days  (when z < −{ZSCORE_THRESHOLD})")
    print(f"  SHORT trig: close < {SMA_DAYS}-DMA for {CONSECUTIVE_DAYS} consec days  (when z > +{ZSCORE_THRESHOLD})")
    print(f"  Exit      : mirror cross of 21-DMA, or {TIME_STOP_DAYS}d time stop")
    print(f"  Cost      : {COST_ROUND_TRIP_PIPS} pips RT, COT lagged +{COT_PUBLISH_LAG_BDAYS} bdays")
    print()

    cot = load_cot()
    cot.index = cot.index + pd.offsets.BDay(COT_PUBLISH_LAG_BDAYS)

    print("  Fetching FX prices...")
    idx = pd.bdate_range(start=START, end=END)
    fx_close = {}
    sma = {}
    for pair, *_ in PAIRS:
        s = _fetch_fx(pair).reindex(idx).ffill()
        fx_close[pair] = s
        sma[pair] = s.rolling(SMA_DAYS, min_periods=SMA_DAYS).mean()

    pair_names = [p[0] for p in PAIRS]
    positions = pd.DataFrame(0.0, index=idx, columns=pair_names)
    trades: list[dict] = []

    for pair, ccy, sign, pip in PAIRS:
        if ccy not in cot.columns:
            print(f"  ⚠️  skipping {pair}: no COT data for {ccy}")
            continue

        pair_pos = sign * cot[ccy]
        rmean = pair_pos.rolling(ZSCORE_WINDOW_WEEKS, min_periods=52).mean()
        rstd  = pair_pos.rolling(ZSCORE_WINDOW_WEEKS, min_periods=52).std()
        z = ((pair_pos - rmean) / rstd).reindex(idx, method="ffill")

        px = fx_close[pair]
        ma = sma[pair]

        below = (px < ma)
        above = (px > ma)
        below_2d = (below & below.shift(1).fillna(False)).infer_objects(copy=False)
        above_2d = (above & above.shift(1).fillna(False)).infer_objects(copy=False)

        in_trade = 0      # 0 = flat, +1 = long, -1 = short
        entry_dt = None
        days_held = 0
        for t in idx:
            zt = z.loc[t]
            if pd.isna(px.loc[t]) or pd.isna(ma.loc[t]) or pd.isna(zt):
                positions.loc[t, pair] = 0.0
                continue

            if in_trade == 0:
                # Look for new entry
                if (zt > ZSCORE_THRESHOLD) and bool(below_2d.loc[t]):
                    positions.loc[t, pair] = -1.0
                    in_trade = -1
                    entry_dt = t
                    days_held = 0
                elif (zt < -ZSCORE_THRESHOLD) and bool(above_2d.loc[t]):
                    positions.loc[t, pair] = +1.0
                    in_trade = +1
                    entry_dt = t
                    days_held = 0
                else:
                    positions.loc[t, pair] = 0.0
            else:
                days_held += 1
                # Exit conditions
                if in_trade == -1:
                    exit_now = bool(above_2d.loc[t]) or (days_held >= TIME_STOP_DAYS)
                else:  # in_trade == +1
                    exit_now = bool(below_2d.loc[t]) or (days_held >= TIME_STOP_DAYS)

                if exit_now:
                    positions.loc[t, pair] = 0.0
                    trades.append({"pair": pair, "side": "short" if in_trade == -1 else "long",
                                   "entry": entry_dt, "exit": t, "bars_held": days_held})
                    in_trade = 0
                    entry_dt = None
                    days_held = 0
                else:
                    positions.loc[t, pair] = float(in_trade)

    # ── Returns and costs ──────────────────────────────────────────────────
    fx_close_df = pd.DataFrame(fx_close)
    fx_ret = fx_close_df.pct_change()
    held = positions.shift(1).fillna(0)
    gross_pair_ret = held * fx_ret

    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    pip_by_pair = {p[0]: p[3] for p in PAIRS}
    turnover = positions.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    for name in pair_names:
        cost_per_pair[name] = turnover[name] * (cost_per_unit_pips * pip_by_pair[name]) / fx_close_df[name]
    cost_total = cost_per_pair.sum(axis=1)

    gross_port = gross_pair_ret.sum(axis=1)
    net_port = (gross_port - cost_total).dropna()

    burn_in_start = pd.Timestamp(START) + pd.DateOffset(years=2)
    net_port = net_port[net_port.index >= burn_in_start]
    gross_port = gross_port.reindex(net_port.index)
    cost_total = cost_total.reindex(net_port.index)

    # ── Metrics ────────────────────────────────────────────────────────────
    def stats(returns: pd.Series) -> dict:
        ann_ret = returns.mean() * TRADING_DAYS
        ann_vol = returns.std() * np.sqrt(TRADING_DAYS)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve = (1 + returns).cumprod()
        max_dd = float(((curve / curve.cummax()) - 1).min())
        hit = float((returns > 0).mean())
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=float(curve.iloc[-1] - 1))

    s_gross = stats(gross_port)
    s_net = stats(net_port)
    calmar = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] != 0 else float("nan")

    trades_df = pd.DataFrame(trades)
    n_trades = len(trades_df)
    n_long = n_short = 0
    if n_trades > 0:
        for tr in trades:
            mask = (gross_pair_ret.index >= tr["entry"]) & (gross_pair_ret.index <= tr["exit"])
            tr["trade_ret"] = float(gross_pair_ret.loc[mask, tr["pair"]].sum())
        trades_df = pd.DataFrame(trades)
        n_long = int((trades_df["side"] == "long").sum())
        n_short = int((trades_df["side"] == "short").sum())
        win_rate = float((trades_df["trade_ret"] > 0).mean())
        long_win = float((trades_df.loc[trades_df["side"] == "long", "trade_ret"] > 0).mean()) if n_long else float("nan")
        short_win = float((trades_df.loc[trades_df["side"] == "short", "trade_ret"] > 0).mean()) if n_short else float("nan")
        avg_trade = float(trades_df["trade_ret"].mean())
        avg_bars = float(trades_df["bars_held"].mean())
    else:
        win_rate = long_win = short_win = avg_trade = avg_bars = float("nan")

    print("\n" + "=" * 70)
    print(f"  Strategy #13 — CFTC positioning extreme + 21-DMA reversal (long + short)")
    print("=" * 70)
    print(f"  Backtest range       : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Trades fired         : {n_trades}  ({n_long} long, {n_short} short)")
    if n_trades > 0:
        print(f"  Win rate (overall)   : {win_rate*100:.1f}%")
        print(f"  Win rate (long)      : {long_win*100:.1f}%  ({n_long} trades)")
        print(f"  Win rate (short)     : {short_win*100:.1f}%  ({n_short} trades)")
        print(f"  Avg trade return     : {avg_trade*100:+.2f}%")
        print(f"  Avg bars held        : {avg_bars:.1f}")
        by_pair = trades_df.groupby(["pair", "side"]).size().to_dict()
        print(f"  Trades per pair/side : {by_pair}")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}%")
    print(f"  {'Calmar (net)':<18} {' ':>10} {calmar:>10.2f}")
    print("=" * 70)

    # Plot
    gross_curve = (1 + gross_port).cumprod()
    net_curve = (1 + net_port).cumprod()
    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #13 — CFTC positioning extreme + 21-DMA reversal (long + short)\n"
        f"{net_port.index[0].strftime('%Y-%m-%d')} to {END}  ·  "
        f"{n_trades} trades ({n_long}L / {n_short}S)  ·  net of {COST_ROUND_TRIP_PIPS:.0f} pips RT"
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
    plot_out = REPORTS / "strategy_13_cot_extreme_long_short.png"
    plt.savefig(plot_out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_out.relative_to(REPO)}")

    if csv_out is not None and n_trades > 0:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port
        out_df["cost"] = cost_total
        out_df["net_return"] = net_port
        out_df["cum_gross"] = gross_curve
        out_df["cum_net"] = net_curve
        for name in pair_names:
            out_df[f"position_{name}"] = positions[name].reindex(net_port.index)
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        trades_csv = csv_out.with_name(csv_out.stem + "_trades.csv")
        trades_df.to_csv(trades_csv, index=False)
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")
        print(f"Trade log : {trades_csv.relative_to(REPO)}  ({n_trades} trades)")

    return dict(net=s_net, gross=s_gross, calmar=calmar,
                n_trades=n_trades, n_long=n_long, n_short=n_short,
                trades=trades_df if n_trades > 0 else None)


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_13_cot_extreme_long_short_track_record.csv")
