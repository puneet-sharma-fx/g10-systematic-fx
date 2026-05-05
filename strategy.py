"""
G10SystematicFX — main strategy class.

Combines carry, momentum, and COT signals into a composite z-score,
applies the vol-regime filter, then sizes positions using volatility targeting.

Usage:
    from strategy import G10SystematicFX, run_full_backtest
    result = run_full_backtest()
    result.returns.cumsum().plot()
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import BACKTEST, G10_PAIRS, SIGNAL_PARAMS
from data.fetchers import fetch_fx_prices, fetch_short_rates, fetch_vix
from data.cftc import fetch_cot
from signals.carry.carry import CarrySignal
from signals.momentum.momentum import MomentumSignal
from signals.sentiment.cot import COTSignal
from signals.vol_regime.vol_regime import VolRegimeFilter
from backtest.engine import run_walk_forward, BacktestResult
from backtest.metrics import print_summary

log = logging.getLogger(__name__)


class G10SystematicFX:
    """
    Signal combination and position sizing.

    Signals are combined as a weighted average z-score. Positions are:
      - Long top-N pairs by composite score
      - Short bottom-N pairs by composite score
      - Sized to target annualised portfolio volatility
      - Scaled by vol-regime filter scalar
    """

    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or BACKTEST
        weights = {k: v["weight"] for k, v in SIGNAL_PARAMS.items()}
        self.signal_weights = weights

        self.carry = CarrySignal()
        self.momentum = MomentumSignal()
        self.cot = COTSignal()
        self.vol_filter = VolRegimeFilter()

    # ── Signal combination ────────────────────────────────────────────────────

    def composite_score(
        self,
        rebalance_dates: pd.DatetimeIndex,
        **data,
    ) -> pd.DataFrame:
        carry_z = self.carry.compute(rebalance_dates, **data)
        mom_z = self.momentum.compute(rebalance_dates, **data)
        cot_z = self.cot.compute(rebalance_dates, **data)

        w = self.signal_weights
        composite = (
            carry_z * w["carry"]
            + mom_z * w["momentum"]
            + cot_z * w["cot"]
        )
        return composite

    # ── Position sizing ───────────────────────────────────────────────────────

    def compute_weights(
        self,
        rebalance_dates: pd.DatetimeIndex,
        **data,
    ) -> pd.DataFrame:
        """
        Returns a DataFrame of notional weights (rows = dates, columns = pairs).
        Weights are signed: positive = long, negative = short.
        Row sums are not constrained to 1 (the strategy is dollar-neutral by construction
        when n_long == n_short, but individual weights reflect vol-targeting).
        """
        scores = self.composite_score(rebalance_dates, **data)
        regime_scalar = self.vol_filter.compute(rebalance_dates, **data)

        n_long = int(self.cfg["n_long"])
        n_short = int(self.cfg["n_short"])
        target_vol = float(self.cfg["target_ann_vol"])
        vol_window = int(self.cfg["realised_vol_window"])

        fx_prices: pd.DataFrame = data["fx_prices"]
        px_rebal = fx_prices.reindex(rebalance_dates, method="ffill")
        realised_vol = (
            fx_prices.pct_change()
            .rolling(vol_window, min_periods=5)
            .std()
            * np.sqrt(252)  # annualised
        ).reindex(rebalance_dates, method="ffill")

        weights = pd.DataFrame(0.0, index=rebalance_dates, columns=scores.columns)

        for dt in rebalance_dates:
            row = scores.loc[dt].dropna()
            if row.empty:
                continue

            ranked = row.sort_values(ascending=False)
            longs = ranked.head(n_long).index.tolist()
            shorts = ranked.tail(n_short).index.tolist()

            for pair in longs:
                vol = realised_vol.loc[dt, pair] if pair in realised_vol.columns else None
                if vol and vol > 0:
                    w = (target_vol / n_long) / vol
                else:
                    w = 1.0 / n_long
                weights.loc[dt, pair] = +w

            for pair in shorts:
                vol = realised_vol.loc[dt, pair] if pair in realised_vol.columns else None
                if vol and vol > 0:
                    w = (target_vol / n_short) / vol
                else:
                    w = 1.0 / n_short
                weights.loc[dt, pair] = -w

        # Apply vol-regime scalar (row-wise multiply)
        weights = weights.mul(regime_scalar, axis=0)
        return weights


# ── Convenience runner ────────────────────────────────────────────────────────

def run_full_backtest(cfg: dict | None = None) -> BacktestResult:
    """
    Fetch all data, run walk-forward backtest, print summary, return result.
    """
    cfg = cfg or BACKTEST
    start, end = cfg["start"], cfg["end"]
    freq = cfg["rebalance_freq"]

    log.info("Fetching data: %s → %s", start, end)
    fx_prices = fetch_fx_prices(start, end)
    short_rates = fetch_short_rates(start, end)
    vix = fetch_vix(start, end)
    cot = fetch_cot(start, end)

    data = dict(fx_prices=fx_prices, short_rates=short_rates, vix=vix, cot=cot)

    rebalance_dates = pd.date_range(start=start, end=end, freq=freq)
    # Snap to actual trading days
    rebalance_dates = fx_prices.index[
        fx_prices.index.searchsorted(rebalance_dates, side="right") - 1
    ].unique()

    wf = cfg["walk_forward"]
    strategy = G10SystematicFX(cfg)

    result = run_walk_forward(
        strategy=strategy,
        fx_prices=fx_prices,
        data=data,
        rebalance_dates=rebalance_dates,
        train_years=wf["train_years"],
        test_months=wf["test_months"],
        cost_bps=cfg["cost_bps_roundtrip"],
    )

    print_summary(result.returns, label="G10 Systematic FX (walk-forward, net of costs)")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    result = run_full_backtest()

    import matplotlib.pyplot as plt
    cum = (1 + result.returns).cumprod()
    cum.plot(title="G10 Systematic FX — Cumulative Returns (walk-forward, net)", figsize=(12, 5))
    plt.tight_layout()
    plt.savefig("reports/equity_curve.png", dpi=150)
    print("Equity curve saved to reports/equity_curve.png")
