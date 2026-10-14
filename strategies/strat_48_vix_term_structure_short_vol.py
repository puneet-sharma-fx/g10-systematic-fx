"""
Strategy #48 — Short VIX futures only in contango (VIX / VIX3M term-structure filter)

First volatility strategy in the repo. VIX futures usually trade above spot
VIX (contango) because investors pay up for crash insurance; a short-VIX-
futures position harvests that roll-down — the volatility risk premium.
The catch is the left tail: SVXY lost 83% on 6-Feb-2018. Simon & Campasano
(2014, J. Derivatives, "The VIX Futures Basis") show the premium is earned
when the curve is in contango and lost in backwardation, so the signal is
simply: hold short-vol only when VIX < VIX3M.

Timestamp discipline (lesson of notebooks/fx_timestamp_audit.py): the VIX
index closes at 4:15pm ET, after SVXY's 4:00pm close. The strategy therefore
uses YESTERDAY's term structure to set today's position. The same-day
version is printed as a look-ahead diagnostic only.

Spec:
  - Instrument : SVXY (ProShares short VIX short-term futures ETF; −1x until
                 Feb-2018, −0.5x after — the series is what a holder got)
  - Signal     : ratio = VIX / VIX3M at close D−1
  - Position   : 100% SVXY if ratio < 1 (contango), else cash at US 3M rate
  - Cost       : 10 bps round-trip per switch
  - Period     : SVXY inception (Oct-2011) – 2024 in-sample, 2025+ hold-out

Benchmarks: SVXY buy-and-hold; SPY buy-and-hold.

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > 0.5
  2. MaxDD at least 20pp better than SVXY buy-and-hold
  3. At least 3 of 4 sub-period Sharpes positive
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import Result, fetch_close, short_rates, split, stats, turnover_cost  # noqa: E402

NUMBER = 48
TITLE = "Short VIX futures (SVXY) only in contango — VIX/VIX3M filter"
COST_BPS_RT = 10.0


def build(lag_days: int = 1) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """(net returns, SVXY returns, signal frame). lag_days=0 is the look-ahead diagnostic."""
    svxy = fetch_close("SVXY")
    idx = svxy.index
    vix = fetch_close("^VIX").reindex(idx).ffill()
    vix3m = fetch_close("^VIX3M").reindex(idx).ffill()
    ratio = vix / vix3m
    in_contango = (ratio < 1).astype(float)
    # position held over (D-1 close, D close]; decided from ratio known `lag_days` closes earlier
    pos = in_contango.shift(1 + lag_days).fillna(0.0)
    svxy_ret = svxy.pct_change().fillna(0.0)
    cash = short_rates(idx, point_in_time=False)["USD"] / 100 / 252
    net = pos * svxy_ret + (1 - pos) * cash - turnover_cost(pos, COST_BPS_RT)
    frame = pd.DataFrame({"vix": vix, "vix3m": vix3m, "ratio": ratio, "position": pos,
                          "svxy_ret": svxy_ret, "net_ret": net})
    return net.iloc[1:], svxy_ret.iloc[1:], frame


def run() -> dict:
    net, svxy_ret, frame = build(lag_days=1)
    spy = fetch_close("SPY").pct_change().reindex(net.index).fillna(0.0)
    res = Result(NUMBER, TITLE, net=net, benchmarks={"SVXY buy-and-hold": svxy_ret, "SPY buy-and-hold": spy})

    ins, hold = split(net)
    s_ins, s_bh = stats(ins), stats(split(svxy_ret)[0])
    subs = res.summary()["subperiods"]
    criteria = {
        "In-sample net Sharpe > 0.5": s_ins["sharpe"] > 0.5,
        f"MaxDD ≥20pp better than SVXY B&H ({s_bh['max_dd']:.0%} → {s_ins['max_dd']:.0%})":
            s_ins["max_dd"] - s_bh["max_dd"] >= 0.20,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    s = res.print(criteria)

    pos = frame["position"].loc[net.index]
    print(f"  Time in SVXY: {pos.mean():.0%} | switches/yr: {pos.diff().abs().sum() / (len(pos) / 252):.1f}")
    print("  SVXY's 5 worst days — strategy position and return that day:")
    for d in svxy_ret.nsmallest(5).index:
        print(f"    {d.date()}  SVXY {svxy_ret[d]:+.1%} | in market: {'yes' if pos[d] else 'no '} | strategy {net[d]:+.1%}")
    diag, _, _ = build(lag_days=0)
    print(f"  Look-ahead diagnostic (same-day VIX, NOT tradable): in-sample SR {stats(split(diag)[0])['sharpe']:+.2f}")
    res.save(extra=frame.loc[net.index], slug=f"strategy_{NUMBER}_vix_term_structure_short_vol")
    return s


if __name__ == "__main__":
    run()
