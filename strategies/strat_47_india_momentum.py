"""
Strategy #47 — Indian equities 12-1 momentum, Nifty 100 universe (quarterly, long-only)

Momentum is the best-documented Indian equity anomaly (research/
india_equities_v2.md §10, Tier 1: gross SR 1.5–2.0, net 1.0–1.5). #38
(low-vol) beat Nifty 50 but lost to an equal-weight of its own universe
(IR −0.42) — its "edge" was the equal-weight/size tilt. This test is built
to catch that trap: the decisive benchmark is equal-weight of the same names.

Spec:
  - Universe : #38's ~100-stock Nifty 100 list (same survivorship bias:
               current constituents, not point-in-time)
  - Signal   : 12-1 total return (t−252 to t−21 trading days); ≥ 252d history
  - Portfolio: long top-30 equal-weight
  - Rebalance: quarter-end (Mar/Jun/Sep/Dec)
  - Cost     : 30 bps round-trip per unit of turnover (STT 0.1% each side
               on delivery + brokerage/slippage)
  - Period   : 2011–2024 in-sample, 2025+ hold-out. Returns in INR.

Benchmarks: Nifty 50 buy-and-hold (^NSEI); equal-weight of the same universe
(quarterly rebalanced, same cost); #38-style low-vol is in STRATEGIES.md.

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > Nifty 50 buy-and-hold Sharpe
  2. IR > 0.2 vs equal-weight of the same universe (the #38 trap)
  3. At least 3 of 4 sub-period Sharpes positive
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import Result, fetch_close, information_ratio, split, stats, turnover_cost  # noqa: E402
from strat_38_india_nifty_low_vol import UNIVERSE  # noqa: E402

NUMBER = 47
TITLE = "India 12-1 momentum, Nifty 100 top-30 (quarterly, long-only)"
LOOKBACK, SKIP, TOP_N, COST_BPS_RT = 252, 21, 30, 30.0
DATA_START = "2009-01-01"


def load() -> pd.DataFrame:
    cols = {}
    for t in UNIVERSE:
        try:
            cols[t] = fetch_close(f"{t}.NS", start=DATA_START)
        except Exception:
            print(f"  skip {t} (no data)")
    px = pd.DataFrame(cols).sort_index()
    return px[px.index.dayofweek < 5]


def quarter_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(idx.to_series().groupby(idx.to_period("Q")).max().values)


def run() -> dict:
    px = load()
    rets = px.pct_change(fill_method=None)
    history = px.notna().cumsum()
    signal = (px.shift(SKIP) / px.shift(LOOKBACK) - 1).where(history >= LOOKBACK)
    qe = quarter_ends(px.index)

    target = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    ew_target = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    for d in qe:
        s = signal.loc[d].dropna()
        if len(s) < TOP_N:
            continue
        w = pd.Series(0.0, index=px.columns)
        w[s.nlargest(TOP_N).index] = 1.0 / TOP_N
        target.loc[d] = w
        eligible = s.index
        e = pd.Series(0.0, index=px.columns)
        e[eligible] = 1.0 / len(eligible)
        ew_target.loc[d] = e

    def book(t: pd.DataFrame) -> pd.Series:
        w = t.ffill().shift(1).fillna(0.0)
        return (w * rets.fillna(0)).sum(axis=1) - turnover_cost(w, COST_BPS_RT)

    net = book(target).loc["2011-01-01":]
    ew = book(ew_target).loc[net.index]
    nifty = fetch_close("^NSEI", start=DATA_START).pct_change().reindex(net.index).fillna(0)

    res = Result(NUMBER, TITLE, net=net, benchmarks={"Nifty 50 B&H": nifty, "EW same universe": ew})
    ins, hold = split(net)
    subs = res.summary()["subperiods"]
    criteria = {
        f"Net Sharpe > Nifty 50 B&H ({stats(split(nifty)[0])['sharpe']:.2f})":
            stats(ins)["sharpe"] > stats(split(nifty)[0])["sharpe"],
        f"IR > 0.2 vs EW same universe ({information_ratio(ins, split(ew)[0]):+.2f})":
            information_ratio(ins, split(ew)[0]) > 0.2,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    s = res.print(criteria)
    print(f"  Universe with data: {px.shape[1]} stocks | CAGR-ish ann ret strat {stats(ins)['ann_ret']:+.1%} "
          f"vs EW {stats(split(ew)[0])['ann_ret']:+.1%} vs Nifty {stats(split(nifty)[0])['ann_ret']:+.1%}")
    res.save(extra=pd.DataFrame({"net_ret": net, "ew_ret": ew, "nifty_ret": nifty}),
             slug=f"strategy_{NUMBER}_india_momentum")
    return s


if __name__ == "__main__":
    run()
