"""
Parser module for reading competition data from text files.
Replaces Firebase storage for competition results and rosters.
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

# File paths
RESULTS_FILE = 'Planning/competitionResults_standardized.txt'
ROSTERS_FILE = 'Planning/competitionRosters_standardized.txt'

# Cache for parsed data
_competitions_cache: Optional[List[Dict[str, Any]]] = None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    try:
        date_str = date_str.strip()
        
        # Handle dates with time like "November 28, 2025 11:59pm"
        if 'pm' in date_str.lower() or 'am' in date_str.lower():
            # Extract just the date part before the time
            date_part = date_str.split()[0:3]  # Get first 3 parts (month, day, year)
            date_str = ' '.join(date_part)
        
        # Handle date ranges like "January 9-10, 2026"
        if '-' in date_str and ',' in date_str:
            # Take the start date
            parts = date_str.split(',')
            if len(parts) == 2:
                month_day = parts[0].strip()
                year = parts[1].strip()
                # Extract start day
                if '-' in month_day:
                    month = month_day.split()[0]
                    start_day = month_day.split('-')[0].split()[-1]
                    date_str = f"{month} {start_day}, {year}"
        
        # Try common formats
        for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%B %d %Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        # Fallback
        return datetime.strptime(date_str, '%B %d, %Y')
    except Exception:
        return None


def normalize_competition_name(name: str) -> str:
    """Normalize competition name for matching"""
    return name.upper().strip()


def normalize_competition_type(type_str: str) -> str:
    """Normalize competition type to match database schema.
    
    Maps:
    - "Satellite Invitational" -> "satellite"
    - "Invitational" -> "invitational"
    - "Official Regional Championship" -> "official" or "regional"
    - "Official State Championship" -> "official" or "state"
    """
    if not type_str:
        return ""
    
    type_lower = type_str.lower().strip()
    
    if "satellite" in type_lower:
        return "satellite"
    elif "regional" in type_lower:
        return "regional"
    elif "state" in type_lower:
        return "state"
    elif "national" in type_lower:
        return "national"
    elif "invitational" in type_lower:
        return "invitational"
    elif "official" in type_lower:
        return "official"
    else:
        return type_lower


def parse_competition_results() -> Dict[str, Dict[str, Any]]:
    """Parse competition results from the standardized file.
    
    Returns:
        Dict mapping competition name to results data:
        {
            "COMP NAME": {
                "date": datetime,
                "type": str,
                "duosmium": str,
                "teams": {
                    "A": {
                        "events": {eventName: placement, ...},
                        "overall": {"rank": int, "outOf": int}
                    },
                    ...
                }
            }
        }
    """
    results = {}
    
    if not os.path.exists(RESULTS_FILE):
        return results
    
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = content.split('================================================================================')
    
    for section in sections:
        section = section.strip()
        if not section or 'BRONX SCIENCE OLYMPIAD' in section or 'Notes:' in section:
            continue

        lines = section.split('\n')
        current_competition = None
        current_team = None
        event_results = {}
        duosmium_link = None
        comp_date = None
        comp_type = None
        comp_location = None
        comp_overnight = None
        comp_teams = None
        comp_registration_opens = None
        comp_registration_closes = None
        comp_roster_released = None
        comp_status = None

        def ensure_comp():
            nonlocal current_competition
            if current_competition and current_competition not in results:
                results[current_competition] = {
                    "date": comp_date,
                    "type": comp_type,
                    "duosmium": duosmium_link,
                    "location": comp_location,
                    "overnight": comp_overnight,
                    "numTeams": comp_teams,
                    "registrationOpens": comp_registration_opens,
                    "registrationCloses": comp_registration_closes,
                    "rosterReleased": comp_roster_released,
                    "status": comp_status,
                    "teams": {}
                }

        def save_team():
            nonlocal current_competition, current_team, event_results
            if current_competition and current_team is not None and event_results:
                ensure_comp()
                team_entry = results[current_competition]["teams"].get(current_team, {})
                team_entry["events"] = event_results
                results[current_competition]["teams"][current_team] = team_entry

        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            # Competition name (all caps with year) or "UPCOMING COMPETITIONS" section
            if re.match(r'^[A-Z\s]+20[0-9]{2}-[0-9]{2}$', line) or line == 'UPCOMING COMPETITIONS 2025-26':
                save_team()
                if line == 'UPCOMING COMPETITIONS 2025-26':
                    # Skip the section header, will be handled by next competition name
                    continue
                current_competition = line
                current_team = None
                event_results = {}
                duosmium_link = None
                comp_date = None
                comp_type = None
                comp_location = None
                comp_overnight = None
                comp_teams = None
                comp_registration_opens = None
                comp_registration_closes = None
                comp_roster_released = None
                comp_status = None
                continue

            # Date line
            if line.startswith('Date:'):
                date_str = line.replace('Date:', '').strip()
                comp_date = parse_date(date_str)
                continue

            # Type line
            if line.startswith('Type:'):
                comp_type = normalize_competition_type(line.replace('Type:', '').strip())
                continue

            # Location line
            if line.startswith('Location:'):
                comp_location = line.replace('Location:', '').strip()
                continue

            # Overnight line
            if line.startswith('Overnight:'):
                overnight_str = line.replace('Overnight:', '').strip()
                # Extract time range if present in parentheses
                time_match = re.search(r'\(([^)]+)\)', overnight_str)
                if time_match:
                    comp_overnight = time_match.group(1)
                elif overnight_str.lower() == 'yes':
                    comp_overnight = True
                elif overnight_str.lower() == 'no':
                    comp_overnight = False
                else:
                    comp_overnight = overnight_str if overnight_str else None
                continue

            # Teams line
            if line.startswith('Teams:'):
                teams_str = line.replace('Teams:', '').strip()
                # Handle ranges like "1-2"
                if '-' in teams_str:
                    comp_teams = teams_str
                else:
                    try:
                        comp_teams = int(teams_str)
                    except:
                        comp_teams = teams_str
                continue

            # Registration Opens line
            if line.startswith('Registration Opens:'):
                date_str = line.replace('Registration Opens:', '').strip()
                comp_registration_opens = parse_date(date_str)
                continue

            # Registration Closes line
            if line.startswith('Registration Closes:'):
                date_str = line.replace('Registration Closes:', '').strip()
                comp_registration_closes = parse_date(date_str)
                continue

            # Roster Released line
            if line.startswith('Roster Released:'):
                date_str = line.replace('Roster Released:', '').strip()
                comp_roster_released = parse_date(date_str)
                continue

            # Status line (for maybe competitions)
            if line.startswith('Status:'):
                comp_status = line.replace('Status:', '').strip()
                continue

            # Duosmium link
            if 'duosmium.org' in line.lower():
                duosmium_link = line.strip()
                continue

            # Team results header
            if line.startswith('Team ') and line.endswith(' Results:'):
                save_team()
                current_team = line.split()[1]
                event_results = {}
                continue

            # Skip "Results: Pending" lines for upcoming competitions
            if line.startswith('Results:') and 'Pending' in line:
                # Mark as upcoming competition with no results yet
                if current_competition:
                    ensure_comp()
                    results[current_competition]["upcoming"] = True
                continue
            
            # Overall results
            if line.startswith('Overall:'):
                if current_competition and current_team:
                    overall_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*out of\s*(\d+)', line)
                    rank, out_of = None, None
                    if overall_match:
                        rank = int(overall_match.group(1))
                        out_of = int(overall_match.group(2))
                    else:
                        rank_match = re.search(r'(\d+)(?:st|nd|rd|th)?$', line)
                        if rank_match:
                            rank = int(rank_match.group(1))
                            out_of = 0
                    if rank is not None:
                        ensure_comp()
                        team_entry = results[current_competition]["teams"].get(current_team, {})
                        team_entry["overall"] = {"rank": rank, "outOf": out_of}
                        results[current_competition]["teams"][current_team] = team_entry
                continue

            # Event line: "Event Name: number"
            if ':' in line and re.search(r':\s*\d+[\*◊]?', line):
                if current_team:
                    parts = line.split(':', 1)
                    event_name = parts[0].strip()
                    placement_part = parts[1].strip()
                    
                    # Extract the number first, even if there's a ◊ or * marker
                    # The ◊ symbol indicates disqualification/no-show but the placement number is still valid
                    clean_placement = re.sub(r'[^\d]', '', placement_part)
                    
                    # Handle DQ or special markers
                    if '(DQ)' in placement_part or (not clean_placement and ('DQ' in placement_part.upper())):
                        # Explicit DQ with no number - skip or use None
                        continue  # Skip DQ entries without numbers
                    elif clean_placement:
                        # Extract the number (even if there's a ◊ marker)
                        # The ◊ is just a notation, the placement number is still valid
                        placement = int(clean_placement)
                        event_results[event_name] = placement
                    else:
                        # No number found, skip
                        continue

        save_team()

    return results


def parse_competition_rosters() -> Dict[str, Dict[str, Any]]:
    """Parse competition rosters from the standardized file.
    
    Returns:
        Dict mapping competition name to rosters with metadata:
        {
            "COMP NAME": {
                "date": datetime,
                "type": str,
                "teams": {
                    "A": [
                        {"event": "Event Name", "participants": ["Name1", "Name2"]},
                        ...
                    ],
                    "B": [...],
                    ...
                }
            }
        }
    """
    rosters = {}
    
    if not os.path.exists(ROSTERS_FILE):
        return rosters
    
    with open(ROSTERS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = content.split('================================================================================')
    
    for section in sections:
        section = section.strip()
        if not section or 'BRONX SCIENCE OLYMPIAD' in section or 'Notes:' in section:
            continue
            
        lines = section.split('\n')
        current_competition = None
        current_team = None
        current_events = []
        comp_date = None
        comp_type = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Competition header or "UPCOMING COMPETITIONS" section
            if re.match(r'^[A-Z\s]+20[0-9]{2}-[0-9]{2}$', line) or line == 'UPCOMING COMPETITIONS 2025-26':
                if current_competition and current_team and current_events:
                    if current_competition not in rosters:
                        rosters[current_competition] = {"date": comp_date, "type": comp_type, "teams": {}}
                    rosters[current_competition]["teams"][current_team] = current_events
                
                if line == 'UPCOMING COMPETITIONS 2025-26':
                    # Skip the section header, will be handled by next competition name
                    continue
                
                current_competition = line
                current_team = None
                current_events = []
                comp_date = None
                comp_type = None
                comp_location = None
                comp_overnight = None
                comp_teams = None
                comp_registration_opens = None
                comp_registration_closes = None
                comp_roster_released = None
                comp_status = None
                
            # Date line
            elif line.startswith('Date:'):
                date_str = line.replace('Date:', '').strip()
                comp_date = parse_date(date_str)
                
            # Type line
            elif line.startswith('Type:'):
                comp_type = normalize_competition_type(line.replace('Type:', '').strip())
                
            # Location line
            elif line.startswith('Location:'):
                comp_location = line.replace('Location:', '').strip()
                
            # Overnight line
            elif line.startswith('Overnight:'):
                overnight_str = line.replace('Overnight:', '').strip()
                # Extract time range if present in parentheses
                import re as re_module
                time_match = re_module.search(r'\(([^)]+)\)', overnight_str)
                if time_match:
                    comp_overnight = time_match.group(1)
                elif overnight_str.lower() == 'yes':
                    comp_overnight = True
                elif overnight_str.lower() == 'no':
                    comp_overnight = False
                else:
                    comp_overnight = overnight_str if overnight_str else None
                    
            # Teams line
            elif line.startswith('Teams:'):
                teams_str = line.replace('Teams:', '').strip()
                if '-' in teams_str:
                    comp_teams = teams_str
                else:
                    try:
                        comp_teams = int(teams_str)
                    except:
                        comp_teams = teams_str
                        
            # Registration Opens line
            elif line.startswith('Registration Opens:'):
                date_str = line.replace('Registration Opens:', '').strip()
                comp_registration_opens = parse_date(date_str)
                
            # Registration Closes line
            elif line.startswith('Registration Closes:'):
                date_str = line.replace('Registration Closes:', '').strip()
                comp_registration_closes = parse_date(date_str)
                
            # Roster Released line
            elif line.startswith('Roster Released:'):
                date_str = line.replace('Roster Released:', '').strip()
                comp_roster_released = parse_date(date_str)
                
            # Status line
            elif line.startswith('Status:'):
                comp_status = line.replace('Status:', '').strip()
                
            # Team header
            elif line.startswith('Team ') and line.endswith(':') and not line.endswith(' Results:'):
                if current_competition and current_team and current_events:
                    if current_competition not in rosters:
                        rosters[current_competition] = {"date": comp_date, "type": comp_type, "teams": {}}
                    rosters[current_competition]["teams"][current_team] = current_events
                
                current_team = line.split()[1].rstrip(':')
                current_events = []
                
            # Skip "Roster: Pending" lines for upcoming competitions
            elif line.startswith('Roster:') and 'Pending' in line:
                # Mark as upcoming competition with no roster yet
                if current_competition:
                    if current_competition not in rosters:
                        rosters[current_competition] = {"date": comp_date, "type": comp_type, "teams": {}, "upcoming": True}
                    else:
                        rosters[current_competition]["upcoming"] = True
                continue
            
            # Event line: "Event: Participant1, Participant2"
            elif ':' in line and ',' in line:
                if current_team:
                    parts = line.split(':')
                    if len(parts) == 2:
                        event_name = parts[0].strip()
                        participants_part = parts[1].strip()
                        participants = [p.strip() for p in participants_part.split(',') if p.strip()]
                        current_events.append({
                            "event": event_name,
                            "participants": participants
                        })
        
        # Save last team
        if current_competition and current_team and current_events:
            if current_competition not in rosters:
                rosters[current_competition] = {
                    "date": comp_date,
                    "type": comp_type,
                    "location": comp_location,
                    "overnight": comp_overnight,
                    "numTeams": comp_teams,
                    "registrationOpens": comp_registration_opens,
                    "registrationCloses": comp_registration_closes,
                    "rosterReleased": comp_roster_released,
                    "status": comp_status,
                    "teams": {}
                }
            rosters[current_competition]["teams"][current_team] = current_events
    
    return rosters


def get_all_competitions() -> List[Dict[str, Any]]:
    """Get all competitions with results and rosters combined.
    
    Returns list of competition documents matching the Firebase structure:
    [
        {
            "id": str (generated),
            "name": str,
            "date": datetime,
            "type": str,
            "duosmium": str,
            "teamPlacement": [
                {
                    "team": "A",
                    "event": "Event Name",
                    "participants": ["Name1", "Name2"]
                },
                ...
            ],
            "results": {
                "teamRank": int,
                "teamOutOf": int,
                "eventResults": [
                    {
                        "eventName": "Event Name",
                        "team": "A",
                        "placement": int,
                        "outOf": int
                    },
                    ...
                ]
            }
        },
        ...
    ]
    """
    global _competitions_cache
    
    # Use cache if available
    if _competitions_cache is not None:
        return _competitions_cache
    
    results_data = parse_competition_results()
    rosters_data = parse_competition_rosters()
    
    competitions = []
    
    # Combine results and rosters by competition name
    all_comp_names = set(results_data.keys()) | set(rosters_data.keys())
    
    for comp_name in all_comp_names:
        comp_results = results_data.get(comp_name, {})
        comp_rosters_data = rosters_data.get(comp_name, {})
        
        # Skip if no data at all (unless it's an upcoming competition)
        is_upcoming = comp_results.get('upcoming') or comp_rosters_data.get('upcoming')
        if not comp_results and not comp_rosters_data:
            continue
        
        # Extract metadata - prefer results file, fallback to rosters file
        comp_date = comp_results.get('date') or comp_rosters_data.get('date')
        comp_type_raw = comp_results.get('type') or comp_rosters_data.get('type') or ''
        comp_type = normalize_competition_type(comp_type_raw)
        duosmium = comp_results.get('duosmium')
        comp_location = comp_results.get('location') or comp_rosters_data.get('location')
        # For overnight, prefer results file, but handle False explicitly (False or None evaluates to None)
        comp_overnight = comp_results.get('overnight') if 'overnight' in comp_results else comp_rosters_data.get('overnight')
        comp_teams = comp_results.get('numTeams') or comp_rosters_data.get('numTeams')
        comp_registration_opens = comp_results.get('registrationOpens') or comp_rosters_data.get('registrationOpens')
        comp_registration_closes = comp_results.get('registrationCloses') or comp_rosters_data.get('registrationCloses')
        comp_roster_released = comp_results.get('rosterReleased') or comp_rosters_data.get('rosterReleased')
        comp_status = comp_results.get('status') or comp_rosters_data.get('status')
        
        # For upcoming competitions, skip if no date (means it's not fully parsed)
        if is_upcoming and not comp_date:
            continue
        
        # Get teams from rosters
        rosters_teams = comp_rosters_data.get('teams', {})
        
        # Build team placement
        team_placement = []
        for team_letter, events_list in rosters_teams.items():
            for event_data in events_list:
                team_placement.append({
                    "team": team_letter,
                    "event": event_data["event"],
                    "participants": event_data["participants"]
                })
        
        # Build event results
        event_results = []
        teams_data = comp_results.get('teams', {})
        
        for team_letter, team_data in teams_data.items():
            events = team_data.get('events', {})
            overall = team_data.get('overall', {})
            out_of = overall.get('outOf', 0)
            
            for event_name, placement in events.items():
                event_results.append({
                    "eventName": event_name,
                    "team": team_letter,
                    "placement": placement,
                    "outOf": out_of
                })
        
        # Get overall team rank (use first team's overall if available)
        team_rank = 0
        team_out_of = 0
        if teams_data:
            first_team = list(teams_data.keys())[0]
            overall = teams_data[first_team].get('overall', {})
            team_rank = overall.get('rank', 0)
            team_out_of = overall.get('outOf', 0)
        
        # Create competition document
        # Format date for JSON serialization (use timestamp for compatibility)
        date_value = None
        if comp_date:
            # Store as ISO string for frontend compatibility
            date_value = comp_date.isoformat()
        
        comp_doc = {
            "id": comp_name.replace(' ', '_').replace('-', '_').lower(),  # Generate ID from name
            "name": comp_name,
            "date": date_value,
            "type": comp_type,
            "duosmium": duosmium,
            "location": comp_location,
            "overnight": comp_overnight,
            "numTeams": comp_teams,
            "registrationOpens": comp_registration_opens.isoformat() if comp_registration_opens else None,
            "registrationCloses": comp_registration_closes.isoformat() if comp_registration_closes else None,
            "rosterReleased": comp_roster_released.isoformat() if comp_roster_released else None,
            "status": comp_status,
            "teamPlacement": team_placement,
            "results": {
                "teamRank": team_rank,
                "teamOutOf": team_out_of,
                "eventResults": event_results
            }
        }
        
        competitions.append(comp_doc)
    
    # Sort by date (newest first)
    competitions.sort(key=lambda x: x.get('date') or '', reverse=True)
    
    # Cache the results
    _competitions_cache = competitions
    
    return competitions


def clear_cache():
    """Clear the competitions cache (useful for testing or reloading)"""
    global _competitions_cache
    _competitions_cache = None

