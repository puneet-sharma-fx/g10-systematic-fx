"""
G3 economic-dashboard data ingestion layer (skeleton).

Single facade for pulling macro indicators across US, UK and Euro Area, organised
into the five categories the dashboard cares about:

  - consumer        : retail sales, PCE, consumer confidence/sentiment
  - inflation       : CPI/HICP/PCE deflator, PPI, inflation expectations
  - investment      : industrial production, capex orders, GDP nowcasts, PMI
  - trade           : trade balance, current account
  - housing         : house price indices, starts/permits, mortgage rates

Public API:

  list_catalog(country=None, category=None) -> pd.DataFrame
      Browse what's available. Filter by country (US/UK/EA) or category.

  get(code, start=None, end=None, use_cache=True) -> pd.Series
      Pull one series by namespaced code (e.g. "US:CPI_HEADLINE"). Routes to
      the right source. Returns a pandas Series indexed by release date.

  get_many(codes, start=None, end=None) -> pd.DataFrame
      Pull a list of codes and align them into a wide DataFrame.

  refresh_all(country=None, category=None) -> dict[str, int]
      Bulk-refresh every cached series (or a filtered subset). Returns row
      counts per code. Use for the daily-cron refresh job.

Source routing per the research doc (research/economic_dashboard_data_sources.md):

  FRED is the trunk (~70% of the catalog). It mirrors:
    - US: BLS CPI/PPI, BEA PCE, Case-Shiller, FHFA, GDPNow, Michigan, NY Fed,
      retail sales, housing starts, mortgage rates, ISM/NAPM headline
    - UK: ONS CPI, ONS GDP (some series)
    - EA: Eurostat HICP, ECB MRO rate, Eurozone industrial production

  ECB SDMX, Eurostat SDMX, and ONS Zebedee are the long-tail sources for
  series FRED doesn't carry. Stubs included; not all live yet.

Cache layout: `data/economic_cache/<code>.pkl` (one pickle per series — no
extra dependency vs parquet/feather, well-supported across pandas versions).
Gitignored. Cache TTL not enforced — call refresh_all() to update.

Requires:
  - `FRED_API_KEY` environment variable (free at fred.stlouisfed.org)
  - `fredapi` (already a repo dependency)
  - `pandasdmx` (NOT yet installed — needed only for ECB/Eurostat live mode)

CLI:
  python -m data.economic --list                          # show full catalog
  python -m data.economic --list US                       # filter by country
  python -m data.economic --list US inflation             # filter further
  python -m data.economic --get US:CPI_HEADLINE           # fetch one
  python -m data.economic --refresh-all                   # bulk refresh
"""
from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "economic_cache"
CACHE_DIR.mkdir(exist_ok=True)

Country  = Literal["US", "UK", "EA"]
Category = Literal["consumer", "inflation", "investment", "trade", "housing"]
Source   = Literal["fred", "ecb", "eurostat", "ons", "stub"]


# ── Series catalog ───────────────────────────────────────────────────────────
@dataclass(frozen=True)
class SeriesSpec:
    code:        str          # canonical namespaced ID, e.g. "US:CPI_HEADLINE"
    country:     Country
    category:    Category
    description: str
    source:      Source       # which puller routes the request
    source_id:   str          # the raw upstream identifier (FRED series ID, etc.)
    frequency:   str          # "D" / "W" / "M" / "Q" — informational
    typical_lag_days: int     # rough release lag — informational


