"""
Quick exploration: change in 2Y rate differential (EU − US) vs next-day EURUSD return.

Independent variable (X) : Δ (EU 2Y − US 2Y), in percentage points, today vs yesterday
Dependent variable   (y) : EURUSD return tomorrow (close-to-close from today's close)

Hypothesis (UIP / textbook):
  When EU rates rise relative to US rates, EURUSD should appreciate.
  → Expected sign of β: POSITIVE.

Reality (empirical, well-documented):
  UIP fails at short horizons. β is typically ≈ 0 or weakly negative at the daily horizon.
  This is the "forward-rate bias" that makes carry trades profitable on average over months.

Data:
  US 2Y    : FRED `DGS2`            (daily)
  EU 2Y    : ECB SDW YC AAA 2Y      (daily — Euro-area AAA benchmark, ~German Bund curve)
  EURUSD   : yfinance `EURUSD=X`    (daily close)
"""
from __future__ import annotations

import io
import logging
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from fredapi import Fred
from scipy import stats

logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)

START = "2010-01-04"
END   = "2024-12-31"

HERE = Path(__file__).resolve().parent


def fetch_us_2y() -> pd.Series:
    fred = Fred(api_key=os.environ["FRED_API_KEY"])
    s = fred.get_series("DGS2", observation_start=START, observation_end=END)
    s.index = pd.to_datetime(s.index)
    s.name = "US_2Y"
    return s.dropna()


def fetch_eu_2y() -> pd.Series:
    url = (
        "https://data-api.ecb.europa.eu/service/data/YC/"
        "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y"
        f"?format=csvdata&startPeriod={START}&endPeriod={END}"
    )
    r = requests.get(url, headers={"Accept": "text/csv"}, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    s = pd.Series(df["OBS_VALUE"].values, index=pd.to_datetime(df["TIME_PERIOD"]), name="EU_2Y")
    return s.sort_index().dropna()


def fetch_eurusd() -> pd.Series:
    df = yf.download("EURUSD=X", start=START, end=END, auto_adjust=True, progress=False)
    s = df["Close"].squeeze()
    s.name = "EURUSD"
    s.index = pd.to_datetime(s.index)
    return s.dropna()


def main() -> None:
    print(f"Fetching data {START} → {END} ...")
    us = fetch_us_2y()
    eu = fetch_eu_2y()
    px = fetch_eurusd()
    print(f"  US 2Y  : {len(us)} daily obs")
    print(f"  EU 2Y  : {len(eu)} daily obs")
    print(f"  EURUSD : {len(px)} daily obs")

    # Align on common business-day index
    idx = pd.bdate_range(start=START, end=END)
    us = us.reindex(idx).ffill()
    eu = eu.reindex(idx).ffill()
    px = px.reindex(idx).ffill()

    # Rate differential (in percentage points)
    rate_diff = (eu - us).rename("rate_diff_pp")

    # Daily change in differential (in percentage points)
    d_diff = rate_diff.diff().rename("d_diff_pp")

    # Next-day EURUSD return
    fwd_ret = px.pct_change().shift(-1).rename("fwd_ret")

    # Combine and drop missing
    df = pd.concat([d_diff, fwd_ret], axis=1).dropna()

    # Regression
    slope, intercept, r, p, stderr = stats.linregress(df["d_diff_pp"], df["fwd_ret"])
    r2 = r ** 2

    print()
    print("─── Regression: next-day EURUSD return  ~  α + β · Δ(EU 2Y − US 2Y) ───")
    print(f"  N observations : {len(df):,}")
    print(f"  β (slope)      : {slope:+.5f}   (EURUSD return per +1pp Δ in rate diff)")
    print(f"  α (intercept)  : {intercept:+.6f}")
    print(f"  R²             : {r2:.5f}")
    print(f"  Correlation r  : {r:+.4f}")
    print(f"  p-value        : {p:.4g}")
    print(f"  Std err of β   : {stderr:.5f}")
    print(f"  t-statistic    : {slope / stderr:+.2f}")

    # Same-day check (for contrast)
    same_day = pd.concat([d_diff, px.pct_change().rename("same_day_ret")], axis=1).dropna()
    s2 = stats.linregress(same_day["d_diff_pp"], same_day["same_day_ret"])
    print()
    print(f"  Same-day  contemporaneous: β={s2.slope:+.5f}, R²={s2.rvalue**2:.5f}, p={s2.pvalue:.3g}")
    print(f"  Next-day  predictive    : β={slope:+.5f}, R²={r2:.5f}, p={p:.3g}")

    # Plot — scatter with regression line
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: full scatter
    ax = axes[0]
    ax.scatter(df["d_diff_pp"], df["fwd_ret"], alpha=0.25, s=8, color="#1f77b4")
    xs = np.linspace(df["d_diff_pp"].min(), df["d_diff_pp"].max(), 100)
    ax.plot(xs, intercept + slope * xs, "r-", lw=2,
            label=f"β = {slope:+.4f},  R² = {r2:.4f},  p = {p:.2g}")
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlabel("Δ (EU 2Y − US 2Y) today, percentage points")
    ax.set_ylabel("Next-day EURUSD return")
    ax.set_title(f"Daily — N = {len(df):,}")
    ax.legend(loc="upper left")

    # Right: same data, but bucketed into deciles of X
    ax = axes[1]
    df_b = df.copy()
    df_b["bucket"] = pd.qcut(df_b["d_diff_pp"], 10, labels=False, duplicates="drop")
    g = df_b.groupby("bucket").agg(
        x_mean=("d_diff_pp", "mean"),
        y_mean=("fwd_ret", "mean"),
        y_sem=("fwd_ret", lambda s: s.std() / np.sqrt(len(s))),
        n=("fwd_ret", "size"),
    )
    ax.errorbar(g["x_mean"], g["y_mean"], yerr=g["y_sem"], fmt="o-", color="#d62728",
                capsize=4, markersize=8, lw=1.5)
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlabel("Δ (EU 2Y − US 2Y) decile-mean today, pp")
    ax.set_ylabel("Mean next-day EURUSD return, decile-aggregate")
    ax.set_title("Decile-aggregated (cleaner signal)")
    ax.grid(True, alpha=0.3)

    plt.suptitle("Δ 2Y rate differential vs next-day EURUSD return  (2010–2024)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = HERE / "rate_diff_2y_vs_eurusd.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved: {out}")


if __name__ == "__main__":
    main()
