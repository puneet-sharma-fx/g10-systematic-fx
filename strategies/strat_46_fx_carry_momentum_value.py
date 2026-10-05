"""
Strategy #46 — FX carry + momentum + value combined (Asness-Moskowitz-Pedersen 2013)

Each FX pillar has failed alone here: carry (#20 SR 0.07), momentum (#11
−0.34), value (#45 −0.15). AMP's point is that the three are close to
uncorrelated (value vs carry +0.02 in #45), so an equal mix can earn a
positive Sharpe even when each leg is weak. This is that test — signal
definitions are fixed by #45 so nothing is tuned here.

Spec:
  - Universe : 10 G10 ccys incl. USD
  - Signals  : carry  = 3M rate − US 3M (point-in-time)
               momentum = 12-1 month return vs USD (aligned FX)
               value  = −5y change in log REER (#45)
  - Portfolio: each signal → demeaned rank weights (Σ|w| = 1); combined
               weights = equal average of the three; month-end rebalance
  - Returns  : aligned FX + carry accrual, net of per-pair bps costs
  - Period   : 2011–2024 in-sample, 2025+ hold-out

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > 0.3
  2. Combined Sharpe above the best single pillar (diversification works)
  3. At least 3 of 4 sub-period Sharpes positive
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import Result, foreign_vs_usd_returns, split, stats  # noqa: E402
from strat_45_fx_value_reer import (carry_score, momentum_score, portfolio,  # noqa: E402
                                    rank_weights, value_score)

NUMBER = 46
TITLE = "FX carry + momentum + value, equal-weight (AMP 2013)"


def run() -> dict:
    rets = foreign_vs_usd_returns()
    idx = rets.index
    pillars = {"carry": rank_weights(carry_score(idx).dropna(how="any")),
               "momentum": rank_weights(momentum_score(idx).dropna(how="any")),
               "value": rank_weights(value_score(idx).dropna(how="any"))}
    common = pillars["carry"].index.intersection(pillars["momentum"].index).intersection(pillars["value"].index)
    combo_w = sum(w.loc[common] for w in pillars.values()) / 3
    net, gross = portfolio(combo_w, rets)
    legs = {k: portfolio(w.loc[common], rets)[0] for k, w in pillars.items()}

    res = Result(NUMBER, TITLE, net=net, gross=gross, benchmarks={f"{k} alone": v for k, v in legs.items()})
    ins, hold = split(net)
    leg_sr = {k: stats(split(v)[0])["sharpe"] for k, v in legs.items()}
    subs = res.summary()["subperiods"]
    criteria = {
        "In-sample net Sharpe > 0.3": stats(ins)["sharpe"] > 0.3,
        f"Beats best single pillar ({max(leg_sr, key=leg_sr.get)} {max(leg_sr.values()):+.2f})":
            stats(ins)["sharpe"] > max(leg_sr.values()),
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    s = res.print(criteria)
    print("  Pillar correlations (in-sample daily):")
    print(pd.DataFrame({k: split(v)[0] for k, v in legs.items()}).corr().round(2).to_string())
    res.save(extra=pd.DataFrame({"gross_ret": gross, "net_ret": net, **{f"{k}_net": v for k, v in legs.items()}}),
             slug=f"strategy_{NUMBER}_fx_carry_momentum_value")
    return s


if __name__ == "__main__":
    run()
