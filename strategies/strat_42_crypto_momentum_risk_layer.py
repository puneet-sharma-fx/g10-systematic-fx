"""
Strategy #42 — Risk layer for crypto momentum (#35): vol-target + BTC 200-DMA regime

#35 (top-3 of 10 crypto majors by 90d return, monthly) is the repo's cleanest
win (SR 1.44, robust per #37) but its −88% MaxDD makes it un-holdable. #36
showed a VIX-based filter fails here: crypto crashes are not equity-panic
events. This tests two crypto-native controls instead.

Spec (base identical to #35, re-built on backtest/common.py and extended to
2026 for a hold-out):
  - Base     : 10 majors, eligible after 60d history, long top-3 EW by trailing
               90-calendar-day return, month-end rebalance, 30 bps RT per leg
  - Layer A  : vol-target — scale exposure to 50% annualised using the
               trailing 30-day realised vol of the current basket; cap 1.0
               (no leverage, remainder in cash). Scale updated weekly.
  - Layer B  : regime — exposure 0 when yesterday's BTC close < its 200-DMA
  - Combined : A × B  ← the strategy under test; A-only and B-only are
               diagnostics
  - Cash earns 0. Costs charged on all exposure changes.
  - Period   : 2015–2024 in-sample, 2025+ hold-out. 365-day annualisation.

Pre-registered pass criteria (combined vs base, set before first run):
  1. In-sample MaxDD improves by ≥ 25pp (base ≈ −88%)
  2. In-sample net Sharpe ≥ base Sharpe − 0.10
  3. In-sample Calmar improves
  4. Hold-out Sharpe ≥ base hold-out Sharpe − 0.10
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import Result, fetch_close, split, stats, turnover_cost  # noqa: E402

NUMBER = 42
TITLE = "Crypto momentum (#35) + vol-target + BTC 200-DMA regime"
DAYS = 365
START = "2015-01-01"
COINS = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "BNB": "BNB-USD", "ADA": "ADA-USD",
         "DOGE": "DOGE-USD", "AVAX": "AVAX-USD", "LINK": "LINK-USD", "DOT": "DOT-USD", "XRP": "XRP-USD"}
LOOKBACK, MIN_HISTORY, TOP_N, COST_BPS_RT = 90, 60, 3, 30.0
VOL_TARGET, VOL_WINDOW, REGIME_DMA = 0.50, 30, 200
SUBPERIODS = {"2018 bear": ("2018-01-01", "2018-12-31"), "2019-20": ("2019-01-01", "2020-12-31"),
              "2021 bull": ("2021-01-01", "2021-12-31"), "2022 crash": ("2022-01-01", "2022-12-31"),
              "2023-24": ("2023-01-01", "2024-12-31")}


def base_weights() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(#35 target weights held on each day, daily coin returns)."""
    raw = {c: fetch_close(t) for c, t in COINS.items()}
    idx = pd.date_range(START, max(s.index.max() for s in raw.values()), freq="D")
    px = pd.DataFrame({c: s.reindex(idx).ffill() for c, s in raw.items()})
    eligible = pd.DataFrame({c: idx >= s.index.min() + pd.Timedelta(days=MIN_HISTORY)
                             for c, s in raw.items()}, index=idx)
    lb = (px / px.shift(LOOKBACK) - 1).where(eligible)
    rebal = idx[idx.is_month_end]
    target = pd.DataFrame(np.nan, index=idx, columns=px.columns)
    for d in rebal:
        s = lb.loc[d].dropna()
        if s.empty:
            continue
        w = pd.Series(0.0, index=px.columns)
        w[s.nlargest(min(TOP_N, len(s))).index] = 1.0 / min(TOP_N, len(s))
        target.loc[d] = w
    held = target.ffill().fillna(0.0).shift(1).fillna(0.0)
    first = rebal[0] + pd.Timedelta(days=1)
    return held.loc[first:], px.pct_change().fillna(0.0).loc[first:]


def vol_scalar(held: pd.DataFrame, rets: pd.DataFrame) -> pd.Series:
    """Weekly-updated min(1, target / trailing vol of the CURRENT basket)."""
    hist = pd.Series(index=held.index, dtype=float)
    for d in held.index[held.index.dayofweek == 6]:          # Sundays
        w = held.loc[d]
        past = rets.loc[:d].iloc[-VOL_WINDOW - 1:-1]          # strictly before d
        if len(past) < VOL_WINDOW or w.abs().sum() == 0:
            continue
        vol = (past @ w).std() * np.sqrt(DAYS)
        hist[d] = min(1.0, VOL_TARGET / vol) if vol > 0 else 1.0
    return hist.ffill().fillna(1.0)


