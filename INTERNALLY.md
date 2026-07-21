# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Two parallel tracks in this repo

This repo holds two distinct strategy bodies of work that share `data/`, `reports/`, and `live/track_record/` but are otherwise independent:

1. **v1 G10 framework** — [strategy.py](strategy.py) + [signals/](signals/) + [backtest/](backtest/). Weekly cross-sectional long/short portfolio over all 9 G10 pairs. Walk-forward harness. Composite z-score across carry/momentum/COT. **v1 net Sharpe ≈ 0.16** (baseline, naive signal definitions — known weak).
2. **Single-pair rate-diff strategies** — [strategies/](strategies/). One numbered module per pair (`strat_01..strat_08`) running `pos[t+1] = sign(Δ(base_2Y − quote_2Y)[t])` with a 1-day hold and a 5-pip RT cost. Headline result: **EURUSD net Sharpe 2.75**, 5 of 8 pairs >1.0 net.

When you're asked to "change the strategy," disambiguate which track. Edits to [signals/](signals/) and [strategy.py](strategy.py) do **not** affect the `strategies/` modules and vice versa.

## Commands

```bash
# Track 1 — full walk-forward backtest (writes reports/equity_curve.png)
python strategy.py

# Track 2 — single-pair rate-differential strategies
python strategies/_fetch_yields.py            # one-time: populate data/raw/tvc_2y_yields.csv
python strategies/strat_01_eu_us_2y_diff_eurusd.py
python strategies/strat_02_gb_us_2y_diff_gbpusd.py   # ... strat_03 … strat_08
python strategies/_export_csvs.py             # regenerate the 3 committed track-record CSVs

# Test suite (synthetic data, no network or API key required)
pytest

# Single test file / single test
pytest tests/test_signals.py
pytest tests/test_signals.py::TestCarrySignal::test_cross_section_zero_mean

# Install deps
pip install -r requirements.txt
```