# Sources: FRED for the trunk (most series); UK and EA non-FRED noted with their
# native source so the puller knows what to do. Where a UK/EA series IS mirrored
# on FRED we use FRED for cache + caching simplicity.
CATALOG: tuple[SeriesSpec, ...] = (
    # ───────────────────────────── US ────────────────────────────────────
    # consumer
    SeriesSpec("US:RETAIL_SALES",         "US", "consumer",   "Advance Monthly Retail Sales (RSAFS)",                    "fred", "RSAFS",            "M", 14),
    SeriesSpec("US:RETAIL_SALES_EXAUTO",  "US", "consumer",   "Retail sales ex-motor-vehicle",                            "fred", "RSXFS",            "M", 14),
    SeriesSpec("US:PCE_NOMINAL",          "US", "consumer",   "Personal Consumption Expenditures (nominal)",              "fred", "PCE",              "M", 30),
    SeriesSpec("US:PCE_REAL",             "US", "consumer",   "Real PCE",                                                 "fred", "PCEC96",           "M", 30),
    SeriesSpec("US:CONSUMER_CONF_MICH",   "US", "consumer",   "U-Michigan Consumer Sentiment",                            "fred", "UMCSENT",          "M", 14),
    SeriesSpec("US:CONSUMER_CONF_CB",     "US", "consumer",   "Conference Board Consumer Confidence (headline)",          "fred", "CSCICP03USM665S",  "M", 0),
    # inflation
    SeriesSpec("US:CPI_HEADLINE",         "US", "inflation",  "CPI All Items SA (CPIAUCSL)",                              "fred", "CPIAUCSL",         "M", 10),
    SeriesSpec("US:CPI_CORE",             "US", "inflation",  "CPI ex food & energy SA (CPILFESL)",                       "fred", "CPILFESL",         "M", 10),
    SeriesSpec("US:PCE_PRICE_INDEX",      "US", "inflation",  "PCE price index (headline)",                               "fred", "PCEPI",            "M", 30),
    SeriesSpec("US:PCE_CORE",             "US", "inflation",  "PCE price index ex food & energy (core)",                  "fred", "PCEPILFE",         "M", 30),
    SeriesSpec("US:PPI_FINAL_DEMAND",     "US", "inflation",  "PPI Final Demand (SA)",                                    "fred", "PPIFIS",           "M", 10),
    SeriesSpec("US:INFL_EXPECT_MICH_1Y",  "US", "inflation",  "U-Michigan 1y inflation expectations",                     "fred", "MICH",             "M", 14),
    SeriesSpec("US:INFL_EXPECT_5Y5Y",     "US", "inflation",  "5y5y TIPS-derived inflation expectations",                 "fred", "T5YIFR",           "D", 1),
    SeriesSpec("US:WAGE_ECI",             "US", "inflation",  "Employment Cost Index (wages & salaries, civilian)",       "fred", "ECIWAG",           "Q", 30),
    # investment
    SeriesSpec("US:INDPRO",               "US", "investment", "Industrial Production index (G.17)",                       "fred", "INDPRO",           "M", 15),
    SeriesSpec("US:CAPACITY_UTIL",        "US", "investment", "Capacity Utilization, total industry",                     "fred", "TCU",              "M", 15),
    SeriesSpec("US:DURABLE_GOODS_ORDERS", "US", "investment", "Manufacturers' new orders, durable goods",                 "fred", "DGORDER",          "M", 25),
    SeriesSpec("US:CAPEX_NONDEF_ORDERS",  "US", "investment", "Non-defense capital goods orders ex-aircraft (capex proxy)","fred", "NEWORDER",         "M", 25),
    SeriesSpec("US:GDPNOW",               "US", "investment", "Atlanta Fed GDPNow nowcast",                               "fred", "GDPNOW",           "D", 1),
    SeriesSpec("US:MFG_NEW_ORDERS",       "US", "investment", "Manufacturers' new orders, total mfg (AMTMNO)",            "fred", "AMTMNO",           "M", 30),
    SeriesSpec("US:ISM_MFG",              "US", "investment", "ISM Manufacturing PMI — discontinued free; paid only",     "stub", "ISM_PMI",          "M", 1),
    # trade
    SeriesSpec("US:TRADE_BALANCE",        "US", "trade",      "Trade balance, goods & services (BOPGSTB)",                "fred", "BOPGSTB",          "M", 35),
    SeriesSpec("US:CURRENT_ACCOUNT",      "US", "trade",      "Current Account Balance (BoP)",                            "fred", "IEABC",            "Q", 75),
    # housing
    SeriesSpec("US:CASE_SHILLER",         "US", "housing",    "S&P/Case-Shiller National HPI (SA)",                       "fred", "CSUSHPISA",        "M", 60),
    SeriesSpec("US:FHFA_HPI",             "US", "housing",    "FHFA House Price Index (US, SA)",                          "fred", "USSTHPI",          "Q", 30),
    SeriesSpec("US:HOUSING_STARTS",       "US", "housing",    "New residential housing starts (SAAR)",                    "fred", "HOUST",            "M", 17),
    SeriesSpec("US:HOUSING_PERMITS",      "US", "housing",    "New residential building permits (SAAR)",                  "fred", "PERMIT",           "M", 17),
    SeriesSpec("US:EXISTING_HOME_SALES",  "US", "housing",    "Existing home sales (NAR, FRED mirror, SAAR)",             "fred", "EXHOSLUSM495S",    "M", 20),
    SeriesSpec("US:MORTGAGE_30Y",         "US", "housing",    "Freddie Mac 30y fixed mortgage rate (PMMS)",               "fred", "MORTGAGE30US",     "W", 1),

    # ───────────────────────────── UK ────────────────────────────────────
    # consumer
    SeriesSpec("UK:RETAIL_SALES",         "UK", "consumer",   "ONS retail sales volume index (FRED mirror)",              "fred", "GBRSLRTTO02IXOBSAM","M", 25),
    SeriesSpec("UK:GFK_CONSUMER_CONF",    "UK", "consumer",   "GfK consumer confidence (XLSX from GfK)",                  "stub", "GFK_UK_CC",        "M", 30),
    # inflation
    SeriesSpec("UK:CPI_HEADLINE",         "UK", "inflation",  "UK CPI All Items (FRED mirror of ONS)",                    "fred", "CPALTT01GBM659N",  "M", 17),
    SeriesSpec("UK:CPI_CORE",             "UK", "inflation",  "UK CPI ex food/energy/alcohol/tobacco",                    "fred", "CPGRLE01GBM657N",  "M", 17),
    SeriesSpec("UK:HICP_HEADLINE",        "UK", "inflation",  "UK HICP all-items (Eurostat-style)",                       "fred", "CP0000GBM086NEST", "M", 17),
    # investment
    SeriesSpec("UK:INDPRO",               "UK", "investment", "UK Index of Production (FRED mirror)",                     "fred", "GBRPROINDMISMEI",  "M", 40),
    SeriesSpec("UK:GDP_QOQ",              "UK", "investment", "UK real GDP, QoQ (ONS / FRED mirror)",                     "fred", "CLVMNACSCAB1GQUK", "Q", 45),
    SeriesSpec("UK:UK_FLASH_PMI_MFG",     "UK", "investment", "S&P Global UK Mfg Flash PMI (no FRED — scrape)",           "stub", "SPGUK_MFG_PMI",    "M", 0),
    # trade
    SeriesSpec("UK:TRADE_BALANCE",        "UK", "trade",      "UK trade balance (goods+services, ONS via FRED)",          "fred", "XTNTVA01GBM664S",  "M", 40),
    # housing
    SeriesSpec("UK:NATIONWIDE_HPI",       "UK", "housing",    "Nationwide House Price Index (UK)",                        "stub", "NATIONWIDE_HPI",   "M", 1),
    SeriesSpec("UK:LAND_REGISTRY_HPI",    "UK", "housing",    "Gov't Land Registry UK HPI (transactions-based)",          "stub", "LAND_REG_HPI",     "M", 60),

    # ───────────────────────────── EA / EU ──────────────────────────────
    # consumer
    SeriesSpec("EA:RETAIL_SALES",         "EA", "consumer",   "Euro area retail trade volume (Eurostat via FRED)",        "fred", "EA19SLRTTO01IXOBSAM","M", 30),
    SeriesSpec("EA:CONSUMER_CONF_DG",     "EA", "consumer",   "DG ECFIN Consumer Confidence (no FRED)",                   "stub", "DGECFIN_CC",       "M", 0),
    # inflation
    SeriesSpec("EA:HICP_HEADLINE",        "EA", "inflation",  "Euro area HICP all items (Eurostat via FRED)",             "fred", "CP0000EZ19M086NEST","M", 17),
    SeriesSpec("EA:HICP_CORE",            "EA", "inflation",  "Euro area HICP ex food/energy/alcohol/tobacco (Eurostat native)", "eurostat", "prc_hicp_manr", "M", 17),
    # investment
    SeriesSpec("EA:INDPRO",               "EA", "investment", "Euro area industrial production (Eurostat via FRED)",      "fred", "EA19PRINTO01IXOBSAM","M", 45),
    SeriesSpec("EA:HCOB_FLASH_PMI_MFG",   "EA", "investment", "HCOB / S&P Global Eurozone Mfg Flash PMI",                 "stub", "HCOB_EA_MFG_PMI",  "M", 0),
    SeriesSpec("EA:IFO_BUSINESS_CLIMATE", "EA", "investment", "ifo Business Climate Index (Germany)",                     "stub", "IFO_GER_BCI",      "M", 0),
    SeriesSpec("EA:ZEW_SENTIMENT",        "EA", "investment", "ZEW Indicator of Economic Sentiment (Germany)",            "stub", "ZEW_GER",          "M", 0),
    # trade
    SeriesSpec("EA:TRADE_BALANCE",        "EA", "trade",      "Euro area trade balance (ECB BPM6)",                       "ecb",  "BP6.M.N.I8.W1.S1.S1.T.B.GS.._Z._Z._Z.EUR._T._X.N", "M", 60),
    # housing
    SeriesSpec("EA:HPI_QUARTERLY",        "EA", "housing",    "Eurostat House Price Index (quarterly, EA-wide)",          "eurostat", "prc_hpi_q",   "Q", 90),
    SeriesSpec("EA:EUROPACE_EPX_DE",      "EA", "housing",    "Europace EPX (monthly Germany HPI)",                       "stub", "EUROPACE_EPX",     "M", 14),
)


