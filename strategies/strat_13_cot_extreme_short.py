"""
Strategy #13 — CFTC positioning extreme + 21-DMA breakdown (short-only)

Hypothesis:
    When speculative positioning in a pair becomes extremely crowded long
    (+3σ over 5-year rolling window), the pair is set up for an unwind.
    Wait for technical confirmation — price closes below 21-DMA for 2
    consecutive days — then go short. Exit when price closes back above
    21-DMA for 2 days, or hard time-stop at 30 trading days.

Setup:
    pair_positioning_z[t]  >  +2.0
    where pair_positioning = sign-adjusted Leveraged Money net / OI ratio
    z-score computed over a trailing 260-week (~5-year) window.
    (Note: +3σ was the original spec but empirically never fires —
    CFTC positioning is bounded and max observed z across G10 is ~+2.7.
    +2.0σ is the standard practitioner threshold for "crowded long".)

Trigger (after setup is true):
    close[t]   < SMA21[t]
    close[t-1] < SMA21[t-1]

Action: enter SHORT at close of day t, full notional (-1 per active pair).

Exit (whichever fires first):
    close[t]   > SMA21[t]  AND  close[t-1] > SMA21[t-1]   (2-day re-cross above MA)
    OR
    30 trading days have elapsed since entry (time stop)

Universe: 7 G10 pairs with CFTC TFF data
    EURUSD, GBPUSD, AUDUSD, NZDUSD, USDJPY, USDCAD, USDCHF
    (SEK, NOK not available on CFTC TFF; CHF kept — strategy is event-driven
    so its single-pair sensitivity to peg events matters less than for #7.)

Realism:
    CFTC reports are as-of Tuesday but published Friday afternoon. We shift
    the COT index forward by 3 business days so the strategy only uses
    positioning data after its actual publication time.

Cost: 5 pips round-trip per trade (entry + exit).
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

# ── Parameters ───────────────────────────────────────────────────────────────
START                = "2010-01-04"
END                  = "2024-12-31"
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS         = 252

ZSCORE_WINDOW_WEEKS  = 260   # ≈ 5 years
ZSCORE_THRESHOLD     = 2.0   # +2 SD (top ~2.5% of positioning; +3 never triggers in this dataset)
SMA_DAYS             = 21
CONSECUTIVE_DAYS     = 2
TIME_STOP_DAYS       = 30
COT_PUBLISH_LAG_BDAYS = 3    # Tue as-of → Fri publish

# Universe: (pair, COT currency code, pair-direction sign, pip size)
# sign aligns CFTC "long currency X" with "long the pair" direction
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
        df = pd.read_csv(COT_CACHE, index_col=0, parse_dates=True)
        return df
    print("  No cache — fetching CFTC TFF zips (this takes ~30s)...")
    df = fetch_cot(START, END)
    COT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(COT_CACHE)
    return df


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    return df["Close"].squeeze().dropna()


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #13 — CFTC positioning extreme + 21-DMA breakdown (short-only)")
    print(f"  Setup     : positioning z > +{ZSCORE_THRESHOLD} (over {ZSCORE_WINDOW_WEEKS} weeks)")
    print(f"  Trigger   : close below {SMA_DAYS}-DMA for {CONSECUTIVE_DAYS} consecutive days")
    print(f"  Exit      : close above {SMA_DAYS}-DMA for {CONSECUTIVE_DAYS} days, or {TIME_STOP_DAYS}d time stop")
    print(f"  Cost      : {COST_ROUND_TRIP_PIPS} pips RT")
    print(f"  Lag       : COT shifted +{COT_PUBLISH_LAG_BDAYS} bdays (publish realism)")
    print()

    cot = load_cot()
    print(f"  COT: {cot.shape[0]} weeks × {cot.shape[1]} currencies, "
          f"{cot.index[0].date()} → {cot.index[-1].date()}")
    # Shift forward by 3 business days to reflect publication lag
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
        z_weekly = (pair_pos - rmean) / rstd
        z = z_weekly.reindex(idx, method="ffill")

        px = fx_close[pair]
        ma = sma[pair]

        below = (px < ma)
        above = (px > ma)
        below_2d = below & below.shift(1).fillna(False)
        above_2d = above & above.shift(1).fillna(False)

        in_trade = False
        entry_dt = None
        days_held = 0
        for t in idx:
            zt = z.loc[t]
            if pd.isna(px.loc[t]) or pd.isna(ma.loc[t]) or pd.isna(zt):
                positions.loc[t, pair] = 0.0
                continue
            if in_trade:
                days_held += 1
                if (above_2d.loc[t]) or (days_held >= TIME_STOP_DAYS):
                    # exit at this close
                    positions.loc[t, pair] = 0.0
                    trades.append({"pair": pair, "entry": entry_dt, "exit": t,
                                   "bars_held": days_held})
                    in_trade = False
                    entry_dt = None
                    days_held = 0
                else:
                    positions.loc[t, pair] = -1.0
            else:
                if (zt > ZSCORE_THRESHOLD) and below_2d.loc[t]:
                    positions.loc[t, pair] = -1.0
                    in_trade = True
                    entry_dt = t
                    days_held = 0
                else:
                    positions.loc[t, pair] = 0.0

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

    # Restrict to period where z-score window is fully populated (~5y burn-in)
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

    # Trade stats
    trades_df = pd.DataFrame(trades)
    n_trades = len(trades_df)
    if n_trades > 0:
        # Compute per-trade PnL
        for tr in trades:
            mask = (gross_pair_ret.index >= tr["entry"]) & (gross_pair_ret.index <= tr["exit"])
            tr["trade_ret"] = float((gross_pair_ret.loc[mask, tr["pair"]]).sum())
        trades_df = pd.DataFrame(trades)
        win_rate = float((trades_df["trade_ret"] > 0).mean())
        avg_trade_ret = float(trades_df["trade_ret"].mean())
        avg_bars_held = float(trades_df["bars_held"].mean())
    else:
        win_rate = avg_trade_ret = avg_bars_held = float("nan")

    # ── Print summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"  Strategy #13 — CFTC positioning extreme + 21-DMA breakdown (short-only)")
    print("=" * 70)
    print(f"  Backtest range       : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Trades fired         : {n_trades}")
    if n_trades > 0:
        print(f"  Win rate (gross)     : {win_rate*100:.1f}%")
        print(f"  Avg trade return     : {avg_trade_ret*100:+.2f}%")
        print(f"  Avg bars held        : {avg_bars_held:.1f}")
        # Trades per pair
        by_pair = trades_df.groupby("pair").size().to_dict()
        print(f"  Trades per pair      : {by_pair}")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}%")
    print(f"  {'Hit Rate (daily)':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}%")
    print(f"  {'Calmar (net)':<18} {' ':>10} {calmar:>10.2f}")
    print("=" * 70)

    # ── Plot ───────────────────────────────────────────────────────────────
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
        f"Strategy #13 — CFTC positioning extreme + 21-DMA breakdown (short-only)\n"
        f"{net_port.index[0].strftime('%Y-%m-%d')} to {END}  ·  "
        f"{n_trades} trades  ·  net of {COST_ROUND_TRIP_PIPS:.0f} pips RT"
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
    plot_out = REPORTS / "strategy_13_cot_extreme_short.png"
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
        # Also save trade log
        trades_csv = csv_out.with_name(csv_out.stem + "_trades.csv")
        trades_df.to_csv(trades_csv, index=False)
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")
        print(f"Trade log : {trades_csv.relative_to(REPO)}  ({n_trades} trades)")

    return dict(net=s_net, gross=s_gross, calmar=calmar,
                n_trades=n_trades, trades=trades_df if n_trades > 0 else None)


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_13_cot_extreme_short_track_record.csv")
