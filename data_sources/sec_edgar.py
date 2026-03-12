"""
data_sources/sec_edgar.py
Fetches Realty Income annual financials from the SEC EDGAR XBRL API and caches them
locally as realty_income_financials.json. No API key needed — SEC data is public.
"""

import requests
import json
from pathlib import Path

# Realty Income's unique identifier in the SEC EDGAR system
CIK = "0000726728"
CACHE_FILE = Path(__file__).parent / "realty_income_financials.json"

# Realty Income has used different XBRL tag names across different filing years,
# so we try each one in order and stop at the first that returns real data.
REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RealEstateRevenueNet",
    "RentalIncome",
    "OperatingLeasesIncomeStatementLeaseRevenue",
]

NET_INCOME_TAGS = [
    "NetIncomeLoss",
    "ProfitLoss",
    "NetIncomeLossAvailableToCommonStockholdersBasic",
]


def download_financials():
    """Download Realty Income Corporation financials from SEC and save to file."""
    print("Downloading from SEC EDGAR...")
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"
    headers = {"User-Agent": "FinancialAssistant user@example.com"}

    data = requests.get(url, headers=headers).json()
    us_gaap = data["facts"]["us-gaap"]

    results = {}

    # Try each revenue tag until we find one that has actual data
    for tag in REVENUE_TAGS:
        entries = us_gaap.get(tag, {}).get("units", {}).get("USD", [])
        annual = [e for e in entries if e.get("form") == "10-K" and e.get("fp") == "FY" and e.get("val", 0) > 0]
        if annual:
            print(f"  Found revenue data in tag: {tag}")
            for entry in annual:
                year = str(entry["fy"])
                if year not in results:
                    results[year] = {}
                results[year]["revenue"] = entry["val"]
                results[year]["year"] = entry["fy"]
            break

    # Same thing for net income
    for tag in NET_INCOME_TAGS:
        entries = us_gaap.get(tag, {}).get("units", {}).get("USD", [])
        annual = [e for e in entries if e.get("form") == "10-K" and e.get("fp") == "FY"]
        if annual:
            print(f"  Found net income data in tag: {tag}")
            for entry in annual:
                year = str(entry["fy"])
                if year not in results:
                    results[year] = {}
                results[year]["net_income"] = entry["val"]
            break

    # Write to the cache file so we don't have to hit the API every time
    CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} years of data")
    return results


def get_financials(year=None):
    """Load financials from the cache file, downloading from SEC first if needed."""
    if not CACHE_FILE.exists():
        download_financials()

    with open(CACHE_FILE) as f:
        data = json.load(f)

    if year:
        return data.get(str(year), {})

    # Default to the most recent year if none is specified
    latest = sorted(data.keys())[-1]
    return data[latest]


if __name__ == "__main__":
    data = download_financials()

    print("--- Realty Income (O) Annual Financials ---")
    for year in sorted(data.keys(), reverse=True)[:5]:
        d = data[year]
        rev = d.get("revenue", 0)
        inc = d.get("net_income", 0)
        print(f"  {year}: Revenue=${rev:,.0f}  |  Net Income=${inc:,.0f}")