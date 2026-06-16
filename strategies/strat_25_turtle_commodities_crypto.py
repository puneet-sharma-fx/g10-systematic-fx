"""
Strategy #25 — Turtle System 1 on commodities + crypto (Gold, Silver, Copper,
Oil, NatGas, Soybeans, Bitcoin, Ethereum)

The honest cross-asset test. Strategies #11, #23, #24 all rejected trend-
following / breakout on G10 spot FX. The literature on Turtle Trading
(Faith 2007, Covel 2017) is clear: the original Dennis-Eckhardt rules
worked spectacularly on COMMODITIES and FUTURES in the 1980s, not on FX.

If our backtest is correct, applying the SAME 20-day breakout / 10-day
reversion / 2N hard stop spec from #24 to a commodities + crypto universe
should produce a materially different result. If it does — the rejection
of TA on FX is well-isolated to that asset class, not a code bug. If it
ALSO fails on commodities — either our implementation is wrong, or
breakout/trend-following has decayed across all asset classes post-2010.

Universe (8 instruments via yfinance continuous futures + spot crypto):
  - GC=F  Gold futures
  - SI=F  Silver futures
  - HG=F  Copper futures
  - CL=F  WTI crude oil futures
  - NG=F  Natural gas futures
  - ZS=F  Soybean futures
  - BTC-USD  Bitcoin spot
  - ETH-USD  Ethereum spot

Each instrument has its own data start date (e.g. BTC from 2014, ETH from
2017). The portfolio weight on day t is computed only across instruments
with valid data on that day.

Rules (identical to #24b — pure 20/10/2N, NO last-loser filter):
  - N = 20-day ATR (mean of true range; using daily H/L/C from yfinance)
  - Long entry  : close[t] > 20-day high of closes (lagged 1d)
    Short entry : close[t] < 20-day low  of closes (lagged 1d)
  - Long exit   : close[t] < 10-day low  of closes (lagged 1d)
    Short exit  : close[t] > 10-day high of closes (lagged 1d)
  - Hard stop   : 2N below entry (long) / above entry (short)
  - One position at a time per instrument. Execution lagged 1 day.

Position sizing: INVERSE-VOL weighted, not equal-weight. With BTC at 70%
realised vol and gold at 12%, naive equal-weight would let BTC dominate
portfolio risk. Instead:
    weight[i, t] = position[i, t] × TARGET_INSTR_VOL / realised_vol[i, t]
    TARGET_INSTR_VOL = 5%
    cap per instrument = ±30%
So when active, each instrument contributes roughly 5% vol to the portfolio.

Costs: 10 bps round-trip per leg = 5 bps per unit of turnover, applied uniformly
across all instruments. Slightly conservative for liquid futures, fair for
retail crypto.

Comparison anchors:
  - #24b (Turtle on G10 FX, no filter): Sharpe −0.28, 689 trades, PF 0.87
  - This (#25, Turtle on commodities + crypto, no filter): Sharpe = ?

Period: 2010-01 → 2024-12 (instruments included from their first available
data date).
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
ATR_PERIOD              = 20
ENTRY_BREAKOUT_LOOKBACK = 20
EXIT_REVERSION_LOOKBACK = 10
HARD_STOP_ATR_MULT      = 2.0
TARGET_INSTR_VOL        = 0.05      # each active instrument targets 5% vol
MAX_INSTR_WEIGHT        = 0.30
VOL_LOOKBACK_DAYS       = 21
COST_RT_BPS             = 10.0       # 10 bps round-trip (5 bps per leg)
TRADING_DAYS            = 252
START                   = "2010-01-04"
END                     = "2024-12-31"

# Universe with display name and yfinance ticker
UNIVERSE = [
    ("GOLD",   "GC=F"),
    ("SILVER", "SI=F"),
    ("COPPER", "HG=F"),
    ("OIL_WTI","CL=F"),
    ("NATGAS", "NG=F"),
    ("SOYBEAN","ZS=F"),
    ("BTC",    "BTC-USD"),
    ("ETH",    "ETH-USD"),
]


def _fetch_ohlc(ticker: str, name: str) -> pd.DataFrame:
    df = yf.download(ticker, start=START, end=END,
                     auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"No data for {ticker} ({name})")
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


def _compute_turtle_positions(ohlc: pd.DataFrame, name: str) -> tuple[pd.Series, list[dict]]:
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
        elif position == +1:
            in_signal_state_prev = False
            assert stop_level is not None and entry_close is not None
            if c < xl or c < stop_level:
                pnl_pct = (c - entry_close) / entry_close
                exit_reason = "stop" if c < stop_level else "reversion"
                trades.append({
                    "instr": name, "side": "long",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": pnl_pct,
                    "duration_days": int((date - entry_date).days),
                    "exit_reason": exit_reason,
                })
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
                    "instr": name, "side": "short",
                    "entry_date": entry_date, "exit_date": date,
                    "entry_close": entry_close, "exit_close": c,
                    "pnl_pct": pnl_pct,
                    "duration_days": int((date - entry_date).days),
                    "exit_reason": exit_reason,
                })
                position = 0
                stop_level = None
                entry_close = None
                entry_atr = None
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
        avg_long_pct = float(df[df["side"] == "long"]["pnl_pct"].mean())  if (df["side"] == "long").any()  else 0.0,
        avg_short_pct = float(df[df["side"] == "short"]["pnl_pct"].mean()) if (df["side"] == "short").any() else 0.0,
        sum_pnl_pct   = float(df["pnl_pct"].sum()),
        n_stop_exits  = int(exits_by_reason.get("stop", 0)),
        n_reversion_exits = int(exits_by_reason.get("reversion", 0)),
    )


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #25 — Turtle System 1 on commodities + crypto")
    print(f"  Universe                    : {len(UNIVERSE)} instruments (metals, energy, ag, crypto)")
    print(f"  N (ATR period)              : {ATR_PERIOD} days")
    print(f"  Entry breakout              : {ENTRY_BREAKOUT_LOOKBACK}-day high/low")
    print(f"  Exit reversion              : {EXIT_REVERSION_LOOKBACK}-day low/high")
    print(f"  Hard stop                   : {HARD_STOP_ATR_MULT}N from entry (fixed)")
    print(f"  Last-trade-loser filter     : OFF (per #24a dead-lock pathology)")
    print(f"  Per-instr vol target        : {TARGET_INSTR_VOL*100:.0f}% (inverse-vol sizing)")
    print(f"  Per-instr weight cap        : ±{MAX_INSTR_WEIGHT*100:.0f}%")
    print(f"  Cost                        : {COST_RT_BPS:.0f} bps round-trip per leg")
    print()

    instr_names = [u[0] for u in UNIVERSE]

    print(f"  Fetching OHLC for {len(UNIVERSE)} instruments...")
    ohlc_by_instr: dict[str, pd.DataFrame] = {}
    for name, ticker in UNIVERSE:
        try:
            ohlc_by_instr[name] = _fetch_ohlc(ticker, name)
            df = ohlc_by_instr[name]
            print(f"    {name:<8} ({ticker:<9}): {len(df):>5} rows, {df.index[0].date()} → {df.index[-1].date()}")
        except Exception as exc:
            print(f"    {name:<8} ({ticker:<9}): FAILED ({exc})")

    idx = pd.bdate_range(start=START, end=END)
    positions_df = pd.DataFrame(0, index=idx, columns=instr_names, dtype=float)
    close_df     = pd.DataFrame(index=idx, columns=instr_names, dtype=float)
    vol_df       = pd.DataFrame(index=idx, columns=instr_names, dtype=float)
    data_avail   = pd.DataFrame(False, index=idx, columns=instr_names, dtype=bool)
    trades_all: list[dict] = []
    trades_by_instr: dict[str, list[dict]] = {}

    for name, _ in UNIVERSE:
        if name not in ohlc_by_instr:
            continue
        ohlc_raw = ohlc_by_instr[name]
        ohlc = ohlc_raw.reindex(idx).ffill()
        # Mark data availability from first non-NaN date
        first_date = ohlc_raw.index.min()
        data_avail[name] = idx >= first_date

        pos, trades = _compute_turtle_positions(ohlc, name)
        positions_df[name] = pos.reindex(idx).fillna(0).astype(float)
        close_df[name]     = ohlc["close"]
        # Realised vol
        ret = ohlc["close"].pct_change()
        vol_df[name] = ret.rolling(VOL_LOOKBACK_DAYS, min_periods=10).std() * np.sqrt(TRADING_DAYS)
        trades_all.extend(trades)
        trades_by_instr[name] = trades

    # ── Sizing: inverse-vol weighted ───────────────────────────────────────
    # weight[i, t] = position[i, t] × TARGET_INSTR_VOL / realised_vol[i, t]
    # capped at ±MAX_INSTR_WEIGHT.
    weights = positions_df.mul(TARGET_INSTR_VOL).div(vol_df)
    weights = weights.where(data_avail, 0)  # zero before instrument has data
    weights = weights.clip(lower=-MAX_INSTR_WEIGHT, upper=MAX_INSTR_WEIGHT).fillna(0)
    weights_lag = weights.shift(1).fillna(0)

    fx_ret = close_df.pct_change()
    gross_instr = weights_lag * fx_ret
    gross_port = gross_instr.sum(axis=1)

    # Cost: per unit of turnover, pay half the round-trip (since each leg is half)
    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0   # 5 bps per unit of turnover
    turnover = weights_lag.diff().abs().fillna(0)
    cost_per_instr = turnover * cost_per_unit
    cost_total = cost_per_instr.sum(axis=1)

    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    in_market = (positions_df.abs() > 0).mean()
    avg_gross_exposure = weights_lag.abs().sum(axis=1).mean()

    print()
    print("=" * 78)
    print(f"  Strategy #25 — Turtle System 1 on commodities + crypto")
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
    print("Trade-level breakdown by instrument:")
    print(f"  {'Instr':<9} {'N':>4} {'L':>4} {'S':>4} {'Win%':>6} {'AvgWin':>8} {'AvgLoss':>9} {'MaxWin':>8} {'MaxLoss':>9} {'PF':>6} {'AvgDur':>7} {'Stop':>5} {'Revrt':>6} {'%TIM':>6}")
    for name in instr_names:
        if name not in trades_by_instr:
            continue
        ts = _trade_stats(trades_by_instr[name])
        tim = in_market[name] * 100
        if ts["n"] == 0:
            print(f"  {name:<9}  no completed trades")
            continue
        pf_str = f"{ts['profit_factor']:.2f}" if np.isfinite(ts['profit_factor']) else "inf"
        print(f"  {name:<9} {ts['n']:>4} {ts['n_long']:>4} {ts['n_short']:>4} "
              f"{ts['win_rate']*100:>5.1f}% {ts['avg_win_pct']*100:>7.2f}% {ts['avg_loss_pct']*100:>8.2f}% "
              f"{ts['max_win_pct']*100:>7.2f}% {ts['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts['avg_duration_d']:>6.0f}d {ts['n_stop_exits']:>5} {ts['n_reversion_exits']:>6} {tim:>5.1f}%")
    print()
    ts_all = _trade_stats(trades_all)
    if ts_all["n"] > 0:
        pf_str = f"{ts_all['profit_factor']:.2f}" if np.isfinite(ts_all['profit_factor']) else "inf"
        per_year_per_instr = ts_all["n"] / (len(UNIVERSE) * (len(net_port) / TRADING_DAYS))
        print(f"  ALL       {ts_all['n']:>4} {ts_all['n_long']:>4} {ts_all['n_short']:>4} "
              f"{ts_all['win_rate']*100:>5.1f}% {ts_all['avg_win_pct']*100:>7.2f}% {ts_all['avg_loss_pct']*100:>8.2f}% "
              f"{ts_all['max_win_pct']*100:>7.2f}% {ts_all['max_loss_pct']*100:>8.2f}% {pf_str:>6} "
              f"{ts_all['avg_duration_d']:>6.0f}d {ts_all['n_stop_exits']:>5} {ts_all['n_reversion_exits']:>6}")
        print(f"  Average trades per instrument per year : {per_year_per_instr:.2f}")
        print(f"  Long avg PnL : {ts_all['avg_long_pct']*100:+.2f}%  ·  Short avg PnL: {ts_all['avg_short_pct']*100:+.2f}%")
        print()
        print(f"  COMPARISON — Turtle System 1 (no filter):")
        print(f"    On G10 FX (Strategy #24b)        : Sharpe -0.28, PF 0.87, 689 trades")
        print(f"    On commodities + crypto (#25)    : Sharpe {s_net['sharpe']:+.2f}, PF {ts_all['profit_factor']:.2f}, {ts_all['n']} trades")
        if s_net["sharpe"] > 0.5:
            print(f"  ▶︎ ✅ Materially positive Sharpe on the right asset class. Confirms the literature.")
        elif s_net["sharpe"] > 0.0:
            print(f"  ▶︎ ⚠️  Modestly positive — Turtle parameters partially survive, weaker than 1980s era.")
        elif s_net["sharpe"] > -0.20:
            print(f"  ▶︎ ⚠️  Near-zero — even commodities/crypto don't carry the classical Turtle edge post-2010.")
        else:
            print(f"  ▶︎ ❌ Negative even on commodities/crypto — either implementation issue or trend-following dead across all asset classes.")

    # Plot
    net_curve = (1 + net_port).cumprod()
    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_RT_BPS:.0f} bps RT (Sharpe {s_net['sharpe']:.2f})")
    gross_curve = (1 + gross_port.loc[net_port.index]).cumprod()
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #25 — Turtle System 1 on commodities + crypto (8 instruments, vol-targeted)\n"
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
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_25_turtle_commodities_crypto.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["gross_exposure"] = weights_lag.abs().sum(axis=1).loc[net_port.index]
        for name in instr_names:
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
        trades_per_instr={p: _trade_stats(trades_by_instr[p]) for p in instr_names if p in trades_by_instr},
        time_in_market={p: float(in_market[p]) for p in instr_names if p in trades_by_instr},
        avg_gross_exposure=float(avg_gross_exposure),
        n_obs=len(net_port),
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_25_turtle_commodities_crypto_track_record.csv")
