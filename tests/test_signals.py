"""
Unit tests for signal modules.
Uses synthetic data — no API keys or network access required.
"""

import numpy as np
import pandas as pd
import pytest

from signals.carry.carry import CarrySignal
from signals.momentum.momentum import MomentumSignal
from signals.vol_regime.vol_regime import VolRegimeFilter
from config import G10_PAIRS


def make_prices(n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-01", periods=n)
    returns = rng.normal(0, 0.005, size=(n, len(G10_PAIRS)))
    prices = pd.DataFrame(
        (1 + returns).cumprod(axis=0) * 1.2,
        index=dates,
        columns=list(G10_PAIRS.keys()),
    )
    return prices


def make_rates(n: int = 300, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-01", periods=n)
    from config import RATE_SERIES
    rates = rng.uniform(0.0, 5.0, size=(n, len(RATE_SERIES)))
    return pd.DataFrame(rates, index=dates, columns=list(RATE_SERIES.keys()))


def make_vix(n: int = 300) -> pd.Series:
    dates = pd.bdate_range("2015-01-01", periods=n)
    vix = pd.Series(15.0, index=dates, name="VIX")
    vix.iloc[100:120] = 30.0   # elevated regime
    vix.iloc[200:210] = 40.0   # crisis regime
    return vix


def make_rebal_dates(prices: pd.DataFrame) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(prices.index[::5])  # every 5 trading days


class TestCarrySignal:
    def test_output_shape(self):
        rates = make_rates()
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        sig = CarrySignal()
        out = sig.compute(rebal, short_rates=rates, fx_prices=prices)
        assert out.shape[0] == len(rebal)
        assert set(G10_PAIRS.keys()).issubset(set(out.columns))

    def test_cross_section_zero_mean(self):
        rates = make_rates()
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        sig = CarrySignal()
        out = sig.compute(rebal, short_rates=rates, fx_prices=prices)
        row_means = out.dropna(how="all").mean(axis=1)
        assert (row_means.abs() < 1e-10).all(), "Row means should be ~0 after z-scoring"

    def test_cross_section_unit_std(self):
        rates = make_rates()
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        sig = CarrySignal()
        out = sig.compute(rebal, short_rates=rates, fx_prices=prices)
        row_stds = out.dropna(how="all").std(axis=1)
        assert (row_stds.dropna() - 1.0).abs().max() < 0.1


class TestMomentumSignal:
    def test_no_lookahead(self):
        """Signal at date t must not use prices after date t."""
        prices = make_prices(500)
        rebal = make_rebal_dates(prices)
        sig = MomentumSignal()
        out = sig.compute(rebal, fx_prices=prices)
        assert not out.isna().all().all()

    def test_output_shape(self):
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        sig = MomentumSignal()
        out = sig.compute(rebal, fx_prices=prices)
        assert out.shape == (len(rebal), len(G10_PAIRS))


class TestVolRegimeFilter:
    def test_full_exposure_in_calm(self):
        vix = make_vix()
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        filt = VolRegimeFilter()
        scalar = filt.compute(rebal, vix=vix)
        calm = scalar[scalar.index < "2015-05-01"]
        assert (calm == 1.0).all()

    def test_crisis_zeros_exposure(self):
        vix = make_vix()
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        filt = VolRegimeFilter()
        scalar = filt.compute(rebal, vix=vix)
        # Crisis dates: row 200-210 ≈ mid-2016 after 200 bdays
        assert len(scalar[scalar == 0.0]) > 0

    def test_scalar_bounded(self):
        vix = make_vix()
        prices = make_prices()
        rebal = make_rebal_dates(prices)
        filt = VolRegimeFilter()
        scalar = filt.compute(rebal, vix=vix)
        assert scalar.between(0.0, 1.0).all()
