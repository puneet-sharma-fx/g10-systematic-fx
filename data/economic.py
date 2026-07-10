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
  - `requests` (already a repo dependency — used for ECB/Eurostat/ONS REST)
  - No pandasdmx dependency: ECB and Eurostat SDMX-JSON are parsed directly.

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
from dotenv import load_dotenv

log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "economic_cache"
CACHE_DIR.mkdir(exist_ok=True)

load_dotenv(HERE.parent / ".env")

Country  = Literal["US", "UK", "EA", "JP", "AU", "CA", "CH", "NZ", "SE", "NO"]
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
    SeriesSpec("EA:HICP_CORE",            "EA", "inflation",  "Euro area HICP ex food/energy/alcohol/tobacco (Eurostat)", "eurostat", "prc_hicp_manr?coicop=TOT_X_NRG_FOOD&unit=RCH_A&geo=EA20", "M", 17),
    # investment
    SeriesSpec("EA:INDPRO",               "EA", "investment", "Euro area industrial production (Eurostat via FRED)",      "fred", "EA19PRINTO01IXOBSAM","M", 45),
    SeriesSpec("EA:HCOB_FLASH_PMI_MFG",   "EA", "investment", "HCOB / S&P Global Eurozone Mfg Flash PMI",                 "stub", "HCOB_EA_MFG_PMI",  "M", 0),
    SeriesSpec("EA:IFO_BUSINESS_CLIMATE", "EA", "investment", "ifo Business Climate Index (Germany)",                     "stub", "IFO_GER_BCI",      "M", 0),
    SeriesSpec("EA:ZEW_SENTIMENT",        "EA", "investment", "ZEW Indicator of Economic Sentiment (Germany)",            "stub", "ZEW_GER",          "M", 0),
    # trade
    SeriesSpec("EA:TRADE_BALANCE",        "EA", "trade",      "Euro area trade balance (OECD MEI via FRED — stale past 2022)", "fred", "XTNTVA01EZM664S", "M", 60),
    SeriesSpec("EA:EURIBOR_3M",           "EA", "investment", "EURIBOR 3-month, monthly average (ECB)",                   "ecb",      "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA", "M", 5),
    SeriesSpec("EA:HICP_NATIVE",          "EA", "inflation",  "EA HICP YoY all-items (ECB native — alternate to FRED)",   "ecb",      "ICP/M.U2.N.000000.4.ANR",            "M", 17),
    # housing
    SeriesSpec("EA:HPI_QUARTERLY",        "EA", "housing",    "Eurostat House Price Index (quarterly, EA-wide YoY)",      "eurostat", "prc_hpi_q?unit=RCH_A&purchase=TOTAL&geo=EA20", "Q", 90),
    SeriesSpec("EA:EUROPACE_EPX_DE",      "EA", "housing",    "Europace EPX (monthly Germany HPI)",                       "stub", "EUROPACE_EPX",     "M", 14),

    # ───────────────────────────── JP ────────────────────────────────────
    SeriesSpec("JP:RETAIL_SALES",         "JP", "consumer",   "Japan retail sales index (OECD MEI via FRED)",             "fred", "JPNSLRTTO02IXOBSAM","M", 45),
    SeriesSpec("JP:CPI_HEADLINE",         "JP", "inflation",  "Japan CPI all items (OECD MEI via FRED)",                  "fred", "JPNCPIALLMINMEI",  "M", 25),
    SeriesSpec("JP:INDPRO",               "JP", "investment", "Japan industrial production index (OECD MEI via FRED)",    "fred", "JPNPROINDMISMEI",  "M", 45),
    SeriesSpec("JP:GDP_REAL",             "JP", "investment", "Japan real GDP (quarterly, OECD via FRED)",                "fred", "JPNRGDPEXP",       "Q", 75),
    SeriesSpec("JP:TRADE_BALANCE",        "JP", "trade",      "Japan trade balance, goods+services (OECD via FRED)",      "fred", "JPNXTNTVA01CXMLM", "M", 45),
    SeriesSpec("JP:HPI_BIS",              "JP", "housing",    "Japan house price index (BIS quarterly via FRED)",         "fred", "QJPR628BIS",       "Q", 90),

    # ───────────────────────────── AU ────────────────────────────────────
    SeriesSpec("AU:CPI_HEADLINE",         "AU", "inflation",  "Australia CPI all items (quarterly, OECD via FRED)",       "fred", "AUSCPIALLQINMEI",  "Q", 30),
    SeriesSpec("AU:INDPRO",               "AU", "investment", "Australia industrial production (quarterly, OECD via FRED)","fred", "AUSPROINDQISMEI",  "Q", 70),
    SeriesSpec("AU:GDP_REAL",             "AU", "investment", "Australia real GDP (quarterly, OECD via FRED)",            "fred", "NAEXKP01AUQ661S",  "Q", 70),
    SeriesSpec("AU:POLICY_RATE",          "AU", "investment", "Australia 3m interbank rate (RBA cash rate proxy)",        "fred", "IR3TIB01AUM156N",  "M", 5),
    SeriesSpec("AU:UNEMPLOYMENT",         "AU", "investment", "Australia harmonised unemployment rate (OECD via FRED)",   "fred", "LRHUTTTTAUM156S",  "M", 30),
    SeriesSpec("AU:TRADE_BALANCE",        "AU", "trade",      "Australia trade balance (OECD via FRED)",                  "fred", "AUSXTNTVA01CXMLM", "M", 45),
    SeriesSpec("AU:HPI_CORELOGIC",        "AU", "housing",    "Australia CoreLogic Home Value Index — scraper needed",    "stub", "CORELOGIC_AU",     "M", 14),

    # ───────────────────────────── CA ────────────────────────────────────
    SeriesSpec("CA:RETAIL_SALES",         "CA", "consumer",   "Canada retail sales index (OECD MEI via FRED)",            "fred", "CANSLRTTO02IXOBSAM","M", 45),
    SeriesSpec("CA:CPI_HEADLINE",         "CA", "inflation",  "Canada CPI all items (OECD MEI via FRED)",                 "fred", "CANCPIALLMINMEI",  "M", 25),
    SeriesSpec("CA:INDPRO",               "CA", "investment", "Canada industrial production index (OECD MEI via FRED)",   "fred", "CANPROINDMISMEI",  "M", 60),
    SeriesSpec("CA:GDP_REAL",             "CA", "investment", "Canada real GDP (quarterly, OECD via FRED)",               "fred", "NAEXKP01CAQ661S",  "Q", 60),
    SeriesSpec("CA:TRADE_BALANCE",        "CA", "trade",      "Canada trade balance (OECD via FRED)",                     "fred", "CANXTNTVA01CXMLM", "M", 45),
    SeriesSpec("CA:HPI_BIS",              "CA", "housing",    "Canada house price index (BIS quarterly via FRED)",        "fred", "QCAR628BIS",       "Q", 90),

    # ───────────────────────────── CH ────────────────────────────────────
    SeriesSpec("CH:RETAIL_SALES",         "CH", "consumer",   "Switzerland retail sales index (OECD MEI via FRED)",       "fred", "CHESLRTTO02IXOBSAM","M", 45),
    SeriesSpec("CH:CPI_HEADLINE",         "CH", "inflation",  "Switzerland CPI all items (OECD MEI via FRED)",            "fred", "CHECPIALLMINMEI",  "M", 25),
    SeriesSpec("CH:GDP_REAL",             "CH", "investment", "Switzerland real GDP (quarterly, OECD via FRED)",          "fred", "NAEXKP01CHQ661S",  "Q", 70),
    SeriesSpec("CH:POLICY_RATE",          "CH", "investment", "Switzerland 3m interbank rate (SNB policy proxy)",         "fred", "IR3TIB01CHM156N",  "M", 5),
    SeriesSpec("CH:TRADE_BALANCE",        "CH", "trade",      "Switzerland trade balance (OECD via FRED)",                "fred", "CHEXTNTVA01CXMLM", "M", 45),
    SeriesSpec("CH:HPI_BIS",              "CH", "housing",    "Switzerland house price index (BIS quarterly via FRED)",   "fred", "QCHR628BIS",       "Q", 90),

    # ───────────────────────────── NZ ────────────────────────────────────
    SeriesSpec("NZ:CPI_HEADLINE",         "NZ", "inflation",  "New Zealand CPI all items (quarterly, OECD via FRED)",     "fred", "NZLCPIALLQINMEI",  "Q", 30),
    SeriesSpec("NZ:INDPRO",               "NZ", "investment", "New Zealand industrial production (quarterly)",            "fred", "NZLPROINDQISMEI",  "Q", 70),
    SeriesSpec("NZ:GDP_REAL",             "NZ", "investment", "New Zealand real GDP (quarterly, OECD via FRED)",          "fred", "NAEXKP01NZQ661S",  "Q", 70),
    SeriesSpec("NZ:TRADE_BALANCE",        "NZ", "trade",      "New Zealand trade balance (OECD via FRED)",                "fred", "NZLXTNTVA01CXMLM", "M", 45),
    SeriesSpec("NZ:HPI_REINZ",            "NZ", "housing",    "REINZ House Price Index — scraper needed",                 "stub", "REINZ_HPI",        "M", 14),

    # ───────────────────────────── SE ────────────────────────────────────
    SeriesSpec("SE:RETAIL_SALES",         "SE", "consumer",   "Sweden retail sales index (OECD MEI via FRED)",            "fred", "SWESLRTTO02IXOBSAM","M", 45),
    SeriesSpec("SE:CPI_HEADLINE",         "SE", "inflation",  "Sweden CPI all items (OECD MEI via FRED)",                 "fred", "SWECPIALLMINMEI",  "M", 25),
    SeriesSpec("SE:INDPRO",               "SE", "investment", "Sweden industrial production index (OECD MEI via FRED)",   "fred", "SWEPROINDMISMEI",  "M", 60),
    SeriesSpec("SE:GDP_REAL",             "SE", "investment", "Sweden real GDP (quarterly, OECD via FRED)",               "fred", "NAEXKP01SEQ661S",  "Q", 60),
    SeriesSpec("SE:POLICY_RATE",          "SE", "investment", "Sweden 3m interbank rate (Riksbank policy proxy)",         "fred", "IR3TIB01SEM156N",  "M", 5),
    SeriesSpec("SE:TRADE_BALANCE",        "SE", "trade",      "Sweden trade balance (OECD via FRED)",                     "fred", "SWEXTNTVA01CXMLM", "M", 45),
    SeriesSpec("SE:HPI_BIS",              "SE", "housing",    "Sweden house price index (BIS quarterly via FRED)",        "fred", "QSER628BIS",       "Q", 90),

    # ───────────────────────────── NO ────────────────────────────────────
    SeriesSpec("NO:RETAIL_SALES",         "NO", "consumer",   "Norway retail sales index (OECD MEI via FRED)",            "fred", "NORSLRTTO02IXOBSAM","M", 45),
    SeriesSpec("NO:CPI_HEADLINE",         "NO", "inflation",  "Norway CPI all items (OECD MEI via FRED)",                 "fred", "NORCPIALLMINMEI",  "M", 25),
    SeriesSpec("NO:INDPRO",               "NO", "investment", "Norway industrial production index (OECD MEI via FRED)",   "fred", "NORPROINDMISMEI",  "M", 60),
    SeriesSpec("NO:GDP_REAL",             "NO", "investment", "Norway real GDP (quarterly, OECD via FRED)",               "fred", "NAEXKP01NOQ661S",  "Q", 60),
    SeriesSpec("NO:POLICY_RATE",          "NO", "investment", "Norway 3m interbank rate (Norges Bank policy proxy)",      "fred", "IR3TIB01NOM156N",  "M", 5),
    SeriesSpec("NO:TRADE_BALANCE",        "NO", "trade",      "Norway trade balance (OECD via FRED)",                     "fred", "NORXTNTVA01CXMLM", "M", 45),
    SeriesSpec("NO:HPI_BIS",              "NO", "housing",    "Norway house price index (BIS quarterly via FRED)",        "fred", "QNOR628BIS",       "Q", 90),
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


