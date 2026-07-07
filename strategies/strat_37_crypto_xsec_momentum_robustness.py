"""
Strategy #37 — Parameter robustness check on #35 (crypto xsec momentum)

#35 earned net Sharpe 1.44 on the baseline spec: 90d lookback, top-3 EW. The
most legitimate criticism of that result is "the edge is concentrated in 2021
— is 90d/top-3 the only spec that worked, or is the momentum-in-crypto edge
robust across neighbouring parameter choices?"

This strategy answers exactly that. It sweeps two axes:

  - Lookback  ∈ {30, 60, 90, 120, 180, 252}  calendar-day windows
  - Top-N     ∈ {2, 3, 4, 5}                  number of longs held equal-weight

That is 6 × 4 = 24 backtests of the SAME #35 spec (same universe, same monthly
rebalance, same 30 bps RT cost). No new signal is being tested — this is a
robustness matrix over the existing edge.

Pass criteria (for the edge to be considered robust, not spec-lucky):

  1. Median net Sharpe across the 24-cell grid ≥ 1.0
  2. Fraction of cells with net Sharpe > 1.0 ≥ 50%
  3. All neighbouring cells of the baseline (60d/90d/120d × 2/3/4) ≥ 0.9
  4. No cell with Sharpe < 0 (i.e. no spec is actively harmful)

If those pass → #35's edge generalises across parameter choice and the
baseline spec was not overfit.

If they fail → the "win" is fragile and any deployment would require picking
a very specific spec, which is a red flag.
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

# ── Robustness grid ─────────────────────────────────────────────────────────
LOOKBACK_GRID = [30, 60, 90, 120, 180, 252]
TOPN_GRID     = [2, 3, 4, 5]
BASELINE_LB   = 90
BASELINE_N    = 3

# ── Fixed params (identical to #35) ──────────────────────────────────────────
MIN_HISTORY_DAYS  = 60
COST_RT_BPS       = 30.0
TRADING_DAYS      = 365
REBALANCE_FREQ    = "ME"
START             = "2015-01-01"
END               = "2024-12-31"

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
    df = yf.download(ticker, start=START, end=END, auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"No data for {ticker} ({name})")
    s = df["Close"].dropna()
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    s.index = pd.to_datetime(s.index)
    s.name = name
    return s.sort_index()


def _stats(returns: pd.Series) -> dict:
    returns = returns.dropna()
    if len(returns) == 0:
        return dict(sharpe=0.0, ann_ret=0.0, ann_vol=0.0, max_dd=0.0, cum=0.0)
    ann_ret = float(returns.mean() * TRADING_DAYS)
    ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS))
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0.0
    curve   = (1 + returns).cumprod()
    max_dd  = float(((curve / curve.cummax()) - 1).min())
    return dict(sharpe=sharpe, ann_ret=ann_ret, ann_vol=ann_vol,
                max_dd=max_dd, cum=float(curve.iloc[-1] - 1))


def _run_variant(price_df: pd.DataFrame, eligible: pd.DataFrame,
                 rebal_dates: pd.DatetimeIndex,
                 lookback_days: int, top_n: int) -> tuple[dict, pd.Series]:
    """One #35 backtest for a given (lookback, top-N)."""
    idx = price_df.index
    coin_names = list(price_df.columns)

    ret_lb = (price_df / price_df.shift(lookback_days)) - 1.0
    ret_lb = ret_lb.where(eligible, np.nan)

    target_w = pd.DataFrame(0.0, index=idx, columns=coin_names)
    for d in rebal_dates:
        s = ret_lb.loc[d].dropna()
        if s.empty:
            continue
        n_pick = min(top_n, len(s))
        winners = s.nlargest(n_pick).index.tolist()
        w = pd.Series(0.0, index=coin_names)
        w.loc[winners] = 1.0 / n_pick
        target_w.loc[d] = w.values

    rebal_mask_1d = pd.Series(idx.isin(rebal_dates), index=idx)
    rebal_mask = pd.DataFrame(
        np.broadcast_to(rebal_mask_1d.values[:, None], target_w.shape),
        index=idx, columns=coin_names,
    )
    target_w = target_w.where(rebal_mask, np.nan).ffill().fillna(0.0)

    weights_lag = target_w.shift(1).fillna(0.0)
    coin_ret = price_df.pct_change().fillna(0.0)
    gross_port = (weights_lag * coin_ret).sum(axis=1)

    cost_per_unit = COST_RT_BPS / 2.0 / 10000.0
    turnover = weights_lag.diff().abs().fillna(0.0)
    cost_total = turnover.sum(axis=1) * cost_per_unit

    if len(rebal_dates):
        first_active = rebal_dates[0] + pd.Timedelta(days=1)
        gross_port = gross_port.loc[gross_port.index >= first_active]
        cost_total = cost_total.loc[cost_total.index >= first_active]
    net_port = (gross_port - cost_total).dropna()

    return _stats(net_port), net_port


