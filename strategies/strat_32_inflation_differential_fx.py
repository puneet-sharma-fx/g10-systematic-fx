"""
Strategy #32 — Cross-sectional inflation-differential momentum on G10 FX

The first strategy in the repo to USE the new economic-data ingestion layer
(`data/economic.py`) as a SIGNAL SOURCE, rather than as research backdrop.
Tests the cleanest macroeconomic prediction in textbook FX: the Taylor-rule
implication that currencies experiencing higher inflation see more hawkish
central-bank responses, ergo currency appreciation against currencies with
lower inflation.

Spec:
  - Universe : 9 G10 pairs vs USD (EUR, GBP, AUD, NZD, JPY, CAD, CHF, SEK, NOK)
  - Signal   : For each non-USD currency C on month t,
                  diff[C, t] = CPI_YoY[C, t] - CPI_YoY[US, t]
               where CPI_YoY is the trailing 12-month change in headline CPI
               (or already-published YoY rate for series that report it that way).
  - Rebalance: End of each month, rank currencies by `diff`.
               Long top-3 currencies (highest relative inflation → most-hawkish
               outlook → expected appreciation),
               Short bottom-3 currencies (lowest relative inflation).
               Equal weight ±1/6 per leg → max gross 6/6 = 100%, net 0
               (cross-sectional market-neutral by construction).
  - Hold     : 1 month, then re-rank.
  - Cost     : 5 pips RT applied on actual turnover.

Theoretical basis:
  - Taylor (1993, NBER 100) — central bank reaction function on inflation gap.
  - Molodtsova & Papell (2009, JIE) — Taylor-rule fundamentals predict
    G10 FX out-of-sample for 11 of 12 currencies at 1-month horizon.
  - Engel & West (2005, JPE) — present-value FX pricing using rate
    expectations driven by inflation/output gaps.
  - Clarida-Galí-Gertler (1999) — open-economy Taylor rules.

What our existing repo predicts FAILS:
  - Pure rate-differential signals are timing-artefact-suspect (per #21).
    But INFLATION-differentials are slower-moving, monthly-released, and
    less prone to intraday timestamp misalignment — the strategy is
    structurally cleaner.
  - Cross-sectional momentum on 1-day or 1-week FX returns failed (#11, #31).
    But the inflation signal updates monthly and reflects fundamentals,
    not short-term price moves.

Honest expectation:
  - If the Molodtsova-Papell finding holds, this should print a positive
    net Sharpe (literature suggests ~0.3-0.5 at monthly horizons).
  - If it fails alongside our previous monthly cross-sectional tests, that
    further supports "G10 FX is hard at all horizons in 2010-2024."

Universe: 9 G10 currencies vs USD. CPI data via `data/economic.py`.
Period: 2010-2024 (or as far as CPI data extends; OECD MEI mirrors stop
in 2023-2025 for several countries — backtest will use what's available).
"""
from __future__ import annotations

import logging
import os
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

sys.path.insert(0, str(REPO))
from data.economic import get  # noqa: E402

# ── Strategy parameters ──────────────────────────────────────────────────────
N_LONG               = 3         # long top-3 by inflation differential
N_SHORT              = 3         # short bottom-3
COST_ROUND_TRIP_PIPS = 5.0
TRADING_DAYS         = 252
START                = "2010-01-04"
END                  = "2024-12-31"