def _pull_ecb(source_id: str, start: Optional[str] = None,
              end: Optional[str] = None) -> pd.Series:
    """
    ECB SDMX-JSON via direct REST. Lighter than pandasdmx, no extra dependency.

    source_id format: "<DATASET>/<SERIES_KEY>"
      e.g. "ICP/M.U2.N.000000.4.ANR"        — EA HICP YoY
           "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA" — EURIBOR 3M monthly avg
    """
    import requests
    if "/" not in source_id:
        raise ValueError(f"ECB source_id must be 'DATASET/SERIES_KEY', got {source_id!r}")
    url = f"https://data-api.ecb.europa.eu/service/data/{source_id}"
    r = requests.get(url, timeout=60, headers={"Accept": "application/json"})
    r.raise_for_status()
    payload = r.json()
    ds = payload.get("dataSets", [{}])[0]
    series_dict = ds.get("series", {})
    if not series_dict:
        return pd.Series(dtype=float, name=source_id)
    # First (and usually only) series
    series_key = next(iter(series_dict))
    obs = series_dict[series_key].get("observations", {})
    # Resolve obs index → date string
    time_values = (payload.get("structure", {})
                   .get("dimensions", {})
                   .get("observation", [{}])[0]
                   .get("values", []))
    out = {}
    for obs_idx, val_arr in obs.items():
        i = int(obs_idx)
        if i < len(time_values):
            date_str = time_values[i].get("id", "")
            if val_arr and val_arr[0] is not None:
                try:
                    out[pd.to_datetime(date_str)] = float(val_arr[0])
                except Exception:
                    continue
    s = pd.Series(out).sort_index()
    if start:
        s = s.loc[s.index >= pd.to_datetime(start)]
    if end:
        s = s.loc[s.index <= pd.to_datetime(end)]
    return s