# ── Source pullers ───────────────────────────────────────────────────────────
def _fred_client():
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "FRED_API_KEY not set. Get a free key at "
            "https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    from fredapi import Fred
    return Fred(api_key=api_key)


def _pull_fred(series_id: str, start: Optional[str] = None,
               end: Optional[str] = None) -> pd.Series:
    fred = _fred_client()
    return fred.get_series(series_id, observation_start=start, observation_end=end)


def _pull_ecb(flow_key: str, start: Optional[str] = None,
              end: Optional[str] = None) -> pd.Series:
    """ECB SDMX via pandasdmx. Requires the dependency to be installed."""
    try:
        import pandasdmx as sdmx
    except ImportError as exc:
        raise NotImplementedError(
            "ECB SDMX pull requires `pandasdmx`. Install with `pip install pandasdmx`."
        ) from exc
    # flow_key encodes the full SDMX key. For an MVP we just dispatch and let
    # the caller construct the key correctly.
    flow, key = flow_key.split(".", 1) if "." in flow_key else (flow_key, None)
    resp = sdmx.Request("ECB").data(flow, key=key)
    df = resp.to_pandas()
    if isinstance(df, pd.DataFrame):
        df = df.squeeze("columns") if df.shape[1] == 1 else df.iloc[:, 0]
    if start:
        df = df.loc[df.index >= pd.to_datetime(start)]
    if end:
        df = df.loc[df.index <= pd.to_datetime(end)]
    return df