# Each currency has: (FX pair ticker on Yahoo, pip size, is_usd_quote_currency)
# is_usd_quote: True means pair is base=foreign, quote=USD (like EURUSD)
#               False means pair is base=USD, quote=foreign (like USDJPY)
# Effective return for "foreign currency strength vs USD":
#   - If is_usd_quote=True (EURUSD): currency_return = pct_change(price)
#   - If is_usd_quote=False (USDJPY): currency_return = -pct_change(price)
CURRENCIES = {
    "EU":  {"pair": "EURUSD", "pip": 0.0001, "usd_quote": True,  "cpi_code": "EA:HICP_NATIVE",  "yoy_already": True},
    "GB":  {"pair": "GBPUSD", "pip": 0.0001, "usd_quote": True,  "cpi_code": "UK:CPI_HEADLINE", "yoy_already": False},
    "AU":  {"pair": "AUDUSD", "pip": 0.0001, "usd_quote": True,  "cpi_code": "AU:CPI_HEADLINE", "yoy_already": False},
    "NZ":  {"pair": "NZDUSD", "pip": 0.0001, "usd_quote": True,  "cpi_code": "NZ:CPI_HEADLINE", "yoy_already": False},
    "JP":  {"pair": "USDJPY", "pip": 0.01,   "usd_quote": False, "cpi_code": "JP:CPI_HEADLINE", "yoy_already": False},
    "CA":  {"pair": "USDCAD", "pip": 0.0001, "usd_quote": False, "cpi_code": "CA:CPI_HEADLINE", "yoy_already": False},
    "CH":  {"pair": "USDCHF", "pip": 0.0001, "usd_quote": False, "cpi_code": "CH:CPI_HEADLINE", "yoy_already": False},
    "SE":  {"pair": "USDSEK", "pip": 0.0001, "usd_quote": False, "cpi_code": "SE:CPI_HEADLINE", "yoy_already": False},
    "NO":  {"pair": "USDNOK", "pip": 0.0001, "usd_quote": False, "cpi_code": "NO:CPI_HEADLINE", "yoy_already": False},
}
US_CPI_CODE         = "US:CPI_HEADLINE"
US_CPI_YOY_ALREADY  = False


def _fetch_currency_strength(spec: dict) -> pd.Series:
    """Daily series of 'foreign currency in USD' regardless of Yahoo quote conv."""
    df = yf.download(f"{spec['pair']}=X", start=START, end=END,
                     auto_adjust=True, progress=False)
    s = df["Close"].squeeze().dropna()
    s.index = pd.to_datetime(s.index)
    if spec["usd_quote"]:
        return s             # already foreign/USD
    return 1.0 / s            # flip to foreign/USD