def _pull_eurostat(source_id: str, start: Optional[str] = None,
                   end: Optional[str] = None) -> pd.Series:
    """
    Eurostat JSON-stat via direct REST. No pandasdmx dependency.

    source_id format: "<dataset>?<param>=<value>&<param>=<value>"
      e.g. "prc_hicp_manr?coicop=CP00&unit=RCH_A&geo=EA20"   — EA HICP YoY
           "prc_hpi_q?unit=RCH_A&purchase=TOTAL&geo=EA20"     — EA HPI YoY
    """
    import requests
    if "?" in source_id:
        dataset, qs = source_id.split("?", 1)
        params_dict: dict[str, str] = {}
        for pair in qs.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params_dict[k] = v
    else:
        dataset, params_dict = source_id, {}
    params_dict.setdefault("format", "JSON")
    params_dict.setdefault("lang", "EN")
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}"
    r = requests.get(url, params=params_dict, timeout=60)
    r.raise_for_status()
    payload = r.json()
    values = payload.get("value", {})
    times = (payload.get("dimension", {})
             .get("time", {}).get("category", {}).get("index", {}))
    # times maps "2024-01" -> position_index
    inv_times = {pos: t for t, pos in times.items()}
    out = {}
    for pos_str, val in values.items():
        try:
            pos = int(pos_str)
        except ValueError:
            continue
        # Single-cell datasets: pos maps directly to time
        # Multi-dim datasets: pos is a flat index into product of dims; we
        # rely on the caller's params being specific enough that time is the
        # only varying dimension
        if pos in inv_times:
            try:
                out[pd.to_datetime(inv_times[pos])] = float(val)
            except Exception:
                continue
    s = pd.Series(out).sort_index()
    if start:
        s = s.loc[s.index >= pd.to_datetime(start)]
    if end:
        s = s.loc[s.index <= pd.to_datetime(end)]
    return s


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
