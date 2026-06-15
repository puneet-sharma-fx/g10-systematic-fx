"""
Strategy #22 — Carry crash filter overlay (Brunnermeier-Nagel-Pedersen 2009)

The overlay is a deployable risk-management layer that scales positions of a
base carry-style strategy down during crash conditions. It is NOT a directional
signal — it's a risk filter intended to reduce left-tail crash exposure with
minimal Sharpe drag.

The base strategy used here is Strategy #18 (equal-weight rate-diff portfolio),
re-implemented inline for self-containment. The overlay is independent of the
base and can be re-applied to any future carry-style strategy.

CAVEAT: Strategy #18's base Sharpe is suspected to contain intraday timing
leakage (per Strategy #21's verification of #1). The interesting comparison
here is NOT the absolute Sharpe — it's the DELTA in skewness, max drawdown
and Calmar between unfiltered (#18) and filtered (#22). The overlay's value
is in its risk-shape change, which holds regardless of the base signal's
timing characteristics.

Crash filter inputs (two indicators, multiplicative combination):

  1) VIX level — proxy for global risk appetite
       vix_scale[t] = clip(1 − max(0, VIX[t] − 20) / 20, 0, 1)
       VIX  20 → 1.00   (full position)
       VIX  25 → 0.75
       VIX  30 → 0.50
       VIX  35 → 0.25
       VIX 40+ → 0.00   (flat)

  2) Self-momentum (trailing strategy drawdown)
       trailing_20d = 20-day rolling sum of the UNFILTERED strategy's net return
       z_tr20[t]    = (trailing_20d[t] − mean_252d) / std_252d
       mom_scale[t] = 0.5 if z_tr20 < −1.0 else 1.0
       Halves exposure during persistent strategy drawdowns.

Combined scalar (lagged 1 day to avoid look-ahead):
       scale[t] = (vix_scale[t−1] × mom_scale[t−1]) ∈ [0, 1]
       w_filtered[pair, t] = w_base[pair, t] × scale[t]

Per the literature (Brunnermeier, Nagel, Pedersen 2009): VIX + TED-spread
filtering of FX carry reduces skewness from ≈ −2.5 to ≈ −0.5 with modest
Sharpe drag. We omit TED here because TEDRATE was discontinued by FRED in
Jan 2022; SOFR-OIS would be the modern equivalent but is not in the existing
fetcher layer. Two-indicator construction is the realistic implementation on
public data through 2024.
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
YIELDS_CSV = REPO / "data" / "raw" / "tvc_2y_yields.csv"

# Re-use Strategy #10/#18 parameters
TARGET_VOL          = 0.10
MAX_PER_PAIR        = 0.30
MAX_PER_PAIR_LEV    = 0.60
VOL_LOOKBACK_DAYS   = 21
CALIBRATION_WINDOW  = 63
MAX_LEVERAGE        = 3.0
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS        = 252
START               = "2010-01-04"
END                 = "2024-12-31"

UNIVERSE = [
    ("EURUSD", "EU", "US", 0.0001),
    ("GBPUSD", "GB", "US", 0.0001),
    ("AUDUSD", "AU", "US", 0.0001),
    ("USDCAD", "US", "CA", 0.0001),
]

# Crash filter parameters
VIX_FULL_BELOW       = 20.0
VIX_FLAT_ABOVE       = 40.0
MOM_LOOKBACK_DAYS    = 20
MOM_REGIME_WINDOW    = 252
MOM_Z_TRIGGER        = -1.0
MOM_SCALE_ON_TRIGGER = 0.5


def _fetch_fx(pair: str) -> pd.Series:
    df = yf.download(f"{pair}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    s.name = pair
    return s.dropna()


def _fetch_vix() -> pd.Series:
    df = yf.download("^VIX", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.index = pd.to_datetime(s.index)
    s.name = "VIX"
    return s.dropna()


def _stats(returns: pd.Series) -> dict:
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew())
    return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1))


def _build_portfolio(weights: pd.DataFrame,
                     fx_ret: pd.DataFrame,
                     fx_close: pd.DataFrame,
                     pip_by_pair: dict) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Apply weights to returns and compute gross_port, cost_total, net_port."""
    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    gross_pair_ret = weights * fx_ret
    turnover = weights.diff().abs().fillna(0)
    cost_per_pair = pd.DataFrame(index=weights.index, columns=weights.columns, dtype=float)
    for name in weights.columns:
        cost_per_pair[name] = turnover[name] * (cost_per_unit_pips * pip_by_pair[name]) / fx_close[name]
    cost_total = cost_per_pair.sum(axis=1)
    gross_port = gross_pair_ret.sum(axis=1)
    net_port = (gross_port - cost_total).dropna()
    return gross_port.loc[net_port.index], cost_total.loc[net_port.index], net_port


