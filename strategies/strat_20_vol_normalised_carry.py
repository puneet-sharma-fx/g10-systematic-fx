"""
Strategy #20 — Classical vol-normalised carry (G10, monthly rebalance)

Implementation of the Dupuy (2021) "Risk-Adjusted Return Managed Carry Trade"
specification on G10 FX. This is the canonical *level-based* carry signal,
distinct from the *change-based* d_diff signal used in Strategies #1–#18.

Signal:
    rate_diff[pair, t]     = rate_base[t] − rate_quote[t]            # LEVEL, not change
    realised_vol[pair, t]  = 30-day rolling std of FX return × √252  # annualised
    score[pair, t]         = rate_diff[pair, t] / realised_vol[pair, t]

Rebalance: end of each business month.
Position:  rank all 8 G10 pairs by score; long top-2, short bottom-2; ±1/2 each.
Hold:      1 month until next rebalance.
Cost:      5 pips round-trip per unit of turnover.

Reference: Dupuy, P. (2021). "Risk-Adjusted Return Managed Carry Trade",
Journal of Banking & Finance. G10 raw carry SR 0.76 → vol-normalised SR 1.07.
Skewness flips from −0.76 (carry crash tail) to +0.97.
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

# ── Parameters ────────────────────────────────────────────────────────────────
START                  = "2010-01-04"
END                    = "2024-12-31"
COST_ROUND_TRIP_PIPS   = 5.0
TRADING_DAYS           = 252
MONTHS_PER_YEAR        = 12

VOL_WINDOW_DAYS        = 30        # Dupuy spec — 30-day realised vol
N_LONG                 = 2         # top-2 pairs by carry score
N_SHORT                = 2         # bottom-2 pairs by carry score
LEG_WEIGHT             = 1.0 / (N_LONG + N_SHORT)   # equal weight per position

# Universe: (pair, base_ccy, quote_ccy, pip_size)
# 7 G10 pairs with available TVC 2Y yield data (NOK excluded — no TVC data)
PAIRS = [
    ("EURUSD", "EU", "US", 0.0001),
    ("GBPUSD", "GB", "US", 0.0001),
    ("AUDUSD", "AU", "US", 0.0001),
    ("NZDUSD", "NZ", "US", 0.0001),
    ("USDJPY", "US", "JP", 0.01),
    ("USDCAD", "US", "CA", 0.0001),
    ("USDCHF", "US", "CH", 0.0001),
]


def _load_yields() -> pd.DataFrame:
    return pd.read_csv(YIELDS_CSV, index_col=0, parse_dates=True)


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    return df["Close"].squeeze().dropna()


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #20 — Classical vol-normalised carry (G10, monthly)")
    print(f"  Signal      : (rate_base − rate_quote) / {VOL_WINDOW_DAYS}d realised FX vol")
    print(f"  Universe    : {len(PAIRS)} G10 pairs")
    print(f"  Rebalance   : monthly (end-of-business-month)")
    print(f"  Position    : long top-{N_LONG} / short bottom-{N_SHORT}, ±{LEG_WEIGHT:.3f} each")
    print(f"  Cost        : {COST_ROUND_TRIP_PIPS} pips RT\n")

    yields = _load_yields()
    pair_names = [p[0] for p in PAIRS]
    pip_by_pair = {p[0]: p[3] for p in PAIRS}
    print("Fetching FX prices...")
    fx_close = {}
    for pair, *_ in PAIRS:
        fx_close[pair] = _fetch_fx(pair)
    print(f"  {len(PAIRS)} pairs fetched\n")

    # Daily aligned index (business days)
    idx_daily = pd.bdate_range(start=START, end=END)
    fx_daily = pd.DataFrame({p: fx_close[p].reindex(idx_daily).ffill()
                             for p in pair_names})

    # ── Per-pair: rate_diff (LEVEL), realised vol, score ───────────────────
    rate_diff = pd.DataFrame(index=idx_daily, columns=pair_names, dtype=float)
    for pair, base, quote, _pip in PAIRS:
        base_y  = yields[base].reindex(idx_daily).ffill()
        quote_y = yields[quote].reindex(idx_daily).ffill()
        rate_diff[pair] = base_y - quote_y     # ← LEVEL, NOT change

    fx_ret_daily = fx_daily.pct_change()
    realised_vol = fx_ret_daily.rolling(VOL_WINDOW_DAYS, min_periods=20).std() * np.sqrt(TRADING_DAYS)

    score = rate_diff / realised_vol.replace(0, np.nan)

    # ── Resample to month-end for the rebalance dates ──────────────────────
    score_monthly = score.resample("BME").last()
    fx_monthly = fx_daily.resample("BME").last()

    # ── Build monthly portfolio weights ────────────────────────────────────
    weights_monthly = pd.DataFrame(0.0, index=score_monthly.index, columns=pair_names)

    for t in score_monthly.index:
        s = score_monthly.loc[t].dropna()
        if len(s) < N_LONG + N_SHORT:
            continue
        ranked = s.sort_values(ascending=False)
        for p in ranked.head(N_LONG).index:
            weights_monthly.loc[t, p] = +LEG_WEIGHT
        for p in ranked.tail(N_SHORT).index:
            weights_monthly.loc[t, p] = -LEG_WEIGHT

    # Position applies to NEXT month's return
    positions_monthly = weights_monthly.shift(1).fillna(0)

    # Monthly returns per pair (close-to-close)
    pair_ret_monthly = fx_monthly.pct_change()
    gross_pair = positions_monthly * pair_ret_monthly
    gross_port_monthly = gross_pair.sum(axis=1)

    # Cost: turnover × (2.5 pips / spot)
    cost_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    turnover = weights_monthly.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=weights_monthly.index, columns=pair_names, dtype=float)
    for pair, *_ in PAIRS:
        cost_per_pair[pair] = turnover[pair] * (cost_unit_pips * pip_by_pair[pair]) / fx_monthly[pair]
    cost_total_monthly = cost_per_pair.sum(axis=1)

    net_port_monthly = (gross_port_monthly - cost_total_monthly).dropna()

    # Drop early months when realised vol not yet populated
    first_valid_score = score.dropna(how="all").index.min()
    burn_in_start = first_valid_score + pd.DateOffset(months=2)
    net_port_monthly = net_port_monthly[net_port_monthly.index >= burn_in_start]
    gross_port_monthly = gross_port_monthly.reindex(net_port_monthly.index)
    cost_total_monthly = cost_total_monthly.reindex(net_port_monthly.index)

    # ── Metrics (annualised on 12 periods/year) ─────────────────────────────
    def stats(returns: pd.Series) -> dict:
        ann_ret = float(returns.mean() * MONTHS_PER_YEAR)
        ann_vol = float(returns.std() * np.sqrt(MONTHS_PER_YEAR))
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        curve = (1 + returns).cumprod()
        max_dd = float(((curve / curve.cummax()) - 1).min())
        hit = float((returns > 0).mean())
        return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=max_dd, hit=hit, cum=float(curve.iloc[-1] - 1))

    s_gross = stats(gross_port_monthly)
    s_net = stats(net_port_monthly)
    calmar = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] != 0 else float("nan")

    # Skewness (Dupuy's key finding: VN carry has +ve skew)
    monthly_skew = float(net_port_monthly.skew())

    # Trade stats
    avg_monthly_turnover = float(turnover.sum(axis=1).mean())
    n_rebalances = int((turnover.sum(axis=1) > 0).sum())
    cum_cost_drag = float(cost_total_monthly.sum())

    print("=" * 70)
    print(f"  Strategy #20 — Classical vol-normalised carry")
    print("=" * 70)
    print(f"  Backtest range       : {net_port_monthly.index[0].date()} → {net_port_monthly.index[-1].date()}")
    print(f"  Monthly obs          : {len(net_port_monthly):,}")
    print(f"  Rebalances           : {n_rebalances:,}")
    print(f"  Avg monthly Σ|Δw|    : {avg_monthly_turnover:.3f}")
    print(f"  Cumulative cost drag : {cum_cost_drag*100:.2f}%")
    print()
    print(f"  {'':<18} {'GROSS':>10} {'NET':>10}")
    print(f"  {'Ann. Return':<18} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}%")
    print(f"  {'Ann. Vol':<18} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}%")
    print(f"  {'Sharpe':<18} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f}")
    print(f"  {'Max Drawdown':<18} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}%")
    print(f"  {'Cumulative':<18} {s_gross['cum']*100:>9.2f}% {s_net['cum']*100:>9.2f}%")
    print(f"  {'Hit Rate (monthly)':<18} {s_gross['hit']*100:>9.2f}% {s_net['hit']*100:>9.2f}%")
    print(f"  {'Calmar (net)':<18} {' ':>10} {calmar:>10.2f}")
    print(f"  {'Monthly skew (net)':<18} {' ':>10} {monthly_skew:>10.2f}")
    print("=" * 70)
    print(f"\n  Dupuy 2021 reference: raw carry SR 0.76 → VN carry SR 1.07 on G10")
    print(f"  This run net Sharpe: {s_net['sharpe']:.2f}")
    if monthly_skew > 0:
        print(f"  ✓ Monthly skew +{monthly_skew:.2f} — confirms Dupuy's tail-risk benefit "
              f"(raw carry typically has negative skew)")
    else:
        print(f"  ⚠ Monthly skew {monthly_skew:.2f} — does NOT confirm Dupuy's tail-risk benefit")

    # Plot
    gross_curve = (1 + gross_port_monthly).cumprod()
    net_curve = (1 + net_port_monthly).cumprod()
    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.3, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #20 — Classical vol-normalised carry (G10, monthly)\n"
        f"{net_port_monthly.index[0].strftime('%Y-%m')} to {END[:7]}  ·  "
        f"long top-{N_LONG} / short bottom-{N_SHORT} by `(rate_diff)/vol`  ·  "
        f"net Sharpe {s_net['sharpe']:.2f}, monthly skew {monthly_skew:+.2f}"
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
    plot_out = REPORTS / "strategy_20_vol_normalised_carry.png"
    plt.savefig(plot_out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port_monthly.index)
        out_df["gross_return"] = gross_port_monthly
        out_df["cost"] = cost_total_monthly
        out_df["net_return"] = net_port_monthly
        out_df["cum_gross"] = gross_curve
        out_df["cum_net"] = net_curve
        for pair in pair_names:
            out_df[f"weight_{pair}"] = weights_monthly[pair].reindex(net_port_monthly.index)
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")

    return dict(net=s_net, gross=s_gross, calmar=calmar,
                monthly_skew=monthly_skew,
                n_rebalances=n_rebalances, n_obs=len(net_port_monthly))


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_20_vol_normalised_carry_track_record.csv")
