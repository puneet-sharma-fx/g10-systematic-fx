"""
Strategy #49 — Short-vol (#48) + diversified TSMOM (#43), each sized to 10% vol

#48 (short VIX futures in contango) passes its criteria but runs 47% vol
with −66% MaxDD; #43 (TSMOM across 25 ETFs) fails standalone (SR 0.29) but
earns +2.95% in SPY's worst months. Short-vol loses in exactly those crashes,
so the two should offset — "sell insurance, hold trend as the hedge".

Spec:
  - Sleeve A : #48 signal (SVXY when VIX/VIX3M < 1 at D−1), exposure scaled to
               10% ex-ante vol (EWMA com 20 of SVXY returns, updated weekly,
               capped at 1.0); idle capital earns US 3M
  - Sleeve B : #43 TSMOM net returns, scaled to 10% ex-ante vol (EWMA com 60,
               updated weekly, leverage multiplier capped at 1.5); rescaling
               trades charged 10 bps RT on gross leverage
  - Portfolio: 50% A + 50% B, daily
  - Period   : Oct-2011 – 2024 in-sample, 2025+ hold-out

Second test (diagnostic, own criteria): 80% of a 60/40 SPY/IEF + 20% raw
#43 TSMOM, vs plain 60/40 — does trend improve a normal portfolio?

Pre-registered pass criteria for the portfolio (set before first run):
  1. In-sample net Sharpe > 0.6
  2. Sharpe above both sleeves alone (diversification works)
  3. Mean return > 0 in SPY's worst-decile months (the hedge works)
  4. Hold-out Sharpe > 0
Second test passes if the blend has higher Sharpe AND smaller MaxDD than 60/40.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backtest.common import (REPORTS, TRACK, fetch_close, short_rates, split,  # noqa: E402
                             stats, turnover_cost)
import strat_43_diversified_tsmom as tsmom  # noqa: E402
import strat_48_vix_term_structure_short_vol as shortvol  # noqa: E402

NUMBER = 49
TITLE = "Short-vol (#48) + diversified TSMOM (#43), 10% vol each"
TARGET_VOL, SV_COM, TS_COM, TS_CAP, COST_BPS_RT = 0.10, 20, 60, 1.5, 10.0
STRESS = {"Feb-2018 Volmageddon": ("2018-01-26", "2018-02-09"),
          "Q4-2018 selloff": ("2018-10-01", "2018-12-24"),
          "Mar-2020 COVID": ("2020-02-19", "2020-03-23"),
          "2022 bear": ("2022-01-03", "2022-10-12"),
          "Aug-2024 yen unwind": ("2024-07-31", "2024-08-07"),
          "Apr-2025 tariff shock": ("2025-04-02", "2025-04-08")}


def weekly(series: pd.Series) -> pd.Series:
    """Hold each Friday's value through the following week (lagged one day)."""
    fri = series[series.index.dayofweek == 4]
    return fri.reindex(series.index).ffill().shift(1)


def short_vol_sleeve() -> tuple[pd.Series, pd.Series]:
    _, svxy_ret, frame = shortvol.build(lag_days=1)
    idx = svxy_ret.index
    pos = frame["position"].loc[idx]
    vol = svxy_ret.ewm(com=SV_COM, min_periods=20).std() * np.sqrt(252)
    scale = weekly((TARGET_VOL / vol).clip(upper=1.0)).fillna(0.0)
    exposure = pos * scale
    cash = short_rates(idx, point_in_time=False)["USD"] / 100 / 252
    net = exposure * svxy_ret + (1 - exposure) * cash - turnover_cost(exposure, COST_BPS_RT)
    return net, exposure


def tsmom_sleeve() -> tuple[pd.Series, pd.Series]:
    px, rets = tsmom.load()
    w = tsmom.weights(px, rets)
    gross = (w * rets.fillna(0)).sum(axis=1)
    raw = (gross - turnover_cost(w, tsmom.COST_BPS_RT)).loc["2011-01-01":]
    vol = raw.ewm(com=TS_COM, min_periods=60).std() * np.sqrt(252)
    k = weekly((TARGET_VOL / vol).clip(upper=TS_CAP)).fillna(1.0)
    gross_lev = w.abs().sum(axis=1).reindex(raw.index)
    rescale_cost = k.diff().abs().fillna(0) * gross_lev * (COST_BPS_RT / 2 / 1e4)
    return k * raw - rescale_cost, raw


