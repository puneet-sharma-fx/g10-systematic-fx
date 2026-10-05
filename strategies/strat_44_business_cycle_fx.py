"""
Strategy #44 — Business-cycle differential FX (Colacito-Riddiough-Sarno 2020)

CRS (JFE 2020, "Business Cycles and Currency Returns") sort currencies on
the strength of the domestic business cycle (output gap): strong-cycle
currencies earn higher subsequent returns than weak-cycle ones — strong
economies get rate hikes priced in and attract capital. SR ≈ 0.7 in their
sample. Monthly, so the Yahoo timestamp issue cannot matter.

Spec:
  - Universe : USD, EUR (Germany CLI), GBP, AUD, JPY, CAD — the six G10
               economies whose OECD CLI is still published on FRED (NZ ends
               2019; CH, SE, NO end 2022)
  - Signal   : OECD amplitude-adjusted CLI LEVEL (≈ output-gap proxy,
               centred at 100). Month M usable from end of M+1 (publication lag).
  - Portfolio: rank all 6 (incl. USD) monthly; long top-2 (+0.25 each),
               short bottom-2 (−0.25 each); USD leg implicit
  - Returns  : aligned FX + carry accrual, net of per-pair bps costs
  - Period   : 2011–2024 in-sample, 2025+ hold-out

Caveat: FRED serves the latest CLI vintage; real-time CLI was revised, so
the in-sample result is mildly optimistic. The hold-out is less exposed.

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > 0.3
  2. At least 3 of 4 sub-period Sharpes positive
  3. Signal not "stuck": no currency sits in the same leg > 70% of months
     (the #32 inflation-differential pathology)
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import (FX_COST_BPS_RT, Result, fetch_fred, foreign_vs_usd_returns,  # noqa: E402
                             split, stats, turnover_cost)

NUMBER = 44
TITLE = "Business-cycle differential FX (OECD CLI level, CRS 2020)"
CLI = {"USD": "USALOLITOAASTSAM", "EUR": "DEULOLITOAASTSAM", "GBP": "GBRLOLITOAASTSAM",
       "AUD": "AUSLOLITOAASTSAM", "JPY": "JPNLOLITOAASTSAM", "CAD": "CANLOLITOAASTSAM"}
PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD"]
COST_BY_CCY = {(p[3:] if p.startswith("USD") else p[:3]): FX_COST_BPS_RT[p] for p in PAIRS}
TOP_N, LEG_WEIGHT = 2, 0.25


def cli_point_in_time(index: pd.DatetimeIndex) -> pd.DataFrame:
    cols = {}
    for ccy, sid in CLI.items():
        s = fetch_fred(sid).copy()
        s.index = s.index + pd.offsets.MonthEnd(2)
        cols[ccy] = s
    df = pd.DataFrame(cols).sort_index()
    return df.reindex(df.index.union(index)).ffill().reindex(index)


def build_weights(rets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(daily held weights on foreign ccys, month-end ranks incl. USD)."""
    idx = rets.index
    cli = cli_point_in_time(idx)
    month_end = idx.to_series().groupby(idx.to_period("M")).max().values
    target = pd.DataFrame(np.nan, index=idx, columns=rets.columns)
    legs = pd.DataFrame(0, index=month_end, columns=list(CLI))
    for d in month_end:
        score = cli.loc[d].dropna()
        if len(score) < len(CLI):
            continue
        order = score.sort_values()
        w = pd.Series(0.0, index=list(CLI))
        w[order.index[-TOP_N:]] = LEG_WEIGHT
        w[order.index[:TOP_N]] = -LEG_WEIGHT
        legs.loc[d] = np.sign(w)
        target.loc[d] = w[rets.columns]          # USD weight is implicit (−Σ foreign)
    return target.ffill().shift(1).fillna(0.0), legs


def run() -> dict:
    rets = foreign_vs_usd_returns(pairs=PAIRS)
    held, legs = build_weights(rets)
    gross = (held * rets.fillna(0)).sum(axis=1)
    net = gross - turnover_cost(held, COST_BY_CCY)
    passive = rets.fillna(0).mean(axis=1)

    res = Result(NUMBER, TITLE, net=net, gross=gross, benchmarks={"Passive long foreign basket": passive})
    ins, hold = split(net)
    legs_ins = legs.loc[:"2024-12-31"]
    legs_ins = legs_ins[(legs_ins != 0).any(axis=1)]
    same_leg = pd.concat([(legs_ins == 1).mean(), (legs_ins == -1).mean()], axis=1).max(axis=1)
    subs = res.summary()["subperiods"]
    criteria = {
        "In-sample net Sharpe > 0.3": stats(ins)["sharpe"] > 0.3,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        f"Not stuck: max same-leg share ≤ 70% ({same_leg.idxmax()} {same_leg.max():.0%})": same_leg.max() <= 0.70,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    s = res.print(criteria)
    print("  Share of months long / short (in-sample):")
    for c in CLI:
        print(f"    {c}: long {(legs_ins[c] == 1).mean():.0%} | short {(legs_ins[c] == -1).mean():.0%}")
    res.save(extra=pd.DataFrame({"gross_ret": gross, "net_ret": net}),
             slug=f"strategy_{NUMBER}_business_cycle_fx")
    return s


if __name__ == "__main__":
    run()
