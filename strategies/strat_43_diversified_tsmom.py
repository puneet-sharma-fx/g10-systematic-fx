"""
Strategy #43 — Diversified time-series momentum (Moskowitz-Ooi-Pedersen 2012) on 25 ETFs

The canonical CTA strategy. Our trend results so far: dead in G10 spot
(#11, #23, #24, #27), alive but thin on 8 commodities+crypto (#25 SR 0.43,
#28 0.42). TSMOM's documented Sharpe comes from breadth — many weakly
correlated markets across asset classes — which no test here has had.

Instruments are ETFs, not Yahoo "=F" futures: Yahoo continuous futures are
unadjusted front-month and carry fake roll jumps (large for oil/natgas).
ETF prices embed the real roll cost and dividends (auto-adjusted).

Spec (MOP 2012, monthly):
  - Universe (25): equity SPY QQQ IWM EFA EWJ EWG EWU EEM FXI ·
                   bonds IEF TLT TIP LQD BWX ·
                   commodities GLD SLV USO UNG DBA DBB ·
                   FX FXE FXY FXB FXA FXC
  - Signal   : sign of trailing 12-month total return minus US 3M cash return
  - Sizing   : w_i = sign_i × (40% / σ_i) / N, σ_i = EWMA daily vol (com 60d)
               annualised, measured at the rebalance date. N = instruments live.
  - Rebalance: month-end; weights held flat to next month-end
  - Cost     : 10 bps round-trip per unit of turnover (conservative for ETFs)
  - Period   : 2011–2024 in-sample (≥ 12m history needed), 2025+ hold-out

Benchmarks: SPY buy-and-hold; 60/40 SPY/IEF (monthly rebalanced).

Pre-registered pass criteria (set before first run):
  1. In-sample net Sharpe > 0.4
  2. At least 3 of 4 sub-period Sharpes positive
  3. Crisis alpha: mean monthly return > 0 in SPY's worst-decile months
  4. Hold-out Sharpe > 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import Result, fetch_close, short_rates, split, stats, turnover_cost  # noqa: E402

NUMBER = 43
TITLE = "Diversified TSMOM, 25 ETFs (MOP 2012)"
UNIVERSE = {
    "equity": ["SPY", "QQQ", "IWM", "EFA", "EWJ", "EWG", "EWU", "EEM", "FXI"],
    "bonds": ["IEF", "TLT", "TIP", "LQD", "BWX"],
    "commodities": ["GLD", "SLV", "USO", "UNG", "DBA", "DBB"],
    "fx": ["FXE", "FXY", "FXB", "FXA", "FXC"],
}
TICKERS = [t for group in UNIVERSE.values() for t in group]
LOOKBACK_M, VOL_COM, INSTR_VOL, COST_BPS_RT = 12, 60, 0.40, 10.0
DATA_START = "2008-01-01"


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    px = pd.DataFrame({t: fetch_close(t, start=DATA_START) for t in TICKERS}).sort_index()
    px = px[px.index.dayofweek < 5].ffill()
    return px, px.pct_change()


def weights(px: pd.DataFrame, rets: pd.DataFrame) -> pd.DataFrame:
    month_ends = px.groupby(px.index.to_period("M")).tail(1).index
    cash = short_rates(px.index, point_in_time=False)["USD"] / 100
    cash_12m = (1 + cash / 252).cumprod()
    excess_12m = (px / px.shift(252)) - (cash_12m / cash_12m.shift(252)).values[:, None]
    vol = rets.ewm(com=VOL_COM, min_periods=60).std() * np.sqrt(252)
    raw = np.sign(excess_12m) * (INSTR_VOL / vol)
    live = raw.notna().sum(axis=1).replace(0, np.nan)
    target = raw.div(live, axis=0).loc[month_ends]
    return target.reindex(px.index).ffill().shift(1).fillna(0.0)


def run() -> dict:
    px, rets = load()
    w = weights(px, rets)
    gross = (w * rets.fillna(0)).sum(axis=1)
    net = (gross - turnover_cost(w, COST_BPS_RT)).loc["2011-01-01":]
    spy = rets["SPY"].loc[net.index]
    sixty_forty = (0.6 * rets["SPY"] + 0.4 * rets["IEF"]).loc[net.index]

    res = Result(NUMBER, TITLE, net=net, gross=gross.loc[net.index],
                 benchmarks={"SPY buy-and-hold": spy, "60/40 SPY/IEF": sixty_forty})
    ins, hold = split(net)
    m_strat = (1 + ins).resample("ME").prod() - 1
    m_spy = (1 + split(spy)[0]).resample("ME").prod() - 1
    worst = m_spy <= m_spy.quantile(0.10)
    subs = res.summary()["subperiods"]
    criteria = {
        "In-sample net Sharpe > 0.4": stats(ins)["sharpe"] > 0.4,
        "≥3 of 4 sub-periods positive": sum(v > 0 for v in subs.values()) >= 3,
        f"Crisis alpha: mean return in SPY worst-decile months > 0 ({m_strat[worst].mean():+.2%})":
            m_strat[worst].mean() > 0,
        "Hold-out Sharpe > 0": stats(hold)["sharpe"] > 0,
    }
    s = res.print(criteria)

    print(f"  Corr with SPY (daily, in-sample): {ins.corr(split(spy)[0]):+.2f}")
    print(f"  Avg gross leverage: {w.loc[net.index].abs().sum(axis=1).mean():.2f}")
    print("  Contribution by asset class (in-sample ann. return):")
    for group, tickers in UNIVERSE.items():
        contrib = (w[tickers] * rets[tickers].fillna(0)).sum(axis=1).loc[ins.index]
        print(f"    {group:<12} {contrib.mean() * 252:+.2%}  (standalone SR {stats(contrib)['sharpe']:+.2f})")
    track = pd.DataFrame({"gross_ret": gross.loc[net.index], "net_ret": net,
                          "gross_leverage": w.loc[net.index].abs().sum(axis=1)})
    res.save(extra=track, slug=f"strategy_{NUMBER}_diversified_tsmom")
    return s


if __name__ == "__main__":
    run()
