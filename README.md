# g10-systematic-fx

Mid-frequency systematic FX strategy across the G10 universe — built end-to-end on **public-only data sources** (FRED, yfinance, CFTC) so the workflow is fully reproducible without a Bloomberg Terminal.

**Stack:** Python · pandas · scipy · statsmodels · yfinance · FRED API · CFTC public reports
**Status:** v1 backtest framework complete; live track record begins post-launch and is committed weekly to `live/track_record/track-record.csv`.

---

## Strategy

A weekly-rebalanced cross-sectional long/short strategy on 9 G10 pairs. Three independent signals are cross-sectionally z-scored, weighted, then gated by a vol-regime filter. Positions are sized to a target portfolio volatility.

| Pillar | Source | Signal |
|---|---|---|
| **Carry** (40%) | FRED — central-bank policy rates | Smoothed annualised rate differential (base − quote) |
| **Momentum** (35%) | yfinance — daily FX spot | Dual-window time-series momentum (21d fast vs 63d slow) |
| **COT positioning** (25%) | CFTC weekly Commitments of Traders | Speculative net positioning, normalised by open interest |
| **Vol regime** (gate) | yfinance / FRED — VIX | Step-function exposure scalar at the 80th and 95th VIX percentiles |

**Universe:** EURUSD, GBPUSD, AUDUSD, NZDUSD, USDJPY, USDCAD, USDCHF, USDSEK, USDNOK
**Rebalance:** Weekly (Friday close)
**Position sizing:** Vol-targeted, top-3 long / bottom-3 short
**Target:** Sharpe > 1.0, net of 2 bps round-trip cost

---

## Repo structure

```
g10-systematic-fx/
├── config.py                       Universe, FRED series, signal weights, backtest params
├── strategy.py                     G10SystematicFX class + run_full_backtest() entry point
│
├── data/
│   ├── fetchers.py                 FRED (rates, VIX) + yfinance (FX spot)
│   └── cftc.py                     CFTC COT zip downloader and parser
│
├── signals/
│   ├── _base.py                    BaseSignal ABC + cross_section_zscore() helper
│   ├── carry/carry.py              Rate-differential carry signal
│   ├── momentum/momentum.py        Dual-window time-series momentum
│   ├── sentiment/cot.py            CFTC speculator-positioning signal
│   └── vol_regime/vol_regime.py    VIX-based exposure scalar
│
├── backtest/
│   ├── costs.py                    Turnover-based bps cost model
│   ├── metrics.py                  Sharpe, Sortino, max drawdown, Calmar, hit rate
│   └── engine.py                   Walk-forward driver (3y train / 6m test, expanding)
│
├── live/track_record/
│   └── track-record.csv            Weekly P&L log (committed every Friday post-launch)
│
├── pine/strategy.pine              Pine Script port for TradingView publishing
└── tests/                          14 unit tests, no API key required
```

---

## Setup

```bash
pip install -r requirements.txt

# Get a free FRED API key at https://fred.stlouisfed.org/docs/api/api_key.html
export FRED_API_KEY=your_key_here

# Run the full walk-forward backtest
python strategy.py

# Run unit tests (no API key needed — uses synthetic data)
pytest
```

---

## Backtest methodology

- **Walk-forward:** Expanding-window train/test split, 3 years training / 6 months testing per fold. The strategy can never see future data — train-set data is explicitly truncated at the window boundary inside `backtest/engine.py`.
- **Transaction costs:** 2 bps round-trip applied on actual turnover (sum of absolute weight changes per period).
- **Vol targeting:** Each pair sized inversely to its 21-day realised volatility, scaled to a 10% annualised portfolio target.
- **Stress periods covered:** 2010 EU debt, 2013 taper tantrum, 2015 China devaluation, 2018 Q4, 2020 COVID, 2022 BOJ defence, 2023 SVB cluster.

---

## Data sources

- **FRED** — G10 short-rate series (Fed Funds, ECB DFR, BoE SONIA, OECD 3M for AUD/NZD/JPY/CAD/CHF/SEK/NOK), VIX
- **yfinance** — G10 FX daily spot, VIX fallback
- **CFTC** — Weekly Commitments of Traders, legacy futures-only report, downloaded from `cftc.gov/dea/newcot/`

Bloomberg is the production-grade equivalent used in professional treasury work; this repo runs entirely on public data.

---

## Roadmap

- [x] v1 backtest framework with carry / momentum / COT / vol-regime signals
- [x] Walk-forward harness with realistic costs
- [x] Unit-test coverage on signals + metrics
- [ ] First full historical backtest (post-FRED-key setup)
- [ ] Pine Script port for TradingView Pro+ live publishing
- [ ] Live paper-trading track record (committed every Friday)
- [ ] v2 enhancements: positioning-percentile reversal in COT, smooth vol-regime scalar
