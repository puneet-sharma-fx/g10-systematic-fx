"""
Strategy #35 — Cross-sectional 3-month momentum on crypto majors

Motivation: after #32 (FX inflation-differential — rejected), #33 (SPY 200-DMA
— borderline) and #34 (Faber 5-asset GTAA — rejected), the only pattern that
has repeatedly earned positive net Sharpe in this repo is trend-following on
commodities + crypto (#25, #28, #29). Of those, crypto has been the largest
contributor to per-instrument PnL. Two indirect observations:

  1. Crypto is the highest-vol, most-trending asset class in the universe.
  2. Momentum is the most-documented systematic anomaly across asset classes.

Combining the two: cross-sectional momentum inside crypto — same edge as the
Jegadeesh-Titman equity-momentum result, applied where trends are strongest —
should be the highest-prior spec I have not yet tested.

Spec:
  - Universe (10 majors): BTC, ETH, SOL, BNB, ADA, DOGE, AVAX, LINK, DOT, XRP
    (staggered listings — instruments enter the ranking universe as data
    becomes available; require ≥ 60 days of history to be eligible.)
  - Signal    : trailing 90-calendar-day total return per coin
  - Portfolio : long-only, top-3 by signal, equal-weight (1/3 each)
                Fewer than 3 eligible → equal-weight all eligible (cash rest).
  - Rebalance : monthly (last calendar day of month → weights applied next day)
  - Costs     : 30 bps round-trip per leg (15 bps per unit of turnover).
                Conservative for retail crypto — real spread + fees vary
                widely by venue. Deliberately punitive.
  - Vol scale : none in base spec — equal $ weight per leg. Diagnostic reason:
                if the strategy needs vol-scaling to work on top of the
                anomaly, that's a weaker result than clean equal-weight.

Benchmarks (all three matter — this is the critical stress-test):
  - BTC buy-and-hold
  - ETH buy-and-hold
  - Equal-weight passive of the eligible universe, monthly rebalanced

Diagnostics:
  - Net Sharpe vs each benchmark (must beat all three to be interesting)
  - Sub-period Sharpe: 2018 bear, 2019-2020 recovery, 2021 bull, 2022 crash,
    2023-2024 recovery
  - Conditional Sharpe on the top-picked coins vs the equal-weight universe:
    does the momentum ranking add anything above passive?

Prior: HIGH by construction (strongest documented anomaly on the strongest-
trending asset class) but I've been wrong about "high priors" three times in a
row now, so treating this as a genuine test not a foregone win.
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

# ── Strategy parameters ──────────────────────────────────────────────────────
LOOKBACK_DAYS        = 90        # ~3 months of calendar days (crypto trades 7/7)
MIN_HISTORY_DAYS     = 60        # need ≥ 60 days to be eligible
TOP_N                = 3
COST_RT_BPS          = 30.0      # retail crypto — spread + fees
TRADING_DAYS         = 365       # crypto trades every day
REBALANCE_FREQ       = "ME"      # month-end
START                = "2015-01-01"
END                  = "2024-12-31"

UNIVERSE = [
    ("BTC",   "BTC-USD"),
    ("ETH",   "ETH-USD"),
    ("SOL",   "SOL-USD"),
    ("BNB",   "BNB-USD"),
    ("ADA",   "ADA-USD"),
    ("DOGE",  "DOGE-USD"),
    ("AVAX",  "AVAX-USD"),
    ("LINK",  "LINK-USD"),
    ("DOT",   "DOT-USD"),
    ("XRP",   "XRP-USD"),
]


def _fetch_close(ticker: str, name: str) -> pd.Series:
    df = yf.download(ticker, start=START, end=END,
                     auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"No data for {ticker} ({name})")
    s = df["Close"].dropna()
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    s.index = pd.to_datetime(s.index)
    s.name = name
    return s.sort_index()


def _stats(returns: pd.Series) -> dict:
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew()) if returns.std() > 0 else 0.0
    downside_vol = float(returns[returns < 0].std() * np.sqrt(TRADING_DAYS))
    sortino = ann_ret / downside_vol if downside_vol > 0 else 0.0
    return dict(ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe, sortino=sortino,
                max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1) if len(curve) else 0.0)


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #35 — Cross-sectional 3M momentum on crypto majors")
    print(f"  Universe            : {len(UNIVERSE)} coins")
    print(f"  Lookback            : {LOOKBACK_DAYS} calendar days")
    print(f"  Top-N               : {TOP_N} (long-only, equal-weight)")
    print(f"  Rebalance frequency : monthly (last-of-month)")
    print(f"  Min history         : {MIN_HISTORY_DAYS} days for eligibility")
    print(f"  Cost                : {COST_RT_BPS:.0f} bps round-trip per leg")
    print()

    print(f"  Fetching prices for {len(UNIVERSE)} coins...")
    price_by_coin: dict[str, pd.Series] = {}
    for name, ticker in UNIVERSE:
        try:
            s = _fetch_close(ticker, name)
            price_by_coin[name] = s
            print(f"    {name:<6} ({ticker:<9}): {len(s):>5} rows, "
                  f"{s.index[0].date()} → {s.index[-1].date()}")
        except Exception as exc:
            print(f"    {name:<6} ({ticker:<9}): FAILED ({exc})")

    coin_names = [n for n, _ in UNIVERSE if n in price_by_coin]
    idx = pd.date_range(start=START, end=END, freq="D")
    price_df = pd.DataFrame(index=idx, columns=coin_names, dtype=float)
    first_date_by_coin: dict[str, pd.Timestamp] = {}
    for name in coin_names:
        s = price_by_coin[name].reindex(idx).ffill()
        price_df[name] = s
        first_date_by_coin[name] = price_by_coin[name].index.min()

    # eligibility mask: coin has ≥ MIN_HISTORY_DAYS of history at date t
    eligible = pd.DataFrame(False, index=idx, columns=coin_names)
    for name in coin_names:
        elig_from = first_date_by_coin[name] + pd.Timedelta(days=MIN_HISTORY_DAYS)
        eligible[name] = idx >= elig_from

    # trailing 90d total return
    ret_lb = (price_df / price_df.shift(LOOKBACK_DAYS)) - 1.0
    ret_lb = ret_lb.where(eligible, np.nan)

    # rebalance dates: last calendar day of each month
    rebal_dates = pd.date_range(start=START, end=END, freq=REBALANCE_FREQ)
    rebal_dates = rebal_dates.intersection(idx)

    # build target weights on rebalance dates, forward-fill between
    target_w = pd.DataFrame(0.0, index=idx, columns=coin_names)
    for d in rebal_dates:
        s = ret_lb.loc[d]
        s = s.dropna()
        if s.empty:
            continue
        # rank by trailing return, pick top-N (or all if fewer eligible)
        n_pick = min(TOP_N, len(s))
        winners = s.nlargest(n_pick).index.tolist()
        w = pd.Series(0.0, index=coin_names)
        w.loc[winners] = 1.0 / n_pick
        target_w.loc[d] = w.values

    # weights held until next rebal — forward-fill from rebal dates only
    rebal_mask_1d = pd.Series(target_w.index.isin(rebal_dates), index=target_w.index)
    rebal_mask = pd.DataFrame(
        np.broadcast_to(rebal_mask_1d.values[:, None], target_w.shape),
        index=target_w.index, columns=target_w.columns,
    )
    target_w = target_w.where(rebal_mask, np.nan)
    target_w = target_w.ffill().fillna(0.0)

    # execution lag: use previous day's weights to earn today's return
    weights_lag = target_w.shift(1).fillna(0.0)
    coin_ret = price_df.pct_change().fillna(0.0)

    gross_instr = weights_lag * coin_ret
    gross_port  = gross_instr.sum(axis=1)

    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0
    turnover = weights_lag.diff().abs().fillna(0.0)
    cost_total = turnover.sum(axis=1) * cost_per_unit

    # trim to first rebal date
    if len(rebal_dates):
        first_active = rebal_dates[0] + pd.Timedelta(days=1)
        gross_port = gross_port.loc[gross_port.index >= first_active]
        cost_total = cost_total.loc[cost_total.index >= first_active]
    net_port = (gross_port - cost_total).dropna()

    s_gross = _stats(gross_port.loc[net_port.index])
    s_net   = _stats(net_port)
    calmar  = s_net["ann_ret"] / abs(s_net["max_dd"]) if s_net["max_dd"] else float("nan")

    # ── Benchmarks ───────────────────────────────────────────────────────
    btc_ret = price_df["BTC"].pct_change().reindex(net_port.index).fillna(0.0)
    eth_ret = price_df["ETH"].pct_change().reindex(net_port.index).fillna(0.0) if "ETH" in coin_names else pd.Series(0.0, index=net_port.index)

    # equal-weight passive of the eligible universe (monthly rebal)
    ew_w_target = eligible.astype(float)
    ew_w_target = ew_w_target.div(ew_w_target.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    ew_w_target = ew_w_target.where(rebal_mask, np.nan).ffill().fillna(0.0)
    ew_w_lag = ew_w_target.shift(1).fillna(0.0)
    ew_ret = (ew_w_lag * coin_ret).sum(axis=1).reindex(net_port.index).fillna(0.0)
    # deduct passive rebal cost (much lower turnover)
    ew_turn = ew_w_lag.diff().abs().fillna(0.0).sum(axis=1)
    ew_cost = ew_turn * cost_per_unit
    ew_net = (ew_ret - ew_cost).reindex(net_port.index).fillna(0.0)

    s_btc = _stats(btc_ret)
    s_eth = _stats(eth_ret)
    s_ew  = _stats(ew_net)

    print()
    print("=" * 82)
    print(f"  Strategy #35 — Crypto cross-sectional 3M momentum, long-top-{TOP_N}, monthly")
    print("=" * 82)
    print(f"  Sample                  : {net_port.index[0].date()} → {net_port.index[-1].date()}")
    print(f"  Observations            : {len(net_port):,} calendar days")
    print(f"  Rebalances              : {len(rebal_dates)}")
    print(f"  Cumulative cost drag    : {cost_total.sum()*100:5.2f}%")
    print(f"  Avg # eligible coins    : {eligible.loc[net_port.index].sum(axis=1).mean():.1f}")
    print()
    print(f"  {'':<22} {'GROSS':>10} {'NET':>10} {'BTC B&H':>10} {'ETH B&H':>10} {'EW passive':>11}")
    print(f"  {'Ann. Return':<22} {s_gross['ann_ret']*100:>9.2f}% {s_net['ann_ret']*100:>9.2f}% "
          f"{s_btc['ann_ret']*100:>9.2f}% {s_eth['ann_ret']*100:>9.2f}% {s_ew['ann_ret']*100:>10.2f}%")
    print(f"  {'Ann. Vol':<22} {s_gross['ann_vol']*100:>9.2f}% {s_net['ann_vol']*100:>9.2f}% "
          f"{s_btc['ann_vol']*100:>9.2f}% {s_eth['ann_vol']*100:>9.2f}% {s_ew['ann_vol']*100:>10.2f}%")
    print(f"  {'Sharpe':<22} {s_gross['sharpe']:>10.2f} {s_net['sharpe']:>10.2f} "
          f"{s_btc['sharpe']:>10.2f} {s_eth['sharpe']:>10.2f} {s_ew['sharpe']:>11.2f}")
    print(f"  {'Sortino':<22} {s_gross['sortino']:>10.2f} {s_net['sortino']:>10.2f} "
          f"{s_btc['sortino']:>10.2f} {s_eth['sortino']:>10.2f} {s_ew['sortino']:>11.2f}")
    print(f"  {'Max Drawdown':<22} {s_gross['max_dd']*100:>9.2f}% {s_net['max_dd']*100:>9.2f}% "
          f"{s_btc['max_dd']*100:>9.2f}% {s_eth['max_dd']*100:>9.2f}% {s_ew['max_dd']*100:>10.2f}%")
    print(f"  {'Cumulative':<22} {s_gross['cum']*100:>9.0f}% {s_net['cum']*100:>9.0f}% "
          f"{s_btc['cum']*100:>9.0f}% {s_eth['cum']*100:>9.0f}% {s_ew['cum']*100:>10.0f}%")
    print("=" * 82)

    # ── Sub-period analysis ──────────────────────────────────────────────
    periods = [
        ("2018 bear",       "2018-01-01", "2018-12-31"),
        ("2019-2020 recov", "2019-01-01", "2020-12-31"),
        ("2021 bull",       "2021-01-01", "2021-12-31"),
        ("2022 crash",      "2022-01-01", "2022-12-31"),
        ("2023-2024 recov", "2023-01-01", "2024-12-31"),
    ]
    print()
    print("Sub-period analysis (net):")
    print(f"  {'Period':<18} {'Days':>6} {'Strat':>8} {'BTC':>8} {'ETH':>8} {'EW':>8}")
    for label, ps, pe in periods:
        m = (net_port.index >= ps) & (net_port.index <= pe)
        if not m.any():
            continue
        sp_strat = _stats(net_port.loc[m])
        sp_btc   = _stats(btc_ret.loc[m])
        sp_eth   = _stats(eth_ret.loc[m])
        sp_ew    = _stats(ew_net.loc[m])
        print(f"  {label:<18} {int(m.sum()):>6} "
              f"{sp_strat['sharpe']:>8.2f} {sp_btc['sharpe']:>8.2f} "
              f"{sp_eth['sharpe']:>8.2f} {sp_ew['sharpe']:>8.2f}")

    # ── Conditional Sharpe test: strategy vs equal-weight on same days ──
    # On days when the strategy holds top-N picks, is it earning more than the
    # equal-weight passive of the same universe would have earned?
    print()
    print("Head-to-head vs EW passive (same universe, same rebal cadence, same costs):")
    diff = net_port - ew_net
    s_diff = _stats(diff)
    print(f"  Excess return (strat − EW passive) : {s_diff['ann_ret']*100:+.2f}%/yr")
    print(f"  Excess vol                         : {s_diff['ann_vol']*100:.2f}%")
    print(f"  Information ratio                  : {s_diff['sharpe']:+.2f}")
    print(f"  Excess cumulative                  : {s_diff['cum']*100:+.1f} pp")
    print(f"  Excess hit rate                    : {s_diff['hit']*100:.1f}%")

    # ── Verdict ──────────────────────────────────────────────────────────
    print()
    print("VERDICT:")
    beats_btc = s_net["sharpe"] > s_btc["sharpe"]
    beats_eth = s_net["sharpe"] > s_eth["sharpe"]
    beats_ew  = s_net["sharpe"] > s_ew["sharpe"]
    ir_positive = s_diff["sharpe"] > 0.30
    print(f"  Beats BTC B&H Sharpe    : {'YES' if beats_btc else 'no'}")
    print(f"  Beats ETH B&H Sharpe    : {'YES' if beats_eth else 'no'}")
    print(f"  Beats EW passive Sharpe : {'YES' if beats_ew else 'no'}")
    print(f"  IR vs EW > 0.30         : {'YES' if ir_positive else 'no'}")
    if beats_btc and beats_eth and beats_ew and ir_positive:
        print(f"  ▶︎ ✅ CLEAN WIN — beats every benchmark including the naive passive.")
    elif beats_ew and ir_positive:
        print(f"  ▶︎ ✅ Beats naive passive with material IR — the momentum tilt earns its keep.")
    elif s_net["sharpe"] > 0.5 and beats_ew:
        print(f"  ▶︎ ⚠️  Positive Sharpe and beats EW, but marginal — not a slam dunk.")
    else:
        print(f"  ▶︎ ❌ Does not add value above equal-weight passive.")

    # ── Plot ─────────────────────────────────────────────────────────────
    net_curve = (1 + net_port).cumprod()
    btc_curve = (1 + btc_ret).cumprod()
    eth_curve = (1 + eth_ret).cumprod()
    ew_curve  = (1 + ew_net).cumprod()
    fig, axes = plt.subplots(3, 1, figsize=(13, 11),
                             gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
    ax = axes[0]
    ax.plot(net_curve.index, net_curve.values, color="#2ca02c", lw=2.0,
            label=f"Strategy #35 net (Sharpe {s_net['sharpe']:.2f})")
    ax.plot(ew_curve.index,  ew_curve.values,  color="#7f7f7f", lw=1.2,
            label=f"EW passive (Sharpe {s_ew['sharpe']:.2f})")
    ax.plot(btc_curve.index, btc_curve.values, color="#ff9500", lw=1.2, alpha=0.8,
            label=f"BTC B&H (Sharpe {s_btc['sharpe']:.2f})")
    ax.plot(eth_curve.index, eth_curve.values, color="#5865f2", lw=1.2, alpha=0.8,
            label=f"ETH B&H (Sharpe {s_eth['sharpe']:.2f})")
    ax.set_yscale("log")
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Cumulative return (× log)")
    ax.set_title(
        f"Strategy #35 — Crypto cross-sectional 3M momentum, long-top-{TOP_N}, monthly rebal\n"
        f"{net_port.index[0].date()} → {net_port.index[-1].date()}  ·  "
        f"net Sharpe {s_net['sharpe']:.2f}, MaxDD {s_net['max_dd']*100:.1f}%, "
        f"IR vs EW {s_diff['sharpe']:+.2f}"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, which="both")

    ax = axes[1]
    drawdown = (net_curve / net_curve.cummax()) - 1
    ax.fill_between(drawdown.index, drawdown.values, 0, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown (net)")
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.plot(diff.index, (1 + diff).cumprod().values, color="#8e44ad", lw=1.4)
    ax.axhline(1.0, color="k", lw=0.5)
    ax.set_ylabel("Strat / EW (cum)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = REPORTS / "strategy_35_crypto_xsec_momentum.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    if csv_out is not None:
        out_df = pd.DataFrame(index=net_port.index)
        out_df["gross_return"] = gross_port.loc[net_port.index]
        out_df["cost"]         = cost_total.loc[net_port.index]
        out_df["net_return"]   = net_port
        out_df["btc_bh_return"] = btc_ret
        out_df["eth_bh_return"] = eth_ret
        out_df["ew_passive_return"] = ew_net
        for name in coin_names:
            out_df[f"weight_{name}"] = weights_lag[name].reindex(net_port.index).fillna(0.0)
        out_df["cum_net"] = net_curve
        out_df["cum_ew"]  = ew_curve
        out_df.index.name = "date"
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, float_format="%.6f")
        print(f"CSV (daily): {csv_out.relative_to(REPO)}  ({len(out_df):,} rows × {out_df.shape[1]} cols)")

    return dict(
        net=s_net, gross=s_gross,
        btc_bh=s_btc, eth_bh=s_eth, ew_passive=s_ew,
        excess=s_diff, calmar=calmar,
        n_obs=len(net_port),
        n_rebals=len(rebal_dates),
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_35_crypto_xsec_momentum_track_record.csv")
