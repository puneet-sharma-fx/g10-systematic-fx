"""
Strategy #40 — Dollar carry factor (time-series DOL, Lustig-Roussanov-Verdelhan 2014)

The dollar factor (DOL) is the average return of all foreign currencies vs
USD. LRV (2014, JFE "Countercyclical Currency Risk Premia") show its SIGN is
predictable: go long the foreign basket when the average foreign short rate
is above the US rate, short it (long USD) when the US is the high-yielder.
This is a single time-series bet on the dollar — orthogonal to the
cross-sectional carry/momentum tests already rejected here (#11, #20, #31).

First strategy built on backtest/common.py: aligned FX (no Yahoo look-ahead),
carry accrual included, per-pair bps costs.

Spec (LRV 2014, G10 version):
  - Universe : 9 foreign ccys vs USD (EUR GBP AUD NZD JPY CAD CHF SEK NOK)
  - Signal   : mean(foreign 3M rate) − US 3M rate  (OECD monthly, point-in-time
               lagged one month for publication)
  - Position : +1/9 each foreign ccy if signal > 0, −1/9 each if < 0
  - Rebalance: monthly (last trading day)
  - Returns  : spot + carry accrual, net of per-pair bps costs
  - Period   : 2011–2024 in-sample; 2025+ hold-out reported separately

Benchmarks:
  - Passive long DOL (always long the foreign basket)
  - Passive short DOL (always long USD) — the 2011–2024 dollar bull market
    makes this the hard benchmark: a signal that was just "long USD most of
    the time" should not get credit for it.

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > 0.3
  2. IR > 0.2 vs the better of passive long / passive short DOL
  3. At least 3 of 4 sub-period Sharpes positive
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import (FX_COST_BPS_RT, G10_VS_USD, Result, foreign_vs_usd_returns,  # noqa: E402
                             information_ratio, short_rates, split, stats, turnover_cost)

NUMBER = 40
TITLE = "Dollar carry factor (time-series DOL, LRV 2014)"
COST_BY_CCY = {(p[3:] if p.startswith("USD") else p[:3]): FX_COST_BPS_RT[p] for p in G10_VS_USD}


def build() -> tuple[Result, dict[str, bool], pd.DataFrame]:
    rets = foreign_vs_usd_returns()
    idx = rets.index
    rates = short_rates(idx, point_in_time=True)
    foreign = [c for c in rets.columns]
    signal = rates[foreign].mean(axis=1) - rates["USD"]

    month_end = idx.to_series().groupby(idx.to_period("M")).max()
    direction = np.sign(signal.loc[month_end.values]).reindex(idx).ffill().fillna(0)
    weights = pd.DataFrame({c: direction / len(foreign) for c in foreign})
    held = weights.shift(1).fillna(0)                   # decided at close D, earns D+1

    gross = (held * rets).sum(axis=1)
    net = gross - turnover_cost(held, COST_BY_CCY)
    long_dol = rets.mean(axis=1)
    short_dol = -long_dol

    res = Result(NUMBER, TITLE, net=net, gross=gross,
                 benchmarks={"Passive long DOL": long_dol, "Passive long USD": short_dol})

    ins, hold = split(net)
    best_bench = max((long_dol, short_dol), key=lambda b: stats(split(b)[0])["sharpe"])
    subs = res.summary()["subperiods"]
    criteria = {
        "In-sample net Sharpe > 0.3": stats(ins)["sharpe"] > 0.3,
        "IR > 0.2 vs better passive DOL leg": information_ratio(ins, split(best_bench)[0]) > 0.2,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    track = pd.DataFrame({"signal_pp": signal, "direction": held.iloc[:, 0] * len(foreign),
                          "gross_ret": gross, "net_ret": net})
    return res, criteria, track


def run() -> dict:
    res, criteria, track = build()
    s = res.print(criteria)
    d = track["direction"]
    print(f"  Time long foreign basket: {(d > 0).mean():.0%} | long USD: {(d < 0).mean():.0%} "
          f"| switches: {int((d.diff().abs() > 0).sum())}")
    res.save(extra=track, slug=f"strategy_{NUMBER}_dollar_carry_factor")
    return s


if __name__ == "__main__":
    run()