def drawdown(r: pd.Series) -> pd.Series:
    c = (1 + r).cumprod()
    return c / c.cummax() - 1


def run() -> dict:
    sv, sv_exposure = short_vol_sleeve()
    ts, ts_raw = tsmom_sleeve()
    idx = sv.index.intersection(ts.index)
    sv, ts, ts_raw = sv.loc[idx], ts.loc[idx], ts_raw.loc[idx]
    combo = 0.5 * sv + 0.5 * ts
    spy = fetch_close("SPY").pct_change().reindex(idx).fillna(0)
    ief = fetch_close("IEF").pct_change().reindex(idx).fillna(0)
    sixty40 = 0.6 * spy + 0.4 * ief
    blend = 0.8 * sixty40 + 0.2 * ts_raw

    series = {"Portfolio (#49)": combo, "Short-vol sleeve": sv, "TSMOM sleeve": ts,
              "SPY": spy, "60/40": sixty40, "60/40 + 20% TSMOM": blend}
    ins = {k: stats(split(v)[0]) for k, v in series.items()}
    hold = {k: stats(split(v)[1]) for k, v in series.items()}

    m_combo = (1 + split(combo)[0]).resample("ME").prod() - 1
    m_spy = (1 + split(spy)[0]).resample("ME").prod() - 1
    worst = m_spy <= m_spy.quantile(0.10)
    criteria = {
        f"In-sample net Sharpe > 0.6 ({ins['Portfolio (#49)']['sharpe']:.2f})": ins["Portfolio (#49)"]["sharpe"] > 0.6,
        f"Beats both sleeves (SV {ins['Short-vol sleeve']['sharpe']:.2f}, TS {ins['TSMOM sleeve']['sharpe']:.2f})":
            ins["Portfolio (#49)"]["sharpe"] > max(ins["Short-vol sleeve"]["sharpe"], ins["TSMOM sleeve"]["sharpe"]),
        f"Mean > 0 in SPY worst-decile months ({m_combo[worst].mean():+.2%})": m_combo[worst].mean() > 0,
        f"Hold-out Sharpe > 0 ({hold['Portfolio (#49)']['sharpe']:+.2f})": hold["Portfolio (#49)"]["sharpe"] > 0,
    }
    blend_pass = (ins["60/40 + 20% TSMOM"]["sharpe"] > ins["60/40"]["sharpe"]
                  and ins["60/40 + 20% TSMOM"]["max_dd"] > ins["60/40"]["max_dd"])

    print(f"\nStrategy #{NUMBER} — {TITLE}")
    print(f"  {'':<20} {'SR':>6} {'ret':>8} {'vol':>7} {'MaxDD':>7} {'Calmar':>7} || {'hold SR':>7} {'hold DD':>8}")
    for k in series:
        i, h = ins[k], hold[k]
        print(f"  {k:<20} {i['sharpe']:>+6.2f} {i['ann_ret']:>+8.1%} {i['ann_vol']:>7.1%} {i['max_dd']:>7.0%} "
              f"{i['calmar']:>7.2f} || {h['sharpe']:>+7.2f} {h['max_dd']:>8.0%}")
    corr = split(sv)[0].corr(split(ts)[0])
    print(f"  Sleeve correlation (daily, in-sample): {corr:+.2f}")
    print(f"  Pre-registered criteria: {sum(criteria.values())}/4 pass")
    for name, ok in criteria.items():
        print(f"    {'✓' if ok else '✗'} {name}")
    print(f"  Second test (60/40 + 20% TSMOM beats 60/40 on Sharpe AND MaxDD): {'PASS' if blend_pass else 'FAIL'}")

    stress_rows = {}
    for name, (a, b) in STRESS.items():
        stress_rows[name] = {k: float((1 + v.loc[a:b]).prod() - 1) for k, v in series.items()
                             if k in ("Portfolio (#49)", "Short-vol sleeve", "TSMOM sleeve", "SPY")}
    stress = pd.DataFrame(stress_rows).T
    print("  Stress windows (cumulative return):")
    print(stress.map(lambda x: f"{x:+.1%}").to_string())

    chart(series, ins, hold, stress, sv, ts, criteria, blend_pass)
    TRACK.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"short_vol_sleeve": sv, "tsmom_sleeve": ts, "net_ret": combo,
                  "short_vol_exposure": sv_exposure.reindex(idx), "blend_6040_tsmom": blend}
                 ).to_csv(TRACK / f"strategy_{NUMBER}_short_vol_plus_tsmom_track_record.csv")
    return {"in_sample": ins, "holdout": hold, "criteria": criteria, "blend_pass": blend_pass}


