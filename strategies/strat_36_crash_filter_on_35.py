"""
Strategy #36 — Crash-filter overlay on Strategy #35 (crypto cross-sectional
3M momentum)

Same VIX + self-momentum crash scalar used in #22 and #29. Applied here to
#35 — the first clean directional win in the repo. #35 earned net Sharpe
1.44 but at MaxDD −87.9%, driven by 2018 and 2022 crypto crashes. The
question this strategy tests:

  Can the same overlay that removed 7.7pp of MaxDD from #28 also materially
  dent #35's −87.9% MaxDD without hurting the Sharpe?

Why this is the right next step:
  - #29 established that the overlay is BASE-SPECIFIC (it worked on #28 but
    hurt #25). The conditional Sharpe test is the diagnostic: on days when
    the filter binds (scale < 0.95), does the base earn NEGATIVE Sharpe?
    That's the pre-condition for the overlay to add value.
  - #35 has −87.9% MaxDD concentrated in 2018 (crypto winter) and 2022 (Luna
    → FTX). Both were high-VIX periods. So the VIX component should bind
    during exactly the drawdowns we want to trim.
  - The self-momentum gate should further reduce exposure when the strategy
    is already in a drawdown — the classic "crash filter" behaviour.

Filter spec (identical to #22 and #29 — no retuning, honest replication):
  - VIX scalar      : 1.0 if VIX ≤ 20; 0.0 if VIX ≥ 40; linear in between
  - Self-momentum   : 0.5 when trailing-20d base return is < −1σ of trailing
                      252d; otherwise 1.0
  - Combined scalar : VIX_scale × MOM_scale, clipped to [0, 1]
  - Lag             : 1 day (scale[t] set at end of t−1, applied at t)

Cost: 30 bps RT per leg (matches #35, deliberately punitive for retail crypto).
Crypto trades 7/7 so we use 365 trading-day convention; VIX (SPX-only)
gets ffilled across weekends/holidays.

Pre-registered pass criteria:
  - Sharpe ≥ base (or improve).
  - MaxDD improves by ≥ 5 percentage points.
  - Information Ratio > 0.
  - Conditional Sharpe test PASSES: on filter-binding days, base Sharpe < 0
    while filtered Sharpe > base Sharpe (i.e., filter removes bad days
    specifically, not good days).

Anything less = overlay is base-inappropriate. Cross-spec-independence
matters: #22, #29 both worked; #30 (on #25 Turtle base) did not. #36 has to
earn its slot.
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

BASE_CSV = TRACK / "strategy_35_crypto_xsec_momentum_track_record.csv"

# ── Crash filter parameters (identical to #22/#29, no retuning) ──────────────
VIX_FULL_BELOW       = 20.0
VIX_FLAT_ABOVE       = 40.0
MOM_LOOKBACK_DAYS    = 20
MOM_REF_DAYS         = 252
MOM_Z_TRIGGER        = -1.0
MOM_SCALE_ON_TRIGGER = 0.5

COST_RT_BPS          = 30.0      # match #35
TRADING_DAYS         = 365       # crypto trades every day
START                = "2015-01-01"
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
    curve = (1 + returns.fillna(0)).cumprod()
    peak  = curve.cummax()
    in_dd = (curve < peak).astype(int)
    spells: list[int] = []
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
    print(f"\nReading #35 base from {BASE_CSV.relative_to(REPO)}")
    base = pd.read_csv(BASE_CSV, parse_dates=["date"], index_col="date")
    print(f"  {len(base):,} rows, {base.index[0].date()} → {base.index[-1].date()}")

    weight_cols = sorted([c for c in base.columns if c.startswith("weight_")])
    instruments = [c.replace("weight_", "") for c in weight_cols]
    print(f"  Weight columns: {len(weight_cols)} — {', '.join(instruments)}")

    # ── Fetch VIX ────────────────────────────────────────────────────────
    print("\nFetching VIX (^VIX) from yfinance...")
    raw_vix = yf.download("^VIX", start=START, end=END, auto_adjust=True, progress=False)
    vix = raw_vix["Close"].squeeze()
    vix.index = pd.to_datetime(vix.index)
    # VIX only trades on NYSE days — reindex to #35's calendar and ffill
    vix = vix.reindex(base.index).ffill().bfill()
    print(f"  VIX series : {len(vix):,} rows, range {float(vix.min()):.1f} → {float(vix.max()):.1f}")

    # ── Build the crash scalar (identical spec to #22/#29) ───────────────
    vix_above = (vix - VIX_FULL_BELOW).clip(lower=0)
    range_span = VIX_FLAT_ABOVE - VIX_FULL_BELOW
    vix_scale = (1.0 - vix_above / range_span).clip(lower=0.0, upper=1.0)

    base_net = base["net_return"]
    tr20 = base_net.rolling(MOM_LOOKBACK_DAYS).sum()
    mu252 = tr20.rolling(MOM_REF_DAYS, min_periods=63).mean()
    sd252 = tr20.rolling(MOM_REF_DAYS, min_periods=63).std()
    z_tr20 = ((tr20 - mu252) / sd252).reindex(base.index).fillna(0)
    mom_scale = pd.Series(np.where(z_tr20 < MOM_Z_TRIGGER, MOM_SCALE_ON_TRIGGER, 1.0),
                          index=base.index)

    scale_raw = (vix_scale * mom_scale).clip(lower=0.0, upper=1.0)
    scale = scale_raw.shift(1).fillna(1.0)

    # ── Apply scalar to #35's weights and recompute ──────────────────────
    weights_base = base[weight_cols]
    weights_filt = weights_base.mul(scale, axis=0)

    gross_filt = base["gross_return"] * scale

    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0
    turnover_filt = weights_filt.diff().abs().sum(axis=1).fillna(0)
    cost_filt = turnover_filt * cost_per_unit

    net_filt = (gross_filt - cost_filt).dropna()
    base_net_clean = base_net.dropna()

    # ── Metrics ──────────────────────────────────────────────────────────
    s_base = _stats(base_net_clean)
    s_filt = _stats(net_filt)
    calmar_base = s_base["ann_ret"] / abs(s_base["max_dd"]) if s_base["max_dd"] else float("nan")
    calmar_filt = s_filt["ann_ret"] / abs(s_filt["max_dd"]) if s_filt["max_dd"] else float("nan")

    common_idx = base_net_clean.index.intersection(net_filt.index)
    active_ret = (net_filt - base_net_clean).loc[common_idx]
    tracking_err = float(active_ret.std() * np.sqrt(TRADING_DAYS))
    ir = float(active_ret.mean() * TRADING_DAYS / tracking_err) if tracking_err > 0 else 0.0

    base_cost = base["cost"].sum()
    filt_cost_total = cost_filt.sum()
    n_years = len(base_net_clean) / TRADING_DAYS
    cost_of_insurance_bps = (filt_cost_total - base_cost) / n_years * 10000

    dd_base = _drawdown_durations(base_net_clean)
    dd_filt = _drawdown_durations(net_filt)

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

    n_filter_active = int((scale < 0.95).sum())
    n_filter_off    = int((scale < 0.05).sum())
    mean_scale      = float(scale.mean())

    # ── Print headline ───────────────────────────────────────────────────
    print()
    print("=" * 92)
    print("  Strategy #36 — Crash-filter overlay on Strategy #35 (crypto xsec momentum)")
    print("=" * 92)
    print(f"  {'METRIC':<22} {'#35 BASE':>14} {'#36 FILTERED':>18} {'Δ':>14}")
    print(f"  {'Net Sharpe':<22} {s_base['sharpe']:>14.2f} {s_filt['sharpe']:>18.2f} {s_filt['sharpe']-s_base['sharpe']:>+14.2f}")
    print(f"  {'Sortino':<22} {s_base['sortino']:>14.2f} {s_filt['sortino']:>18.2f} {s_filt['sortino']-s_base['sortino']:>+14.2f}")
    print(f"  {'Ann. Return':<22} {s_base['ann_ret']*100:>13.2f}% {s_filt['ann_ret']*100:>17.2f}% {(s_filt['ann_ret']-s_base['ann_ret'])*100:>+13.2f}%")
    print(f"  {'Ann. Vol':<22} {s_base['ann_vol']*100:>13.2f}% {s_filt['ann_vol']*100:>17.2f}% {(s_filt['ann_vol']-s_base['ann_vol'])*100:>+13.2f}%")
    print(f"  {'Max Drawdown':<22} {s_base['max_dd']*100:>13.2f}% {s_filt['max_dd']*100:>17.2f}% {(s_filt['max_dd']-s_base['max_dd'])*100:>+13.2f}%")
    print(f"  {'Calmar':<22} {calmar_base:>14.2f} {calmar_filt:>18.2f} {calmar_filt-calmar_base:>+14.2f}")
    print(f"  {'Daily Skew':<22} {s_base['skew']:>14.2f} {s_filt['skew']:>18.2f} {s_filt['skew']-s_base['skew']:>+14.2f}")
    print(f"  {'Daily Hit Rate':<22} {s_base['hit']*100:>13.2f}% {s_filt['hit']*100:>17.2f}% {(s_filt['hit']-s_base['hit'])*100:>+13.2f}%")
    print(f"  {'Cumulative':<22} {s_base['cum']*100:>13.0f}% {s_filt['cum']*100:>17.0f}% {(s_filt['cum']-s_base['cum'])*100:>+13.0f}%")
    print("=" * 92)

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
    print(f"  {'':<22} {'#35 BASE':>14} {'#36 FILTERED':>18}")
    print(f"  {'Median DD spell (days)':<22} {dd_base['median_dd_days']:>14} {dd_filt['median_dd_days']:>18}")
    print(f"  {'Max DD spell (days)':<22} {dd_base['max_dd_days']:>14} {dd_filt['max_dd_days']:>18}")
    print(f"  {'% of days underwater':<22} {dd_base['pct_underwater']*100:>13.1f}% {dd_filt['pct_underwater']*100:>17.1f}%")
    print()
    if not np.isnan(cond_filt_sharpe):
        print(f"Conditional Sharpe on filter-binding days (scale < 0.95, {n_binding} days):")
        print(f"  Base #35 Sharpe (those days)    : {cond_base_sharpe:+.2f}")
        print(f"  Filtered #36 Sharpe (those days): {cond_filt_sharpe:+.2f}")
        removed_bad = cond_filt_sharpe > cond_base_sharpe
        print(f"  → filter removed BAD days specifically? {'YES' if removed_bad else 'NO'}")
        if cond_base_sharpe < 0:
            print(f"  → base Sharpe is NEGATIVE on binding days — overlay has the right target.")
        else:
            print(f"  → base Sharpe is POSITIVE on binding days — overlay is removing good days (cf. #30).")

    # ── Sub-period comparison ────────────────────────────────────────────
    periods = [
        ("2018 bear",       "2018-01-01", "2018-12-31"),
        ("2019-2020 recov", "2019-01-01", "2020-12-31"),
        ("2021 bull",       "2021-01-01", "2021-12-31"),
        ("2022 crash",      "2022-01-01", "2022-12-31"),
        ("2023-2024 recov", "2023-01-01", "2024-12-31"),
    ]
    print()
    print("Sub-period Sharpe comparison (net):")
    print(f"  {'Period':<18} {'Days':>6} {'#35 base':>10} {'#36 filt':>10} {'Δ':>8}  {'MDD base':>10} {'MDD filt':>10}")
    for label, ps, pe in periods:
        m_b = (base_net_clean.index >= ps) & (base_net_clean.index <= pe)
        m_f = (net_filt.index >= ps) & (net_filt.index <= pe)
        if not m_b.any():
            continue
        sp_b = _stats(base_net_clean.loc[m_b])
        sp_f = _stats(net_filt.loc[m_f])
        print(f"  {label:<18} {int(m_b.sum()):>6} {sp_b['sharpe']:>10.2f} {sp_f['sharpe']:>10.2f} "
              f"{sp_f['sharpe']-sp_b['sharpe']:>+8.2f} {sp_b['max_dd']*100:>9.1f}% {sp_f['max_dd']*100:>9.1f}%")

    # ── Verdict against pre-registered criteria ──────────────────────────
    print()
    print("VERDICT (pre-registered criteria):")
    sharpe_ok = s_filt["sharpe"] >= s_base["sharpe"]
    mdd_ok    = (s_filt["max_dd"] - s_base["max_dd"]) >= 0.05      # ≥ 5pp less negative
    ir_ok     = ir > 0.0
    cond_ok   = (not np.isnan(cond_filt_sharpe)) and (cond_base_sharpe < 0) and (cond_filt_sharpe > cond_base_sharpe)
    print(f"  1. Sharpe stays or improves               : {'PASS' if sharpe_ok else 'FAIL'} ({s_filt['sharpe']:.2f} vs {s_base['sharpe']:.2f})")
    print(f"  2. MaxDD improves ≥ 5pp                   : {'PASS' if mdd_ok else 'FAIL'} ({(s_filt['max_dd']-s_base['max_dd'])*100:+.1f}pp)")
    print(f"  3. Information ratio > 0                  : {'PASS' if ir_ok else 'FAIL'} ({ir:+.2f})")
    print(f"  4. Conditional Sharpe test (base<0, filt>base): {'PASS' if cond_ok else 'FAIL'} (base {cond_base_sharpe:+.2f}, filt {cond_filt_sharpe:+.2f})")
    all_pass = sharpe_ok and mdd_ok and ir_ok and cond_ok
    if all_pass:
        print(f"  ▶︎ ✅ ALL CRITERIA PASS — overlay is deployable on #35.")
    else:
        n_pass = int(sharpe_ok) + int(mdd_ok) + int(ir_ok) + int(cond_ok)
        print(f"  ▶︎ ⚠️  {n_pass}/4 criteria met. Overlay is base-inappropriate for #35 in this spec.")

    # ── Plot ─────────────────────────────────────────────────────────────
    base_curve = (1 + base_net_clean).cumprod()
    filt_curve = (1 + net_filt).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)

    ax = axes[0]
    ax.plot(base_curve.index, base_curve.values, color="#1f77b4", lw=1.4, alpha=0.85,
            label=f"#35 base (Sharpe {s_base['sharpe']:.2f}, MaxDD {s_base['max_dd']*100:.1f}%)")
    ax.plot(filt_curve.index, filt_curve.values, color="#2ca02c", lw=2,
            label=f"#36 filtered (Sharpe {s_filt['sharpe']:.2f}, MaxDD {s_filt['max_dd']*100:.1f}%, IR {ir:+.2f})")
    ax.set_yscale("log")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (× log)")
    ax.set_title(
        f"Strategy #36 — Crash filter (VIX + self-momentum) overlay on Strategy #35\n"
        f"{base.index[0].date()} → {base.index[-1].date()}  ·  "
        f"VIX 20→40 linear scale  ·  Mom gate at z(tr20d) < −1σ → 0.5"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, which="both")

    ax = axes[1]
    dd_base_series = (base_curve / base_curve.cummax()) - 1
    dd_filt_series = (filt_curve / filt_curve.cummax()) - 1
    ax.fill_between(dd_base_series.index, dd_base_series.values, 0, color="#1f77b4", alpha=0.35, label="#35 DD")
    ax.fill_between(dd_filt_series.index, dd_filt_series.values, 0, color="#2ca02c", alpha=0.45, label="#36 DD")
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

    plt.tight_layout()
    out = REPORTS / "strategy_36_crash_filter_on_35.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # ── CSV ──────────────────────────────────────────────────────────────
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
    csv_out = TRACK / "strategy_36_crash_filter_on_35_track_record.csv"
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
