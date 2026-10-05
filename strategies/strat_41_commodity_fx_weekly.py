"""
Strategy #41 — Commodity → commodity-currency lead-lag, weekly (copper→AUD, Brent→NOK, WTI→CAD)

#17 (oil → next-day USDCAD, SR 3.96) turned out to be the Yahoo FX timestamp
look-ahead (#19, notebooks/fx_timestamp_audit.py). The economic idea — that
commodity-currency FX under-reacts to its terms-of-trade driver — was never
tested cleanly. This is that test, at a weekly horizon where a few hours of
timestamp noise cannot matter, on aligned FX.

Ferraro-Rogoff-Rossi (2015, JIMF) find the oil→CAD link is mostly
contemporaneous at daily frequency; a lagged weekly edge would be new.
Prior is therefore sceptical.

Spec:
  - Legs     : AUD ← copper (HG=F), NOK ← Brent (BZ=F), CAD ← WTI (CL=F)
  - Signal   : sign of the commodity's Friday-to-Friday return (week w)
  - Position : long the currency vs USD for week w+1 if signal > 0, else short
  - Portfolio: equal-weight the three legs (1/3 each)
  - Returns  : aligned FX spot + carry accrual, net of per-pair bps costs
  - Period   : 2011–2024 in-sample; 2025+ hold-out

Pre-registered pass criteria (set before first run):
  1. Portfolio in-sample net Sharpe > 0.3
  2. At least 2 of 3 legs have positive net Sharpe
  3. At least 3 of 4 sub-period Sharpes positive
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import (FX_COST_BPS_RT, Result, fetch_close, foreign_vs_usd_returns,  # noqa: E402
                             split, stats, turnover_cost)

NUMBER = 41
TITLE = "Commodity → commodity-FX, weekly (copper→AUD, Brent→NOK, WTI→CAD)"
LEGS = {  # ccy: (commodity ticker, pair for costs)
    "AUD": ("HG=F", "AUDUSD"),
    "NOK": ("BZ=F", "USDNOK"),
    "CAD": ("CL=F", "USDCAD"),
}


def leg_returns(ccy: str, fx_ret: pd.Series) -> tuple[pd.Series, pd.Series]:
    """(net daily return, daily held position) for one leg."""
    ticker, pair = LEGS[ccy]
    cmdty = fetch_close(ticker).reindex(fx_ret.index).ffill()
    fridays = fx_ret.index[fx_ret.index.dayofweek == 4]
    weekly_sig = np.sign(cmdty.loc[fridays].pct_change())
    pos = weekly_sig.reindex(fx_ret.index).ffill().fillna(0)
    held = pos.shift(1).fillna(0)
    net = held * fx_ret - turnover_cost(held, FX_COST_BPS_RT[pair])
    return net, held


def build() -> tuple[Result, dict[str, bool], pd.DataFrame, dict[str, dict]]:
    fx = foreign_vs_usd_returns(pairs=[p for _, p in LEGS.values()])
    nets, helds = {}, {}
    for ccy in LEGS:
        nets[ccy], helds[ccy] = leg_returns(ccy, fx[ccy].fillna(0))
    net = pd.DataFrame(nets).mean(axis=1)
    passive = fx[list(LEGS)].fillna(0).mean(axis=1)

    res = Result(NUMBER, TITLE, net=net, benchmarks={"Passive long AUD/NOK/CAD": passive})
    leg_stats = {c: stats(split(n)[0]) for c, n in nets.items()}
    subs = res.summary()["subperiods"]
    criteria = {
        "Portfolio in-sample net Sharpe > 0.3": stats(split(net)[0])["sharpe"] > 0.3,
        "≥2 of 3 legs positive": sum(s["sharpe"] > 0 for s in leg_stats.values()) >= 2,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        "Hold-out Sharpe > 0": stats(split(net)[1])["sharpe"] > 0,
    }
    track = pd.DataFrame({**{f"pos_{c}": h for c, h in helds.items()},
                          **{f"net_{c}": n for c, n in nets.items()}, "net_portfolio": net})
    return res, criteria, track, leg_stats


def run() -> dict:
    res, criteria, track, leg_stats = build()
    s = res.print(criteria)
    for c, st in leg_stats.items():
        print(f"    leg {c} ← {LEGS[c][0]}: SR {st['sharpe']:+.2f} | ret {st['ann_ret']:+.2%}")
    res.save(extra=track, slug=f"strategy_{NUMBER}_commodity_fx_weekly")
    return s


if __name__ == "__main__":
    run()
