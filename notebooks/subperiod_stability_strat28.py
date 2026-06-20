"""
Sub-period stability of Strategy #28 — 20/50 DMA crossover on commodities + crypto.

The companion analysis to `subperiod_stability_strat25.py`. Same four regimes
(ZIRP / Divergence / COVID / Hiking), same per-instrument decomposition — but
applied to the MA-crossover P&L on the same 8-instrument universe.

The motivating question (yesterday's finding on #25): the +0.43 full-sample
Sharpe hid the fact that 2022-24 LOST money on that strategy, with the entire
−35% MaxDD living in the most recent regime. Does Strategy #28 share the same
vulnerability — and is the dominance of crypto / weakness of commodities the
same — or does the MA-crossover spec behave differently from the Turtle spec
on the same universe?

If #25 and #28 agree on regime structure → the universe is the problem in
2022-24, not the signal → deployment caveat applies to both.

If they differ → one spec is more robust to the hiking regime than the other
→ meaningful choice for which spec to actually deploy.

Output:
  - reports/subperiod_stability_strat28.png   (bar charts + per-instrument heatmap)
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

DAILY_CSV  = TRACK / "strategy_28_ma_crossover_commodities_crypto_track_record.csv"
TRADES_CSV = TRACK / "strategy_28_ma_crossover_commodities_crypto_track_record_trades.csv"

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
    print("\nSub-period stability — Strategy #28 (20/50 MA crossover on commodities + crypto)\n")

    daily = pd.read_csv(DAILY_CSV, parse_dates=["date"], index_col="date")
    print(f"  Loaded daily series: {len(daily):,} rows, {daily.index[0].date()} → {daily.index[-1].date()}")

    # Re-fetch close prices to derive per-instrument daily returns
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
            r_nonzero = r[r != 0]
            if len(r_nonzero) < 30:
                row += f" {'--':>20}"
                instr_regime_sharpe.loc[instr, regime_name] = np.nan
                continue
            mu  = r.mean() * TRADING_DAYS
            sig = r.std() * np.sqrt(TRADING_DAYS)
            sharpe_i = mu / sig if sig > 0 else 0.0
            instr_regime_sharpe.loc[instr, regime_name] = sharpe_i
            row += f" {sharpe_i:>+19.2f} "
        r = per_instr_gross[instr]
        mu  = r.mean() * TRADING_DAYS
        sig = r.std() * np.sqrt(TRADING_DAYS)
        sharpe_full_i = mu / sig if sig > 0 else 0.0
        instr_regime_sharpe.loc[instr, "FULL"] = sharpe_full_i
        row += f" {sharpe_full_i:>+9.2f}"
        print(row)
    print("=" * 100)

    # ── Side-by-side comparison vs #25 (Turtle) on the same universe ───────
    print()
    print("Comparison vs Strategy #25 (Turtle 20/10/2N on same universe):")
    print("=" * 80)
    print(f"  Regime                  | #25 Turtle Sharpe | #28 MA-Cross Sharpe | Δ")
    print("-" * 80)
    # Reference: #25 regime Sharpes from yesterday's analysis
    strat25_sharpes = {
        "ZIRP 2010-15":       0.31,
        "Divergence 2016-19": 0.41,
        "COVID 2020-21":      1.81,
        "Hiking 2022-24":    -0.48,
    }
    for r in regime_records:
        s25 = strat25_sharpes.get(r["regime"], np.nan)
        s28 = r["sharpe"]
        delta = s28 - s25
        print(f"  {r['regime']:<22}  | {s25:>+17.2f} | {s28:>+19.2f} | {delta:>+5.2f}")
    s25_full = 0.43
    s28_full = s_full["sharpe"]
    print(f"  {'FULL SAMPLE':<22}  | {s25_full:>+17.2f} | {s28_full:>+19.2f} | {s28_full-s25_full:>+5.2f}")
    print("=" * 80)

    # ── Interpretation ─────────────────────────────────────────────────────
    print()
    sharpes_by_regime = {r["regime"]: r["sharpe"] for r in regime_records}
    positive_regimes = [r for r, s in sharpes_by_regime.items() if s > 0]
    print(f"  Regimes with positive Sharpe: {len(positive_regimes)} of 4")
    if len(positive_regimes) == 4:
        print(f"  ▶︎ ✅ Regime-stable: positive Sharpe in ALL four eras.")
    elif len(positive_regimes) >= 2:
        print(f"  ▶︎ ⚠️  Regime-partial: positive in {positive_regimes}.")
    else:
        print(f"  ▶︎ ❌ Regime-concentrated: positive in only {len(positive_regimes)} era.")
    best_regime = max(sharpes_by_regime, key=sharpes_by_regime.get)
    worst_regime = min(sharpes_by_regime, key=sharpes_by_regime.get)
    print(f"  Best regime:  {best_regime} (Sharpe {sharpes_by_regime[best_regime]:+.2f})")
    print(f"  Worst regime: {worst_regime} (Sharpe {sharpes_by_regime[worst_regime]:+.2f})")

    # ── Plot: 2-panel ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), gridspec_kw={"height_ratios": [1, 1.4]})

    ax = axes[0]
    regime_names = [r["regime"] for r in regime_records]
    sharpes_28 = [r["sharpe"] for r in regime_records]
    sharpes_25_list = [strat25_sharpes.get(r["regime"], 0.0) for r in regime_records]
    x = np.arange(len(regime_names) + 1)
    width = 0.4
    ax.bar(x - width/2, sharpes_25_list + [s25_full],
           width=width, color="#1f77b4", alpha=0.85, edgecolor="black", linewidth=0.8,
           label="#25 Turtle 20/10/2N")
    ax.bar(x + width/2, sharpes_28 + [s_full["sharpe"]],
           width=width, color="#2ca02c", alpha=0.85, edgecolor="black", linewidth=0.8,
           label="#28 20/50 MA Crossover")
    ax.set_xticks(x)
    ax.set_xticklabels(regime_names + ["FULL"], rotation=15)
    for i, v in enumerate(sharpes_25_list + [s25_full]):
        ax.text(i - width/2, v, f"{v:+.2f}", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=9, color="#1f77b4")
    for i, v in enumerate(sharpes_28 + [s_full["sharpe"]]):
        ax.text(i + width/2, v, f"{v:+.2f}", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=9, color="#2ca02c", fontweight="bold")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Annualised Sharpe (net)")
    ax.set_title(
        "Strategy #28 — Sub-period stability (20/50 MA crossover on commodities + crypto)\n"
        "Side-by-side comparison vs Strategy #25 (Turtle) on the same universe"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, axis="y")

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
    ax.set_title("Per-instrument annualised Sharpe by regime (gross of cost) — Strategy #28")
    plt.colorbar(im, ax=ax, label="Sharpe", fraction=0.025, pad=0.02)

    plt.tight_layout()
    out = REPORTS / "subperiod_stability_strat28.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    return regime_records, instr_regime_sharpe


if __name__ == "__main__":
    main()