`FRED_API_KEY` env var is required to run [strategy.py](strategy.py) (track 1) and [strategies/strat_01_eu_us_2y_diff_eurusd.py](strategies/strat_01_eu_us_2y_diff_eurusd.py) (track 2's #1 uses FRED `DGS2` + ECB SDW directly, not the TVC cache). Tests use synthetic data and do NOT need it. Free key at https://fred.stlouisfed.org/docs/api/api_key.html.

## Architecture — Track 1 (G10 framework)

The pipeline is a single linear flow orchestrated by [strategy.py](strategy.py) → [backtest/engine.py](backtest/engine.py):

```
fetch_* → data dict → strategy.compute_weights(rebalance_dates, **data)
                          ↓
                  signals (carry/momentum/cot) compute z-score DataFrames
                          ↓
                  weighted average → composite score
                          ↓
                  vol_filter.compute() → scalar Series
                          ↓
                  rank → top-N long / bottom-N short → vol-target sizing → × regime scalar
                          ↓
                  walk-forward harness applies costs and computes OOS returns
```

**Signal contract** ([signals/_base.py](signals/_base.py)): Every `BaseSignal.compute()` returns a DataFrame indexed by `rebalance_dates`, columns = pair names from `G10_PAIRS`, values = cross-sectionally z-scored floats (NaN allowed). Use `BaseSignal.cross_section_zscore()` to enforce row-wise mean≈0, std≈1. This invariant is what makes the weighted-sum combination in [strategy.py:66-70](strategy.py#L66-L70) coherent across heterogeneous signal sources.

**`VolRegimeFilter` deliberately breaks the signal contract** — it returns a scalar `Series` (values in [0,1]), not a z-scored DataFrame. It is applied multiplicatively to position weights, not added to the composite score. Do not subclass `BaseSignal` for it.

**Data dict convention**: Every function downstream of `run_full_backtest()` receives the full `data` dict as `**data` kwargs and pulls only what it needs. Keys are stable: `fx_prices`, `short_rates`, `vix`, `cot`. Adding a new signal means adding a new fetcher key here and reading it inside `compute()`.

**Column naming asymmetry** — important when wiring new signals:
- `fx_prices` and `weights`: columns are **pair** names (`EURUSD`, `USDJPY`, ...)
- `short_rates` and `cot`: columns are **currency** names (`EUR`, `USD`, `JPY`, ...)
- Pair → currency mapping lives in `G10_PAIRS[pair]["base"]` and `["quote"]`. See [signals/carry/carry.py:27-33](signals/carry/carry.py#L27-L33) or [signals/sentiment/cot.py:32-44](signals/sentiment/cot.py#L32-L44) for the pattern.

**Pair direction convention** ([config.py:7-20](config.py#L7-L20)): Pairs are listed as base/quote vs USD. A positive composite score means **long the pair as listed**. For `EURUSD` that's long EUR / short USD; for `USDJPY` that's long USD / short JPY. The carry signal computes `rate[base] - rate[quote]`, so the sign convention is enforced at the signal level — do not flip signs again in the strategy layer.

**SEK and NOK have no CFTC data** ([config.py:87](config.py#L87)) — they're not CME-traded. The COT signal returns NaN for `USDSEK`/`USDNOK`, which `cross_section_zscore` propagates through. This is intentional, not a bug.

## Walk-forward and look-ahead

[backtest/engine.py](backtest/engine.py) is the only place data slicing happens. `_slice_data()` truncates every DataFrame/Series in the data dict to the train-window end date, then the strategy recomputes weights on that subset. **Never read data outside the dict argument inside a signal's `compute()`** — that's the only mechanism preventing look-ahead.

Forward returns in `_compute_pair_returns()` use `pct_change().shift(-1)` so the period-`t` weight earns the return from `t` to `t+1`. This is why `BacktestResult.returns` ends one period before the last rebalance date.

Walk-forward is expanding-window by default (`expanding=True`); 3y train / 6m test; refitting happens at every test-window boundary, not every rebalance.

## Architecture — Track 2 (single-pair rate-diff strategies)

All eight pairs share one engine: [strategies/_rate_diff_strategy.py:run_rate_diff_strategy()](strategies/_rate_diff_strategy.py#L68). Each `strat_0N_*.py` is a thin wrapper that calls it with `pair`, `base_ccy`, `quote_ccy`. **Strategy #1 is the exception** — it has its own `run()` ([strategies/strat_01_eu_us_2y_diff_eurusd.py](strategies/strat_01_eu_us_2y_diff_eurusd.py)) because its rate-leg data sources (FRED `DGS2` + ECB SDW) differ from the rest (TradingView TVC via `tvDatafeed`).

**Data prerequisite for #2–#8**: [strategies/_fetch_yields.py](strategies/_fetch_yields.py) must run first to populate `data/raw/tvc_2y_yields.csv` (gitignored). All eight pairs reuse this one CSV.

**Pip-based cost model** ([strategies/_rate_diff_strategy.py:124-127](strategies/_rate_diff_strategy.py#L124-L127)): cost is `|Δposition| × (2.5 pips × pip_size) / spot_price`, NOT bps on turnover. Pip size is `0.0001` for most G10 but `0.01` for JPY pairs — handled by `_pip_size_for()`. This is structurally different from track 1's `compute_costs()` in [backtest/costs.py](backtest/costs.py); do not cross-wire them.

**SEK cost-model artefact** ([strategies/README.md:288](strategies/README.md#L288)): USDSEK's 2.13 net Sharpe is partly inflated because the fixed 5-pip RT cost is fractionally tiny at SEK spot ~10.5 (≈0.24 bps vs ≈2.27 bps on EURUSD). Real-world USDSEK spreads are wider in pip terms, not narrower. Flag this when discussing the result.

**CHF is a known signal failure** (net Sharpe 0.00 — SNB peg + safe-haven dynamics). NOK is deferred (no TVC NO 2Y series). Don't "fix" either by tweaking; they're documented honest limits.

**Import path quirk**: `strategies/_export_csvs.py` does `sys.path.insert(0, HERE)` so that `strat_01_*.py` can do `from _rate_diff_strategy import …` (no `strategies.` prefix). Run track-2 modules with `python strategies/strat_XX.py` from the repo root — they assume `HERE`/`REPO` are derived from the script's `__file__`.

## Tests

Tests are synthetic — they construct random prices/rates/VIX and assert structural invariants (output shape, cross-section z-score properties, no-lookahead, regime-filter bounds). When adding a signal, mirror the shape/z-score tests in [tests/test_signals.py](tests/test_signals.py); don't introduce network calls into tests.

## Live track record

CSVs are gitignored by default; `.gitignore` exempts only [live/track_record/*.csv](live/track_record/). Three track-record CSVs are currently committed (strategies #1 EURUSD, #2 GBPUSD, #6 USDCAD — the cleanest results). Other per-pair CSVs (#3–#5, #7–#8) are deliberately *not* committed because of caveats (short history, fat-tail DD, cost artefact, failed signal). Regenerate the three committed CSVs via `python strategies/_export_csvs.py`.

Other CSVs (TVC yield cache at `data/raw/tvc_2y_yields.csv`, any data exports) stay gitignored — be careful when adding new exports.

## Known v1 limitations (documented in README)

The current naive signal definitions produce near-zero per-signal Sharpe on G10 FX 2013–2024 (track 1). The iteration trail is committed publicly; planned v2 changes are listed under "Next iterations" in [README.md](README.md). Frame any signal-redefinition work as a versioned change, not a stealth refactor of v1 behaviour.

## Caveats inherited from track 2

Per [strategies/PLAN.md:58-63](strategies/PLAN.md#L58-L63) and [strategies/README.md](strategies/README.md): timing-alignment risk (Yahoo FX close vs FRED/ECB/TVC rate fixings), sub-period stability untested across ZIRP vs post-ZIRP regimes, pair-specific cost realism (5 pips is fair for EURUSD/USDCAD, tight for USDNOK/USDSEK), and no vol-targeting (positions are full ±1). When proposing improvements, anchor on one of these — those are the live research questions.