def _cpi_to_yoy(s: pd.Series, already_yoy: bool) -> pd.Series:
    """Return year-over-year inflation in percent."""
    s = s.dropna()
    if already_yoy:
        return s             # already %YoY
    return (s / s.shift(12) - 1.0) * 100.0


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


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #32 — Cross-sectional inflation differential on G10 FX")
    print(f"  Universe   : {len(CURRENCIES)} non-USD currencies")
    print(f"  Signal     : trailing-12m CPI YoY differential vs US")
    print(f"  Positions  : long top-{N_LONG}, short bottom-{N_SHORT} by differential")
    print(f"  Rebalance  : monthly, end-of-month sort with 1-day execution lag")
    print(f"  Cost       : {COST_ROUND_TRIP_PIPS} pips RT")
    print()

    # ── Fetch CPI for US + each non-USD country (uses our economic catalog) ──
    print("Fetching CPI series via data.economic catalog...")
    us_cpi_raw = get(US_CPI_CODE)
    us_yoy = _cpi_to_yoy(us_cpi_raw, US_CPI_YOY_ALREADY)
    print(f"  US YoY : {len(us_yoy):>3} months, range {us_yoy.index[0].date()} → {us_yoy.index[-1].date()}")

    cpi_yoy: dict[str, pd.Series] = {}
    for code, spec in CURRENCIES.items():
        try:
            raw = get(spec["cpi_code"])
            y = _cpi_to_yoy(raw, spec["yoy_already"])
            cpi_yoy[code] = y
            print(f"  {code} YoY : {len(y):>3} months, range {y.index[0].date()} → {y.index[-1].date()}")
        except Exception as exc:
            print(f"  {code} : FAILED ({exc}) — dropping from universe")

    # ── Align all CPI YoY series + US YoY on a common monthly grid ─────────
    cpi_df = pd.DataFrame(cpi_yoy)
    us_yoy_m = us_yoy.copy()
    cpi_df, us_yoy_m = cpi_df.align(us_yoy_m, axis=0, join="outer")

    # AU and NZ are quarterly — forward-fill so they're sortable monthly
    cpi_df = cpi_df.resample("MS").last()
    us_yoy_m = us_yoy_m.resample("MS").last()
    cpi_df = cpi_df.ffill(limit=3)
    us_yoy_m = us_yoy_m.ffill(limit=3)

    # Differential vs US
    diff_df = cpi_df.sub(us_yoy_m, axis=0)
    diff_df = diff_df.dropna(how="all")

    # ── Fetch FX prices and align to daily business calendar ──────────────
    print("\nFetching FX prices...")
    fx_strength = {}
    for code, spec in CURRENCIES.items():
        if code not in cpi_yoy:
            continue
        fx_strength[code] = _fetch_currency_strength(spec)
        print(f"  {code}: {len(fx_strength[code])} daily rows")

    daily_idx = pd.bdate_range(start=START, end=END)
    fx_df = pd.DataFrame(fx_strength).reindex(daily_idx).ffill()
    fx_ret = fx_df.pct_change()

    # ── Build monthly target weights from the diff series ─────────────────
    target_w_monthly = pd.DataFrame(0.0, index=diff_df.index, columns=diff_df.columns)
    leg_weight = 1.0 / (N_LONG + N_SHORT)
    for date in diff_df.index:
        diffs = diff_df.loc[date].dropna()
        if len(diffs) < (N_LONG + N_SHORT):
            continue
        ranks = diffs.rank(method="first")
        n = len(diffs)
        # Top N_LONG by diff → LONG
        long_mask = ranks > (n - N_LONG)
        # Bottom N_SHORT by diff → SHORT
        short_mask = ranks <= N_SHORT
        for c in diffs.index:
            if long_mask[c]:
                target_w_monthly.loc[date, c] = +leg_weight
            elif short_mask[c]:
                target_w_monthly.loc[date, c] = -leg_weight

    # ── Project monthly weights onto the daily grid (carry forward) ───────
    weights_daily = target_w_monthly.reindex(daily_idx).ffill().fillna(0.0)
    weights_lag = weights_daily.shift(1).fillna(0.0)

    # ── P&L and cost ──────────────────────────────────────────────────────
    gross_per = weights_lag * fx_ret
    gross_port = gross_per.sum(axis=1)

    cost_per_unit_pips = COST_ROUND_TRIP_PIPS / 2.0
    turnover = weights_lag.diff().abs().fillna(0)
    # Cost in % of NAV: turnover × half-spread / spot. For pairs that are 1/spot
    # the "pip in NAV terms" is approximately the same magnitude — apply to
    # the underlying yfinance quote for pip-to-percent conversion.
    cost_total = pd.Series(0.0, index=daily_idx)
    for code, spec in CURRENCIES.items():
        if code not in turnover.columns:
            continue
        # Recover the yfinance quote so we can do pip-percent correctly
        raw_pair = fx_df[code]  # foreign in USD
        # If pair was originally USDxxx, spot = 1 / raw_pair
        spot = (1.0 / raw_pair) if not spec["usd_quote"] else raw_pair
        cost_code = turnover[code] * (cost_per_unit_pips * spec["pip"]) / spot
        cost_total = cost_total.add(cost_code, fill_value=0)

    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")
    avg_gross_exposure = weights_lag.abs().sum(axis=1).mean()
    n_rebalances = int((target_w_monthly.diff().abs().sum(axis=1) > 0).sum())

    print()
    print("=" * 80)
    print(f"  Strategy #32 — Cross-sectional inflation-differential momentum on G10 FX")
    print("=" * 80)
    print(f"  Sample                   : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Observations             : {len(net_port):,}")
    print(f"  Rebalances               : {n_rebalances} monthly")
    print(f"  Avg portfolio gross expo : {avg_gross_exposure*100:5.1f}%  (target: 100%)")
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
    print("=" * 80)

    # Per-currency time-in-market
    print()
    print(f"Per-currency time-in-market (fraction of days):")
    print(f"  {'CCY':<6} {'Long %':>8} {'Short %':>9} {'Active %':>10}")
    for code in CURRENCIES:
        if code not in weights_lag.columns:
            continue
        n = len(weights_lag)
        long_pct  = (weights_lag[code] > 0).sum() / n * 100
        short_pct = (weights_lag[code] < 0).sum() / n * 100
        print(f"  {code:<6} {long_pct:>7.1f}% {short_pct:>8.1f}% {long_pct + short_pct:>9.1f}%")

    # ── Reference: how the literature predicts vs our result ──────────────
    print()
    print(f"  REFERENCE — Molodtsova & Papell (2009, JIE) Taylor-rule prediction:")
    print(f"    Out-of-sample beats random walk for 11/12 G10 pairs at 1m horizon")
    print(f"    Implied Sharpe of ~0.3-0.5 net at monthly rebalance on G10")
    print(f"    This run  : Sharpe {s_net['sharpe']:+.2f} net, {s_gross['sharpe']:+.2f} gross")
    if s_net["sharpe"] > 0.3:
        print(f"  ▶︎ ✅ Material positive — inflation-differential signal works on G10 FX.")
    elif s_net["sharpe"] > 0.0:
        print(f"  ▶︎ ⚠️  Modestly positive — partial confirmation of the literature.")
    elif s_net["sharpe"] > -0.2:
        print(f"  ▶︎ ⚠️  Near zero — inflation signal doesn't extract material edge.")
    else:
        print(f"  ▶︎ ❌ Negative — yet another macro signal fails on G10 FX in 2010-2024.")

    # ── Plot ───────────────────────────────────────────────────────────────
    net_curve = (1 + net_port).cumprod()
    gross_curve = (1 + gross_port.loc[net_port.index]).cumprod()
    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(gross_curve.index, gross_curve.values, color="#1f77b4", lw=1.2, alpha=0.55,
            label=f"Gross (Sharpe {s_gross['sharpe']:.2f})")
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"Net of {COST_ROUND_TRIP_PIPS:.0f} pips RT (Sharpe {s_net['sharpe']:.2f})")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (×)")
    ax.set_title(
        f"Strategy #32 — Cross-sectional inflation differential on G10 FX (Taylor rule)\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"long top-{N_LONG} / short bottom-{N_SHORT} by CPI YoY vs US, monthly rebalance"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    dd = (net_curve / net_curve.cummax()) - 1
    ax.fill_between(dd.index, dd.values, 0, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown (net)")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    gross_exposure = weights_lag.abs().sum(axis=1).loc[net_port.index]
    ax.plot(gross_exposure.index, gross_exposure.values, color="#d62728", lw=0.5)
    ax.fill_between(gross_exposure.index, gross_exposure.values, 0, color="#d62728", alpha=0.2)
    ax.set_ylabel("Gross exposure")
    ax.set_ylim(0, 1.10)
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_32_inflation_differential_fx.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["gross_exposure"] = weights_lag.abs().sum(axis=1).loc[net_port.index]
        for code in CURRENCIES:
            if code in weights_lag.columns:
                out_df[f"weight_{code}"] = weights_lag[code].loc[net_port.index]
        out_df["cum_gross"] = (1 + gross_port.loc[net_port.index]).cumprod()
        out_df["cum_net"]   = net_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(net=s_net, gross=s_gross, calmar=calmar,
                avg_gross_exposure=float(avg_gross_exposure),
                n_rebalances=n_rebalances, n_obs=len(net_port))


if __name__ == "__main__":
    if not os.environ.get("FRED_API_KEY"):
        print("\nERROR: FRED_API_KEY env var not set. Get a free key at "
              "https://fred.stlouisfed.org/docs/api/api_key.html")
        sys.exit(1)
    run(csv_out=TRACK / "strategy_32_inflation_differential_fx_track_record.csv")
