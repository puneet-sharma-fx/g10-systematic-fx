"""
Aligned-FX re-check of the six strategies that paired Yahoo FX with another
data source (#13 COT, #16 VIX, #20 carry, #22 VIX overlay, #26 carry-TSMOM,
#32 CPI). See notebooks/fx_timestamp_audit.py for the timestamp finding.

Method: run each strategy script UNCHANGED twice — once on legacy Yahoo FX,
once with every "=X" download re-dated one row earlier (close[D] ≈ 00:00 UTC
D+1, the aligned convention in backtest/common.py). Nothing else differs, so
the Sharpe change isolates the look-ahead. Chart/CSV writes are suppressed so
published artefacts are not overwritten.

Run:  python notebooks/aligned_recheck.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.figure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import yfinance as yf  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
STRATS = REPO / "strategies"
TMP_20 = REPO / "data" / "cache" / "recheck_strategy_20.csv"

_original_download = yf.download
_aligned = False


def _download(tickers, *args, **kwargs):
    df = _original_download(tickers, *args, **kwargs)
    if _aligned and isinstance(tickers, str) and tickers.endswith("=X") and df is not None and len(df):
        df = df.shift(-1).iloc[:-1]
    return df


yf.download = _download
plt.savefig = lambda *a, **k: None
matplotlib.figure.Figure.savefig = lambda *a, **k: None


def _load(rel: str):
    path = STRATS / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def run_mode(aligned: bool) -> dict[str, float]:
    global _aligned
    _aligned = aligned
    out = {}
    out["#13 COT extreme L/S"] = _quiet(_load("strat_13_cot_extreme_long_short.py").run)["net"]["sharpe"]
    out["#16 VIX safe-haven short"] = _quiet(_load("rejected/strat_16_vix_safe_haven_short.py").run)["net"]["sharpe"]
    TMP_20.parent.mkdir(parents=True, exist_ok=True)
    out["#20 vol-normalised carry"] = _quiet(_load("strat_20_vol_normalised_carry.py").run, csv_out=TMP_20)["net"]["sharpe"]
    r22 = _quiet(_load("strat_22_carry_crash_filter_overlay.py").run)
    out["#22 base (#18 rate-diff)"] = r22["base"]["sharpe"]
    out["#22 crash-filtered"] = r22["filtered"]["sharpe"]
    m26 = _load("strat_26_carry_tsmom_filter.py")
    base = pd.read_csv(TMP_20, parse_dates=["date"], index_col="date")
    out["#26a carry-TSMOM soft"] = _quiet(m26.run_variant, 0.5, "a", base)["filtered"]["sharpe"]
    out["#26b carry-TSMOM hard"] = _quiet(m26.run_variant, 0.0, "b", base)["filtered"]["sharpe"]
    out["#32 inflation differential"] = _quiet(_load("strat_32_inflation_differential_fx.py").run)["net"]["sharpe"]
    return out


def main() -> None:
    legacy = run_mode(aligned=False)
    aligned = run_mode(aligned=True)
    df = pd.DataFrame({"legacy SR": legacy, "aligned SR": aligned})
    df["change"] = df["aligned SR"] - df["legacy SR"]
    print("\nAligned-FX re-check (net Sharpe, each script's own period and costs)")
    print(df.to_string(float_format=lambda x: f"{x:+.2f}"))


if __name__ == "__main__":
    main()
