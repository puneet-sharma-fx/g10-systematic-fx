"""
Strategy #39 — US SPDR sector 12-1 cross-sectional momentum

Classic Jegadeesh-Titman (1993, JoF) applied to the 11 SPDR sector ETFs.
Signal = trailing 12-month total return, skipping the most recent month
(the "12-1" standard from JT to avoid the well-known 1-month reversal
effect at the individual-stock level). Monthly rebalance, long top-3
equal-weight.

Why this spec is worth testing now:
  - Sector-level momentum has not been directly tested in this repo.
  - #33 (SPY 200-DMA) was borderline; #34 (Faber 5-asset GTAA) was rejected.
    Both were TIMING rules on a single index or a broad multi-asset basket.
  - This is a CROSS-SECTIONAL ranking within US equities — a different
    signal shape and the exact one that worked spectacularly on crypto
    (#35, robustness-confirmed by #37). Same structural bet — momentum
    picks the strongest constituents of a coherent universe.
  - Sector momentum has a long academic history (Moskowitz-Grinblatt 1999,
    Chen-De Bondt 2004). Post-2010 evidence is mixed — some regime
    dependence — but it's never been cleanly tested vs SPY on 2010-2024
    with proper JT construction here.

Spec (per research/fx_signals_advanced.md and Jegadeesh-Titman 1993):
  - Universe : 11 SPDR sector ETFs (XLK/XLF/XLE/XLV/XLI/XLY/XLP/XLU/XLB/XLRE/XLC)
  - Signal   : Trailing 12M total return, skipping most recent month
               (i.e. sum of daily returns over t-252 to t-21).
  - Portfolio: Long top-3, equal-weight (1/3 per position), long-only.
  - Rebalance: Monthly (last trading day of month).
  - Cost     : 5 bps RT per leg (US ETFs, retail cost, deliberately
               non-trivial to avoid ETF-cost-arbitrage illusion).
  - Staggered: XLRE listed 2015-10, XLC listed 2018-06 — enter the
               ranking universe naturally as data becomes available.
               Require ≥ 252 trading days of history before eligibility.

Benchmarks:
  - SPY buy-and-hold (the natural "did I add alpha vs the index?" test)
  - Equal-weight of eligible sectors, monthly rebalanced (apples-to-apples
    test of whether the momentum ranking adds anything above naive
    diversification of the same universe)

Pre-registered pass criteria:
  1. Net Sharpe > 0.5 (deployable prior)
  2. Beats SPY B&H Sharpe
  3. IR > 0.20 vs equal-weight passive of same universe (proves the
     momentum ranking adds value beyond mere sector diversification)
  4. At least 3 of 5 sub-period Sharpes are positive (regime robustness)

If all pass → sector momentum works, extends the successful #35 pattern
into a second asset class.
If (1) and (2) pass but (3) fails → same pathology as #38 India low-vol
(strategy beats cap-weighted index but not equal-weight of universe).
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

# ── Strategy parameters ─────────────────────────────────────────────────────
LOOKBACK_DAYS       = 252     # trailing 12M
SKIP_DAYS           = 21      # skip last 1M (JT standard)
MIN_HISTORY_DAYS    = 252     # eligibility requirement
TOP_N               = 3
COST_RT_BPS         = 5.0     # US ETF retail cost
TRADING_DAYS        = 252
REBALANCE_FREQ      = "ME"    # month-end
START               = "2010-01-01"
END                 = "2024-12-31"

UNIVERSE = [
    ("XLK",  "Technology"),
    ("XLF",  "Financials"),
    ("XLE",  "Energy"),
    ("XLV",  "Health Care"),
    ("XLI",  "Industrials"),
    ("XLY",  "Consumer Discretionary"),
    ("XLP",  "Consumer Staples"),
    ("XLU",  "Utilities"),
    ("XLB",  "Materials"),
    ("XLRE", "Real Estate"),
    ("XLC",  "Communication Services"),
]


def _fetch_close(ticker: str) -> pd.Series | None:
    try:
        df = yf.download(ticker, start=START, end=END, auto_adjust=True, progress=False)
        if df.empty:
            return None
        s = df["Close"].dropna()
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        s.index = pd.to_datetime(s.index)
        s.name = ticker
        return s.sort_index()
    except Exception:
        return None


def _stats(returns: pd.Series) -> dict:
    returns = returns.dropna()
    if len(returns) == 0:
        return dict(sharpe=0.0, ann_ret=0.0, ann_vol=0.0, max_dd=0.0, cum=0.0, cagr=0.0, sortino=0.0, hit=0.0)
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    dvol    = float(returns[returns < 0].std() * np.sqrt(TRADING_DAYS))
    sortino = ann_ret / dvol if dvol > 0 else 0.0
    n_years = len(returns) / TRADING_DAYS
    cagr    = float((curve.iloc[-1]) ** (1 / n_years) - 1) if n_years > 0 else 0.0
    return dict(sharpe=sharpe, ann_ret=ann_ret, ann_vol=ann_vol, max_dd=max_dd,
                cum=float(curve.iloc[-1] - 1), cagr=cagr, sortino=sortino, hit=hit)


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #39 — US SPDR sector 12-1 cross-sectional momentum")
    print(f"  Universe          : {len(UNIVERSE)} SPDR sector ETFs")
    print(f"  Lookback          : {LOOKBACK_DAYS}d ({LOOKBACK_DAYS/21:.0f}M), skip last {SKIP_DAYS}d")
    print(f"  Top-N             : {TOP_N} (long-only, equal-weight)")
    print(f"  Rebalance         : monthly")
    print(f"  Cost              : {COST_RT_BPS} bps RT per leg")
    print()

    print(f"  Fetching prices...")
    price_by_ticker: dict[str, pd.Series] = {}
    for ticker, name in UNIVERSE:
        s = _fetch_close(ticker)
        if s is not None:
            price_by_ticker[ticker] = s
            print(f"    {ticker:<5} ({name:<24}): {len(s):>5} rows, {s.index[0].date()} → {s.index[-1].date()}")
        else:
            print(f"    {ticker:<5} ({name}): FAILED")

    tickers = [t for t, _ in UNIVERSE if t in price_by_ticker]
    idx = pd.bdate_range(start=START, end=END)
    price_df = pd.DataFrame(index=idx, columns=tickers, dtype=float)
    first_date: dict[str, pd.Timestamp] = {}
    for t in tickers:
        price_df[t] = price_by_ticker[t].reindex(idx).ffill()
        first_date[t] = price_by_ticker[t].index.min()

    # Eligibility mask: need ≥ MIN_HISTORY_DAYS from first_date
    eligible = pd.DataFrame(False, index=idx, columns=tickers)
    for t in tickers:
        elig_from = first_date[t] + pd.Timedelta(days=int(MIN_HISTORY_DAYS * 365 / 252))
        eligible[t] = idx >= elig_from

    # 12-1 momentum signal: return from t-252 to t-21
    ret_signal = (price_df.shift(SKIP_DAYS) / price_df.shift(LOOKBACK_DAYS)) - 1.0
    ret_signal = ret_signal.where(eligible, np.nan)

    # Rebalance dates: last business day of month
    rebal_dates = pd.date_range(start=START, end=END, freq=REBALANCE_FREQ).intersection(idx)

    # Build target weights on rebal dates
    target_w = pd.DataFrame(0.0, index=idx, columns=tickers)
    for d in rebal_dates:
        sig = ret_signal.loc[d].dropna()
        if sig.empty:
            continue
        n_pick = min(TOP_N, len(sig))
        winners = sig.nlargest(n_pick).index.tolist()
        w = pd.Series(0.0, index=tickers)
        w.loc[winners] = 1.0 / n_pick
        target_w.loc[d] = w.values

    # Hold weights until next rebal (forward-fill from rebal dates only)
    rebal_mask_1d = pd.Series(idx.isin(rebal_dates), index=idx)
    rebal_mask = pd.DataFrame(
        np.broadcast_to(rebal_mask_1d.values[:, None], target_w.shape),
        index=idx, columns=tickers,
    )
    target_w = target_w.where(rebal_mask, np.nan).ffill().fillna(0.0)

    weights_lag = target_w.shift(1).fillna(0.0)
    daily_ret = price_df.pct_change().fillna(0.0)
    gross_port = (weights_lag * daily_ret).sum(axis=1)

    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0
    turnover = weights_lag.diff().abs().fillna(0.0)
    cost_total = turnover.sum(axis=1) * cost_per_unit

    first_active = rebal_dates[0] + pd.Timedelta(days=1)
    gross_port = gross_port.loc[gross_port.index >= first_active]
    cost_total = cost_total.loc[cost_total.index >= first_active]
    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    # ── Benchmarks ──────────────────────────────────────────────────────
    spy = _fetch_close("SPY")
    spy_ret = spy.pct_change().reindex(net_port.index).fillna(0.0) if spy is not None else pd.Series(0.0, index=net_port.index)
    s_spy = _stats(spy_ret)

    # EW passive of eligible sectors, monthly rebal
    ew_target = eligible.astype(float)
    ew_target = ew_target.div(ew_target.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    ew_target = ew_target.where(rebal_mask, np.nan).ffill().fillna(0.0)
    ew_lag = ew_target.shift(1).fillna(0.0)
    ew_ret = (ew_lag * daily_ret).sum(axis=1)
    ew_turn = ew_lag.diff().abs().fillna(0.0).sum(axis=1)
    ew_cost = ew_turn * cost_per_unit
    ew_net = (ew_ret - ew_cost).reindex(net_port.index).fillna(0.0)
    s_ew = _stats(ew_net)

    # ── Print ────────────────────────────────────────────────────────────
    print()
    print("=" * 88)
    print(f"  Strategy #39 — US SPDR sector 12-1 momentum, long-top-{TOP_N}, monthly")
    print("=" * 88)
    print(f"  Sample                : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Observations          : {len(net_port):,} trading days ({len(net_port)/TRADING_DAYS:.1f} years)")
    print(f"  Rebalances            : {len(rebal_dates)}")
    print(f"  Cumulative cost drag  : {cost_total.sum()*100:5.2f}%")
    print()
    print(f"  {'':<20} {'GROSS':>11} {'NET':>11} {'SPY B&H':>11} {'EW sectors':>12}")
    print(f"  {'CAGR':<20} {s_gross['cagr']*100:>10.2f}% {s_net['cagr']*100:>10.2f}% {s_spy['cagr']*100:>10.2f}% {s_ew['cagr']*100:>11.2f}%")
    print(f"  {'Ann Return':<20} {s_gross['ann_ret']*100:>10.2f}% {s_net['ann_ret']*100:>10.2f}% {s_spy['ann_ret']*100:>10.2f}% {s_ew['ann_ret']*100:>11.2f}%")
    print(f"  {'Ann Vol':<20} {s_gross['ann_vol']*100:>10.2f}% {s_net['ann_vol']*100:>10.2f}% {s_spy['ann_vol']*100:>10.2f}% {s_ew['ann_vol']*100:>11.2f}%")
    print(f"  {'Sharpe':<20} {s_gross['sharpe']:>11.2f} {s_net['sharpe']:>11.2f} {s_spy['sharpe']:>11.2f} {s_ew['sharpe']:>12.2f}")
    print(f"  {'Sortino':<20} {s_gross['sortino']:>11.2f} {s_net['sortino']:>11.2f} {s_spy['sortino']:>11.2f} {s_ew['sortino']:>12.2f}")
    print(f"  {'MaxDD':<20} {s_gross['max_dd']*100:>10.2f}% {s_net['max_dd']*100:>10.2f}% {s_spy['max_dd']*100:>10.2f}% {s_ew['max_dd']*100:>11.2f}%")
    print(f"  {'Calmar (net)':<20} {'':>11} {calmar:>11.2f}")
    print(f"  {'Cumulative':<20} {s_gross['cum']*100:>10.0f}% {s_net['cum']*100:>10.0f}% {s_spy['cum']*100:>10.0f}% {s_ew['cum']*100:>11.0f}%")
    print("=" * 88)

    # ── IR vs benchmarks ────────────────────────────────────────────────
    excess_spy = net_port - spy_ret
    excess_ew  = net_port - ew_net
    ir_spy = float(excess_spy.mean() * TRADING_DAYS / (excess_spy.std() * np.sqrt(TRADING_DAYS))) if excess_spy.std() > 0 else 0.0
    ir_ew  = float(excess_ew.mean()  * TRADING_DAYS / (excess_ew.std()  * np.sqrt(TRADING_DAYS))) if excess_ew.std()  > 0 else 0.0
    print()
    print("Excess-return diagnostics:")
    print(f"  IR vs SPY B&H       : {ir_spy:+.2f}  (ann. excess {excess_spy.mean()*TRADING_DAYS*100:+.2f}%, TE {excess_spy.std()*np.sqrt(TRADING_DAYS)*100:.2f}%)")
    print(f"  IR vs EW sectors    : {ir_ew:+.2f}  (ann. excess {excess_ew.mean()*TRADING_DAYS*100:+.2f}%, TE {excess_ew.std()*np.sqrt(TRADING_DAYS)*100:.2f}%)")

    # ── Sub-period analysis ─────────────────────────────────────────────
    periods = [
        ("2011-2014 recov",  "2011-01-01", "2014-12-31"),
        ("2015-2018 vol",    "2015-01-01", "2018-12-31"),
        ("2019-2020 COVID",  "2019-01-01", "2020-12-31"),
        ("2021-2022 infl",   "2021-01-01", "2022-12-31"),
        ("2023-2024 AI/hike","2023-01-01", "2024-12-31"),
    ]
    print()
    print("Sub-period Sharpe comparison (net):")
    print(f"  {'Period':<20} {'Days':>6} {'Strat':>8} {'SPY':>8} {'EW':>8}")
    n_pos_periods = 0
    for label, ps, pe in periods:
        m = (net_port.index >= ps) & (net_port.index <= pe)
        if not m.any():
            continue
        sp_s = _stats(net_port.loc[m])
        sp_p = _stats(spy_ret.loc[m])
        sp_e = _stats(ew_net.loc[m])
        if sp_s["sharpe"] > 0:
            n_pos_periods += 1
        print(f"  {label:<20} {int(m.sum()):>6} {sp_s['sharpe']:>8.2f} {sp_p['sharpe']:>8.2f} {sp_e['sharpe']:>8.2f}")

    # ── Verdict ─────────────────────────────────────────────────────────
    print()
    print("VERDICT (pre-registered criteria):")
    c1 = s_net["sharpe"] > 0.5
    c2 = s_net["sharpe"] > s_spy["sharpe"]
    c3 = ir_ew > 0.20
    c4 = n_pos_periods >= 3
    print(f"  1. Net Sharpe > 0.5                : {'PASS' if c1 else 'FAIL'} ({s_net['sharpe']:+.2f})")
    print(f"  2. Beats SPY B&H Sharpe            : {'PASS' if c2 else 'FAIL'} ({s_net['sharpe']:+.2f} vs {s_spy['sharpe']:+.2f})")
    print(f"  3. IR vs EW sectors > 0.20         : {'PASS' if c3 else 'FAIL'} ({ir_ew:+.2f})")
    print(f"  4. ≥ 3 of 5 sub-periods positive   : {'PASS' if c4 else 'FAIL'} ({n_pos_periods}/5 positive)")
    n_pass = int(c1) + int(c2) + int(c3) + int(c4)
    if n_pass == 4:
        print(f"  ▶︎ ✅ CLEAN WIN — sector momentum works. Extends #35 pattern to US equities.")
    elif n_pass >= 2:
        print(f"  ▶︎ ⚠️  {n_pass}/4 — partial validation.")
    else:
        print(f"  ▶︎ ❌ {n_pass}/4 — sector momentum does not add value here.")

    # ── Plot ────────────────────────────────────────────────────────────
    net_curve = (1 + net_port).cumprod()
    spy_curve = (1 + spy_ret).cumprod()
    ew_curve  = (1 + ew_net).cumprod()

    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"#39 Sector momentum net (SR {s_net['sharpe']:.2f}, CAGR {s_net['cagr']*100:.1f}%)")
    ax.plot(ew_curve.index, ew_curve.values, color="#7f7f7f", lw=1.2,
            label=f"EW sectors passive (SR {s_ew['sharpe']:.2f}, CAGR {s_ew['cagr']*100:.1f}%)")
    ax.plot(spy_curve.index, spy_curve.values, color="#1f77b4", lw=1.2,
            label=f"SPY B&H (SR {s_spy['sharpe']:.2f}, CAGR {s_spy['cagr']*100:.1f}%)")
    ax.set_yscale("log")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (× log)")
    ax.set_title(
        f"Strategy #39 — US SPDR sector 12-1 momentum, long-top-{TOP_N}, monthly rebal  ·  "
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}\n"
        f"IR vs SPY {ir_spy:+.2f}  ·  IR vs EW sectors {ir_ew:+.2f}"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, which="both")

    ax = axes[1]
    dd_s = (net_curve / net_curve.cummax()) - 1
    dd_p = (spy_curve / spy_curve.cummax()) - 1
    ax.fill_between(dd_s.index, dd_s.values, 0, color="#2ca02c", alpha=0.4, label="#39 DD")
    ax.fill_between(dd_p.index, dd_p.values, 0, color="#1f77b4", alpha=0.25, label="SPY DD")
    ax.set_ylabel("Drawdown")
    ax.set_xlabel("Date")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_39_us_sector_momentum.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["spy_return"]   = spy_ret
        out_df["ew_sectors_return"] = ew_net
        for t in tickers:
            out_df[f"weight_{t}"] = weights_lag[t].reindex(net_port.index).fillna(0.0)
        out_df["cum_net"] = net_curve
        out_df["cum_spy"] = spy_curve
        out_df["cum_ew"]  = ew_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")

    return dict(
        net=s_net, gross=s_gross, spy=s_spy, ew=s_ew,
        ir_vs_spy=ir_spy, ir_vs_ew=ir_ew, calmar=calmar,
        n_obs=len(net_port), n_rebals=len(rebal_dates),
        criteria_passed=n_pass,
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_39_us_sector_momentum_track_record.csv")
