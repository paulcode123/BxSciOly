#!/usr/bin/env python3
"""
Backfill missing `date` fields for Competitions using Planning/competitionResults_standardized.txt

Usage:
  python backfill_competition_dates.py              # dry-run (no writes)
  python backfill_competition_dates.py --apply      # perform writes
  python backfill_competition_dates.py --api-base http://localhost:8000/api --apply
"""

import argparse
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

import requests


DEFAULT_API_BASE = "http://localhost:8000/api"
PLANNING_FILE = "Planning/competitionResults_standardized.txt"


def normalize_name(name: str) -> str:
    """Normalize competition name for fuzzy matching: lowercase, alnum only."""
    if not isinstance(name, str):
        return ""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def parse_competition_dates_from_file(path: str) -> Dict[str, str]:
    """Parse planning file and return mapping: normalized_competition_name -> ISO date (YYYY-MM-DD)."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by separator lines of '='
    sections = re.split(r"\n=+\n", content)
    mapping: Dict[str, str] = {}

    for raw in sections:
        section = raw.strip()
        if not section:
            continue
        # Skip headers and notes blocks
        if "BRONX SCIENCE OLYMPIAD" in section or "Event Orders by Season" in section or section.startswith("Notes:"):
            continue

        lines = [ln.strip() for ln in section.splitlines() if ln.strip()]
        if not lines:
            continue

        # First non-empty line should be competition name like "RICKARDS SATELLITE INVITATIONAL 2024-25"
        comp_name = lines[0]
        # Find a line beginning with "Date: Month D, YYYY"
        date_line = next((ln for ln in lines if ln.lower().startswith("date:")), None)
        if not date_line:
            continue

        # Extract the date substring after 'Date:'
        m = re.match(r"^Date:\s*(.*)$", date_line, re.IGNORECASE)
        if not m:
            continue
        date_str = m.group(1).strip()

        # Try parsing date in formats like "November 2, 2024"
        dt = None
        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                pass

        if not dt:
            # Fallback: try extracting YYYY-MM-DD pieces
            m2 = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", date_str)
            if m2:
                y, mo, d = map(int, m2.groups())
                try:
                    dt = datetime(y, mo, d)
                except ValueError:
                    dt = None

        if not dt:
            # Could not parse, skip
            continue

        iso_date = dt.date().isoformat()  # YYYY-MM-DD
        mapping[normalize_name(comp_name)] = iso_date

    return mapping


def fetch_competitions(api_base: str) -> List[Tuple[str, dict]]:
    """Fetch competitions and return list of (id, data). Supports Firebase-style array of {id: data}."""
    url = f"{api_base}/Competitions"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    competitions: List[Tuple[str, dict]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and len(item) == 1:
                _id, doc = next(iter(item.items()))
                competitions.append((_id, doc))
            elif isinstance(item, dict) and "id" in item:
                competitions.append((item["id"], item))
    elif isinstance(data, dict):
        # Rare case: dict-of-dicts
        for _id, doc in data.items():
            competitions.append((_id, doc))
    return competitions


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill competition dates from planning file")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Base URL for the API (default: %(default)s)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (otherwise dry-run)")
    args = parser.parse_args()

    print("📖 Parsing planning file for dates…")
    name_to_date = parse_competition_dates_from_file(PLANNING_FILE)
    print(f"   Found {len(name_to_date)} competition date entries")

    print("⬇️  Fetching competitions from API…")
    comps = fetch_competitions(args.api_base)
    print(f"   Retrieved {len(comps)} competitions")

    # Build normalized name -> (id, data) mapping (handle collisions by storing list)
    name_to_docs: Dict[str, List[Tuple[str, dict]]] = {}
    for comp_id, comp in comps:
        comp_name = comp.get("name") or comp.get("Name") or ""
        norm = normalize_name(comp_name)
        name_to_docs.setdefault(norm, []).append((comp_id, comp))

    updated = 0
    skipped = 0
    unmatched = []

    for norm_name, iso_date in name_to_date.items():
        docs = name_to_docs.get(norm_name, [])
        if not docs:
            unmatched.append(norm_name)
            continue

        for comp_id, comp in docs:
            has_date = "date" in comp and comp["date"] not in (None, "")
            action = "PATCH" if args.apply else "DRY-RUN"
            print(f"{action}: {comp.get('name', comp_id)} -> date {iso_date}")
            if args.apply:
                try:
                    resp = requests.patch(
                        f"{args.api_base}/Competitions/{comp_id}",
                        headers={"Content-Type": "application/json"},
                        json={"date": iso_date},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        updated += 1
                    else:
                        print(f"   ❌ Failed to update {comp_id}: {resp.status_code} {resp.text}")
                except Exception as e:
                    print(f"   ❌ Error updating {comp_id}: {e}")
            else:
                skipped += 1

    print()
    print("✅ Done.")
    print(f"   Updated: {updated}")
    if not args.apply:
        print(f"   (Dry-run) Would update: {skipped}")
    if unmatched:
        print(f"   Unmatched competitions in planning file (names didn't match DB): {len(unmatched)}")
        # Optionally show a few
        for nm in unmatched[:10]:
            print(f"     - {nm}")


if __name__ == "__main__":
    main()








