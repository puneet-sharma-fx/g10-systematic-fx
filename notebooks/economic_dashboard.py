"""
G10 economic dashboard.

Reads the catalog from `data/economic.py`, fetches a curated set of indicators
per country, computes latest reading + MoM + YoY + 5-year z-score for each,
and writes a single-page markdown report to `reports/economic_dashboard.md`.

Run:
  FRED_API_KEY=... python3 -m notebooks.economic_dashboard

The dashboard is designed to be reproducible from a daily cron — it always
overwrites `reports/economic_dashboard.md` and the accompanying summary CSV
at `reports/economic_dashboard.csv`. No per-day file proliferation.

Curated per country: the most important indicator from each of the five
categories (consumer, inflation, investment, trade, housing). For US we
include a few extras (PCE core, GDPNow, mortgage rate). For pairs where a
category is unavailable (e.g., AU has no consumer-spending indicator),
the slot is gracefully skipped.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"

sys.path.insert(0, str(REPO))
from data.economic import get, list_catalog  # noqa: E402

log = logging.getLogger(__name__)

# ── Curated indicator set per country ────────────────────────────────────────
# Each entry: list of codes to display in dashboard order. We keep ~5-10
# per country — the ones a buy-side macro analyst looks at every morning.
DASHBOARD: dict[str, list[str]] = {
    "US": [
        "US:RETAIL_SALES", "US:CONSUMER_CONF_MICH",
        "US:CPI_HEADLINE", "US:CPI_CORE", "US:PCE_CORE",
        "US:INDPRO", "US:GDPNOW",
        "US:TRADE_BALANCE",
        "US:CASE_SHILLER", "US:HOUSING_STARTS", "US:MORTGAGE_30Y",
    ],
    "UK": [
        "UK:RETAIL_SALES",
        "UK:CPI_HEADLINE", "UK:CPI_CORE",
        "UK:INDPRO", "UK:GDP_QOQ",
        "UK:TRADE_BALANCE",
    ],
    "EA": [
        "EA:RETAIL_SALES",
        "EA:HICP_NATIVE", "EA:HICP_CORE",
        "EA:INDPRO", "EA:EURIBOR_3M",
        "EA:TRADE_BALANCE",
        "EA:HPI_QUARTERLY",
    ],
    "JP": ["JP:RETAIL_SALES", "JP:CPI_HEADLINE", "JP:INDPRO",
           "JP:GDP_REAL", "JP:TRADE_BALANCE", "JP:HPI_BIS"],
    "CA": ["CA:RETAIL_SALES", "CA:CPI_HEADLINE", "CA:INDPRO",
           "CA:GDP_REAL", "CA:TRADE_BALANCE", "CA:HPI_BIS"],
    "CH": ["CH:RETAIL_SALES", "CH:CPI_HEADLINE", "CH:POLICY_RATE",
           "CH:GDP_REAL", "CH:TRADE_BALANCE", "CH:HPI_BIS"],
    "SE": ["SE:RETAIL_SALES", "SE:CPI_HEADLINE", "SE:INDPRO",
           "SE:POLICY_RATE", "SE:TRADE_BALANCE", "SE:HPI_BIS"],
    "NO": ["NO:RETAIL_SALES", "NO:CPI_HEADLINE", "NO:INDPRO",
           "NO:POLICY_RATE", "NO:TRADE_BALANCE", "NO:HPI_BIS"],
    "AU": ["AU:CPI_HEADLINE", "AU:INDPRO", "AU:GDP_REAL",
           "AU:POLICY_RATE", "AU:UNEMPLOYMENT", "AU:TRADE_BALANCE"],
    "NZ": ["NZ:CPI_HEADLINE", "NZ:INDPRO", "NZ:GDP_REAL", "NZ:TRADE_BALANCE"],
}

COUNTRY_LABELS = {
    "US": "United States", "UK": "United Kingdom", "EA": "Euro Area",
    "JP": "Japan", "CA": "Canada", "CH": "Switzerland",
    "AU": "Australia", "NZ": "New Zealand", "SE": "Sweden", "NO": "Norway",
}

# Indicators that are levels (rates/yields/balances) where MoM/YoY should be
# differences (in bps for rates), not percent changes.
LEVEL_INDICATORS = {
    # Rates / yields (changes in bp / pp)
    "US:MORTGAGE_30Y", "US:INFL_EXPECT_5Y5Y", "US:GDPNOW", "US:INFL_EXPECT_MICH_1Y",
    "EA:EURIBOR_3M", "AU:POLICY_RATE", "CH:POLICY_RATE", "SE:POLICY_RATE", "NO:POLICY_RATE",
    "AU:UNEMPLOYMENT",
    # Series whose value is ALREADY a year-over-year % rate (Eurostat RCH_A unit)
    "EA:HICP_NATIVE", "EA:HICP_CORE", "EA:HPI_QUARTERLY",
    # Balances (large absolute values, changes are absolute)
    "US:TRADE_BALANCE", "UK:TRADE_BALANCE", "EA:TRADE_BALANCE",
    "JP:TRADE_BALANCE", "AU:TRADE_BALANCE", "CA:TRADE_BALANCE",
    "CH:TRADE_BALANCE", "NZ:TRADE_BALANCE", "SE:TRADE_BALANCE", "NO:TRADE_BALANCE",
    "US:CURRENT_ACCOUNT",
}

# Series whose values are large (trade balances, GDP). Each entry maps code →
# (divisor, suffix) so that displayed value = raw_value / divisor. FRED is
# inconsistent on units: US BoP series report in millions of $, while
# OECD-MEI mirrors for UK/EA report in raw native currency, and CXMLM-pattern
# mirrors for CA/JP/AU/NZ/CH/SE/NO report in millions of native currency.
LARGE_VALUE_INDICATORS: dict[str, tuple[float, str]] = {
    "US:TRADE_BALANCE":   (1e3, "bn"),  # millions of $ → bn
    "US:CURRENT_ACCOUNT": (1e3, "bn"),  # millions of $ → bn
    "UK:TRADE_BALANCE":   (1e9, "bn"),  # raw £ → bn
    "EA:TRADE_BALANCE":   (1e9, "bn"),  # raw € → bn
    "JP:TRADE_BALANCE":   (1e3, "bn"),  # millions of ¥ → bn ¥
    "CA:TRADE_BALANCE":   (1e3, "bn"),  # millions of C$ → bn
    "AU:TRADE_BALANCE":   (1e3, "bn"),  # millions of A$ → bn
    "CH:TRADE_BALANCE":   (1e3, "bn"),  # millions of CHF → bn
    "NZ:TRADE_BALANCE":   (1e3, "bn"),  # millions of NZ$ → bn
    "SE:TRADE_BALANCE":   (1e3, "bn"),  # millions of kr → bn
    "NO:TRADE_BALANCE":   (1e3, "bn"),  # millions of kr → bn
}


def _infer_freq(s: pd.Series) -> str:
    """Return one of 'M', 'Q', 'W', 'D' based on the last 12 observations."""
    if len(s) < 4:
        return "M"
    deltas = pd.Series(s.index[-12:]).diff().dt.days.dropna()
    median_days = float(deltas.median()) if len(deltas) else 30.0
    if median_days >= 80:
        return "Q"
    if median_days >= 25:
        return "M"
    if median_days >= 5:
        return "W"
    return "D"


def _yoy_lag(freq: str) -> int:
    return {"M": 12, "Q": 4, "W": 52, "D": 252}.get(freq, 12)


def _z_lookback(freq: str) -> int:
    return {"M": 60, "Q": 20, "W": 260, "D": 1260}.get(freq, 60)


def compute_row(code: str, s: pd.Series, label: str) -> dict:
    if s.empty:
        return {"code": code, "label": label, "ok": False}
    s = s.dropna()
    if len(s) < 3:
        return {"code": code, "label": label, "ok": False}
    freq = _infer_freq(s)
    latest = float(s.iloc[-1])
    latest_date = s.index[-1]
    is_level = code in LEVEL_INDICATORS

    # MoM / QoQ
    mom = None
    if len(s) >= 2:
        prev = float(s.iloc[-2])
        if is_level:
            mom = latest - prev  # absolute difference
        elif prev != 0:
            mom = (latest / prev - 1.0) * 100

    # YoY
    yoy = None
    yoy_lag = _yoy_lag(freq)
    if len(s) >= yoy_lag + 1:
        prev_year = float(s.iloc[-(yoy_lag + 1)])
        if is_level:
            yoy = latest - prev_year
        elif prev_year != 0:
            yoy = (latest / prev_year - 1.0) * 100

    # z-score vs 5y trailing window
    z = None
    z_n = _z_lookback(freq)
    window = s.iloc[-z_n:] if len(s) >= z_n else s
    if len(window) >= 6 and window.std() > 0:
        z = float((latest - window.mean()) / window.std())

    # release age
    age_days = (datetime.now() - latest_date.to_pydatetime()).days

    return {
        "code": code, "label": label, "ok": True,
        "latest": latest, "latest_date": latest_date,
        "mom": mom, "yoy": yoy, "z5y": z,
        "freq": freq, "is_level": is_level, "age_days": age_days,
    }


def render_markdown_table(rows: list[dict]) -> str:
    headers = ["Indicator", "Latest", "Date", "MoM/QoQ", "YoY", "5y z", "Freq", "Age"]
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---:" if i > 0 else "---" for i in range(len(headers))]) + "|"]
    for r in rows:
        if not r.get("ok"):
            out.append(f"| {r['label']} | — | — | — | — | — | — | — |")
            continue
        # Scale large values (trade balances, current account) per per-series map
        if r["code"] in LARGE_VALUE_INDICATORS:
            scale, unit_suffix = LARGE_VALUE_INDICATORS[r["code"]]
            latest_fmt = f"{r['latest'] / scale:+.1f}{unit_suffix}"
            mom_str = (f"{r['mom'] / scale:+.1f}{unit_suffix}"
                       if r["mom"] is not None else "—")
            yoy_str = (f"{r['yoy'] / scale:+.1f}{unit_suffix}"
                       if r["yoy"] is not None else "—")
        else:
            latest_fmt = (
                f"{r['latest']:,.0f}" if abs(r['latest']) >= 100
                else f"{r['latest']:.2f}"
            )
            units_chg = " bp" if r["is_level"] and "RATE" in r["code"] else ("" if r["is_level"] else "%")
            mom_str = f"{r['mom']:+.2f}{units_chg}" if r["mom"] is not None else "—"
            yoy_str = f"{r['yoy']:+.2f}{units_chg}" if r["yoy"] is not None else "—"
        date_fmt = r["latest_date"].strftime("%Y-%m")
        mom_fmt = mom_str
        yoy_fmt = yoy_str
        z_fmt = f"{r['z5y']:+.2f}σ" if r["z5y"] is not None else "—"
        age = r["age_days"]
        age_fmt = f"{age}d" if age < 365 else f"{age // 30}m"
        # bold if z > 1.5 or yoy hot/cold
        if r["z5y"] is not None and abs(r["z5y"]) > 1.5:
            mom_fmt = f"**{mom_fmt}**"
            yoy_fmt = f"**{yoy_fmt}**"
            z_fmt = f"**{z_fmt}**"
        out.append(
            f"| {r['label']} | {latest_fmt} | {date_fmt} | {mom_fmt} | {yoy_fmt} | "
            f"{z_fmt} | {r['freq']} | {age_fmt} |"
        )
    return "\n".join(out)


def build_dashboard(start: str | None = None) -> tuple[str, pd.DataFrame]:
    cat = list_catalog()
    catdict = cat.set_index("code").to_dict("index")

    md_parts: list[str] = []
    md_parts.append(f"# G10 Economic Dashboard")
    md_parts.append(f"_Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}_")
    md_parts.append("")
    md_parts.append(
        "Auto-generated from `data/economic.py` catalog. Cells show the latest "
        "reading, the change from the prior period (MoM for monthly series, QoQ "
        "for quarterly), the year-over-year change, the 5-year trailing z-score "
        "(bold when |z| > 1.5σ), the series frequency, and the age of the latest "
        "release."
    )
    md_parts.append("")

    all_rows: list[dict] = []
    for country in ["US", "UK", "EA", "JP", "CA", "CH", "AU", "NZ", "SE", "NO"]:
        codes = DASHBOARD.get(country, [])
        if not codes:
            continue
        country_rows: list[dict] = []
        for code in codes:
            if code not in catdict:
                continue
            spec = catdict[code]
            try:
                s = get(code, start=start)
            except Exception as exc:
                log.warning("Failed %s: %s", code, exc)
                s = pd.Series(dtype=float)
            row = compute_row(code, s, spec["description"])
            row["country"] = country
            row["category"] = spec["category"]
            country_rows.append(row)
            all_rows.append(row)
        if not country_rows:
            continue
        md_parts.append(f"## {COUNTRY_LABELS[country]} ({country})")
        md_parts.append("")
        md_parts.append(render_markdown_table(country_rows))
        md_parts.append("")

    # Summary section
    md_parts.append("---")
    md_parts.append("")
    md_parts.append("## Cross-country summary")
    md_parts.append("")

    # Median 5y z by category across countries
    df_summary = pd.DataFrame([r for r in all_rows if r.get("ok")])
    if not df_summary.empty:
        pivot = df_summary.pivot_table(
            index="country", columns="category", values="z5y", aggfunc="median"
        )
        md_parts.append(
            "Median 5y trailing z-score by country × category. Positive means "
            "running hot vs the trailing 5-year window; negative means cold."
        )
        md_parts.append("")
        # Render pivot manually as markdown
        cols = list(pivot.columns)
        header = "| Country | " + " | ".join(cols) + " |"
        sep = "|" + "---|" + "|".join(["---:"] * len(cols)) + "|"
        md_parts.append(header)
        md_parts.append(sep)
        for country, row in pivot.iterrows():
            cells = [f"{row[c]:+.2f}" if pd.notna(row[c]) else "—" for c in cols]
            md_parts.append(f"| **{country}** | " + " | ".join(cells) + " |")
        md_parts.append("")

    # Stale-release flag
    md_parts.append("### Release timeliness")
    md_parts.append("")
    if not df_summary.empty:
        fresh = df_summary[df_summary["age_days"] <= 60]
        stale = df_summary[df_summary["age_days"] > 180]
        md_parts.append(f"- Fresh (≤60d): **{len(fresh)} series**")
        md_parts.append(f"- Stale (>180d): **{len(stale)} series**")
        if len(stale) > 0:
            md_parts.append("  - Stale series (FRED OECD-MEI mirrors often lag):")
            for _, r in stale.iterrows():
                md_parts.append(f"    - `{r['code']}` ({r['age_days']}d old)")

    md_parts.append("")
    md_parts.append("---")
    md_parts.append("")
    md_parts.append(
        "Source: `data/economic.py` ingestion layer. See "
        "`research/economic_dashboard_data_sources.md` for the full catalog "
        "of indicators, agencies, and access methods."
    )

    return "\n".join(md_parts), pd.DataFrame(all_rows)


def main():
    parser = argparse.ArgumentParser(description="Generate the G10 economic dashboard.")
    parser.add_argument("--start", help="Earliest date to fetch (YYYY-MM-DD)")
    parser.add_argument(
        "--out", default=str(REPORTS / "economic_dashboard.md"),
        help="Output markdown path (default: reports/economic_dashboard.md)",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s  %(message)s")

    md, df = build_dashboard(start=args.start)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md)
    csv_out = out.with_suffix(".csv")
    df_clean = df[df["ok"]].copy()
    df_clean["latest_date"] = df_clean["latest_date"].dt.strftime("%Y-%m-%d")
    df_clean.to_csv(csv_out, index=False, float_format="%.4f")
    print(f"Wrote {out}  ({len(md.splitlines())} lines)")
    print(f"Wrote {csv_out}  ({len(df_clean)} indicators)")

    fresh_count = int((df_clean["age_days"] <= 60).sum())
    stale_count = int((df_clean["age_days"] > 180).sum())
    print(f"Fresh series (≤60d): {fresh_count}  ·  Stale (>180d): {stale_count}")


if __name__ == "__main__":
    main()
