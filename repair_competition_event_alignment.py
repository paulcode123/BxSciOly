#!/usr/bin/env python3
"""
Repair script: Realign event placements for Competitions already in the database
by parsing Planning/competitionResults_standardized.txt and replacing results.eventResults
with a name-aligned mapping to eliminate index shift errors.

Usage:
  python repair_competition_event_alignment.py           # dry-run
  python repair_competition_event_alignment.py --apply   # patch DB
  python repair_competition_event_alignment.py --api-base http://localhost:8000/api --apply
"""

import argparse
import re
from typing import Dict, List, Tuple

import requests

from datetime import datetime

PLANNING_FILE = "Planning/competitionResults_standardized.txt"
DEFAULT_API_BASE = "http://localhost:8000/api"


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def parse_event_map() -> Dict[str, Dict[str, Dict[str, int]]]:
    """Parse planning file and return mapping:
    { normalized_comp_name: { team_letter: { eventName: placement, ... }, ... } }
    """
    with open(PLANNING_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split('================================================================================')
    out: Dict[str, Dict[str, Dict[str, int]]] = {}

    current_comp = None
    current_team = None

    for block in sections:
        section = block.strip()
        if not section or 'BRONX SCIENCE OLYMPIAD' in section or 'Event Orders by Season' in section or 'Notes:' in section:
            continue
        lines = [ln.strip() for ln in section.splitlines() if ln.strip()]
        if not lines:
            continue
        # First line is comp name
        current_comp = normalize_name(lines[0])
        out.setdefault(current_comp, {})
        current_team = None

        for line in lines[1:]:
            if line.startswith('Team ') and line.endswith(' Results:'):
                current_team = line.split()[1]
                out[current_comp].setdefault(current_team, {})
                continue
            if line.startswith('Overall:'):
                # ignore for alignment, only per-event matters here
                continue
            if ':' in line and re.search(r':\s*\d+[\*◊]?$', line):
                if not current_team:
                    continue
                evt, val = line.split(':', 1)
                evt = evt.strip()
                placement_part = val.strip()
                if '(DQ)' in placement_part:
                    placement = 999
                else:
                    digits = re.sub(r'[^\d]', '', placement_part)
                    if not digits:
                        continue
                    placement = int(digits)
                out[current_comp][current_team][evt] = placement

    return out


def fetch_competitions(api_base: str) -> List[Tuple[str, dict]]:
    resp = requests.get(f"{api_base}/Competitions")
    resp.raise_for_status()
    data = resp.json()
    comps: List[Tuple[str, dict]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and len(item) == 1:
                _id, doc = next(iter(item.items()))
                comps.append((_id, doc))
            elif isinstance(item, dict) and 'id' in item:
                comps.append((item['id'], item))
    elif isinstance(data, dict):
        for _id, doc in data.items():
            comps.append((_id, doc))
    return comps


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair competition event alignment")
    parser.add_argument('--api-base', default=DEFAULT_API_BASE)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    print('📖 Parsing planning file for event maps…')
    comp_event_map = parse_event_map()
    print(f'   Found {len(comp_event_map)} competitions in planning file')

    print('⬇️  Fetching competitions…')
    comps = fetch_competitions(args.api_base)
    print(f'   Retrieved {len(comps)} competitions')

    fixed = 0
    skipped = 0
    for comp_id, comp in comps:
        name = comp.get('name') or ''
        norm = normalize_name(name)
        if norm not in comp_event_map:
            skipped += 1
            continue

        target_events_by_team = comp_event_map[norm]
        # Build corrected eventResults using name-based placement
        corrected: List[dict] = []
        out_of_default = comp.get('results', {}).get('teamOutOf') or comp.get('results', {}).get('teamOutOf'.lower()) or None

        # Try to deduce teams from existing data
        teams_present = set()
        for p in comp.get('teamPlacement', []) or []:
            if p.get('team'):
                teams_present.add(p['team'])
        if not teams_present:
            teams_present = set(target_events_by_team.keys())

        # Gather all distinct event names from teamPlacement to preserve only real events
        event_names = set()
        for p in comp.get('teamPlacement', []) or []:
            if p.get('event'):
                event_names.add(p['event'])

        for team in sorted(teams_present):
            event_map = target_events_by_team.get(team, {})
            # Prefer intersection with roster events if available
            candidates = sorted(event_names) if event_names else sorted(event_map.keys())
            for evt in candidates:
                if evt in event_map:
                    corrected.append({
                        'eventName': evt,
                        'team': team,
                        'placement': event_map[evt],
                        'outOf': out_of_default or 0
                    })

        action = 'PATCH' if args.apply else 'DRY-RUN'
        print(f"{action}: {name} -> {len(corrected)} aligned event results")
        if args.apply:
            try:
                resp = requests.patch(
                    f"{args.api_base}/Competitions/{comp_id}",
                    headers={'Content-Type': 'application/json'},
                    json={'results': {
                        'teamRank': comp.get('results', {}).get('teamRank', 0),
                        'teamOutOf': comp.get('results', {}).get('teamOutOf', 0),
                        'eventResults': corrected,
                    }},
                    timeout=20,
                )
                if resp.status_code == 200:
                    fixed += 1
                else:
                    print(f"   ❌ Failed to patch {comp_id}: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"   ❌ Error patching {comp_id}: {e}")
        else:
            skipped += 1

    print()
    print('✅ Done.')
    print(f'   Fixed: {fixed}')
    if not args.apply:
        print(f'   (Dry-run) Would fix: {skipped}')


if __name__ == '__main__':
    main()








