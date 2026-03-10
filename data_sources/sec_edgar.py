"""
data_sources/sec_edgar.py
Pulls Realty Income Corporation financial data from SEC EDGAR API and saves it locally.
"""

import requests
import json
from pathlib import Path

# Realty Income Corporation's unique ID on SEC EDGAR
CIK = "0000726728"   # Realty Income Corporation
CACHE_FILE = Path("data_sources/realty_income_financials.json")

# Realty Income uses different XBRL tag names across filing years — try all of them
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

    # Try each revenue tag until we find one with real data
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

    # Try each net income tag
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

    # Save to file
    CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} years of data")
    return results


def get_financials(year=None):
    """Load financials from file. Download first if file doesn't exist."""
    if not CACHE_FILE.exists():
        download_financials()

    with open(CACHE_FILE) as f:
        data = json.load(f)

    if year:
        return data.get(str(year), {})

    # Return most recent year if no year specified
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