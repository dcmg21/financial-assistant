"""
data_sources/press_release_client.py
Search and retrieve press releases from the local JSON file.
"""

import json
from pathlib import Path

# Absolute path so this works regardless of where the app is launched from
FILE = Path(__file__).parent / "press_releases.json"


def load_all():
    """Load all press releases from file."""
    with open(FILE) as f:
        return json.load(f)


def search(keyword=None, category=None, metro=None, limit=5):
    """
    Search press releases by keyword, category, or metro area.
    Examples:
        search(keyword="acquisition")
        search(category="earnings")
        search(metro="Chicago")
    """
    releases = load_all()

    if keyword:
        releases = [r for r in releases if keyword.lower() in r["title"].lower()
                    or keyword.lower() in r["summary"].lower()]

    if category:
        releases = [r for r in releases if r["category"] == category]

    if metro:
        releases = [r for r in releases
                    if any(metro.lower() in m.lower() for m in r.get("metro_areas", []))]

    # Most recent first
    releases.sort(key=lambda x: x["date"], reverse=True)
    return releases[:limit]


def get_recent(limit=3):
    """Return the most recent press releases."""
    return search(limit=limit)


if __name__ == "__main__":
    print("=== Most Recent ===")
    for r in get_recent():
        print(f"  [{r['date']}] {r['title']}")

    print("\n=== Acquisitions ===")
    for r in search(category="acquisition"):
        print(f"  [{r['date']}] {r['title']}")

    print("\n=== Chicago News ===")
    for r in search(metro="Chicago"):
        print(f"  [{r['date']}] {r['title']}")