def _pull_eurostat(dataset: str, start: Optional[str] = None,
                   end: Optional[str] = None) -> pd.Series:
    """Eurostat SDMX via pandasdmx. Default key picks EA19 aggregate."""
    try:
        import pandasdmx as sdmx
    except ImportError as exc:
        raise NotImplementedError(
            "Eurostat SDMX pull requires `pandasdmx`. Install with `pip install pandasdmx`."
        ) from exc
    resp = sdmx.Request("ESTAT").data(dataset)
    df = resp.to_pandas()
    if isinstance(df, pd.DataFrame) and df.shape[1] > 1:
        df = df.iloc[:, 0]  # naive: first column
    if start:
        df = df.loc[df.index >= pd.to_datetime(start)]
    if end:
        df = df.loc[df.index <= pd.to_datetime(end)]
    return df


def _pull_ons(timeseries: str, dataset: str = "MM23",
              start: Optional[str] = None, end: Optional[str] = None) -> pd.Series:
    """ONS Zebedee REST. Default dataset MM23 is the CPI consumer prices dataset."""
    import requests
    url = f"https://api.ons.gov.uk/timeseries/{timeseries}/dataset/{dataset}/data"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    payload = r.json()
    # ONS payload has both monthly and quarterly fields; pick monthly if present
    rows = payload.get("months") or payload.get("quarters") or payload.get("years") or []
    if not rows:
        raise ValueError(f"No data returned for ONS {timeseries} / {dataset}")
    s = pd.Series(
        {pd.to_datetime(row["date"]): float(row["value"]) for row in rows}
    ).sort_index()
    if start:
        s = s.loc[s.index >= pd.to_datetime(start)]
    if end:
        s = s.loc[s.index <= pd.to_datetime(end)]
    return s


def _pull_stub(source_id: str, **_) -> pd.Series:
    """Placeholder for sources not yet wired. Returns empty Series."""
    log.warning("Source not yet implemented for stub series_id=%s. Returning empty Series.",
                source_id)
    return pd.Series(dtype=float, name=source_id)


# ── Catalog helpers ──────────────────────────────────────────────────────────
def _spec_by_code(code: str) -> SeriesSpec:
    for s in CATALOG:
        if s.code == code:
            return s
    raise KeyError(f"Unknown code {code!r}. Run list_catalog() to see what's available.")


def list_catalog(country: Optional[Country] = None,
                 category: Optional[Category] = None) -> pd.DataFrame:
    rows = []
    for s in CATALOG:
        if country and s.country != country:
            continue
        if category and s.category != category:
            continue
        rows.append({
            "code":        s.code,
            "country":     s.country,
            "category":    s.category,
            "description": s.description,
            "source":      s.source,
            "source_id":   s.source_id,
            "frequency":   s.frequency,
            "lag_days":    s.typical_lag_days,
        })
    df = pd.DataFrame(rows)
    return df.sort_values(["country", "category", "code"]).reset_index(drop=True)