def run(csv_out: Path | None = None) -> dict:
    print(f"\nStrategy #37 — Parameter robustness check on #35")
    print(f"  Grid                : {len(LOOKBACK_GRID)} lookbacks × {len(TOPN_GRID)} top-N = {len(LOOKBACK_GRID)*len(TOPN_GRID)} variants")
    print(f"  Lookback ∈ {LOOKBACK_GRID}")
    print(f"  Top-N    ∈ {TOPN_GRID}")
    print(f"  Baseline (from #35) : {BASELINE_LB}d lookback, top-{BASELINE_N}")
    print(f"  Fixed               : monthly rebal, EW, 30 bps RT, {len(UNIVERSE)} coins")
    print()

    print(f"  Fetching prices for {len(UNIVERSE)} coins...")
    price_by_coin: dict[str, pd.Series] = {}
    for name, ticker in UNIVERSE:
        try:
            price_by_coin[name] = _fetch_close(ticker, name)
            print(f"    {name:<6}: {len(price_by_coin[name]):>5} rows")
        except Exception as exc:
            print(f"    {name:<6}: FAILED ({exc})")

    coin_names = [n for n, _ in UNIVERSE if n in price_by_coin]
    idx = pd.date_range(start=START, end=END, freq="D")
    price_df = pd.DataFrame(index=idx, columns=coin_names, dtype=float)
    first_date_by_coin: dict[str, pd.Timestamp] = {}
    for name in coin_names:
        price_df[name] = price_by_coin[name].reindex(idx).ffill()
        first_date_by_coin[name] = price_by_coin[name].index.min()

    eligible = pd.DataFrame(False, index=idx, columns=coin_names)
    for name in coin_names:
        elig_from = first_date_by_coin[name] + pd.Timedelta(days=MIN_HISTORY_DAYS)
        eligible[name] = idx >= elig_from

    rebal_dates = pd.date_range(start=START, end=END, freq=REBALANCE_FREQ).intersection(idx)

    # ── Sweep the grid ────────────────────────────────────────────────────
    print()
    print(f"  Running {len(LOOKBACK_GRID)*len(TOPN_GRID)} variants...")
    sharpe_grid = pd.DataFrame(index=LOOKBACK_GRID, columns=TOPN_GRID, dtype=float)
    annret_grid = pd.DataFrame(index=LOOKBACK_GRID, columns=TOPN_GRID, dtype=float)
    maxdd_grid  = pd.DataFrame(index=LOOKBACK_GRID, columns=TOPN_GRID, dtype=float)

    for lb in LOOKBACK_GRID:
        for n in TOPN_GRID:
            stats, _ = _run_variant(price_df, eligible, rebal_dates, lb, n)
            sharpe_grid.loc[lb, n] = stats["sharpe"]
            annret_grid.loc[lb, n] = stats["ann_ret"]
            maxdd_grid.loc[lb, n]  = stats["max_dd"]
            marker = " ★" if (lb == BASELINE_LB and n == BASELINE_N) else ""
            print(f"    LB={lb:>3}d, N={n}: Sharpe {stats['sharpe']:+.2f}, "
                  f"AnnRet {stats['ann_ret']*100:+6.1f}%, MDD {stats['max_dd']*100:6.1f}%{marker}")

    # ── Grid statistics ──────────────────────────────────────────────────
    all_sharpes = sharpe_grid.values.flatten()
    n_cells = len(all_sharpes)
    baseline_sharpe = float(sharpe_grid.loc[BASELINE_LB, BASELINE_N])
    print()
    print("=" * 78)
    print("  Grid summary")
    print("=" * 78)
    print(f"  Baseline (90d, top-3) net Sharpe : {baseline_sharpe:+.2f}")
    print(f"  Median across grid               : {float(np.median(all_sharpes)):+.2f}")
    print(f"  Mean   across grid               : {float(np.mean(all_sharpes)):+.2f}")
    print(f"  Min                              : {float(np.min(all_sharpes)):+.2f}")
    print(f"  Max                              : {float(np.max(all_sharpes)):+.2f}")
    print(f"  Fraction cells Sharpe > 1.0      : {(all_sharpes > 1.0).sum()}/{n_cells}  ({(all_sharpes > 1.0).mean()*100:.0f}%)")
    print(f"  Fraction cells Sharpe > 0.8      : {(all_sharpes > 0.8).sum()}/{n_cells}  ({(all_sharpes > 0.8).mean()*100:.0f}%)")
    print(f"  Fraction cells Sharpe > 0.0      : {(all_sharpes > 0.0).sum()}/{n_cells}  ({(all_sharpes > 0.0).mean()*100:.0f}%)")

    # neighbours of baseline: LB ∈ {60, 90, 120} × N ∈ {2, 3, 4}
    nbr_lb = [60, 90, 120]
    nbr_n  = [2, 3, 4]
    nbr_sharpes = sharpe_grid.loc[nbr_lb, nbr_n].values.flatten()
    print(f"  Neighbours of baseline (Sharpe)  : min {nbr_sharpes.min():+.2f}, "
          f"median {float(np.median(nbr_sharpes)):+.2f}, max {nbr_sharpes.max():+.2f}")

    # ── Pre-registered pass criteria ─────────────────────────────────────
    c1 = float(np.median(all_sharpes)) >= 1.0
    c2 = (all_sharpes > 1.0).mean() >= 0.50
    c3 = nbr_sharpes.min() >= 0.9
    c4 = (all_sharpes < 0).sum() == 0
    print()
    print("VERDICT (pre-registered criteria):")
    print(f"  1. Median Sharpe ≥ 1.0            : {'PASS' if c1 else 'FAIL'} ({float(np.median(all_sharpes)):+.2f})")
    print(f"  2. ≥50% cells with Sharpe > 1.0   : {'PASS' if c2 else 'FAIL'} ({(all_sharpes > 1.0).mean()*100:.0f}%)")
    print(f"  3. Baseline neighbours ≥ 0.9      : {'PASS' if c3 else 'FAIL'} (min {nbr_sharpes.min():+.2f})")
    print(f"  4. No cell with Sharpe < 0        : {'PASS' if c4 else 'FAIL'} ({(all_sharpes < 0).sum()} negative cells)")
    n_pass = int(c1) + int(c2) + int(c3) + int(c4)
    if n_pass == 4:
        print(f"  ▶︎ ✅ EDGE IS ROBUST — the #35 win generalises across parameters.")
    elif n_pass >= 2:
        print(f"  ▶︎ ⚠️  {n_pass}/4 — edge holds broadly but has some fragile cells.")
    else:
        print(f"  ▶︎ ❌ {n_pass}/4 — the baseline win looks spec-lucky.")

    # ── Plot Sharpe heatmap ──────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, (grid, title, cmap, fmt) in zip(
        axes,
        [(sharpe_grid, "Net Sharpe", "RdYlGn", "%+.2f"),
         (annret_grid * 100, "Ann Return (%)", "RdYlGn", "%+.0f"),
         (maxdd_grid * 100, "Max Drawdown (%)", "RdYlGn_r", "%+.0f")],
    ):
        vals = grid.astype(float).values
        vabs = float(np.abs(vals).max())
        im = ax.imshow(vals, aspect="auto", cmap=cmap,
                       vmin=-vabs if title != "Max Drawdown (%)" else vals.min(),
                       vmax=vabs if title != "Max Drawdown (%)" else 0)
        ax.set_xticks(range(len(TOPN_GRID)))
        ax.set_xticklabels([f"top-{n}" for n in TOPN_GRID])
        ax.set_yticks(range(len(LOOKBACK_GRID)))
        ax.set_yticklabels([f"{lb}d" for lb in LOOKBACK_GRID])
        ax.set_title(title)
        ax.set_xlabel("Top-N held")
        ax.set_ylabel("Lookback")
        for i in range(vals.shape[0]):
            for j in range(vals.shape[1]):
                is_baseline = (LOOKBACK_GRID[i] == BASELINE_LB and TOPN_GRID[j] == BASELINE_N)
                weight = "bold" if is_baseline else "normal"
                edge = "★ " if is_baseline else ""
                ax.text(j, i, edge + (fmt % vals[i, j]),
                        ha="center", va="center", fontsize=9,
                        color="black", fontweight=weight)
        plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

    fig.suptitle(
        f"Strategy #37 — Parameter robustness heatmap on #35 (crypto xsec momentum)\n"
        f"{len(LOOKBACK_GRID)*len(TOPN_GRID)} variants  ·  Baseline ★ = 90d lookback / top-3  ·  "
        f"Median Sharpe {float(np.median(all_sharpes)):+.2f}",
        fontsize=13,
    )
    plt.tight_layout()
    out = REPORTS / "strategy_37_crypto_xsec_momentum_robustness.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # ── CSV ──────────────────────────────────────────────────────────────
    if csv_out is not None:
        long_rows = []
        for lb in LOOKBACK_GRID:
            for n in TOPN_GRID:
                long_rows.append(dict(
                    lookback_days   = lb,
                    top_n           = n,
                    net_sharpe      = float(sharpe_grid.loc[lb, n]),
                    ann_return      = float(annret_grid.loc[lb, n]),
                    max_drawdown    = float(maxdd_grid.loc[lb, n]),
                    is_baseline     = (lb == BASELINE_LB and n == BASELINE_N),
                ))
        out_df = pd.DataFrame(long_rows)
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(csv_out, index=False, float_format="%.6f")
        print(f"CSV saved : {csv_out.relative_to(REPO)}  ({len(out_df)} rows)")

    return dict(
        baseline_sharpe = baseline_sharpe,
        median_sharpe   = float(np.median(all_sharpes)),
        min_sharpe      = float(np.min(all_sharpes)),
        max_sharpe      = float(np.max(all_sharpes)),
        pct_gt_1        = float((all_sharpes > 1.0).mean()),
        pct_gt_0        = float((all_sharpes > 0.0).mean()),
        criteria_passed = n_pass,
    )


if __name__ == "__main__":
    run(csv_out=TRACK / "strategy_37_crypto_xsec_momentum_robustness_track_record.csv")
