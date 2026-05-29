"""
Strategy #10 — Vol-targeted G10 2Y rate-differential portfolio

Converts the per-pair signal from Strategies #1-#8 into a single portfolio with:
  - Continuous, vol-adjusted scoring (not binary ±1)
  - Cross-sectional z-scoring across the universe each day
  - Position sizing that targets a fixed portfolio volatility
  - Per-pair concentration caps
  - USDCHF excluded (the standalone strategy failed)
  - USDJPY excluded by default (brutal -59% standalone DD)

Signal:
  d_diff[pair, t]     = Δ(base_2Y - quote_2Y) on day t
  fx_vol[pair, t]     = 21d realised vol of pair's daily return, annualised
  score[pair, t]      = d_diff / fx_vol            (vol-adjusted signal)
  z[pair, t]          = cross-section z-score across active pairs on day t
  z_clipped[pair, t]  = clip(z, -CLIP, +CLIP)

Sizing (inverse-vol weighting, scaled to target portfolio vol):
  k[t]          = TARGET_VOL / sqrt(sum_pair(z_clipped^2)) on day t
  raw_w[pair,t] = z_clipped[pair,t] * k[t] / fx_vol[pair,t]
  weight[pair,t]= clip(raw_w, -MAX_PER_PAIR, +MAX_PER_PAIR)

Returns (net of 5 pips round-trip cost on actual turnover):
  pnl[t] = sum_pair(weight[pair, t-1] * fx_return[pair, t]) - cost[t]

Universe (configurable):
  Default core 4: EURUSD, GBPUSD, AUDUSD, USDCAD
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
YIELDS_CSV = REPO / "data" / "raw" / "tvc_2y_yields.csv"

# ── Strategy parameters ──────────────────────────────────────────────────────
TARGET_VOL          = 0.10      # 10% annualised target portfolio vol
MAX_PER_PAIR        = 0.30      # max ±30% gross weight per pair
Z_CLIP              = 2.0       # cap absolute z-score at this many sigmas
VOL_LOOKBACK_DAYS   = 21        # 21-day rolling realised vol window
COST_ROUND_TRIP_PIPS = 5.0      # total bid-ask round-trip in pips
TRADING_DAYS        = 252
START               = "2010-01-04"
END                 = "2024-12-31"

# Universe: (pair, base_ccy, quote_ccy, pip_size)
UNIVERSES = {
    "core4": [
        ("EURUSD", "EU", "US", 0.0001),
        ("GBPUSD", "GB", "US", 0.0001),
        ("AUDUSD", "AU", "US", 0.0001),
        ("USDCAD", "US", "CA", 0.0001),
    ],
    # Variants to try later — wired but not run by default
    "core4_plus_nzd":   None,   # adds NZDUSD
    "core4_plus_sek":   None,   # adds USDSEK (cost model caveat)
    "core4_plus_jpy":   None,   # adds USDJPY with concentration cap
}


def _load_yields() -> pd.DataFrame:
    df = pd.read_csv(YIELDS_CSV, index_col=0, parse_dates=True)
    return df


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    s.name = pair
    return s.dropna()


def run(universe_name: str = "core4", csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #10 — vol-targeted G10 rate-differential portfolio")
    print(f"  Universe   : {universe_name}")
    print(f"  Target vol : {TARGET_VOL:.0%} annualised")
    print(f"  Max per pair: ±{MAX_PER_PAIR:.0%}")
    print(f"  Cost       : {COST_ROUND_TRIP_PIPS} pips round-trip\n")

    pairs = UNIVERSES[universe_name]
    if pairs is None:
        raise NotImplementedError(f"Universe '{universe_name}' not configured")
    pair_names = [p[0] for p in pairs]

    yields = _load_yields()
    print(f"  Fetching FX for {len(pairs)} pairs...")
    fx_dict = {name: _fetch_fx(name) for name, *_ in pairs}

    idx = pd.bdate_range(start=START, end=END)

    # ── Per-pair: rate diff, d_diff, return, realised vol, score ────────────
    d_diff   = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    fx_ret   = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    fx_vol   = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    fx_close = pd.DataFrame(index=idx, columns=pair_names, dtype=float)

    first_valids = []
    for name, base, quote, _pip in pairs:
        if base not in yields.columns or quote not in yields.columns:
            raise KeyError(f"Yield missing for {base} or {quote}")
        base_2y = yields[base].reindex(idx).ffill()
        quote_2y = yields[quote].reindex(idx).ffill()
        px = fx_dict[name].reindex(idx).ffill()

        d_diff[name]   = (base_2y - quote_2y).diff()
        fx_close[name] = px
        fx_ret[name]   = px.pct_change()
        fx_vol[name]   = fx_ret[name].rolling(VOL_LOOKBACK_DAYS, min_periods=10).std() * np.sqrt(TRADING_DAYS)

        first = max(base_2y.dropna().index.min(), quote_2y.dropna().index.min())
        first_valids.append(first)

    # Score: vol-adjusted signal per pair
    score = d_diff / fx_vol

    # Cross-section z-score across pairs each day
    cs_mean = score.mean(axis=1)
    cs_std  = score.std(axis=1).replace(0, np.nan)
    z = score.sub(cs_mean, axis=0).div(cs_std, axis=0)
    z_clipped = z.clip(lower=-Z_CLIP, upper=Z_CLIP)

    # ── Sizing: scale to target portfolio vol ──────────────────────────────
    # Assuming uncorrelated pairs:
    #   portfolio_var(t) = sum_i (w_i * sigma_i)^2
    # With w_i = z_clipped_i * k / sigma_i  →  w_i * sigma_i = z_clipped_i * k
    #   portfolio_var(t) = k^2 * sum_i z_clipped_i^2
    # Want sqrt(portfolio_var) = TARGET_VOL → k = TARGET_VOL / sqrt(sum_i z_clipped_i^2)
    z2_sum_per_day = (z_clipped ** 2).sum(axis=1).replace(0, np.nan)
    k = TARGET_VOL / np.sqrt(z2_sum_per_day)

    raw_w = z_clipped.div(fx_vol).mul(k, axis=0)
    weights = raw_w.clip(lower=-MAX_PER_PAIR, upper=MAX_PER_PAIR).fillna(0)

    # Apply tomorrow's position from today's signal
    weights = weights.shift(1).fillna(0)

    # Drop pre-burn-in (need both yields + vol estimate)
    burn_in_start = max(first_valids) + pd.Timedelta(days=VOL_LOOKBACK_DAYS * 2)
    weights = weights[weights.index >= burn_in_start]
    fx_ret = fx_ret.reindex(weights.index)
    fx_close = fx_close.reindex(weights.index)

    # ── P&L and costs ──────────────────────────────────────────────────────
    gross_pair_ret = weights * fx_ret

    # Cost per pair: turnover * (2.5 pips / spot)
    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    pip_by_pair = {p[0]: p[3] for p in pairs}
    turnover = weights.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=weights.index, columns=pair_names, dtype=float)
    for name in pair_names:
        cost_per_pair[name] = turnover[name] * (cost_per_unit_pips * pip_by_pair[name]) / fx_close[name]
    cost_total = cost_per_pair.sum(axis=1)

    gross_port = gross_pair_ret.sum(axis=1)
    net_port = (gross_port - cost_total).dropna()

    # ── Metrics ────────────────────────────────────────────────────────────
    def stats(returns: pd.Series) -> dict:
        ann_ret = returns.mean() * TRADING_DAYS
        ann_vol = returns.std() * np.sqrt(TRADING_DAYS)
        sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve   = (1 + returns).cumprod()
        max_dd  = float(((curve / curve.cummax()) - 1).min())
        hit     = float((returns > 0).mean())
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=float(curve.iloc[-1] - 1))

    s_gross = stats(gross_port.loc[net_port.index])
    s_net   = stats(net_port)

    # Calmar
    calmar = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] != 0 else float("nan")

    # Turnover stats
    avg_turnover_per_day = turnover.sum(axis=1).mean()
    cum_cost_drag = float(cost_total.sum())

    # ── Print summary ──────────────────────────────────────────────────────
    print("=" * 65)
    print(f"  Strategy #10 — portfolio ({universe_name})")
    print("=" * 65)
    print(f"  Pairs traded         : {', '.join(pair_names)}")
    print(f"  Observations         : {len(net_port):,}")
    print(f"  Avg daily Σ|Δw|      : {avg_turnover_per_day:.3f}")
    print(f"  Cumulative cost drag : {cum_cost_drag*100:.1f}%")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}%")
    print(f"  {'Hit Rate':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}%")
    print(f"  {'Calmar (net)':<18} {' ':>10} {calmar:>10.2f}")
    print("=" * 65)

    # ── Plot ───────────────────────────────────────────────────────────────
    gross_curve = (1 + gross_port.loc[net_port.index]).cumprod()
    net_curve = (1 + net_port).cumprod()
    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f}, vol {s_gross['ann_vol']*100:.1f}%)")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f}, vol {s_net['ann_vol']*100:.1f}%)")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #10 — vol-targeted G10 rate-diff portfolio ({universe_name})\n"
        f"{net_port.index[0].strftime('%Y-%m-%d')} to {END}  ·  "
        f"{len(net_port):,} daily obs  ·  target vol {TARGET_VOL:.0%}, max/pair ±{MAX_PER_PAIR:.0%}, "
        f"net of {COST_ROUND_TRIP_PIPS:.0f} pips RT"
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
    plot_out = REPORTS / f"strategy_10_g10_rate_diff_portfolio_{universe_name}.png"
    plt.savefig(plot_out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_out.relative_to(REPO)}")

    # ── Optional CSV time series ───────────────────────────────────────────
    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"] = cost_total.loc[net_port.index]
        out_df["net_return"] = net_port
        out_df["cum_gross"] = gross_curve
        out_df["cum_net"] = net_curve
        for name in pair_names:
            out_df[f"weight_{name}"] = weights[name].loc[net_port.index]
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(
        net=s_net, gross=s_gross,
        calmar=calmar,
        avg_turnover=avg_turnover_per_day,
        cost_drag=cum_cost_drag,
        n_obs=len(net_port),
        universe=universe_name,
        net_ret_series=net_port,
    )


if __name__ == "__main__":
    run(
        universe_name="core4",
        csv_out=TRACK / "strategy_10_portfolio_core4_track_record.csv",
    )
