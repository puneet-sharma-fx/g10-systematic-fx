"""
Sub-period stability of Strategy #25 — Turtle System 1 on commodities + crypto.

The full-sample headline (2010-2024) was net Sharpe +0.43, PF 1.36, daily skew
+0.82. The natural rigour question: is the edge regime-stable, or concentrated
in one macro period? In particular, the 2020-21 crypto bull market (BTC +600%
in ~18 months, ETH +1,000%) might explain most of the Sharpe — if so, the
strategy is really "1980s Turtle on commodities" + "2020-21 crypto bull bet"
rolled into one number.

This script slices #25's daily returns into the same four macro regimes used
for the rate-diff family analysis (so results are comparable):

  - ZIRP / post-GFC    2010-2015  (zero rates, low vol, weak commodity trends)
  - Divergence          2016-2019  (Fed normalisation, mid-cycle)
  - COVID               2020-2021  (pandemic + reflation, crypto bull market)
  - Hiking cycle        2022-2024  (inflation, commodity supercycle continuation)

For each regime: annualised Sharpe, return, vol, max DD, daily skew, trade
count, trade win rate, profit factor. Also a per-instrument regime Sharpe
to expose which assets drove which periods.

Output:
  - reports/subperiod_stability_strat25.png   (bar charts + per-instrument heatmap)
  - tables printed to stdout
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

TRADING_DAYS = 252
START = "2010-01-04"
END   = "2024-12-31"

DAILY_CSV  = TRACK / "strategy_25_turtle_commodities_crypto_track_record.csv"
TRADES_CSV = TRACK / "strategy_25_turtle_commodities_crypto_track_record_trades.csv"

INSTRUMENTS = ["GOLD", "SILVER", "COPPER", "OIL_WTI", "NATGAS", "SOYBEAN", "BTC", "ETH"]

REGIMES: dict[str, tuple[str, str]] = {
    "ZIRP 2010-15":       ("2010-01-01", "2015-12-31"),
    "Divergence 2016-19": ("2016-01-01", "2019-12-31"),
    "COVID 2020-21":      ("2020-01-01", "2021-12-31"),
    "Hiking 2022-24":     ("2022-01-01", "2024-12-31"),
}


def _stats(returns: pd.Series) -> dict:
    returns = returns.dropna()
    if len(returns) == 0:
        return dict(n_days=0, ann_ret=0.0, ann_vol=0.0, sharpe=0.0,
                    max_dd=0.0, hit=0.0, skew=0.0, cum=0.0)
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    hit     = float((returns > 0).mean())
    skew    = float(returns.skew()) if returns.std() > 0 else 0.0
    return dict(n_days=len(returns), ann_ret=ann_ret, ann_vol=ann_vol, sharpe=sharpe,
                max_dd=max_dd, hit=hit, skew=skew,
                cum=float(curve.iloc[-1] - 1))


def _trade_stats(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return dict(n=0, win_rate=0.0, profit_factor=0.0,
                    avg_win=0.0, avg_loss=0.0, sum_pnl=0.0)
    wins   = trades[trades["pnl_pct"] > 0]
    losses = trades[trades["pnl_pct"] <= 0]
    pf = (wins["pnl_pct"].sum() / abs(losses["pnl_pct"].sum())) if not losses.empty and losses["pnl_pct"].sum() != 0 else float("inf")
    return dict(
        n             = int(len(trades)),
        win_rate      = float(len(wins) / len(trades)),
        profit_factor = float(pf) if np.isfinite(pf) else 99.99,
        avg_win       = float(wins["pnl_pct"].mean()) if not wins.empty else 0.0,
        avg_loss      = float(losses["pnl_pct"].mean()) if not losses.empty else 0.0,
        sum_pnl       = float(trades["pnl_pct"].sum()),
    )


def main():
    print("\nSub-period stability — Strategy #25 (Turtle on commodities + crypto)\n")

    # Load daily-return time series (with per-instrument weights to reconstruct
    # each instrument's daily P&L contribution)
    daily = pd.read_csv(DAILY_CSV, parse_dates=["date"], index_col="date")
    print(f"  Loaded daily series: {len(daily):,} rows, {daily.index[0].date()} → {daily.index[-1].date()}")

    # Re-fetch close prices to derive per-instrument daily returns
    # (the CSV stores weights but not pair returns directly — compute via the
    # diff of cumulative gross approximation is not clean, so simpler: just
    # use the position*weight columns and reconstruct from yfinance)
    # Actually we can decompose gross_return into per-instrument legs by
    # noting gross_return[t] = sum_i weight_i[t] * pair_return_i[t]. We don't
    # have pair_return_i in the CSV, but we have weight_i. We re-fetch.
    import yfinance as yf
    instr_to_ticker = {
        "GOLD":"GC=F","SILVER":"SI=F","COPPER":"HG=F","OIL_WTI":"CL=F",
        "NATGAS":"NG=F","SOYBEAN":"ZS=F","BTC":"BTC-USD","ETH":"ETH-USD",
    }
    pair_returns = {}
    for instr, ticker in instr_to_ticker.items():
        df = yf.download(ticker, start=START, end=END, auto_adjust=True, progress=False)
        s = df["Close"].squeeze().pct_change()
        s.index = pd.to_datetime(s.index)
        pair_returns[instr] = s.reindex(daily.index).fillna(0)
    pair_returns_df = pd.DataFrame(pair_returns)

    # Per-instrument daily gross contribution: weight_lag × pair_return
    per_instr_gross = pd.DataFrame(index=daily.index, columns=INSTRUMENTS, dtype=float)
    for instr in INSTRUMENTS:
        per_instr_gross[instr] = daily[f"weight_{instr}"] * pair_returns_df[instr]

    # Load trade log
    trades = pd.read_csv(TRADES_CSV, parse_dates=["entry_date", "exit_date"])
    print(f"  Loaded trade log:    {len(trades):,} trades\n")

    # ── Headline regime table ──────────────────────────────────────────────
    print("=" * 100)
    print(f"  {'Regime':<22} {'Days':>5} {'Sharpe':>8} {'Ann Ret':>9} {'Ann Vol':>9} {'MaxDD':>8} {'Skew':>7} {'#Tr':>5} {'Win%':>6} {'PF':>6}")
    print("=" * 100)

    regime_records = []
    for regime_name, (start, end) in REGIMES.items():
        mask = (daily.index >= start) & (daily.index <= end)
        ret_slice = daily.loc[mask, "net_return"]
        s = _stats(ret_slice)

        # Trade-level: trades whose ENTRY_DATE falls in regime window
        trade_mask = (trades["entry_date"] >= start) & (trades["entry_date"] <= end)
        ts = _trade_stats(trades.loc[trade_mask])

        regime_records.append({
            "regime": regime_name,
            "n_days": s["n_days"], "sharpe": s["sharpe"], "ann_ret": s["ann_ret"],
            "ann_vol": s["ann_vol"], "max_dd": s["max_dd"], "skew": s["skew"],
            "n_trades": ts["n"], "win_rate": ts["win_rate"], "profit_factor": ts["profit_factor"],
        })
        pf_disp = f"{ts['profit_factor']:.2f}" if ts['profit_factor'] < 99 else "99+"
        print(f"  {regime_name:<22} {s['n_days']:>5} {s['sharpe']:>8.2f} "
              f"{s['ann_ret']*100:>8.2f}% {s['ann_vol']*100:>8.2f}% "
              f"{s['max_dd']*100:>7.2f}% {s['skew']:>+7.2f} "
              f"{ts['n']:>5} {ts['win_rate']*100:>5.1f}% {pf_disp:>6}")

    # Full sample anchor
    s_full = _stats(daily["net_return"])
    ts_full = _trade_stats(trades)
    pf_full_disp = f"{ts_full['profit_factor']:.2f}"
    print("-" * 100)
    print(f"  {'FULL SAMPLE 2010-24':<22} {s_full['n_days']:>5} {s_full['sharpe']:>8.2f} "
          f"{s_full['ann_ret']*100:>8.2f}% {s_full['ann_vol']*100:>8.2f}% "
          f"{s_full['max_dd']*100:>7.2f}% {s_full['skew']:>+7.2f} "
          f"{ts_full['n']:>5} {ts_full['win_rate']*100:>5.1f}% {pf_full_disp:>6}")
    print("=" * 100)

    # ── Per-instrument regime Sharpe table ─────────────────────────────────
    print()
    print("Per-instrument annualised Sharpe by regime:")
    print("=" * 100)
    header = f"  {'Instr':<10}" + "".join(f" {r:>20}" for r in REGIMES.keys()) + f" {'FULL':>10}"
    print(header)
    print("-" * len(header))
    instr_regime_sharpe = pd.DataFrame(index=INSTRUMENTS, columns=list(REGIMES.keys()) + ["FULL"], dtype=float)
    for instr in INSTRUMENTS:
        row = f"  {instr:<10}"
        for regime_name, (start, end) in REGIMES.items():
            mask = (per_instr_gross.index >= start) & (per_instr_gross.index <= end)
            r = per_instr_gross.loc[mask, instr]
            r_nonzero = r[r != 0]   # focus on active days
            if len(r_nonzero) < 30:
                row += f" {'--':>20}"
                instr_regime_sharpe.loc[instr, regime_name] = np.nan
                continue
            mu  = r.mean() * TRADING_DAYS
            sig = r.std() * np.sqrt(TRADING_DAYS)
            sharpe_i = mu / sig if sig > 0 else 0.0
            instr_regime_sharpe.loc[instr, regime_name] = sharpe_i
            row += f" {sharpe_i:>+19.2f} "
        # Full sample
        r = per_instr_gross[instr]
        mu  = r.mean() * TRADING_DAYS
        sig = r.std() * np.sqrt(TRADING_DAYS)
        sharpe_full_i = mu / sig if sig > 0 else 0.0
        instr_regime_sharpe.loc[instr, "FULL"] = sharpe_full_i
        row += f" {sharpe_full_i:>+9.2f}"
        print(row)
    print("=" * 100)

    # ── Interpretation ─────────────────────────────────────────────────────
    print()
    sharpes_by_regime = {r["regime"]: r["sharpe"] for r in regime_records}
    positive_regimes = [r for r, s in sharpes_by_regime.items() if s > 0]
    print(f"  Regimes with positive Sharpe: {len(positive_regimes)} of 4")
    if len(positive_regimes) == 4:
        print(f"  ▶︎ ✅ Regime-stable: positive Sharpe in ALL four eras. Not a single-period fluke.")
    elif len(positive_regimes) >= 2:
        print(f"  ▶︎ ⚠️  Regime-partial: positive in {positive_regimes}. Edge depends on macro environment.")
    else:
        print(f"  ▶︎ ❌ Regime-concentrated: positive in only {len(positive_regimes)} era — headline Sharpe is likely a single-period artefact.")
    best_regime = max(sharpes_by_regime, key=sharpes_by_regime.get)
    worst_regime = min(sharpes_by_regime, key=sharpes_by_regime.get)
    print(f"  Best regime:  {best_regime} (Sharpe {sharpes_by_regime[best_regime]:+.2f})")
    print(f"  Worst regime: {worst_regime} (Sharpe {sharpes_by_regime[worst_regime]:+.2f})")

    # ── Plot: 2-panel ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), gridspec_kw={"height_ratios": [1, 1.4]})

    # Panel 1: regime Sharpe bar chart
    ax = axes[0]
    regime_names = [r["regime"] for r in regime_records]
    sharpes = [r["sharpe"] for r in regime_records]
    colors = ["#2ca02c" if s > 0 else "#d62728" for s in sharpes]
    bars = ax.bar(regime_names + ["FULL"], sharpes + [s_full["sharpe"]],
                  color=colors + ["#1f77b4"], alpha=0.75, edgecolor="black", linewidth=1)
    for bar, val in zip(bars, sharpes + [s_full["sharpe"]]):
        ax.text(bar.get_x() + bar.get_width() / 2, val,
                f"{val:+.2f}",
                ha="center", va="bottom" if val >= 0 else "top",
                fontsize=11, fontweight="bold")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Annualised Sharpe (net)")
    ax.set_title(
        "Strategy #25 — Sub-period stability (Turtle on commodities + crypto)\n"
        "Full-sample net Sharpe is " + f"{s_full['sharpe']:+.2f}" +
        "; this chart shows how that decomposes across macro regimes"
    )
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 2: per-instrument × regime heatmap
    ax = axes[1]
    heat = instr_regime_sharpe.astype(float)
    vmax = float(np.nanmax(np.abs(heat.values)))
    im = ax.imshow(heat.values, aspect="auto", cmap="RdYlGn",
                   vmin=-vmax, vmax=+vmax)
    ax.set_xticks(range(len(heat.columns)))
    ax.set_xticklabels(heat.columns, rotation=15)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index)
    for i in range(len(heat.index)):
        for j in range(len(heat.columns)):
            val = heat.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:+.2f}", ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="black" if abs(val) < vmax * 0.7 else "white")
            else:
                ax.text(j, i, "--", ha="center", va="center", fontsize=9, color="gray")
    ax.set_title("Per-instrument annualised Sharpe by regime (gross of cost)")
    plt.colorbar(im, ax=ax, label="Sharpe", fraction=0.025, pad=0.02)

    plt.tight_layout()
    out = REPORTS / "subperiod_stability_strat25.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    return regime_records, instr_regime_sharpe


if __name__ == "__main__":
    main()