def chart(series, ins, hold, stress, sv, ts, criteria, blend_pass) -> None:
    colors = {"Portfolio (#49)": "#1f77b4", "Short-vol sleeve": "#ff7f0e", "TSMOM sleeve": "#2ca02c",
              "SPY": "#7f7f7f", "60/40": "#9467bd", "60/40 + 20% TSMOM": "#8c564b"}
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.25, 1, 1], hspace=0.42, wspace=0.18)

    ax = fig.add_subplot(gs[0, :])
    for k, r in series.items():
        lw = 2.4 if k == "Portfolio (#49)" else 1.2
        ls = "--" if k in ("60/40", "60/40 + 20% TSMOM") else "-"
        ax.plot((1 + r).cumprod(), label=f"{k}  (SR {ins[k]['sharpe']:+.2f})", color=colors[k], lw=lw, ls=ls)
    ax.set_yscale("log")
    ax.axvline(pd.Timestamp("2025-01-01"), color="grey", ls=":", lw=1)
    ax.text(pd.Timestamp("2025-01-15"), ax.get_ylim()[0] * 1.05, "hold-out →", color="grey", fontsize=9)
    ax.set_title("Growth of $1 (log scale) — in-sample Sharpe in legend", fontsize=11, loc="left")
    ax.legend(fontsize=9, ncol=2, loc="upper left")
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[1, 0])
    for k in ("Portfolio (#49)", "Short-vol sleeve", "TSMOM sleeve", "SPY"):
        ax.plot(drawdown(series[k]) * 100, label=f"{k} ({ins[k]['max_dd']:.0%})", color=colors[k],
                lw=2 if k == "Portfolio (#49)" else 1)
    ax.set_title("Drawdown (%) — in-sample MaxDD in legend", fontsize=11, loc="left")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[1, 1])
    roll = sv.rolling(252).corr(ts)
    ax.plot(roll, color="#d62728")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title(f"Rolling 1-year correlation of the two sleeves (full-period {sv.corr(ts):+.2f})",
                 fontsize=11, loc="left")
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[2, 0])
    cols = ["Portfolio (#49)", "Short-vol sleeve", "TSMOM sleeve", "SPY"]
    x = np.arange(len(stress))
    width = 0.2
    for j, k in enumerate(cols):
        ax.bar(x + (j - 1.5) * width, stress[k] * 100, width, label=k, color=colors[k])
    ax.set_xticks(x)
    ax.set_xticklabels(stress.index, rotation=20, ha="right", fontsize=8)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title("Return in stress windows (%)", fontsize=11, loc="left")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    ax = fig.add_subplot(gs[2, 1])
    ax.axis("off")
    rows = [[k, f"{ins[k]['sharpe']:+.2f}", f"{ins[k]['ann_ret']:+.1%}", f"{ins[k]['ann_vol']:.1%}",
             f"{ins[k]['max_dd']:.0%}", f"{hold[k]['sharpe']:+.2f}"] for k in series]
    tbl = ax.table(cellText=rows, colLabels=["", "Sharpe", "Return", "Vol", "MaxDD", "Hold-out SR"],
                   bbox=[0.0, 0.40, 1.0, 0.60], cellLoc="center", colWidths=[0.30, 0.13, 0.14, 0.12, 0.13, 0.18])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    verdict = "\n".join(f"{'✓' if ok else '✗'} {name}" for name, ok in criteria.items())
    ax.text(0.0, 0.02, f"Pre-registered: {sum(criteria.values())}/4 pass\n{verdict}\n"
                       f"60/40 + 20% TSMOM beats 60/40 (Sharpe & MaxDD): {'PASS' if blend_pass else 'FAIL'}",
            fontsize=8.5, va="bottom", family="monospace", transform=ax.transAxes)
    ax.set_title("Summary — in-sample Oct-2011 to 2024", fontsize=11, loc="left")

    fig.suptitle(f"Strategy #{NUMBER} — {TITLE}", fontsize=14, y=0.93)
    fig.savefig(REPORTS / f"strategy_{NUMBER}_short_vol_plus_tsmom.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    run()
