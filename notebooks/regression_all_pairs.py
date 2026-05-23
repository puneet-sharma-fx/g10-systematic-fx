"""
For each of the 8 Strategy pairs, regress next-day FX return on Δ(rate differential).

X = d_diff[t]      = (base_2Y − quote_2Y)[t] − (base_2Y − quote_2Y)[t−1]
Y = fx_ret[t+1]    = (spot[t+1] / spot[t]) − 1

Produces:
  - reports/regressions_all_pairs.png   (2×4 grid of scatter + regression lines)
  - prints a table of β, R², t, N for each pair
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"
YIELDS_CSV = REPO / "data" / "raw" / "tvc_2y_yields.csv"

START = "2010-01-04"
END   = "2024-12-31"

# Strategy specs: (number, pair, base_ccy, quote_ccy)
SPECS = [
    (1, "EURUSD", "EU", "US"),
    (2, "GBPUSD", "GB", "US"),
    (3, "AUDUSD", "AU", "US"),
    (4, "NZDUSD", "NZ", "US"),
    (5, "USDJPY", "US", "JP"),
    (6, "USDCAD", "US", "CA"),
    (7, "USDCHF", "US", "CH"),
    (8, "USDSEK", "US", "SE"),
]


def main() -> None:
    yields = pd.read_csv(YIELDS_CSV, index_col=0, parse_dates=True)

    results = []
    fig, axes = plt.subplots(2, 4, figsize=(18, 9), sharey=False)
    axes = axes.flatten()

    for ax_idx, (num, pair, base, quote) in enumerate(SPECS):
        print(f"  Strategy #{num} {pair} ...", end=" ", flush=True)
        # FX
        fx = yf.download(f"{pair}=X", start=START, end=END,
                         auto_adjust=True, progress=False)["Close"].squeeze().dropna()
        fx.index = pd.to_datetime(fx.index)

        # Align to business days
        idx = pd.bdate_range(start=START, end=END)
        base_y  = yields[base].reindex(idx).ffill()
        quote_y = yields[quote].reindex(idx).ffill()
        fx      = fx.reindex(idx).ffill()

        # X and Y
        rate_diff = base_y - quote_y
        d_diff    = rate_diff.diff()
        fwd_ret   = fx.pct_change().shift(-1)

        # Drop early period before both yield series have data
        first_valid = max(base_y.dropna().index.min(), quote_y.dropna().index.min())

        df = pd.concat([d_diff.rename("X"), fwd_ret.rename("Y")], axis=1).dropna()
        df = df[df.index >= first_valid]

        # Regression
        r = stats.linregress(df["X"], df["Y"])
        beta, intercept, rval, pval, stderr = r
        r2 = rval ** 2
        n  = len(df)
        t  = beta / stderr if stderr > 0 else float("nan")
        results.append(dict(num=num, pair=pair, base=base, quote=quote,
                            beta=beta, r2=r2, t=t, n=n,
                            period_start=df.index[0].strftime("%Y-%m-%d")))
        print(f"β={beta:+.4f}, R²={r2:.4f}, t={t:+.1f}, n={n}")

        # Scatter + regression line
        ax = axes[ax_idx]
        ax.scatter(df["X"], df["Y"], alpha=0.20, s=6, color="#1f77b4")
        xs = np.linspace(df["X"].min(), df["X"].max(), 100)
        ax.plot(xs, intercept + beta * xs, "r-", lw=2)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        ax.set_xlabel(f"Δ({base} 2Y − {quote} 2Y) on day t, pp")
        ax.set_ylabel(f"{pair} next-day return")
        ax.set_title(
            f"#{num} {pair}\nβ={beta:+.4f}, R²={r2:.4f}, t={t:+.1f}, n={n:,}",
            fontsize=11,
        )
        ax.grid(True, alpha=0.3)

    plt.suptitle(
        "Δ(2Y rate differential) on day t  vs  FX return on day t+1   ·  all G10 pairs",
        fontsize=14, fontweight="bold", y=1.00,
    )
    plt.tight_layout()
    out = REPORTS / "regressions_all_pairs.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {out.relative_to(REPO)}")

    # Summary table
    print()
    print("Summary table:")
    print("=" * 72)
    print(f"{'#':>2}  {'Pair':<8} {'β':>10}  {'R²':>8}  {'t':>7}  {'N':>6}  {'Period start':<12}")
    print("-" * 72)
    for r in results:
        print(f"{r['num']:>2}  {r['pair']:<8} {r['beta']:>+10.4f}  {r['r2']:>8.4f}  {r['t']:>+7.1f}  "
              f"{r['n']:>6,}  {r['period_start']:<12}")
    print("=" * 72)


if __name__ == "__main__":
    main()
