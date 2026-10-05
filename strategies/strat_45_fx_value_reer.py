"""
Strategy #45 — FX value: 5-year real-exchange-rate reversal (Asness-Moskowitz-Pedersen 2013)

Value is the one FX pillar never tested here. AMP's FX value signal is the
negative of the 5-year change in the real exchange rate: currencies that got
expensive in real terms tend to mean-revert over years. Slow, monthly, and
uses inflation-adjusted levels — nothing in common with the dead daily signals.

Spec:
  - Universe : 10 G10 ccys incl. USD
  - Signal   : value_c = −[log REER_c(t) − mean log REER_c over months t−66..t−54]
               (BIS broad REER, FRED RB**BIS; month M usable from end of M+1)
  - Portfolio: cross-sectional rank weights, demeaned, scaled so Σ|w| = 1
               (≈ 0.5 long / 0.5 short); USD weight implicit
  - Rebalance: month-end
  - Returns  : aligned FX + carry accrual, net of per-pair bps costs
  - Period   : 2011–2024 in-sample, 2025+ hold-out

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > 0.3
  2. At least 3 of 4 sub-period Sharpes positive
  3. Correlation with a carry portfolio (same construction) < 0.3 —
     value must be a distinct return stream to earn a place in the triplet
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import (FX_COST_BPS_RT, G10_VS_USD, Result, fetch_fred,  # noqa: E402
                             foreign_vs_usd_returns, fetch_fx, short_rates, split, stats, turnover_cost)

NUMBER = 45
TITLE = "FX value — 5y real exchange rate reversal (AMP 2013)"
CCYS = ["USD", "EUR", "GBP", "AUD", "NZD", "JPY", "CAD", "CHF", "SEK", "NOK"]
REER = {"USD": "RBUSBIS", "EUR": "RBXMBIS", "GBP": "RBGBBIS", "AUD": "RBAUBIS", "NZD": "RBNZBIS",
        "JPY": "RBJPBIS", "CAD": "RBCABIS", "CHF": "RBCHBIS", "SEK": "RBSEBIS", "NOK": "RBNOBIS"}
COST_BY_CCY = {(p[3:] if p.startswith("USD") else p[:3]): FX_COST_BPS_RT[p] for p in G10_VS_USD}


def month_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(idx.to_series().groupby(idx.to_period("M")).max().values)


def rank_weights(score: pd.DataFrame) -> pd.DataFrame:
    """Demeaned cross-sectional ranks, scaled to Σ|w| = 1 per row."""
    r = score.rank(axis=1)
    r = r.sub(r.mean(axis=1), axis=0)
    return r.div(r.abs().sum(axis=1), axis=0)


def value_score(idx: pd.DatetimeIndex) -> pd.DataFrame:
    """Monthly (month-end) value scores, point-in-time."""
    m = pd.DataFrame({c: np.log(fetch_fred(s)) for c, s in REER.items()})
    anchor = m.shift(54).rolling(13).mean()               # mean of months t−66..t−54
    v = -(m - anchor)
    v.index = v.index + pd.offsets.MonthEnd(2)             # publication lag
    me = month_ends(idx)
    return v.reindex(v.index.union(me)).ffill().reindex(me)


def carry_score(idx: pd.DatetimeIndex) -> pd.DataFrame:
    me = month_ends(idx)
    r = short_rates(idx, point_in_time=True).loc[me]
    return r[CCYS].sub(r["USD"], axis=0)


def momentum_score(idx: pd.DatetimeIndex) -> pd.DataFrame:
    """12-1 month return of each ccy vs USD (USD = 0), aligned FX."""
    me = month_ends(idx)
    lvl = {}
    for p in G10_VS_USD:
        px = fetch_fx(p, start="2009-01-01")
        lvl[p[3:] if p.startswith("USD") else p[:3]] = (1 / px) if p.startswith("USD") else px
    lvl = pd.DataFrame(lvl)
    lvl = lvl.reindex(lvl.index.union(me)).ffill().reindex(me)
    mom = lvl.shift(1) / lvl.shift(12) - 1
    mom["USD"] = 0.0
    return mom[CCYS]


def portfolio(weights_me: pd.DataFrame, rets: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """(net, gross) daily returns from month-end weights (USD column dropped)."""
    w = weights_me[rets.columns].reindex(rets.index).ffill().shift(1).fillna(0.0)
    gross = (w * rets.fillna(0)).sum(axis=1)
    return gross - turnover_cost(w, COST_BY_CCY), gross


def run() -> dict:
    rets = foreign_vs_usd_returns()
    idx = rets.index
    value_w = rank_weights(value_score(idx).dropna(how="any"))
    carry_w = rank_weights(carry_score(idx).dropna(how="any"))
    net, gross = portfolio(value_w, rets)
    carry_net, _ = portfolio(carry_w, rets)

    res = Result(NUMBER, TITLE, net=net, gross=gross, benchmarks={"Carry (rank, same construction)": carry_net})
    ins, hold = split(net)
    corr = ins.corr(split(carry_net)[0])
    subs = res.summary()["subperiods"]
    criteria = {
        "In-sample net Sharpe > 0.3": stats(ins)["sharpe"] > 0.3,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        f"Corr with carry < 0.3 ({corr:+.2f})": corr < 0.3,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    s = res.print(criteria)
    res.save(extra=pd.DataFrame({"gross_ret": gross, "net_ret": net}), slug=f"strategy_{NUMBER}_fx_value_reer")
    return s


if __name__ == "__main__":
    run()
