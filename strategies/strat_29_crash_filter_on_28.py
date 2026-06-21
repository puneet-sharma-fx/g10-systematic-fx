"""
Strategy #29 — Carry-crash-filter-style overlay on Strategy #28 (MA crossover on
commodities + crypto)

Takes the VIX + self-momentum crash scalar built for Strategy #22 (originally
applied to the equal-weight rate-diff portfolio #18) and re-applies it to a
DIFFERENT BASE: Strategy #28, the 20/50 MA crossover on commodities + crypto.

Why this is worth doing:
  - #22 applied the same overlay to #18, but #18 itself was later flagged as a
    timing-artefact (the rate-diff family is suspect). So #22's positive overlay
    finding sits on top of a base that isn't deployable as-is.
  - #28, by contrast, is a real trend-following strategy with daily skew +0.50
    and proper structural shape. The Hiking 2022-24 sub-period analysis showed
    #28 had a brutal −26.84% MaxDD even though it earned positive Sharpe over
    that full regime.
  - A crash filter should *trim* that 2022-24 drawdown if the worst days
    correlated with VIX spikes or with the strategy's own drawdown momentum.
  - If the filter helps here, it's a genuine deployable risk overlay on a
    genuine deployable strategy — clean independent validation.
  - If it doesn't help (e.g., the 2022-24 trend-following losses happened
    during low-VIX periods), that's also informative — the overlay's value is
    base-specific.

Filter spec (identical to #22 — no parameter retuning, honest replication):
  - VIX scalar      : 1.0 if VIX ≤ 20; 0.0 if VIX ≥ 40; linear in between
  - Self-momentum   : 0.5 when trailing-20d base return is < −1σ of trailing
                      252d (i.e., the strategy is in a recent drawdown);
                      otherwise 1.0
  - Combined scalar : VIX_scale × MOM_scale, clipped to [0, 1]
  - Lag             : 1 day, no look-ahead (scale[t] is determined at end of
                      day t-1 and applied to day t's positions)
  - Cost recomputed from the NEW turnover that scaling induces — when scale
    changes from 1.0 to 0.5, even unchanged signal weights create turnover.

Outputs the same overlay-specific metrics introduced for #22:
  - Tracking error (annualised σ of active return)
  - Information ratio (active return / tracking error)
  - Cost of insurance (additional bps/yr from filter-induced turnover)
  - Drawdown duration (median, max, longest underwater stretch)
  - Conditional Sharpe when filter is materially binding (scale < 0.95)
  - Days fully flat (scale = 0) and partially scaled

Compare result to #22 (overlay on #18):
  #22: Sharpe 2.90 → 2.91 (Δ ≈ 0), vol −17%, MaxDD −7%, skew +0.05
  #29: Sharpe +0.42 → ?,                  vol ?,        MaxDD ?,    skew ?
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

BASE_CSV = TRACK / "strategy_28_ma_crossover_commodities_crypto_track_record.csv"

# ── Crash filter parameters (identical to #22, no retuning) ──────────────────
VIX_FULL_BELOW       = 20.0      # at VIX ≤ this, no scaling
VIX_FLAT_ABOVE       = 40.0      # at VIX ≥ this, fully flat
MOM_LOOKBACK_DAYS    = 20        # trailing-20d strategy return
MOM_REF_DAYS         = 252       # z-score reference window
MOM_Z_TRIGGER        = -1.0      # z-score threshold for momentum gate
MOM_SCALE_ON_TRIGGER = 0.5       # exposure scalar when momentum gate triggers

# Cost model — match #28's
COST_RT_BPS          = 10.0      # round-trip bps per leg
TRADING_DAYS         = 252
START                = "2010-01-04"
END                  = "2024-12-31"


def _stats(returns: pd.Series) -> dict:
    returns = returns.dropna()
    if len(returns) == 0:
        return dict(n_days=0, ann_ret=0.0, ann_vol=0.0, sharpe=0.0,
                    max_dd=0.0, hit=0.0, skew=0.0, sortino=0.0, cum=0.0)
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew()) if returns.std() > 0 else 0.0
    dvol    = float(returns[returns < 0].std() * np.sqrt(TRADING_DAYS))
    sortino = ann_ret / dvol if dvol > 0 else 0.0
    return dict(n_days=len(returns), ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                sortino=sortino, max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1))


def _drawdown_durations(returns: pd.Series) -> dict:
    """Return median, max, and time-underwater statistics for the equity curve."""
    curve = (1 + returns.fillna(0)).cumprod()
    peak  = curve.cummax()
    in_dd = (curve < peak).astype(int)
    # Identify drawdown spells (runs of consecutive in_dd days)
    spells = []
    cur = 0
    for v in in_dd:
        if v == 1:
            cur += 1
        else:
            if cur > 0:
                spells.append(cur)
            cur = 0
    if cur > 0:
        spells.append(cur)
    if not spells:
        return dict(median_dd_days=0, max_dd_days=0, pct_underwater=0.0)
    return dict(
        median_dd_days = int(np.median(spells)),
        max_dd_days    = int(np.max(spells)),
        pct_underwater = float(in_dd.mean()),
    )


def main():
    print(f"\nReading #28 base from {BASE_CSV.relative_to(REPO)}")
    base = pd.read_csv(BASE_CSV, parse_dates=["date"], index_col="date")
    print(f"  {len(base):,} rows, {base.index[0].date()} → {base.index[-1].date()}")

    weight_cols = sorted([c for c in base.columns if c.startswith("weight_")])
    instruments = [c.replace("weight_", "") for c in weight_cols]
    print(f"  Weight columns: {len(weight_cols)} — {', '.join(instruments)}")

    # ── Fetch VIX ──────────────────────────────────────────────────────────
    print("\nFetching VIX (^VIX) from yfinance...")
    raw_vix = yf.download("^VIX", start=START, end=END, auto_adjust=True, progress=False)
    vix = raw_vix["Close"].squeeze()
    vix.index = pd.to_datetime(vix.index)
    vix = vix.reindex(base.index).ffill()
    print(f"  VIX series : {len(vix):,} rows, range {float(vix.min()):.1f} → {float(vix.max()):.1f}")

    # ── Build the crash scalar (identical spec to #22) ─────────────────────
    # VIX scalar: linear from 1.0 at VIX_FULL_BELOW to 0.0 at VIX_FLAT_ABOVE
    vix_above = (vix - VIX_FULL_BELOW).clip(lower=0)
    range_span = VIX_FLAT_ABOVE - VIX_FULL_BELOW
    vix_scale = (1.0 - vix_above / range_span).clip(lower=0.0, upper=1.0)

    # Self-momentum gate on #28's base net return
    base_net = base["net_return"]
    tr20 = base_net.rolling(MOM_LOOKBACK_DAYS).sum()
    mu252 = tr20.rolling(MOM_REF_DAYS, min_periods=63).mean()
    sd252 = tr20.rolling(MOM_REF_DAYS, min_periods=63).std()
    z_tr20 = ((tr20 - mu252) / sd252).reindex(base.index).fillna(0)
    mom_scale = pd.Series(np.where(z_tr20 < MOM_Z_TRIGGER, MOM_SCALE_ON_TRIGGER, 1.0),
                          index=base.index)

    # Combined, lagged 1 day for no look-ahead
    scale_raw = (vix_scale * mom_scale).clip(lower=0.0, upper=1.0)
    scale = scale_raw.shift(1).fillna(1.0)

    # ── Apply scalar to #28's weights and recompute everything ─────────────
    weights_base = base[weight_cols]
    weights_filt = weights_base.mul(scale, axis=0)

    # Gross return scales linearly: gross_filt = scale × base_gross
    # (since portfolio_return = sum(weight × pair_return) and weights are
    # multiplied by a common scalar each day)
    gross_filt = base["gross_return"] * scale

    # Cost: recompute from filtered turnover
    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0  # 5 bps per unit of turnover
    turnover_filt = weights_filt.diff().abs().sum(axis=1).fillna(0)
    cost_filt = turnover_filt * cost_per_unit

    net_filt = (gross_filt - cost_filt).dropna()
    base_net_clean = base_net.dropna()

    # ── Metrics ────────────────────────────────────────────────────────────
    s_base = _stats(base_net_clean)
    s_filt = _stats(net_filt)
    calmar_base = s_base["ann_ret"] / abs(s_base["max_dd"]) if s_base["max_dd"] else float("nan")
    calmar_filt = s_filt["ann_ret"] / abs(s_filt["max_dd"]) if s_filt["max_dd"] else float("nan")

    # Overlay metrics
    common_idx = base_net_clean.index.intersection(net_filt.index)
    active_ret = (net_filt - base_net_clean).loc[common_idx]
    tracking_err = float(active_ret.std() * np.sqrt(TRADING_DAYS))
    ir = float(active_ret.mean() * TRADING_DAYS / tracking_err) if tracking_err > 0 else 0.0

    # Cost of insurance: additional cost in bps/yr from filter-induced turnover
    base_cost = base["cost"].sum()
    filt_cost_total = cost_filt.sum()
    n_years = len(base_net_clean) / TRADING_DAYS
    cost_of_insurance_bps = (filt_cost_total - base_cost) / n_years * 10000

    # Drawdown durations
    dd_base = _drawdown_durations(base_net_clean)
    dd_filt = _drawdown_durations(net_filt)

    # Conditional Sharpe on filter-binding days
    binding_mask = (scale.loc[common_idx] < 0.95)
    n_binding = int(binding_mask.sum())
    filt_binding = net_filt.loc[common_idx][binding_mask]
    base_binding = base_net_clean.loc[common_idx][binding_mask]
    if len(filt_binding) > 10:
        cond_filt_sharpe = float(filt_binding.mean() * TRADING_DAYS /
                                  (filt_binding.std() * np.sqrt(TRADING_DAYS))) if filt_binding.std() > 0 else 0.0
        cond_base_sharpe = float(base_binding.mean() * TRADING_DAYS /
                                  (base_binding.std() * np.sqrt(TRADING_DAYS))) if base_binding.std() > 0 else 0.0
    else:
        cond_filt_sharpe = cond_base_sharpe = float("nan")

    # Filter activity
    n_filter_active = int((scale < 0.95).sum())
    n_filter_off    = int((scale < 0.05).sum())
    mean_scale      = float(scale.mean())

    # ── Print headline ─────────────────────────────────────────────────────
    print()
    print("=" * 90)
    print("  Strategy #29 — Crash filter overlay on Strategy #28")
    print("=" * 90)
    print(f"  {'METRIC':<22} {'#28 BASE':>14} {'#29 FILTERED':>18} {'Δ':>12}")
    print(f"  {'Net Sharpe':<22} {s_base['sharpe']:>14.2f} {s_filt['sharpe']:>18.2f} {s_filt['sharpe']-s_base['sharpe']:>+12.2f}")
    print(f"  {'Sortino':<22} {s_base['sortino']:>14.2f} {s_filt['sortino']:>18.2f} {s_filt['sortino']-s_base['sortino']:>+12.2f}")
    print(f"  {'Ann. Return':<22} {s_base['ann_ret']*100:>13.2f}% {s_filt['ann_ret']*100:>17.2f}% {(s_filt['ann_ret']-s_base['ann_ret'])*100:>+11.2f}%")
    print(f"  {'Ann. Vol':<22} {s_base['ann_vol']*100:>13.2f}% {s_filt['ann_vol']*100:>17.2f}% {(s_filt['ann_vol']-s_base['ann_vol'])*100:>+11.2f}%")
    print(f"  {'Max Drawdown':<22} {s_base['max_dd']*100:>13.2f}% {s_filt['max_dd']*100:>17.2f}% {(s_filt['max_dd']-s_base['max_dd'])*100:>+11.2f}%")
    print(f"  {'Calmar':<22} {calmar_base:>14.2f} {calmar_filt:>18.2f} {calmar_filt-calmar_base:>+12.2f}")
    print(f"  {'Daily Skew':<22} {s_base['skew']:>14.2f} {s_filt['skew']:>18.2f} {s_filt['skew']-s_base['skew']:>+12.2f}")
    print(f"  {'Daily Hit Rate':<22} {s_base['hit']*100:>13.2f}% {s_filt['hit']*100:>17.2f}% {(s_filt['hit']-s_base['hit'])*100:>+11.2f}%")
    print(f"  {'Cumulative':<22} {s_base['cum']*100:>13.2f}% {s_filt['cum']*100:>17.2f}% {(s_filt['cum']-s_base['cum'])*100:>+11.2f}%")
    print("=" * 90)

    print()
    print("Overlay-specific diagnostics:")
    print(f"  Tracking error (ann.)       : {tracking_err*100:.2f}%")
    print(f"  Information ratio           : {ir:+.2f}")
    print(f"  Cost of insurance           : {cost_of_insurance_bps:+.1f} bps/yr from filter-induced turnover")
    print(f"  Days filter materially binding (scale < 0.95): {n_filter_active:,}  ({n_filter_active/len(scale)*100:.1f}%)")
    print(f"  Days fully flat (scale < 0.05)              : {n_filter_off:,}  ({n_filter_off/len(scale)*100:.1f}%)")
    print(f"  Mean daily scalar           : {mean_scale:.2f}")
    print()
    print("Drawdown duration:")
    print(f"  {'':<22} {'#28 BASE':>14} {'#29 FILTERED':>18}")
    print(f"  {'Median DD spell (days)':<22} {dd_base['median_dd_days']:>14} {dd_filt['median_dd_days']:>18}")
    print(f"  {'Max DD spell (days)':<22} {dd_base['max_dd_days']:>14} {dd_filt['max_dd_days']:>18}")
    print(f"  {'% of days underwater':<22} {dd_base['pct_underwater']*100:>13.1f}% {dd_filt['pct_underwater']*100:>17.1f}%")
    print()
    if not np.isnan(cond_filt_sharpe):
        print(f"Conditional Sharpe on filter-binding days (scale < 0.95):")
        print(f"  Base #28 Sharpe (those days)    : {cond_base_sharpe:+.2f}")
        print(f"  Filtered #29 Sharpe (those days): {cond_filt_sharpe:+.2f}")
        print(f"  → did the filter remove BAD days specifically? "
              f"{'YES' if cond_filt_sharpe > cond_base_sharpe else 'NO'}")

    # ── Plot ───────────────────────────────────────────────────────────────
    base_curve = (1 + base_net_clean).cumprod()
    filt_curve = (1 + net_filt).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)

    ax = axes[0]
    ax.plot(base_curve.index, base_curve.values, color="#1f77b4", lw=1.4, alpha=0.85,
            label=f"#28 base (Sharpe {s_base['sharpe']:.2f}, MaxDD {s_base['max_dd']*100:.1f}%)")
    ax.plot(filt_curve.index, filt_curve.values, color="#2ca02c", lw=2,
            label=f"#29 filtered (Sharpe {s_filt['sharpe']:.2f}, MaxDD {s_filt['max_dd']*100:.1f}%, IR {ir:+.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #29 — Crash filter (VIX + self-momentum) overlay on Strategy #28\n"
        f"{base.index[0].date()} → {base.index[-1].date()}  ·  "
        f"VIX 20→40 linear scale  ·  Mom gate at z(tr20d) < −1σ → 0.5"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    dd_base_series = (base_curve / base_curve.cummax()) - 1
    dd_filt_series = (filt_curve / filt_curve.cummax()) - 1
    ax.fill_between(dd_base_series.index, dd_base_series.values, 0, color="#1f77b4", alpha=0.35, label="#28 DD")
    ax.fill_between(dd_filt_series.index, dd_filt_series.values, 0, color="#2ca02c", alpha=0.45, label="#29 DD")
    ax.set_ylabel("Drawdown")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.plot(scale.index, scale.values, color="#d62728", lw=0.7)
    ax.fill_between(scale.index, scale.values, 1, color="#d62728", alpha=0.2)
    ax.set_ylabel("Crash scalar")
    ax.set_xlabel("Date")
    ax.set_ylim(-0.05, 1.10)
    ax.grid(True, alpha=0.3)
    # Highlight VIX > 30 episodes for context
    vix_high = (vix > 30)
    if vix_high.any():
        for date in vix.index[vix_high]:
            ax.axvline(date, color="orange", lw=0.05, alpha=0.4)

    plt.tight_layout()
    out = REPORTS / "strategy_29_crash_filter_on_28.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # ── CSV ────────────────────────────────────────────────────────────────
    out_df = pd.DataFrame(index=base.index)
    out_df["vix"]                = vix
    out_df["vix_scale"]          = vix_scale
    out_df["trailing_20d_base"]  = tr20
    out_df["z_tr20"]             = z_tr20
    out_df["mom_scale"]          = mom_scale
    out_df["scale_raw"]          = scale_raw
    out_df["scale"]              = scale
    out_df["base_gross_return"]  = base["gross_return"]
    out_df["base_net_return"]    = base["net_return"]
    out_df["filt_gross_return"]  = gross_filt
    out_df["filt_cost"]          = cost_filt
    out_df["filt_net_return"]    = gross_filt - cost_filt
    out_df["cum_base"]           = (1 + base["net_return"].fillna(0)).cumprod()
    out_df["cum_filt"]           = (1 + (gross_filt - cost_filt).fillna(0)).cumprod()
    out_df.index.name = "date"
    csv_out = TRACK / "strategy_29_crash_filter_on_28_track_record.csv"
    out_df.to_csv(csv_out, float_format="%.6f")
    print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")

    return dict(
        base=s_base, filtered=s_filt,
        calmar_base=calmar_base, calmar_filt=calmar_filt,
        tracking_err=tracking_err, ir=ir,
        cost_of_insurance_bps=cost_of_insurance_bps,
        dd_base=dd_base, dd_filt=dd_filt,
        cond_base_sharpe=cond_base_sharpe, cond_filt_sharpe=cond_filt_sharpe,
        n_filter_active=n_filter_active, n_filter_off=n_filter_off,
        mean_scale=mean_scale,
    )


if __name__ == "__main__":
    main()