def run(csv_out: Path | None = None) -> dict:
    print("\nStrategy #22 — Carry crash filter overlay on Strategy #18 (equal-weight portfolio)")
    print(f"  Filter inputs : VIX level + self-momentum (trailing {MOM_LOOKBACK_DAYS}d return)")
    print(f"  VIX scalar    : linear 1.0 at VIX≤{VIX_FULL_BELOW}, 0.0 at VIX≥{VIX_FLAT_ABOVE}")
    print(f"  Momentum gate : scale to {MOM_SCALE_ON_TRIGGER:.2f}x when trailing-{MOM_LOOKBACK_DAYS}d return below {MOM_Z_TRIGGER:+.1f}σ of trailing {MOM_REGIME_WINDOW}d")
    print()

    pair_names = [p[0] for p in UNIVERSE]
    pip_by_pair = {p[0]: p[3] for p in UNIVERSE}

    print(f"  Fetching FX for {len(UNIVERSE)} pairs and VIX...")
    yields = pd.read_csv(YIELDS_CSV, index_col=0, parse_dates=True)
    fx_dict = {name: _fetch_fx(name) for name, *_ in UNIVERSE}
    vix = _fetch_vix()
    print(f"  Yields: {yields.shape}; VIX: {len(vix)} rows")

    idx = pd.bdate_range(start=START, end=END)
    d_diff   = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    fx_ret   = pd.DataFrame(index=idx, columns=pair_names, dtype=float)
    fx_close = pd.DataFrame(index=idx, columns=pair_names, dtype=float)

    first_valids = []
    for name, base, quote, _pip in UNIVERSE:
        base_2y  = yields[base].reindex(idx).ffill()
        quote_2y = yields[quote].reindex(idx).ffill()
        px       = fx_dict[name].reindex(idx).ffill()
        d_diff[name]   = (base_2y - quote_2y).diff()
        fx_close[name] = px
        fx_ret[name]   = px.pct_change()
        first_valids.append(max(base_2y.dropna().index.min(),
                                quote_2y.dropna().index.min()))

    vix_aligned = vix.reindex(idx).ffill()

    # ── Equal-weight raw weights (matches Strategy #18, pre-calibration) ────
    n_pairs = len(pair_names)
    weights_raw = (np.sign(d_diff) / n_pairs).fillna(0)
    weights_raw = weights_raw.clip(lower=-MAX_PER_PAIR, upper=MAX_PER_PAIR).fillna(0)
    weights_raw = weights_raw.shift(1).fillna(0)

    burn_in_start = max(first_valids) + pd.Timedelta(days=VOL_LOOKBACK_DAYS * 2)
    weights_raw = weights_raw[weights_raw.index >= burn_in_start]
    fx_ret_in   = fx_ret.reindex(weights_raw.index)
    fx_close_in = fx_close.reindex(weights_raw.index)
    vix_in      = vix_aligned.reindex(weights_raw.index)

    # ── Calibrate leverage on UNFILTERED strategy ──────────────────────────
    _, _, unlevered_net = _build_portfolio(weights_raw, fx_ret_in, fx_close_in, pip_by_pair)
    rolling_vol = (unlevered_net.rolling(CALIBRATION_WINDOW, min_periods=21)
                   .std() * np.sqrt(TRADING_DAYS))
    leverage_scalar = (TARGET_VOL / rolling_vol).clip(upper=MAX_LEVERAGE)
    leverage_scalar = leverage_scalar.shift(1).reindex(weights_raw.index).fillna(1.0)

    weights_base = weights_raw.mul(leverage_scalar, axis=0)
    weights_base = weights_base.clip(lower=-MAX_PER_PAIR_LEV, upper=MAX_PER_PAIR_LEV)

    gross_base, cost_base, net_base = _build_portfolio(weights_base, fx_ret_in, fx_close_in, pip_by_pair)
    print(f"  Avg leverage scalar          : {leverage_scalar.mean():.2f}x")

    # ── Crash filter scalar ────────────────────────────────────────────────
    # (1) VIX scalar
    vix_scale = (1.0 - (vix_in - VIX_FULL_BELOW).clip(lower=0) / (VIX_FLAT_ABOVE - VIX_FULL_BELOW)).clip(0, 1)

    # (2) Self-momentum scalar — uses base (unfiltered) trailing return
    tr20  = net_base.rolling(MOM_LOOKBACK_DAYS).sum()
    mu252 = tr20.rolling(MOM_REGIME_WINDOW).mean()
    sd252 = tr20.rolling(MOM_REGIME_WINDOW).std()
    z_tr20 = ((tr20 - mu252) / sd252).reindex(weights_raw.index).fillna(0)
    mom_scale = pd.Series(1.0, index=weights_raw.index)
    mom_scale[z_tr20 < MOM_Z_TRIGGER] = MOM_SCALE_ON_TRIGGER

    # (3) Combined, lag by 1 day to avoid look-ahead on same-day VIX close
    scale_raw = (vix_scale * mom_scale).clip(0, 1)
    scale = scale_raw.shift(1).fillna(1.0)

    # ── Filtered weights and P&L ───────────────────────────────────────────
    weights_filt = weights_base.mul(scale, axis=0)
    gross_filt, cost_filt, net_filt = _build_portfolio(weights_filt, fx_ret_in, fx_close_in, pip_by_pair)

    # ── Metrics ────────────────────────────────────────────────────────────
    common_idx = net_base.index.intersection(net_filt.index)
    s_base = _stats(net_base.loc[common_idx])
    s_filt = _stats(net_filt.loc[common_idx])
    calmar_base = s_base["ann_ret"] / abs(s_base["max_dd"]) if s_base["max_dd"] else float("nan")
    calmar_filt = s_filt["ann_ret"] / abs(s_filt["max_dd"]) if s_filt["max_dd"] else float("nan")

    # Days where filter materially kicked in (< 0.95)
    n_active   = int((scale < 0.95).sum())
    n_zero     = int((scale < 0.05).sum())
    mean_scale = float(scale.mean())

    print("=" * 78)
    print("  Strategy #22 — crash filter overlay (vs #18 baseline)")
    print("=" * 78)
    print(f"  Observations              : {len(common_idx):,}")
    print(f"  Days filter active (<0.95): {n_active:,} ({n_active/len(scale)*100:.1f}%)")
    print(f"  Days flat (scale <0.05)   : {n_zero:,} ({n_zero/len(scale)*100:.1f}%)")
    print(f"  Mean daily scalar         : {mean_scale:.2f}")
    print()
    print(f"  {'METRIC':<22} {'#18 BASE':>14} {'#22 FILTERED':>16} {'Δ':>12}")
    print(f"  {'Ann. Return (net)':<22} {s_base['ann_ret']*100:>13.2f}% {s_filt['ann_ret']*100:>15.2f}% {(s_filt['ann_ret']-s_base['ann_ret'])*100:>11.2f}%")
    print(f"  {'Ann. Vol':<22} {s_base['ann_vol']*100:>13.2f}% {s_filt['ann_vol']*100:>15.2f}% {(s_filt['ann_vol']-s_base['ann_vol'])*100:>11.2f}%")
    print(f"  {'Sharpe':<22} {s_base['sharpe']:>14.2f} {s_filt['sharpe']:>16.2f} {s_filt['sharpe']-s_base['sharpe']:>12.2f}")
    print(f"  {'Max Drawdown':<22} {s_base['max_dd']*100:>13.2f}% {s_filt['max_dd']*100:>15.2f}% {(s_filt['max_dd']-s_base['max_dd'])*100:>11.2f}%")
    print(f"  {'Calmar':<22} {calmar_base:>14.2f} {calmar_filt:>16.2f} {calmar_filt-calmar_base:>12.2f}")
    print(f"  {'Daily-return Skew':<22} {s_base['skew']:>14.2f} {s_filt['skew']:>16.2f} {s_filt['skew']-s_base['skew']:>12.2f}")
    print(f"  {'Hit Rate':<22} {s_base['hit']*100:>13.2f}% {s_filt['hit']*100:>15.2f}% {(s_filt['hit']-s_base['hit'])*100:>11.2f}%")
    print(f"  {'Cumulative':<22} {s_base['cum']*100:>13.2f}% {s_filt['cum']*100:>15.2f}% {(s_filt['cum']-s_base['cum'])*100:>11.2f}%")
    print("=" * 78)
    print(f"\n  Interpretation:")
    if s_filt["skew"] > s_base["skew"] + 0.2:
        print(f"    ✅ Skewness materially improved ({s_base['skew']:+.2f} → {s_filt['skew']:+.2f}); crash filter reshapes the tail as intended.")
    elif s_filt["skew"] > s_base["skew"]:
        print(f"    ⚠️  Skewness modestly improved ({s_base['skew']:+.2f} → {s_filt['skew']:+.2f}); marginal benefit.")
    else:
        print(f"    ❌ Skewness did not improve. Filter does not reshape the tail on this base strategy.")
    if abs(s_filt["max_dd"]) < abs(s_base["max_dd"]) * 0.85:
        print(f"    ✅ Max drawdown reduced by >15% — meaningful risk reduction.")
    elif abs(s_filt["max_dd"]) < abs(s_base["max_dd"]):
        print(f"    ⚠️  Max drawdown reduced modestly.")
    if calmar_filt > calmar_base:
        print(f"    ✅ Calmar improved (Sharpe-vs-drawdown trade-off favours overlay).")

    # ── Plot ───────────────────────────────────────────────────────────────
    base_curve = (1 + net_base.loc[common_idx]).cumprod()
    filt_curve = (1 + net_filt.loc[common_idx]).cumprod()

    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(base_curve.index, base_curve.values, color="#1f77b4", lw=1.4, alpha=0.75,
            label=f"#18 base (Sharpe {s_base['sharpe']:.2f}, MaxDD {s_base['max_dd']*100:.1f}%, skew {s_base['skew']:+.2f})")
    ax.plot(filt_curve.index, filt_curve.values, color="#2ca02c", lw=2,
            label=f"#22 crash-filtered (Sharpe {s_filt['sharpe']:.2f}, MaxDD {s_filt['max_dd']*100:.1f}%, skew {s_filt['skew']:+.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #22 — Carry crash filter overlay on #18 (VIX + self-momentum)\n"
        f"{common_idx[0].strftime('%Y-%m-%d')} to {common_idx[-1].strftime('%Y-%m-%d')}  "
        f"·  filter active on {n_active/len(scale)*100:.0f}% of days  ·  mean scalar {mean_scale:.2f}"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    base_dd = (base_curve / base_curve.cummax()) - 1
    filt_dd = (filt_curve / filt_curve.cummax()) - 1
    ax.fill_between(base_dd.index, base_dd.values, 0, color="#1f77b4", alpha=0.30, label="#18 DD")
    ax.fill_between(filt_dd.index, filt_dd.values, 0, color="#2ca02c", alpha=0.50, label="#22 DD")
    ax.set_ylabel("Drawdown")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.plot(scale.loc[common_idx].index, scale.loc[common_idx].values, color="#d62728", lw=0.9)
    ax.fill_between(scale.loc[common_idx].index, scale.loc[common_idx].values, 1.0,
                    color="#d62728", alpha=0.20)
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Crash filter scalar")
    ax.set_xlabel("Date")
    ax.set_ylim(-0.05, 1.10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_22_carry_crash_filter_overlay.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=common_idx)
        out_df["vix"]            = vix_in.loc[common_idx]
        out_df["vix_scale"]      = vix_scale.loc[common_idx]
        out_df["mom_z"]          = z_tr20.loc[common_idx]
        out_df["mom_scale"]      = mom_scale.loc[common_idx]
        out_df["crash_scalar"]   = scale.loc[common_idx]
        out_df["leverage"]       = leverage_scalar.loc[common_idx]
        out_df["net_ret_base"]   = net_base.loc[common_idx]
        out_df["net_ret_filt"]   = net_filt.loc[common_idx]
        out_df["cum_base"]       = base_curve
        out_df["cum_filt"]       = filt_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(
        base=s_base, filtered=s_filt,
        calmar_base=calmar_base, calmar_filt=calmar_filt,
        n_obs=len(common_idx),
        days_filter_active=n_active, days_flat=n_zero,
        mean_scalar=mean_scale,
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_22_crash_filter_overlay_track_record.csv")