# ── Public facade ────────────────────────────────────────────────────────────
def _cache_path(code: str) -> Path:
    safe = code.replace(":", "__")
    return CACHE_DIR / f"{safe}.pkl"


def get(code: str, start: Optional[str] = None, end: Optional[str] = None,
        use_cache: bool = True) -> pd.Series:
    """
    Pull one indicator by its namespaced code. Routes to the right source.

    Examples:
        get("US:CPI_HEADLINE")
        get("UK:RETAIL_SALES", start="2010-01-01")
        get("EA:HICP_HEADLINE", end="2024-12-31", use_cache=False)
    """
    cache_path = _cache_path(code)
    if use_cache and cache_path.exists():
        s = pd.read_pickle(cache_path)
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        if start:
            s = s.loc[s.index >= pd.to_datetime(start)]
        if end:
            s = s.loc[s.index <= pd.to_datetime(end)]
        return s

    spec = _spec_by_code(code)
    if spec.source == "fred":
        s = _pull_fred(spec.source_id, start, end)
    elif spec.source == "ecb":
        s = _pull_ecb(spec.source_id, start, end)
    elif spec.source == "eurostat":
        s = _pull_eurostat(spec.source_id, start, end)
    elif spec.source == "ons":
        s = _pull_ons(spec.source_id, start=start, end=end)
    else:
        s = _pull_stub(spec.source_id)

    s.name = code
    if use_cache and not s.empty:
        try:
            s.to_pickle(cache_path)
        except Exception as exc:
            log.warning("Cache write failed for %s: %s", code, exc)
    return s


def get_many(codes: list[str], start: Optional[str] = None,
             end: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
    """Pull a list of codes and align them into a wide DataFrame (date × code)."""
    cols = {}
    for code in codes:
        try:
            cols[code] = get(code, start=start, end=end, use_cache=use_cache)
        except Exception as exc:
            log.warning("Skip %s: %s", code, exc)
    return pd.DataFrame(cols).sort_index()


def refresh_all(country: Optional[Country] = None,
                category: Optional[Category] = None) -> dict[str, int]:
    """
    Bulk-pull every series (or filtered subset) into the cache. Use for the
    daily-cron job. Returns {code: row_count_pulled}.
    """
    catalog = list_catalog(country=country, category=category)
    results: dict[str, int] = {}
    for _, row in catalog.iterrows():
        code = row["code"]
        try:
            s = get(code, use_cache=False)  # force re-pull
            results[code] = int(len(s))
            log.info("Refreshed %s: %d rows", code, len(s))
        except Exception as exc:
            results[code] = 0
            log.warning("Refresh failed for %s: %s", code, exc)
    return results


# ── CLI ─────────────────────────────────────────────────────────────────────
def _main():
    parser = argparse.ArgumentParser(description="G3 economic data ingestion CLI")
    parser.add_argument("--list", nargs="*", metavar=("COUNTRY", "CATEGORY"),
                        help="List the catalog. Optionally filter by COUNTRY and CATEGORY.")
    parser.add_argument("--get", metavar="CODE",
                        help="Fetch one series by code (e.g. US:CPI_HEADLINE).")
    parser.add_argument("--refresh-all", action="store_true",
                        help="Bulk refresh every cached series.")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end",   help="End date (YYYY-MM-DD)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Bypass cache (force live re-pull)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")

    if args.list is not None:
        country = args.list[0].upper() if len(args.list) >= 1 else None
        category = args.list[1] if len(args.list) >= 2 else None
        df = list_catalog(country=country, category=category)
        print(df.to_string(index=False))
        print(f"\n{len(df)} series  ·  catalog total {len(CATALOG)}")
        return

    if args.get:
        s = get(args.get, start=args.start, end=args.end, use_cache=not args.no_cache)
        if s.empty:
            print(f"(no data for {args.get})")
            return
        print(f"{args.get}  ·  {len(s):,} rows  ·  "
              f"{s.index[0].date()} → {s.index[-1].date()}  ·  "
              f"last value {float(s.iloc[-1]):.2f}")
        print(s.tail(10).to_string())
        return

    if args.refresh_all:
        results = refresh_all()
        ok = sum(1 for n in results.values() if n > 0)
        print(f"Refreshed {ok}/{len(results)} series")
        for code, n in sorted(results.items()):
            status = f"{n:>6} rows" if n > 0 else "  FAILED"
            print(f"  {status}  {code}")
        return

    parser.print_help()


if __name__ == "__main__":
    _main()
