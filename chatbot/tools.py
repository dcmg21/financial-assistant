"""
chatbot/tools.py
Tool functions for the Vertex AI ADK agent.
Each tool maps to one of the three data sources:
  - SEC EDGAR financials
  - Supabase property/financials database
  - Press releases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_sources.sec_edgar import get_financials
from data_sources.press_release_client import search, get_recent
from database.db_client import get_properties as db_get_properties, get_property_financials as db_get_property_financials


# ── SEC EDGAR TOOLS ────────────────────────────────────────────────────────────

def get_annual_financials(year: int = None) -> str:
    """
    Retrieves Realty Income Corporation annual financial data from SEC EDGAR.
    Use this tool when the user asks about revenue, net income, earnings,
    or financial performance for a specific year or the most recent year.

    Args:
        year: The fiscal year to retrieve (e.g. 2023). If not provided,
              returns the most recent year available.

    Returns:
        A formatted string with revenue and net income figures.
    """
    data = get_financials(year=year)
    if not data:
        return "No financial data found for that year."

    yr = data.get("year", year or "latest")
    rev = data.get("revenue")
    inc = data.get("net_income")

    result = f"Realty Income Corporation — Fiscal Year {yr}\n"
    if rev:
        result += f"  Revenue:    ${rev:,.0f}\n"
    if inc:
        result += f"  Net Income: ${inc:,.0f}\n"
    if not rev and not inc:
        result += "  No data available for this year.\n"
    return result


def get_financial_summary() -> str:
    """
    Returns a multi-year summary of Realty Income Corporation financials.
    Use this when the user asks about financial trends, growth, or wants
    a historical overview of the company's performance.

    Returns:
        A formatted multi-year summary of revenue and net income.
    """
    import json
    from pathlib import Path

    cache = Path("data_sources/realty_income_financials.json")
    if not cache.exists():
        return "Financial data not available. Please run sec_edgar.py first."

    with open(cache) as f:
        data = json.load(f)

    lines = ["Realty Income Corporation — Historical Financials\n"]
    for yr in sorted(data.keys(), reverse=True)[:6]:
        d = data[yr]
        rev = d.get("revenue")
        inc = d.get("net_income")
        rev_str = f"${rev:,.0f}" if rev else "N/A"
        inc_str = f"${inc:,.0f}" if inc else "N/A"
        lines.append(f"  {yr}: Revenue={rev_str}  |  Net Income={inc_str}")

    return "\n".join(lines)


# ── PRESS RELEASE TOOLS ────────────────────────────────────────────────────────

def search_press_releases(keyword: str = None, category: str = None,
                          metro: str = None) -> str:
    """
    Searches Realty Income press releases by keyword, category, or metro area.
    Use this tool when the user asks about company news, announcements,
    acquisitions, expansions, or recent business updates.

    Args:
        keyword:  A word or phrase to search for (e.g. "acquisition", "dividend")
        category: Filter by category — options: acquisition, earnings, dividend,
                  expansion, partnership
        metro:    Filter by metro area (e.g. "Chicago", "New York", "Dallas")

    Returns:
        A formatted list of matching press releases.
    """
    results = search(keyword=keyword, category=category, metro=metro, limit=5)
    if not results:
        return "No press releases found matching your query."

    lines = [f"Found {len(results)} press release(s):\n"]
    for r in results:
        lines.append(f"  [{r['date']}] {r['title']}")
        lines.append(f"    Category: {r.get('category', 'N/A')}")
        lines.append(f"    Summary:  {r.get('summary', 'N/A')}")
        if r.get("metro_areas"):
            lines.append(f"    Markets:  {', '.join(r['metro_areas'])}")
        lines.append("")

    return "\n".join(lines)


def get_recent_news() -> str:
    """
    Returns the 3 most recent Realty Income press releases.
    Use this when the user asks what's new, recent announcements,
    or latest company news.

    Returns:
        A formatted list of the most recent press releases.
    """
    results = get_recent(limit=3)
    if not results:
        return "No recent press releases found."

    lines = ["Most recent Realty Income news:\n"]
    for r in results:
        lines.append(f"  [{r['date']}] {r['title']}")
        lines.append(f"    {r.get('summary', '')}")
        lines.append("")

    return "\n".join(lines)


# ── DATABASE / PROPERTY TOOLS ──────────────────────────────────────────────────

def get_properties(metro_area: str = None, property_type: str = None) -> str:
    """
    Retrieves property records from the Realty Income property database.
    Use this when the user asks about properties, locations, square footage,
    or wants to filter properties by region or type.

    Args:
        metro_area:    Filter by metro area (e.g. "Chicago", "Dallas", "Atlanta")
        property_type: Filter by type (e.g. "retail", "industrial", "office")

    Returns:
        A formatted list of matching properties.
    """
    try:
        properties = db_get_properties(metro_area=metro_area, property_type=property_type)

        if not properties:
            return "No properties found matching your query."

        lines = [f"Found {len(properties)} propert(ies):\n"]
        for p in properties:
            lines.append(f"  Property ID: {p.get('property_id')}")
            lines.append(f"    Address:  {p.get('address')}")
            lines.append(f"    Metro:    {p.get('metro_area')}")
            lines.append(f"    Type:     {p.get('property_type')}")
            lines.append(f"    Sq Ft:    {p.get('sq_footage'):,}" if p.get('sq_footage') else "    Sq Ft: N/A")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error retrieving properties: {str(e)}"


def get_property_financials(property_id: int = None, metro_area: str = None) -> str:
    """
    Retrieves financial data for properties from the database.
    Use this when the user asks about property revenue, net income,
    expenses, or financial performance at the property level.

    Args:
        property_id: Specific property ID to look up
        metro_area:  Filter financials by metro area

    Returns:
        A formatted summary of property-level financials.
    """
    try:
        records = db_get_property_financials(property_id=property_id)

        if not records:
            return "No financial records found."

        lines = [f"Property Financials ({len(records)} record(s)):\n"]
        for r in records:
            lines.append(f"  Property ID: {r.get('property_id')}")
            lines.append(f"    Location: {r.get('address', 'N/A')} — {r.get('metro_area', 'N/A')}")
            lines.append(f"    Revenue:  ${r.get('revenue', 0):,.0f}")
            lines.append(f"    Income:   ${r.get('net_income', 0):,.0f}")
            lines.append(f"    Expenses: ${r.get('expenses', 0):,.0f}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error retrieving property financials: {str(e)}"