def regime_scalar(index: pd.DatetimeIndex) -> pd.Series:
    btc = fetch_close("BTC-USD").reindex(index).ffill()
    on = (btc > btc.rolling(REGIME_DMA).mean()).astype(float)
    return on.shift(1).fillna(1.0)                            # yesterday's close decides today


def run_variant(held: pd.DataFrame, rets: pd.DataFrame, scale: pd.Series) -> pd.Series:
    w = held.mul(scale, axis=0)
    return (w * rets).sum(axis=1) - turnover_cost(w, COST_BPS_RT)


def run() -> dict:
    held, rets = base_weights()
    vs, rs = vol_scalar(held, rets), regime_scalar(held.index)
    one = pd.Series(1.0, index=held.index)
    base = run_variant(held, rets, one)
    a_only = run_variant(held, rets, vs)
    b_only = run_variant(held, rets, rs)
    combo = run_variant(held, rets, vs * rs)

    res = Result(NUMBER, TITLE, net=combo, benchmarks={"#35 base": base, "BTC buy-and-hold": rets["BTC"]},
                 periods=DAYS, subperiods=SUBPERIODS)
    sb, sc = stats(split(base)[0], DAYS), stats(split(combo)[0], DAYS)
    hb, hc = stats(split(base)[1], DAYS), stats(split(combo)[1], DAYS)
    criteria = {
        f"MaxDD improves ≥25pp ({sb['max_dd']:.0%} → {sc['max_dd']:.0%})": sc["max_dd"] - sb["max_dd"] >= 0.25,
        f"Sharpe ≥ base − 0.10 ({sb['sharpe']:.2f} → {sc['sharpe']:.2f})": sc["sharpe"] >= sb["sharpe"] - 0.10,
        f"Calmar improves ({sb['calmar']:.2f} → {sc['calmar']:.2f})": sc["calmar"] > sb["calmar"],
        f"Hold-out Sharpe ≥ base − 0.10 ({hb['sharpe']:.2f} → {hc['sharpe']:.2f})": hc["sharpe"] >= hb["sharpe"] - 0.10,
    }
    s = res.print(criteria)
    print("\n  Variant table (in-sample 2015–2024 | hold-out 2025+):")
    for name, r in (("#35 base", base), ("A vol-target", a_only), ("B BTC regime", b_only), ("A×B combined", combo)):
        i, h = stats(split(r)[0], DAYS), stats(split(r)[1], DAYS)
        print(f"    {name:<14} SR {i['sharpe']:+.2f} | ret {i['ann_ret']:+.0%} | vol {i['ann_vol']:.0%} | "
              f"MaxDD {i['max_dd']:.0%} | Calmar {i['calmar']:.2f} || hold-out SR {h['sharpe']:+.2f}, MaxDD {h['max_dd']:.0%}")
    print(f"  Avg exposure: A {vs.mean():.2f} | B {rs.mean():.2f} | A×B {(vs * rs).mean():.2f}")
    track = pd.DataFrame({"base_net": base, "vol_scalar": vs, "regime_on": rs, "net": combo})
    res.save(extra=track, slug=f"strategy_{NUMBER}_crypto_momentum_risk_layer")
    return s


if __name__ == "__main__":
    run()


def sweep() -> pd.DataFrame:
    """Robustness diagnostic: DMA length × vol target (not used for the verdict)."""
    global VOL_TARGET, REGIME_DMA
    held, rets = base_weights()
    rows = []
    for dma in (100, 150, 200, 250):
        for tgt in (0.40, 0.50, 0.60):
            VOL_TARGET, REGIME_DMA = tgt, dma
            r = run_variant(held, rets, vol_scalar(held, rets) * regime_scalar(held.index))
            i, h = stats(split(r)[0], DAYS), stats(split(r)[1], DAYS)
            rows.append({"dma": dma, "vol_tgt": tgt, "SR": i["sharpe"], "MaxDD": i["max_dd"],
                         "holdout SR": h["sharpe"]})
    VOL_TARGET, REGIME_DMA = 0.50, 200
    return pd.DataFrame(rows)
