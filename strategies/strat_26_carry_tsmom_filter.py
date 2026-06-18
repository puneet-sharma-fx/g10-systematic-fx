"""
Strategy #26 — Carry-TSMOM filter overlay on Strategy #20 (vol-normalised carry)

Applies Moskowitz-Ooi-Pedersen (2012, JFE) time-series momentum logic to the
carry FACTOR RETURN itself — not to the underlying FX spot price. The idea:
carry-trade unwinds (2008, 2015 CNY scare, 2022 BoJ pivot, Aug-2024 yen blow-up)
are persistent. Once carry starts losing, it keeps losing for months as carry
investors forcibly deleverage. A TSMOM filter on the carry return catches the
regime change and scales positions down.

Per the v2 research doc:
    carry_12m_return = carry_factor_return.rolling(12).sum()        # months
    scale[t]         = 1.0 if carry_12m_return[t-1] > 0 else 0.5    # soft filter
                       or 0.0 in the "hard off" variant
    new_position[t]  = scale[t] × original_position[t]

Run BOTH variants in this module so we can isolate the contribution of the
filter and the cost of going fully flat:
    #26a : Soft filter (scale = 0.5 when 12m trend is negative)
    #26b : Hard filter (scale = 0.0 when 12m trend is negative)

Base strategy: #20 (Classical vol-normalised carry, monthly).
    Net Sharpe 0.07, Ann return +0.44%, Max DD −20.85%, skew −0.07.

Comparison question: does the carry factor itself exhibit time-series
persistence in its drawdowns? If the filter rescues #20's flat Sharpe, the
post-2008 carry decay isn't quite as dead as #20 suggested — it's regime-
dependent and tradeable with a simple regime filter. If the filter doesn't
help, post-2008 carry is genuinely dead even with TSMOM regime conditioning.

Cost model: when scale changes, even unchanged signal weights become
turnover (e.g., scale 1.0 → 0.5 halves all positions, creating |Δw| = 0.5
per pair). We re-compute new turnover from new weights and pay 5 pips RT.

Implementation: reads #20's monthly weights + returns from CSV (no FX refetch),
applies the filter, recomputes monthly cost from new turnover.

References:
    - Moskowitz, Ooi, Pedersen (2012). "Time Series Momentum", JFE 104(2).
    - Hurst, Ooi, Pedersen (2017). "A Century of Evidence on Trend-Following
      Investing", J. of Portfolio Management 44(1).
    - v2 research doc, section 1, "Carry-TSMOM Filter".
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.WARNING)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"
TRACK = REPO / "live" / "track_record"

BASE_CSV = TRACK / "strategy_20_vol_normalised_carry_track_record.csv"

# ── Strategy parameters ──────────────────────────────────────────────────────
TSMOM_LOOKBACK_MONTHS = 12              # canonical MOP 2012 window
COST_ROUND_TRIP_PIPS  = 5.0             # match #20
MONTHS_PER_YEAR       = 12

# Pip size by pair, matching #20's universe
PIP_BY_PAIR = {
    "EURUSD": 0.0001, "GBPUSD": 0.0001, "AUDUSD": 0.0001, "NZDUSD": 0.0001,
    "USDJPY": 0.01,   "USDCAD": 0.0001, "USDCHF": 0.0001,
}


def _stats_monthly(returns: pd.Series) -> dict:
    """Annualised stats on monthly-return series."""
    returns = returns.dropna()
    if len(returns) == 0:
        return dict(n_months=0, ann_ret=0.0, ann_vol=0.0, sharpe=0.0,
                    max_dd=0.0, hit=0.0, skew=0.0, cum=0.0)
    ann_ret = float(returns.mean() * MONTHS_PER_YEAR)
    ann_vol = float(returns.std() * np.sqrt(MONTHS_PER_YEAR))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew()) if returns.std() > 0 else 0.0
    return dict(n_months=len(returns), ann_ret=ann_ret, ann_vol=ann_vol,
                sharpe=sharpe, max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1))


def run_variant(scale_when_negative: float, label: str, base: pd.DataFrame) -> dict:
    """Apply the TSMOM filter with a given 'scale when 12m return < 0' value."""
    print(f"\nStrategy #26{label} — Carry-TSMOM filter on #20 "
          f"({TSMOM_LOOKBACK_MONTHS}m lookback, scale = "
          f"{1.0:.1f}/{scale_when_negative:.1f})")
    print(f"  Filter rule  : scale = 1.0 if trailing-{TSMOM_LOOKBACK_MONTHS}m carry > 0, "
          f"else {scale_when_negative:.1f}")
    print(f"  Cost         : {COST_ROUND_TRIP_PIPS} pips RT on new turnover\n")

    # ── Build the scale series ─────────────────────────────────────────────
    # trailing_12m[t] uses #20's net returns through month t (known by end of t).
    # Scale applied to weights for next month: shift(1) so filtered_return[t]
    # uses scale that was determined at end of month t-1.
    trailing_12m = base["net_return"].rolling(TSMOM_LOOKBACK_MONTHS,
                                              min_periods=TSMOM_LOOKBACK_MONTHS).sum()
    scale_raw = np.where(trailing_12m > 0, 1.0, scale_when_negative)
    scale_raw = pd.Series(scale_raw, index=base.index)
    scale = scale_raw.shift(1).fillna(1.0)   # apply to next month — no look-ahead

    # ── New weights, new gross return, new cost ────────────────────────────
    weight_cols = [c for c in base.columns if c.startswith("weight_")]
    weights_old = base[weight_cols].copy()
    weights_new = weights_old.mul(scale, axis=0)

    # Gross return scales linearly: new_gross = scale_lag × old_gross
    # (since portfolio_return = sum(weight × pair_return) and weight is scaled
    # by a constant factor each month)
    gross_old = base["gross_return"]
    gross_new = gross_old * scale

    # Cost: recompute from new turnover
    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    new_turnover = weights_new.diff().abs().fillna(0)
    # Approximate cost in return terms: turnover × half-spread / spot
    # We don't have spot in the CSV but #20's cost was tiny (monthly rebalance)
    # so use a flat per-pair scaling. For non-JPY pairs the half-spread of 2.5
    # pips at typical spot ~1.10 = 2.27 bps; for USDJPY at ~110 it's 2.27 bps too.
    # So a uniform 2.27 bps per unit of turnover is a fair approximation.
    cost_per_unit_bps = 2.27e-4
    new_cost = new_turnover.sum(axis=1) * cost_per_unit_bps

    net_new = (gross_new - new_cost).dropna()
    base_net = base["net_return"].dropna()

    # ── Metrics ────────────────────────────────────────────────────────────
    s_base = _stats_monthly(base_net)
    s_filt = _stats_monthly(net_new)
    calmar_base = s_base["ann_ret"] / abs(s_base["max_dd"]) if s_base["max_dd"] else float("nan")
    calmar_filt = s_filt["ann_ret"] / abs(s_filt["max_dd"]) if s_filt["max_dd"] else float("nan")

    # Tracking error and information ratio
    common_idx = base_net.index.intersection(net_new.index)
    active_ret = (net_new - base_net).loc[common_idx]
    tracking_err = float(active_ret.std() * np.sqrt(MONTHS_PER_YEAR))
    ir = float(active_ret.mean() * MONTHS_PER_YEAR / tracking_err) if tracking_err > 0 else 0.0

    # Filter activity
    n_filter_active = int((scale < 1.0).sum())
    n_filter_off    = int((scale == 0.0).sum())
    mean_scale      = float(scale.mean())

    # ── Print ──────────────────────────────────────────────────────────────
    print(f"  {'METRIC':<22} {'#20 BASE':>14} {'#26{label} FILTERED':>20} {'Δ':>10}".replace(
        "{label}", label))
    print(f"  {'Net Sharpe':<22} {s_base['sharpe']:>14.2f} {s_filt['sharpe']:>20.2f} "
          f"{s_filt['sharpe']-s_base['sharpe']:>+10.2f}")
    print(f"  {'Ann. Return':<22} {s_base['ann_ret']*100:>13.2f}% {s_filt['ann_ret']*100:>19.2f}% "
          f"{(s_filt['ann_ret']-s_base['ann_ret'])*100:>+9.2f}%")
    print(f"  {'Ann. Vol':<22} {s_base['ann_vol']*100:>13.2f}% {s_filt['ann_vol']*100:>19.2f}% "
          f"{(s_filt['ann_vol']-s_base['ann_vol'])*100:>+9.2f}%")
    print(f"  {'Max Drawdown':<22} {s_base['max_dd']*100:>13.2f}% {s_filt['max_dd']*100:>19.2f}% "
          f"{(s_filt['max_dd']-s_base['max_dd'])*100:>+9.2f}%")
    print(f"  {'Calmar':<22} {calmar_base:>14.2f} {calmar_filt:>20.2f} "
          f"{calmar_filt-calmar_base:>+10.2f}")
    print(f"  {'Monthly Skew':<22} {s_base['skew']:>14.2f} {s_filt['skew']:>20.2f} "
          f"{s_filt['skew']-s_base['skew']:>+10.2f}")
    print(f"  {'Monthly Hit Rate':<22} {s_base['hit']*100:>13.2f}% {s_filt['hit']*100:>19.2f}% "
          f"{(s_filt['hit']-s_base['hit'])*100:>+9.2f}%")
    print(f"  {'Cumulative':<22} {s_base['cum']*100:>13.2f}% {s_filt['cum']*100:>19.2f}% "
          f"{(s_filt['cum']-s_base['cum'])*100:>+9.2f}%")
    print(f"  {'Tracking error (ann)':<22} {'':<14} {tracking_err*100:>19.2f}%")
    print(f"  {'Information ratio':<22} {'':<14} {ir:>20.2f}")
    print(f"  {'Months filter active':<22} {'':<14} {n_filter_active:>20}  "
          f"({n_filter_active/len(scale)*100:.1f}% of sample)")
    print(f"  {'Months fully flat':<22} {'':<14} {n_filter_off:>20}  "
          f"({n_filter_off/len(scale)*100:.1f}% of sample)")
    print(f"  {'Mean monthly scalar':<22} {'':<14} {mean_scale:>20.2f}")

    return dict(base=s_base, filtered=s_filt,
                calmar_base=calmar_base, calmar_filt=calmar_filt,
                tracking_err=tracking_err, ir=ir,
                scale=scale, net_new=net_new, base_net=base_net,
                weights_new=weights_new, gross_new=gross_new, new_cost=new_cost,
                n_filter_active=n_filter_active, n_filter_off=n_filter_off,
                mean_scale=mean_scale,
                trailing_12m=trailing_12m)


def main():
    print(f"\nReading #20 base track record from {BASE_CSV.relative_to(REPO)}")
    base = pd.read_csv(BASE_CSV, parse_dates=["date"], index_col="date")
    print(f"  {len(base)} months, {base.index[0].date()} → {base.index[-1].date()}")

    res_soft = run_variant(0.5, "a", base)
    res_hard = run_variant(0.0, "b", base)

    print("\n" + "=" * 90)
    print("  HEAD-TO-HEAD COMPARISON")
    print("=" * 90)
    print(f"  {'Metric':<22} {'#20 base':>14} {'#26a soft (0.5)':>18} {'#26b hard (0.0)':>18}")
    print(f"  {'Net Sharpe':<22} {res_soft['base']['sharpe']:>14.2f} "
          f"{res_soft['filtered']['sharpe']:>18.2f} {res_hard['filtered']['sharpe']:>18.2f}")
    print(f"  {'Ann. Return':<22} {res_soft['base']['ann_ret']*100:>13.2f}% "
          f"{res_soft['filtered']['ann_ret']*100:>17.2f}% {res_hard['filtered']['ann_ret']*100:>17.2f}%")
    print(f"  {'Ann. Vol':<22} {res_soft['base']['ann_vol']*100:>13.2f}% "
          f"{res_soft['filtered']['ann_vol']*100:>17.2f}% {res_hard['filtered']['ann_vol']*100:>17.2f}%")
    print(f"  {'Max Drawdown':<22} {res_soft['base']['max_dd']*100:>13.2f}% "
          f"{res_soft['filtered']['max_dd']*100:>17.2f}% {res_hard['filtered']['max_dd']*100:>17.2f}%")
    print(f"  {'Calmar':<22} {res_soft['calmar_base']:>14.2f} "
          f"{res_soft['calmar_filt']:>18.2f} {res_hard['calmar_filt']:>18.2f}")
    print(f"  {'Monthly Skew':<22} {res_soft['base']['skew']:>14.2f} "
          f"{res_soft['filtered']['skew']:>18.2f} {res_hard['filtered']['skew']:>18.2f}")
    print(f"  {'Tracking error':<22} {'-':>14} "
          f"{res_soft['tracking_err']*100:>17.2f}% {res_hard['tracking_err']*100:>17.2f}%")
    print(f"  {'Information ratio':<22} {'-':>14} "
          f"{res_soft['ir']:>18.2f} {res_hard['ir']:>18.2f}")
    print(f"  {'Months filter active':<22} {'-':>14} "
          f"{res_soft['n_filter_active']:>18} {res_hard['n_filter_active']:>18}")
    print(f"  {'Months fully flat':<22} {'-':>14} "
          f"{res_soft['n_filter_off']:>18} {res_hard['n_filter_off']:>18}")
    print(f"  {'Mean monthly scalar':<22} {'-':>14} "
          f"{res_soft['mean_scale']:>18.2f} {res_hard['mean_scale']:>18.2f}")
    print("=" * 90)

    # ── Plot ───────────────────────────────────────────────────────────────
    base_curve = (1 + res_soft["base_net"]).cumprod()
    soft_curve = (1 + res_soft["net_new"]).cumprod()
    hard_curve = (1 + res_hard["net_new"]).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(base_curve.index, base_curve.values, color="#1f77b4", lw=1.4, alpha=0.8,
            label=f"#20 base (Sharpe {res_soft['base']['sharpe']:.2f}, MaxDD {res_soft['base']['max_dd']*100:.1f}%)")
    ax.plot(soft_curve.index, soft_curve.values, color="#2ca02c", lw=2,
            label=f"#26a soft (Sharpe {res_soft['filtered']['sharpe']:.2f}, MaxDD {res_soft['filtered']['max_dd']*100:.1f}%, IR {res_soft['ir']:+.2f})")
    ax.plot(hard_curve.index, hard_curve.values, color="#9467bd", lw=2,
            label=f"#26b hard (Sharpe {res_hard['filtered']['sharpe']:.2f}, MaxDD {res_hard['filtered']['max_dd']*100:.1f}%, IR {res_hard['ir']:+.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #26 — Carry-TSMOM filter overlay on #20 (vol-normalised carry)\n"
        f"{base.index[0].date()} → {base.index[-1].date()}  ·  "
        f"{TSMOM_LOOKBACK_MONTHS}-month lookback  ·  monthly rebalance"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    base_dd = (base_curve / base_curve.cummax()) - 1
    soft_dd = (soft_curve / soft_curve.cummax()) - 1
    hard_dd = (hard_curve / hard_curve.cummax()) - 1
    ax.fill_between(base_dd.index, base_dd.values, 0, color="#1f77b4", alpha=0.30, label="#20 DD")
    ax.fill_between(soft_dd.index, soft_dd.values, 0, color="#2ca02c", alpha=0.40, label="#26a DD")
    ax.fill_between(hard_dd.index, hard_dd.values, 0, color="#9467bd", alpha=0.40, label="#26b DD")
    ax.set_ylabel("Drawdown")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    # Both scale series on the same panel for comparison
    ax.step(res_soft["scale"].index, res_soft["scale"].values,
            color="#2ca02c", lw=1.2, where="post", label="#26a soft scale")
    ax.step(res_hard["scale"].index, res_hard["scale"].values,
            color="#9467bd", lw=1.2, where="post", label="#26b hard scale", alpha=0.7)
    ax.set_ylabel("Filter scalar")
    ax.set_xlabel("Date")
    ax.set_ylim(-0.05, 1.10)
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_26_carry_tsmom_filter.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # ── CSV outputs ────────────────────────────────────────────────────────
    for variant, res in [("a", res_soft), ("b", res_hard)]:
        out_df = pd.DataFrame(index=base.index)
        out_df["trailing_12m_base_ret"] = res["trailing_12m"]
        out_df["scale"]                 = res["scale"]
        out_df["base_gross_return"]     = base["gross_return"]
        out_df["base_net_return"]       = base["net_return"]
        out_df["filt_gross_return"]     = res["gross_new"]
        out_df["filt_cost"]             = res["new_cost"]
        out_df["filt_net_return"]       = res["gross_new"] - res["new_cost"]
        out_df["cum_base"]              = (1 + base["net_return"].fillna(0)).cumprod()
        out_df["cum_filt"]              = (1 + (res["gross_new"] - res["new_cost"]).fillna(0)).cumprod()
        out_df.index.name = "date"
        csv_out = TRACK / f"strategy_26{variant}_carry_tsmom_filter_track_record.csv"
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved: {csv_out.relative_to(REPO)}  ({len(out_df)} rows)")


if __name__ == "__main__":
    main()
