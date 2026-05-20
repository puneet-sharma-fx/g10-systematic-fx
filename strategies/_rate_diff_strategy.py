"""
Common implementation of the rate-differential strategy used by Strategies #2+.

Each numbered strategy is a thin wrapper that calls `run_rate_diff_strategy()`
with the appropriate pair and rate-leg identifiers.

Signal:
    d_diff[t] = Δ(base_2Y − quote_2Y) on day t
    pos[t+1]  = sign(d_diff[t]),  held 1 day

Transaction cost:
    5 pips total round-trip = 2.5 pips per unit of |Δposition|

Data:
    2Y yields : data/raw/tvc_2y_yields.csv  (TVC:XX02Y daily, fetched via tvDatafeed)
    FX spot   : yfinance  (e.g. "GBPUSD=X")
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
REPORTS.mkdir(exist_ok=True)
YIELDS_CSV = REPO / "data" / "raw" / "tvc_2y_yields.csv"

# Defaults
TRADING_DAYS = 252
DEFAULT_COST_PIPS_ROUND_TRIP = 5.0
DEFAULT_PIP_SIZE = 0.0001        # most G10 pairs, 4-decimal quote
JPY_PIP_SIZE     = 0.01          # USDJPY is quoted to 2 decimals


def _pip_size_for(pair: str) -> float:
    return JPY_PIP_SIZE if "JPY" in pair else DEFAULT_PIP_SIZE


def _load_yields() -> pd.DataFrame:
    if not YIELDS_CSV.exists():
        raise FileNotFoundError(
            f"Yields CSV missing: {YIELDS_CSV}. "
            "Run `python strategies/_fetch_yields.py` first."
        )
    df = pd.read_csv(YIELDS_CSV, index_col=0, parse_dates=True)
    return df


def _fetch_fx(pair: str, start: str, end: str) -> pd.Series:
    ticker = f"{pair}=X"
    df = yf.download(ticker, start=start, end=end,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.name = pair
    s.index = pd.to_datetime(s.index)
    return s.dropna()


def run_rate_diff_strategy(
    *,
    number: int,
    pair: str,
    base_ccy: str,
    quote_ccy: str,
    start: str = "2010-01-04",
    end: str = "2024-12-31",
    cost_round_trip_pips: float = DEFAULT_COST_PIPS_ROUND_TRIP,
) -> dict:
    """
    Run a rate-differential strategy on `pair`.

    Signal = Δ(base_2Y − quote_2Y).  pos = sign of signal, held 1 day.

    Parameters
    ----------
    number      : strategy number, used in filename / titles
    pair        : "GBPUSD", "USDJPY", etc.
    base_ccy    : currency-code key in the yields CSV ("GB", "US", "JP", ...)
    quote_ccy   : same, for the quote leg
    """
    cost_per_unit_pips = cost_round_trip_pips / 2.0
    pip_size = _pip_size_for(pair)

    print(f"\nStrategy #{number} — Δ({base_ccy} 2Y − {quote_ccy} 2Y) → next-day {pair}")
    print(f"  Period : {start} → {end}")
    print(f"  Cost   : {cost_round_trip_pips} pips round-trip ({cost_per_unit_pips} pips/unit)\n")

    # Load data
    yields = _load_yields()
    if base_ccy not in yields.columns or quote_ccy not in yields.columns:
        raise KeyError(f"Missing yield series: {base_ccy=}, {quote_ccy=}")

    fx = _fetch_fx(pair, start=start, end=end)
    print(f"  FX  : {len(fx)} daily obs")
    print(f"  {base_ccy} 2Y : {yields[base_ccy].dropna().shape[0]} obs")
    print(f"  {quote_ccy} 2Y : {yields[quote_ccy].dropna().shape[0]} obs\n")

    # Align to common business-day index
    idx = pd.bdate_range(start=start, end=end)
    base_2y = yields[base_ccy].reindex(idx).ffill()
    quote_2y = yields[quote_ccy].reindex(idx).ffill()
    px = fx.reindex(idx).ffill()

    # Signal
    rate_diff = (base_2y - quote_2y).rename("rate_diff_pp")
    d_diff = rate_diff.diff().rename("d_diff_pp")

    raw_signal = np.sign(d_diff)
    position = raw_signal.shift(1).fillna(0)

    spot_ret = px.pct_change()
    gross_ret = position * spot_ret

    pos_change = position.diff().abs().fillna(0)
    cost_in_returns = pos_change * (cost_per_unit_pips * pip_size) / px
    net_ret = (gross_ret - cost_in_returns).dropna()

    # Drop early period before both yield series have data
    first_valid = max(base_2y.dropna().index.min(), quote_2y.dropna().index.min())
    net_ret = net_ret[net_ret.index >= first_valid]
    gross_ret = gross_ret.dropna()
    gross_ret = gross_ret[gross_ret.index >= first_valid]

    # Benchmark = passive long the pair
    bench_ret = spot_ret.dropna()
    bench_ret = bench_ret[bench_ret.index >= first_valid]

    def stats(returns: pd.Series) -> dict:
        ann_ret = returns.mean() * TRADING_DAYS
        ann_vol = returns.std() * np.sqrt(TRADING_DAYS)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve = (1 + returns).cumprod()
        max_dd = float(((curve / curve.cummax()) - 1).min())
        hit = float((returns > 0).mean())
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=float(curve.iloc[-1] - 1))

    s_gross = stats(gross_ret)
    s_net = stats(net_ret)
    s_bench = stats(bench_ret)

    n_trades = int((pos_change > 0).sum())
    avg_turnover = float(pos_change.mean())
    cost_drag = float(cost_in_returns.sum())

    print("=" * 60)
    print(f"  Strategy #{number} — Δ({base_ccy} 2Y − {quote_ccy} 2Y) → {pair} next-day")
    print("=" * 60)
    print(f"  Observations         : {len(net_ret):,}")
    print(f"  Position flips       : {n_trades:,}  ({n_trades/len(net_ret)*100:.1f}% of days)")
    print(f"  Avg daily |Δpos|     : {avg_turnover:.3f}")
    print(f"  Cumulative cost drag : {cost_drag*100:.1f}%")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10} {'Passive '+pair:>17}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}% {s_bench['ann_ret']*100:>16.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}% {s_bench['ann_vol']*100:>16.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f} {s_bench['sharpe']:>17.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}% {s_bench['max_dd']*100:>16.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}% {s_bench['cum']*100:>16.2f}%")
    print(f"  {'Hit Rate':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}% {s_bench['hit']*100:>16.2f}%")
    print("=" * 60)

    # Plot
    gross_curve = (1 + gross_ret).cumprod()
    net_curve = (1 + net_ret).cumprod()
    bench_curve = (1 + bench_ret).cumprod()

    fig, axes = plt.subplots(2, 1, figsize=(12, 8),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.3, alpha=0.6,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {cost_round_trip_pips:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.plot(bench_curve.index, bench_curve.values, color="gray", ls="--", lw=1,
            label=f"Passive long {pair} (Sharpe {s_bench['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #{number} — Δ({base_ccy} 2Y − {quote_ccy} 2Y) → next-day {pair}\n"
        f"{first_valid.strftime('%Y-%m-%d')} to {end}  ·  {len(net_ret):,} daily obs  ·  net of {cost_round_trip_pips:.0f} pips RT"
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
    fname = f"strategy_{number:02d}_{base_ccy.lower()}_{quote_ccy.lower()}_2y_diff_{pair.lower()}.png"
    out = REPORTS / fname
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    return dict(net=s_net, gross=s_gross, benchmark=s_bench,
                n_trades=n_trades, cost_drag=cost_drag,
                pair=pair, base=base_ccy, quote=quote_ccy)
