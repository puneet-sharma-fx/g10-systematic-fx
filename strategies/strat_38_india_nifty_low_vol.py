"""
Strategy #38 — Nifty 100 Low-Volatility (annual rebalance, long-only)

First Indian-equities strategy in this repo. Motivated by the research at
research/india_equities.md §1.2: the low-vol anomaly is the best
risk-adjusted return in Indian equities, with an 18.5-year NSE backtest
(backtestindia.com, Dec 2006 – Jun 2025) showing:

    Low-Vol (top-100 by mcap, 30 lowest-vol) : CAGR 12.85%, SR 0.47
    Nifty 50 benchmark                       : CAGR 10.42%, SR 0.32
    Low-Vol max DD                           : −44.46%   (Nifty −55.12%)
    10-year rolling win rate                 : 100/100

Backed by:
  - Frazzini & Pedersen (2014, JFE) — "Betting Against Beta"
  - Raju (SSRN 4398656) — India-specific low-risk anomaly on 4,400 stocks
  - Joshipura (SSRN 2672764) — Confirmation on S&P CNX 200 2004–2013
  - NSE live indices: Nifty100 Low Volatility 30, Nifty Low Volatility 50
  - Live funds: DSP, Nippon India, Motilal Oswal low-vol products

Why this spec is the right first India build:
  - Different asset class + different anomaly from anything tested here
    (this repo has demonstrated FX momentum FAILS, crypto momentum WORKS,
    but has never touched Indian equities or the low-vol factor).
  - Annual rebalance sidesteps India's STT drag (~0.1% per side) that
    would kill a monthly strategy.
  - Long-only means no shorts to fund, no borrow costs.
  - Public data only (yfinance .NS tickers).

Spec (per research/india_equities.md §1.2):
  - Universe : Top-100 Nifty large caps by market cap (approximated by a
               hardcoded list of ~100 tickers — survivorship-biased,
               documented explicitly below).
  - Signal   : Trailing 252-trading-day realised volatility of daily
               returns.
  - Rebalance: Annually on the last trading day of January.
  - Selection: Bottom 30 by realised vol (lowest 30 stocks are picked).
  - Weighting: Equal weight = 1/30 per position.
  - Cost     : 20 bps round-trip per unit of turnover (per doc:
               "annual rebalance = minimal STT drag (0.2% STT +
               brokerage)"). This is 10 bps per unit of one-way turnover.
  - Period   : 2010-01-01 → 2024-12-31.

CRITICAL CAVEAT — Survivorship bias:
  The universe is a hardcoded list of ~100 tickers based on the recent
  Nifty 100 composition. This means:
    (a) Stocks that were in the Nifty 100 in 2010–2020 but have since
        dropped out are NOT in the universe. Bias: unclear direction —
        droppers were often high-vol failures (favours strategy) but
        occasionally were acquired at premiums (mixed).
    (b) Stocks that entered the Nifty 100 later (LICI 2022, PAYTM 2021,
        ZOMATO 2021, LTIM 2022) enter the eligibility universe naturally
        as yfinance data becomes available.
  Impact on results should be flagged when comparing to the
  backtestindia.com 0.47 Sharpe benchmark. A proper reproduction requires
  point-in-time NSE constituent data (paid).

Benchmarks:
  - Nifty 50 buy-and-hold (^NSEI on yfinance) — the doc's primary benchmark
  - Nifty 100 buy-and-hold (approximated by equal-weight of universe)
  - Equal-weight of universe, annually rebalanced (matches strategy's
    rebal cadence — apples-to-apples test of whether vol-ranking adds
    value above naive diversification)

Pre-registered pass criteria:
  1. Net Sharpe > Nifty 50 B&H Sharpe.
  2. Net Sharpe within striking distance of the doc's cited 0.47
     (allowing for survivorship bias, cost model differences, and the
     2010–2024 vs 2006–2025 sample difference).
  3. MaxDD strictly better (less negative) than Nifty 50.
  4. Beats equal-weight universe rebalance (IR > 0) — proves the vol
     ranking adds value above naive diversification.
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
VOL_LOOKBACK_DAYS = 252            # trailing 12M realised vol
N_SELECTED         = 30            # bottom 30 by vol (as in NSE Nifty100 Low Vol 30)
MIN_HISTORY_DAYS   = 252           # need ≥ 1Y data to be eligible
REBAL_MONTH        = 1             # January
REBAL_DAY_OF_MONTH = 31            # last trading day of Jan (adjusted to actual last trading day)
COST_RT_BPS        = 20.0          # STT + brokerage per doc §1.2 (2×0.1% STT ≈ 20 bps RT)
TRADING_DAYS       = 252
START              = "2010-01-01"
END                = "2024-12-31"

# ── Universe: recent Nifty 100 composition ──────────────────────────────────
# Hardcoded from public Nifty 100 constituent list (approximate, survivorship-
# biased — see docstring caveat). yfinance appends .NS for NSE tickers.
UNIVERSE = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "HINDUNILVR",
    "BHARTIARTL", "ITC", "LT", "KOTAKBANK", "SBIN", "AXISBANK",
    "ASIANPAINT", "MARUTI", "BAJFINANCE", "HCLTECH", "TITAN", "SUNPHARMA",
    "ADANIENT", "ULTRACEMCO", "ONGC", "WIPRO", "NESTLEIND", "TATAMOTORS",
    "ADANIPORTS", "POWERGRID", "NTPC", "JSWSTEEL", "TATASTEEL", "BAJAJFINSV",
    "HDFCLIFE", "SBILIFE", "TECHM", "CIPLA", "DIVISLAB", "BRITANNIA",
    "EICHERMOT", "GRASIM", "TATACONSUM", "DRREDDY", "COALINDIA", "HEROMOTOCO",
    "INDUSINDBK", "HINDALCO", "BAJAJ-AUTO", "APOLLOHOSP", "M&M", "BPCL",
    "IOC", "ADANIGREEN", "LTIM", "PIDILITIND", "SIEMENS", "DABUR",
    "DLF", "SHREECEM", "GODREJCP", "MARICO", "HAVELLS", "BAJAJHLDNG",
    "ICICIPRULI", "ICICIGI", "INDIGO", "HDFCAMC", "AMBUJACEM", "BOSCHLTD",
    "TORNTPHARM", "CHOLAFIN", "VEDL", "GAIL", "PIIND", "SBICARD",
    "PGHH", "MCDOWELL-N", "BERGEPAINT", "COLPAL", "JINDALSTEL", "DMART",
    "SRF", "MOTHERSON", "MRF", "BEL", "LICI", "HINDPETRO",
    "TATAPOWER", "TVSMOTOR", "ZOMATO", "PNB", "BANDHANBNK", "IDFCFIRSTB",
    "BANKBARODA", "CANBK", "VOLTAS", "BIOCON", "NAUKRI", "DIXON",
    "MFSL", "INDHOTEL", "LUPIN", "ABB", "TRENT", "PAGEIND",
]


def _fetch_close(ticker: str) -> pd.Series | None:
    try:
        df = yf.download(f"{ticker}.NS", start=START, end=END,
                         auto_adjust=True, progress=False)
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
        return dict(sharpe=0.0, ann_ret=0.0, ann_vol=0.0, max_dd=0.0, cum=0.0, hit=0.0, sortino=0.0, cagr=0.0)
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
                cum=float(curve.iloc[-1] - 1), hit=hit, sortino=sortino, cagr=cagr)


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #38 — Nifty 100 Low-Volatility (annual rebalance)")
    print(f"  Universe        : {len(UNIVERSE)} Indian large-cap tickers (survivorship-biased)")
    print(f"  Vol lookback    : {VOL_LOOKBACK_DAYS} trading days (12M)")
    print(f"  Selected        : bottom {N_SELECTED} by trailing vol, equal-weight")
    print(f"  Rebalance       : annual (January-end)")
    print(f"  Cost            : {COST_RT_BPS} bps RT per unit of turnover")
    print()

    print(f"  Fetching prices for {len(UNIVERSE)} tickers via yfinance...")
    price_by_ticker: dict[str, pd.Series] = {}
    failed = []
    for i, ticker in enumerate(UNIVERSE):
        s = _fetch_close(ticker)
        if s is not None and len(s) >= MIN_HISTORY_DAYS:
            price_by_ticker[ticker] = s
        else:
            failed.append(ticker)
        if (i + 1) % 20 == 0:
            print(f"    ...{i+1}/{len(UNIVERSE)} fetched, {len(failed)} failed so far")
    print(f"  Successfully fetched : {len(price_by_ticker)} / {len(UNIVERSE)}")
    if failed:
        print(f"  Failed              : {', '.join(failed[:10])}{' ...' if len(failed) > 10 else ''}")

    tickers = sorted(price_by_ticker.keys())
    idx = pd.bdate_range(start=START, end=END)
    price_df = pd.DataFrame(index=idx, columns=tickers, dtype=float)
    first_date_by_ticker: dict[str, pd.Timestamp] = {}
    for t in tickers:
        price_df[t] = price_by_ticker[t].reindex(idx).ffill()
        first_date_by_ticker[t] = price_by_ticker[t].index.min()

    daily_ret = price_df.pct_change()

    # Eligibility: need >= MIN_HISTORY_DAYS of data by date t
    eligible = pd.DataFrame(False, index=idx, columns=tickers)
    for t in tickers:
        first_valid = price_by_ticker[t].index.min()
        elig_from = first_valid + pd.Timedelta(days=int(MIN_HISTORY_DAYS * 365 / 252))
        eligible[t] = idx >= elig_from

    # Rebalance dates: last business day of January each year
    rebal_dates = []
    for year in range(2010, 2025):
        jan_end = pd.Timestamp(f"{year}-01-31")
        # snap to previous business day if not itself
        while jan_end not in idx:
            jan_end -= pd.Timedelta(days=1)
            if jan_end.year < year:
                break
        if jan_end in idx and jan_end.year == year:
            rebal_dates.append(jan_end)
    rebal_dates = pd.DatetimeIndex(rebal_dates)
    print(f"  Rebalance dates : {len(rebal_dates)} ({rebal_dates[0].date()} → {rebal_dates[-1].date()})")

    # Trailing 12M realised vol at each rebal date
    rolling_vol = daily_ret.rolling(VOL_LOOKBACK_DAYS, min_periods=int(VOL_LOOKBACK_DAYS * 0.8)).std() * np.sqrt(TRADING_DAYS)

    # Build target weights on rebal dates
    target_w = pd.DataFrame(0.0, index=idx, columns=tickers)
    picks_by_year = {}
    for d in rebal_dates:
        rv = rolling_vol.loc[d]
        rv = rv.where(eligible.loc[d]).dropna()
        if len(rv) < N_SELECTED:
            print(f"    {d.date()}: only {len(rv)} eligible stocks — skipping (need {N_SELECTED})")
            continue
        picks = rv.nsmallest(N_SELECTED).index.tolist()
        w = pd.Series(0.0, index=tickers)
        w.loc[picks] = 1.0 / N_SELECTED
        target_w.loc[d] = w.values
        picks_by_year[d.year] = picks

    # Forward-fill weights only on rebal dates (hold until next rebal)
    rebal_mask_1d = pd.Series(idx.isin(rebal_dates), index=idx)
    rebal_mask = pd.DataFrame(
        np.broadcast_to(rebal_mask_1d.values[:, None], target_w.shape),
        index=idx, columns=tickers,
    )
    target_w = target_w.where(rebal_mask, np.nan).ffill().fillna(0.0)

    weights_lag = target_w.shift(1).fillna(0.0)
    gross_port = (weights_lag * daily_ret.fillna(0.0)).sum(axis=1)

    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0
    turnover = weights_lag.diff().abs().fillna(0.0)
    cost_total = turnover.sum(axis=1) * cost_per_unit

    # Trim to first active day
    first_active = rebal_dates[0] + pd.Timedelta(days=1)
    gross_port = gross_port.loc[gross_port.index >= first_active]
    cost_total = cost_total.loc[cost_total.index >= first_active]
    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    # ── Benchmarks ──────────────────────────────────────────────────────
    print()
    print(f"  Fetching benchmarks...")
    nifty50 = _fetch_close("^NSEI")  # yfinance uses ^NSEI for Nifty 50; .NS suffix isn't applied here — let's fix
    # Above call fetches "^NSEI.NS" which is wrong. Fetch directly:
    try:
        nifty50_df = yf.download("^NSEI", start=START, end=END, auto_adjust=True, progress=False)
        n50 = nifty50_df["Close"].squeeze()
        n50.index = pd.to_datetime(n50.index)
    except Exception:
        n50 = None
    n50_ret = n50.pct_change().reindex(net_port.index).fillna(0.0) if n50 is not None else pd.Series(0.0, index=net_port.index)
    s_n50 = _stats(n50_ret)

    # Equal-weight passive of the universe, annually rebalanced
    ew_target = eligible.astype(float)
    ew_target = ew_target.div(ew_target.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    ew_target = ew_target.where(rebal_mask, np.nan).ffill().fillna(0.0)
    ew_lag = ew_target.shift(1).fillna(0.0)
    ew_ret = (ew_lag * daily_ret.fillna(0.0)).sum(axis=1)
    ew_turn = ew_lag.diff().abs().fillna(0.0).sum(axis=1)
    ew_cost = ew_turn * cost_per_unit
    ew_net = (ew_ret - ew_cost).reindex(net_port.index).fillna(0.0)
    s_ew = _stats(ew_net)

    # ── Print ────────────────────────────────────────────────────────────
    print()
    print("=" * 92)
    print(f"  Strategy #38 — Nifty 100 Low-Vol 30, annual rebalance, long-only")
    print("=" * 92)
    print(f"  Sample                : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Observations          : {len(net_port):,} trading days ({len(net_port)/TRADING_DAYS:.1f} years)")
    print(f"  Rebalances            : {len(rebal_dates)}")
    print(f"  Cumulative cost drag  : {cost_total.sum()*100:5.2f}%")
    print()
    print(f"  {'':<20} {'GROSS':>11} {'NET':>11} {'Nifty 50':>11} {'EW univ':>11}")
    print(f"  {'CAGR':<20} {s_gross['cagr']*100:>10.2f}% {s_net['cagr']*100:>10.2f}% {s_n50['cagr']*100:>10.2f}% {s_ew['cagr']*100:>10.2f}%")
    print(f"  {'Ann Return':<20} {s_gross['ann_ret']*100:>10.2f}% {s_net['ann_ret']*100:>10.2f}% {s_n50['ann_ret']*100:>10.2f}% {s_ew['ann_ret']*100:>10.2f}%")
    print(f"  {'Ann Vol':<20} {s_gross['ann_vol']*100:>10.2f}% {s_net['ann_vol']*100:>10.2f}% {s_n50['ann_vol']*100:>10.2f}% {s_ew['ann_vol']*100:>10.2f}%")
    print(f"  {'Sharpe':<20} {s_gross['sharpe']:>11.2f} {s_net['sharpe']:>11.2f} {s_n50['sharpe']:>11.2f} {s_ew['sharpe']:>11.2f}")
    print(f"  {'Sortino':<20} {s_gross['sortino']:>11.2f} {s_net['sortino']:>11.2f} {s_n50['sortino']:>11.2f} {s_ew['sortino']:>11.2f}")
    print(f"  {'MaxDD':<20} {s_gross['max_dd']*100:>10.2f}% {s_net['max_dd']*100:>10.2f}% {s_n50['max_dd']*100:>10.2f}% {s_ew['max_dd']*100:>10.2f}%")
    print(f"  {'Calmar (net)':<20} {'':>11} {calmar:>11.2f}")
    print(f"  {'Cumulative':<20} {s_gross['cum']*100:>10.0f}% {s_net['cum']*100:>10.0f}% {s_n50['cum']*100:>10.0f}% {s_ew['cum']*100:>10.0f}%")
    print("=" * 92)

    # ── IR vs benchmarks ────────────────────────────────────────────────
    excess_n50 = net_port - n50_ret
    excess_ew  = net_port - ew_net
    ir_n50 = float(excess_n50.mean() * TRADING_DAYS / (excess_n50.std() * np.sqrt(TRADING_DAYS))) if excess_n50.std() > 0 else 0.0
    ir_ew  = float(excess_ew.mean()  * TRADING_DAYS / (excess_ew.std()  * np.sqrt(TRADING_DAYS))) if excess_ew.std()  > 0 else 0.0
    print()
    print("Excess-return diagnostics:")
    print(f"  IR vs Nifty 50 B&H   : {ir_n50:+.2f}  (ann. excess {excess_n50.mean()*TRADING_DAYS*100:+.2f}%, TE {excess_n50.std()*np.sqrt(TRADING_DAYS)*100:.2f}%)")
    print(f"  IR vs EW universe    : {ir_ew:+.2f}  (ann. excess {excess_ew.mean()*TRADING_DAYS*100:+.2f}%, TE {excess_ew.std()*np.sqrt(TRADING_DAYS)*100:.2f}%)")

    # ── Verdict ─────────────────────────────────────────────────────────
    print()
    print("VERDICT (pre-registered criteria):")
    c1 = s_net["sharpe"] > s_n50["sharpe"]
    c2 = s_net["sharpe"] > 0.30                     # meaningful positive Sharpe (allowing for surv-bias vs 0.47 cited)
    c3 = s_net["max_dd"] > s_n50["max_dd"]          # less negative = better
    c4 = ir_ew > 0.0
    print(f"  1. Beats Nifty 50 Sharpe            : {'PASS' if c1 else 'FAIL'} ({s_net['sharpe']:+.2f} vs {s_n50['sharpe']:+.2f})")
    print(f"  2. Net Sharpe > 0.30                : {'PASS' if c2 else 'FAIL'} ({s_net['sharpe']:+.2f})")
    print(f"  3. MaxDD better (less neg) than N50 : {'PASS' if c3 else 'FAIL'} ({s_net['max_dd']*100:.1f}% vs {s_n50['max_dd']*100:.1f}%)")
    print(f"  4. IR > 0 vs EW universe rebal      : {'PASS' if c4 else 'FAIL'} ({ir_ew:+.2f})")
    n_pass = int(c1) + int(c2) + int(c3) + int(c4)
    if n_pass == 4:
        print(f"  ▶︎ ✅ CLEAN WIN — all 4 criteria met. Indian low-vol anomaly reproduced.")
    elif n_pass >= 2:
        print(f"  ▶︎ ⚠️  {n_pass}/4 — partial validation; check which criteria failed.")
    else:
        print(f"  ▶︎ ❌ {n_pass}/4 — anomaly does not reproduce on this universe/spec.")

    # ── Plot ────────────────────────────────────────────────────────────
    net_curve = (1 + net_port).cumprod()
    n50_curve = (1 + n50_ret).cumprod()
    ew_curve  = (1 + ew_net).cumprod()

    fig, axes = plt.subplots(2, 1, figsize=(13, 9),
                             gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2,
            label=f"#38 Low-Vol 30 net (SR {s_net['sharpe']:.2f}, CAGR {s_net['cagr']*100:.1f}%)")
    ax.plot(ew_curve.index, ew_curve.values, color="#7f7f7f", lw=1.2,
            label=f"EW universe passive (SR {s_ew['sharpe']:.2f}, CAGR {s_ew['cagr']*100:.1f}%)")
    ax.plot(n50_curve.index, n50_curve.values, color="#1f77b4", lw=1.2,
            label=f"Nifty 50 B&H (SR {s_n50['sharpe']:.2f}, CAGR {s_n50['cagr']*100:.1f}%)")
    ax.set_yscale("log")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (× log)")
    ax.set_title(
        f"Strategy #38 — Nifty 100 Low-Vol 30 (annual rebal, long-only)  ·  "
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}\n"
        f"Universe {len(tickers)} tickers (surv-biased)  ·  "
        f"IR vs N50 {ir_n50:+.2f}  ·  IR vs EW {ir_ew:+.2f}"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, which="both")

    ax = axes[1]
    dd_strat = (net_curve / net_curve.cummax()) - 1
    dd_n50   = (n50_curve / n50_curve.cummax()) - 1
    ax.fill_between(dd_strat.index, dd_strat.values, 0, color="#2ca02c", alpha=0.4, label="#38 DD")
    ax.fill_between(dd_n50.index,   dd_n50.values,   0, color="#1f77b4", alpha=0.25, label="Nifty 50 DD")
    ax.set_ylabel("Drawdown")
    ax.set_xlabel("Date")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_38_india_nifty_low_vol.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # ── CSV ─────────────────────────────────────────────────────────────
    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["nifty50_return"] = n50_ret
        out_df["ew_universe_return"] = ew_net
        out_df["cum_net"]      = net_curve
        out_df["cum_n50"]      = n50_curve
        out_df["cum_ew"]       = ew_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df):,} rows)")

    # ── Print picks per year for auditability ───────────────────────────
    print()
    print("Annual picks (bottom-30 by trailing 12M vol):")
    for year in sorted(picks_by_year.keys())[:3]:
        print(f"  {year} ({len(picks_by_year[year])} stocks): {', '.join(picks_by_year[year][:15])}, ...")
    print(f"  ... ({len(picks_by_year)} rebals total)")

    return dict(
        net=s_net, gross=s_gross, nifty50=s_n50, ew=s_ew,
        ir_vs_n50=ir_n50, ir_vs_ew=ir_ew, calmar=calmar,
        n_obs=len(net_port), n_rebals=len(rebal_dates),
        n_universe=len(tickers),
        criteria_passed=n_pass,
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_38_india_nifty_low_vol_track_record.csv")
