"""
Strategy #15 — EURUSD SMA(20) crossover + RSI(14) oversold-recovery combo (long-only)

Classic technical confluence:
    Entry  : within a 5-day rolling window, BOTH of these crosses must fire:
               1. Close crosses above the 20-day SMA
                  (close[t] > SMA20[t]  AND  close[t-1] ≤ SMA20[t-1])
               2. RSI crosses up through 30 from below (oversold → recovering)
                  (RSI[t] > 30  AND  RSI[t-1] ≤ 30)
             When both are present and we are flat → enter long, full notional.

    Exit   : 2 consecutive closes below the 21-day SMA, OR 30-day time stop (safety).

Universe : EURUSD only.
Cost     : 5 pips round-trip per trade.
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

START                  = "2010-01-04"
END                    = "2024-12-31"
COST_ROUND_TRIP_PIPS   = 5.0
TRADING_DAYS           = 252
PIP_SIZE               = 0.0001

SMA_ENTRY_PERIOD       = 20
SMA_EXIT_PERIOD        = 21
RSI_PERIOD             = 14
RSI_OVERSOLD           = 30
CONFLUENCE_WINDOW_DAYS = 5
EXIT_CONSECUTIVE_DAYS  = 2
TIME_STOP_DAYS         = 30


def _rsi(price: pd.Series, period: int = 14) -> pd.Series:
    delta = price.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #15 — EURUSD SMA20 + RSI(14) combo (long-only)")
    print(f"  Entry : 20-DMA cross AND RSI cross above {RSI_OVERSOLD} "
          f"(both within {CONFLUENCE_WINDOW_DAYS}-day rolling window)")
    print(f"  Exit  : {EXIT_CONSECUTIVE_DAYS} consecutive closes below 21-DMA, "
          f"or {TIME_STOP_DAYS}-day time stop")
    print(f"  Cost  : {COST_ROUND_TRIP_PIPS} pips RT\n")

    print("Fetching EURUSD...")
    df = yf.download("EURUSD=X", start=START, end=END, auto_adjust=True, progress=False)
    px = df["Close"].squeeze()
    px.index = pd.to_datetime(px.index)
    idx = pd.bdate_range(start=START, end=END)
    px = px.reindex(idx).ffill().dropna()
    print(f"  {len(px)} daily observations\n")

    # Indicators
    sma20 = px.rolling(SMA_ENTRY_PERIOD).mean()
    sma21 = px.rolling(SMA_EXIT_PERIOD).mean()
    rsi = _rsi(px, RSI_PERIOD)

    # Cross events
    px_cross_above_sma20 = (px > sma20) & (px.shift(1) <= sma20.shift(1))
    rsi_cross_above_30   = (rsi > RSI_OVERSOLD) & (rsi.shift(1) <= RSI_OVERSOLD)

    # Rolling presence: did each fire in the last N days?
    px_recent  = px_cross_above_sma20.rolling(CONFLUENCE_WINDOW_DAYS, min_periods=1).max().astype(bool)
    rsi_recent = rsi_cross_above_30.rolling(CONFLUENCE_WINDOW_DAYS, min_periods=1).max().astype(bool)
    setup      = px_recent & rsi_recent

    # Exit condition: N consecutive closes below SMA21
    below_sma21 = (px < sma21).fillna(False)
    consec_exit = below_sma21
    for k in range(1, EXIT_CONSECUTIVE_DAYS):
        consec_exit = consec_exit & below_sma21.shift(k).fillna(False)

    # ── State machine ───────────────────────────────────────────────────────
    positions = pd.Series(0.0, index=px.index)
    trades: list[dict] = []
    in_trade = False
    entry_dt = None
    days_held = 0

    for t in px.index:
        if pd.isna(px.loc[t]) or pd.isna(sma20.loc[t]) or pd.isna(sma21.loc[t]) or pd.isna(rsi.loc[t]):
            positions.loc[t] = 0.0
            continue
        if in_trade:
            days_held += 1
            if bool(consec_exit.loc[t]) or days_held >= TIME_STOP_DAYS:
                positions.loc[t] = 0.0
                trades.append({"entry": entry_dt, "exit": t, "bars_held": days_held})
                in_trade = False
                entry_dt = None
                days_held = 0
            else:
                positions.loc[t] = 1.0
        else:
            if bool(setup.loc[t]):
                positions.loc[t] = 1.0
                in_trade = True
                entry_dt = t
                days_held = 0
            else:
                positions.loc[t] = 0.0

    # ── P&L ────────────────────────────────────────────────────────────────
    held = positions.shift(1).fillna(0)
    fx_ret = px.pct_change()
    gross_ret = (held * fx_ret).dropna()

    cost_unit = (COST_ROUND_TRIP_PIPS / 2.0) * PIP_SIZE
    turnover = positions.diff().abs().fillna(0)
    cost = (turnover * cost_unit / px).reindex(gross_ret.index).fillna(0)
    net_ret = (gross_ret - cost).dropna()

    # ── Metrics ────────────────────────────────────────────────────────────
    ann_ret = float(net_ret.mean() * TRADING_DAYS)
    ann_vol = float(net_ret.std() * np.sqrt(TRADING_DAYS))
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve = (1 + net_ret).cumprod()
    max_dd = float(((curve / curve.cummax()) - 1).min())
    hit_daily = float((net_ret > 0).mean())
    cum = float(curve.iloc[-1] - 1)

    n_trades = len(trades)
    if n_trades > 0:
        for tr in trades:
            mask = (gross_ret.index >= tr["entry"]) & (gross_ret.index <= tr["exit"])
            tr["trade_ret"] = float(gross_ret.loc[mask].sum())
        trades_df = pd.DataFrame(trades)
        win_rate = float((trades_df["trade_ret"] > 0).mean())
        avg_trade = float(trades_df["trade_ret"].mean())
        avg_bars = float(trades_df["bars_held"].mean())
    else:
        trades_df = pd.DataFrame()
        win_rate = avg_trade = avg_bars = float("nan")

    print("=" * 65)
    print(f"  Strategy #15 — EURUSD SMA20 + RSI(14) combo (long-only)")
    print("=" * 65)
    print(f"  Trades fired         : {n_trades}")
    if n_trades > 0:
        print(f"  Win rate             : {win_rate*100:.1f}%")
        print(f"  Avg trade return     : {avg_trade*100:+.2f}%")
        print(f"  Avg bars held        : {avg_bars:.1f}")
    print(f"  Ann. Return (net)    : {ann_ret*100:+.2f}%")
    print(f"  Ann. Vol (net)       : {ann_vol*100:.2f}%")
    print(f"  Sharpe (net)         : {sharpe:+.2f}")
    print(f"  Max Drawdown         : {max_dd*100:.2f}%")
    print(f"  Hit Rate (daily)     : {hit_daily*100:.2f}%")
    print(f"  Cumulative (15y)     : {cum*100:+.2f}%")
    print("=" * 65)

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(curve.index, curve.values, color="#2ca02c", lw=2,
            label=f"Strategy #15 net (Sharpe {sharpe:+.2f})")
    bench_curve = (1 + fx_ret.reindex(curve.index)).cumprod()
    ax.plot(bench_curve.index, bench_curve.values, color="gray", ls="--", lw=1,
            label="Passive long EURUSD")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(f"Strategy #15 — EURUSD SMA20 + RSI(14) combo (long-only)\n"
                 f"{START} to {END}  ·  {n_trades} trades  ·  net of {COST_ROUND_TRIP_PIPS:.0f} pips RT")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    dd = (curve / curve.cummax()) - 1
    ax.fill_between(dd.index, dd.values, 0, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown (net)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_out = REPORTS / "strategy_15_eurusd_sma_rsi.png"
    plt.savefig(plot_out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_out.relative_to(REPO)}")

    if csv_out is not None and n_trades > 0:
        out_df = pd.DataFrame({
            "eurusd_close": px,
            "sma20": sma20,
            "sma21": sma21,
            "rsi14": rsi,
            "position": positions,
            "gross_return": gross_ret,
            "cost": cost,
            "net_return": net_ret,
            "cum_net": curve,
        })
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        trades_csv = csv_out.with_name(csv_out.stem + "_trades.csv")
        trades_df.to_csv(trades_csv, index=False)
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")
        print(f"Trade log : {trades_csv.relative_to(REPO)}  ({n_trades} trades)")

    return dict(sharpe=sharpe, ann_ret=ann_ret, max_dd=max_dd,
                n_trades=n_trades, win_rate=win_rate)


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_15_eurusd_sma_rsi_track_record.csv")
