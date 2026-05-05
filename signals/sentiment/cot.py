"""
COT sentiment signal: CFTC non-commercial (speculative) net positioning.

For each pair, signal = net_position_base - net_position_quote.
  - net_position_ccy = (NonComm_Long - NonComm_Short) / Open_Interest

For USD-base or USD-quote pairs where USD COT is unavailable on CME FX futures,
only the non-USD leg contributes (sign-adjusted by whether USD is base or quote).

Output is cross-sectionally z-scored.
"""
from __future__ import annotations

import pandas as pd

from config import G10_PAIRS, SIGNAL_PARAMS
from signals._base import BaseSignal


class COTSignal(BaseSignal):
    def __init__(self, smoothing_weeks: int | None = None):
        cfg = SIGNAL_PARAMS["cot"]
        self.smoothing = smoothing_weeks or cfg["smoothing_weeks"]

    def compute(self, rebalance_dates: pd.DatetimeIndex, **data) -> pd.DataFrame:
        cot: pd.DataFrame = data["cot"]  # weekly, columns = currency (e.g. 'EUR', 'GBP', ...)

        # Smooth each currency series
        cot_smooth = cot.rolling(self.smoothing, min_periods=1).mean()

        pair_signals: dict[str, pd.Series] = {}
        for pair, meta in G10_PAIRS.items():
            base, quote = meta["base"], meta["quote"]
            base_cot = cot_smooth[base] if base in cot_smooth.columns else None
            quote_cot = cot_smooth[quote] if quote in cot_smooth.columns else None

            if base_cot is not None and quote_cot is not None:
                pair_signals[pair] = base_cot - quote_cot
            elif base_cot is not None:
                # USD is quote: positive speculative long on base → positive signal
                pair_signals[pair] = base_cot
            elif quote_cot is not None:
                # USD is base: positive speculative long on quote → negative signal
                pair_signals[pair] = -quote_cot

        if not pair_signals:
            return pd.DataFrame(index=rebalance_dates, columns=list(G10_PAIRS.keys()), dtype=float)

        signal_df = pd.DataFrame(pair_signals)

        # COT is weekly; resample to rebalance_dates (last available before each date)
        combined_idx = signal_df.index.union(rebalance_dates).sort_values()
        signal_aligned = signal_df.reindex(combined_idx).ffill().reindex(rebalance_dates)

        return self.cross_section_zscore(signal_aligned)
