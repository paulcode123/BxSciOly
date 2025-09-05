#!/usr/bin/env python3
"""
Script to populate the Competitions collection with past Science Olympiad competition data
This script creates competition documents for all past competitions from the planning documents
"""

import requests
import json
import time
import re
from datetime import datetime

# API base URL - adjust if needed
API_BASE = "http://localhost:8000/api"

# Event mappings for different years
EVENTS_23_24 = [
    "Anatomy and Physiology", "Astronomy", "Chemistry Lab", "Codebusters", 
    "Detector Building", "Disease Detectives", "Dynamic Planet", "Ecology", 
    "Experimental Design", "Fermi Questions", "Forensics", "Forestry", 
    "Fossils", "Geologic Mapping", "Microbe Mission", "Optics", 
    "Wind Power", "Write It Do It"
]

EVENTS_24_25 = [
    "Air Trajectory", "Anatomy and Physiology", "Astronomy", "Bungee Drop", 
    "Chemistry Lab", "Codebusters", "Disease Detectives", "Dynamic Planet", 
    "Ecology", "Electric Vehicle", "Entomology", "Experimental Design", 
    "Forensics", "Fossils", "Geologic Mapping", "Helicopter", 
    "Materials Science", "Microbe Mission", "Optics", "Robot Tour", 
    "Tower", "Wind Power", "Write It Do It"
]

# Competition data extracted from the files
PAST_COMPETITIONS = [
    {
        "name": "RICKARDS SATELLITE INVITATIONAL 2024-25",
        "type": "satellite",
        "duosmium": "https://www.duosmium.org/results/2024-11-02_rickards_invitational_c/",
        "teams": ["A"],
        "outOf": 287,
        "year": "24-25"
    },
    {
        "name": "YALE INVITATIONAL 2023-24",
        "type": "invitational",
        "duosmium": "https://www.duosmium.org/results/2024-02-10_yale_invitational_c/",
        "teams": ["A"],
        "outOf": 56,
        "year": "23-24"
    },
    {
        "name": "NEW YORK STATE CHAMPIONSHIP 2023-24",
        "type": "official",
        "duosmium": "https://www.duosmium.org/results/2024-03-15_NY_states_c/",
        "teams": ["A"],
        "outOf": 59,
        "year": "23-24"
    },
    {
        "name": "SEALS OLYMPIAD 2024-25",
        "type": "satellite",
        "duosmium": "https://www.duosmium.org/results/2024-12-07_sealsoinvitational_c/",
        "teams": ["A", "B"],
        "outOf": 42,
        "year": "24-25"
    },
    {
        "name": "LEXINGTON SATELLITE INVITATIONAL 2024-25",
        "type": "satellite",
        "duosmium": "https://www.duosmium.org/results/2025-04-10_lexington_invitational_c/",
        "teams": ["A", "B"],
        "outOf": 23,
        "year": "24-25"
    },
    {
        "name": "NYC NORTH REGIONAL 2024-25",
        "type": "official",
        "duosmium": "https://www.duosmium.org/results/2025-01-25_NY_nyc_north_regional_c/",
        "teams": ["A", "B", "C"],
        "outOf": 34,
        "year": "24-25"
    },
    {
        "name": "NYC NORTH REGIONAL 2023-24",
        "type": "official",
        "duosmium": "https://www.duosmium.org/results/2024-01-27_NY_nyc_north_regional_c/",
        "teams": ["A", "B", "C"],
        "outOf": 30,
        "year": "23-24"
    },
    {
        "name": "NEW YORK STATE CHAMPIONSHIP 2024-25",
        "type": "official",
        "duosmium": "https://www.duosmium.org/results/2025-03-21_NY_states_c/",
        "teams": ["A"],
        "outOf": 60,
        "year": "24-25"
    },
    {
        "name": "BIRDSO SATELLITE INVITATIONAL 2023-24",
        "type": "satellite",
        "duosmium": "https://www.duosmium.org/results/2024-02-10_birdso_satellite_invitational_c/",
        "teams": ["A", "B", "C"],
        "outOf": 139,
        "year": "23-24"
    },
    {
        "name": "BOYCEVILLE SATELLITE INVITATIONAL 2023-24",
        "type": "satellite",
        "duosmium": "https://www.duosmium.org/results/2023-11-27_boyceville_satellite_invitational_c/",
        "teams": ["A", "B", "C"],
        "outOf": 236,
        "year": "23-24"
    },
    {
        "name": "RICKARDS SATELLITE INVITATIONAL 2023-24",
        "type": "satellite",
        "duosmium": "https://www.duosmium.org/results/2023-11-04_rickards_invitational_c/",
        "teams": ["A"],
        "outOf": 231,
        "year": "23-24"
    }
]

def parse_competition_results():
    """Parse the competition results from the standardized file"""
    results = {}
    
    with open('Planning/competitionResults_standardized.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by competition sections
    sections = content.split('================================================================================')
    
    for section in sections:
        section = section.strip()
        if not section or 'BRONX SCIENCE OLYMPIAD' in section or 'Event Orders by Season' in section or 'Notes:' in section:
            continue
            
        lines = section.split('\n')
        current_competition = None
        current_team = None
        event_results = []
        duosmium_link = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a competition header (all caps with year)
            if re.match(r'^[A-Z\s]+20[0-9]{2}-[0-9]{2}$', line):
                # Save previous competition if exists
                if current_competition and current_team and event_results:
                    if current_competition not in results:
                        results[current_competition] = {"duosmium": duosmium_link, "teams": {}}
                    results[current_competition]["teams"][current_team] = event_results
                
                # Start new competition
                current_competition = line
                current_team = None
                event_results = []
                duosmium_link = None
                
            # Check if this is a duosmium link
            elif 'duosmium.org' in line:
                duosmium_link = line
                
            # Check if this is a team header
            elif line.startswith('Team ') and line.endswith(' Results:'):
                # Save previous team if exists
                if current_competition and current_team and event_results:
                    if current_competition not in results:
                        results[current_competition] = {"duosmium": duosmium_link, "teams": {}}
                    results[current_competition]["teams"][current_team] = event_results
                
                # Start new team
                current_team = line.split()[1]  # Get team letter
                event_results = []
                
            # Check if this is an overall result
            elif line.startswith('Overall:'):
                if current_competition and current_team:
                    overall_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*out of\s*(\d+)', line)
                    if overall_match:
                        if current_competition not in results:
                            results[current_competition] = {"duosmium": duosmium_link, "teams": {}}
                        results[current_competition]["teams"][f"{current_team}_overall"] = {
                            "rank": int(overall_match.group(1)),
                            "outOf": int(overall_match.group(2))
                        }
                    # Handle cases where there's no "out of" number
                    elif re.search(r'(\d+)(?:st|nd|rd|th)?$', line):
                        rank_match = re.search(r'(\d+)(?:st|nd|rd|th)?$', line)
                        if current_competition not in results:
                            results[current_competition] = {"duosmium": duosmium_link, "teams": {}}
                        results[current_competition]["teams"][f"{current_team}_overall"] = {
                            "rank": int(rank_match.group(1)),
                            "outOf": 0
                        }
                        
            # Check if this is an event result line (Event: number)
            elif ':' in line and re.search(r':\s*\d+[\*◊]?$', line):
                if current_team:
                    parts = line.split(':')
                    if len(parts) == 2:
                        placement_part = parts[1].strip()
                        # Handle special cases like (DQ)
                        if '(DQ)' in placement_part:
                            event_results.append(999)  # Use 999 for DQ
                        else:
                            clean_placement = re.sub(r'[^\d]', '', placement_part)
                            if clean_placement:
                                event_results.append(int(clean_placement))
        
        # Save the last team in this section
        if current_competition and current_team and event_results:
            if current_competition not in results:
                results[current_competition] = {"duosmium": duosmium_link, "teams": {}}
            results[current_competition]["teams"][current_team] = event_results
    
    return results

def parse_competition_rosters():
    """Parse the competition rosters from the standardized file"""
    rosters = {}
    
    with open('Planning/competitionRosters_standardized.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by competition sections
    sections = content.split('================================================================================')
    
    for section in sections:
        section = section.strip()
        if not section or 'BRONX SCIENCE OLYMPIAD' in section or 'Notes:' in section:
            continue
            
        lines = section.split('\n')
        current_competition = None
        current_team = None
        current_events = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a competition header (all caps with year)
            if re.match(r'^[A-Z\s]+20[0-9]{2}-[0-9]{2}$', line):
                # Save previous competition if exists
                if current_competition and current_team and current_events:
                    if current_competition not in rosters:
                        rosters[current_competition] = {}
                    rosters[current_competition][current_team] = current_events
                
                # Start new competition
                current_competition = line
                current_team = None
                current_events = []
                
            # Check if this is a team header
            elif line.startswith('Team ') and line.endswith(':') and not line.endswith(' Results:'):
                # Save previous team if exists
                if current_competition and current_team and current_events:
                    if current_competition not in rosters:
                        rosters[current_competition] = {}
                    rosters[current_competition][current_team] = current_events
                
                # Start new team
                current_team = line.split()[1].rstrip(':')  # Get team letter, remove colon
                current_events = []
                
            # Check if this is an event line (Event: Participant1, Participant2)
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
        
        # Save the last team in this section
        if current_competition and current_team and current_events:
            if current_competition not in rosters:
                rosters[current_competition] = {}
            rosters[current_competition][current_team] = current_events
    
    return rosters

def create_competition_document(competition_data, results_data, rosters_data):
    """Create a complete competition document with all required fields"""
    
    # Find matching competition data
    comp_name = competition_data["name"]
    year = competition_data["year"]
    
    # Get events based on year
    events = EVENTS_24_25 if year == "24-25" else EVENTS_23_24
    
    # Get results for this competition - try exact match first, then fuzzy match
    comp_results = results_data.get(comp_name, {})
    comp_rosters = rosters_data.get(comp_name, {})
    
    # If no exact match found, try to find similar names
    if not comp_results:
        for result_name in results_data.keys():
            # Normalize names for comparison
            normalized_comp = comp_name.lower().replace(" ", "").replace("-", "")
            normalized_result = result_name.lower().replace(" ", "").replace("-", "")
            if normalized_comp in normalized_result or normalized_result in normalized_comp:
                comp_results = results_data[result_name]
                print(f"   🔍 Found fuzzy match for results: {result_name}")
                break
    
    if not comp_rosters:
        for roster_name in rosters_data.keys():
            # Normalize names for comparison
            normalized_comp = comp_name.lower().replace(" ", "").replace("-", "")
            normalized_roster = roster_name.lower().replace(" ", "").replace("-", "")
            if normalized_comp in normalized_roster or normalized_roster in normalized_comp:
                comp_rosters = rosters_data[roster_name]
                print(f"   🔍 Found fuzzy match for rosters: {roster_name}")
                break
    
    # Create team placement data
    team_placement = []
    all_event_results = []
    
    for team_letter in competition_data["teams"]:
        # Get roster data for this team
        team_roster = comp_rosters.get(team_letter, [])
        
        # Get results for this team - access through teams subdict
        team_result_numbers = []
        team_overall = {}
        
        if "teams" in comp_results:
            if team_letter in comp_results["teams"]:
                team_result_numbers = comp_results["teams"][team_letter]
            if f"{team_letter}_overall" in comp_results["teams"]:
                team_overall = comp_results["teams"][f"{team_letter}_overall"]
        
        # Create team placement entries
        for event_data in team_roster:
            team_placement.append({
                "team": team_letter,
                "event": event_data["event"],
                "participants": event_data["participants"]
            })
        
        # Create event results
        for i, placement in enumerate(team_result_numbers):
            if i < len(events):
                all_event_results.append({
                    "eventName": events[i],
                    "team": team_letter,
                    "placement": placement,
                    "outOf": competition_data["outOf"]
                })
    
    # Create results object - use the first team's overall results as the main results
    first_team = competition_data["teams"][0]
    first_team_overall = {}
    if "teams" in comp_results and f"{first_team}_overall" in comp_results["teams"]:
        first_team_overall = comp_results["teams"][f"{first_team}_overall"]
    
    results_obj = {
        "teamRank": first_team_overall.get("rank", 0),
        "teamOutOf": first_team_overall.get("outOf", competition_data["outOf"]),
        "eventResults": all_event_results
    }
    
    # Debug: Print what we found for this competition
    print(f"   📊 Results found for {comp_name}: {len(comp_results)} teams")
    print(f"   📊 Rosters found for {comp_name}: {len(comp_rosters)} teams")
    print(f"   📊 Team placement entries: {len(team_placement)}")
    print(f"   📊 Event results: {len(all_event_results)}")
    
    # Debug: Print the actual structure
    if comp_results:
        print(f"   🔍 Results structure: {list(comp_results.keys())}")
    if comp_rosters:
        print(f"   🔍 Rosters structure: {list(comp_rosters.keys())}")
    
    return {
        "name": comp_name,
        "type": competition_data["type"],
        "teamPlacement": team_placement,
        "results": results_obj,
        "duosmium": competition_data["duosmium"]
    }

def delete_all_competitions():
    """Delete all existing competitions"""
    try:
        print("🗑️  Deleting existing competitions...")
        response = requests.get(f"{API_BASE}/Competitions")
        if response.status_code == 200:
            competitions = response.json()
            for competition_data in competitions:
                if isinstance(competition_data, dict):
                    # Handle Firebase format
                    competition_id = list(competition_data.keys())[0]
                else:
                    competition_id = competition_data.get('id')
                
                if competition_id:
                    delete_response = requests.delete(f"{API_BASE}/Competitions/{competition_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted competition {competition_id}")
                    else:
                        print(f"   ❌ Failed to delete competition {competition_id}")
                    time.sleep(0.1)  # Small delay to avoid overwhelming the API
        print("✨ Cleanup complete!")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def create_past_competitions():
    """Create all past Science Olympiad competitions"""
    print("🚀 Creating past Science Olympiad competitions...")
    
    # Parse the data files
    print("📖 Parsing competition data files...")
    results_data = parse_competition_results()
    rosters_data = parse_competition_rosters()
    
    # Debug: Print what we found
    print(f"📊 Found {len(results_data)} competitions in results file:")
    for name in results_data.keys():
        print(f"   - {name}")
    
    print(f"📊 Found {len(rosters_data)} competitions in rosters file:")
    for name in rosters_data.keys():
        print(f"   - {name}")
    
    total_competitions = len(PAST_COMPETITIONS)
    created_competitions = 0
    
    for competition_data in PAST_COMPETITIONS:
        try:
            # Create complete competition document
            competition_document = create_competition_document(competition_data, results_data, rosters_data)
            
            # Debug: Print document structure
            print(f"\n🔍 Debug for {competition_data['name']}:")
            print(f"   Team placement entries: {len(competition_document.get('teamPlacement', []))}")
            print(f"   Event results: {len(competition_document.get('results', {}).get('eventResults', []))}")
            
            response = requests.post(
                f"{API_BASE}/Competitions",
                headers={'Content-Type': 'application/json'},
                json=competition_document
            )
            
            if response.status_code in [200, 201]:
                created_competitions += 1
                print(f"   ✅ Created: {competition_data['name']}")
            else:
                print(f"   ❌ Failed to create: {competition_data['name']} - {response.status_code}")
                print(f"      Response: {response.text}")
            
            time.sleep(0.2)  # Small delay between requests
            
        except Exception as e:
            print(f"   ❌ Error creating {competition_data['name']}: {e}")

def main():
    """Main execution function"""
    print("🎯 Past Science Olympiad Competitions Collection Population Script")
    print("=" * 70)
    
    # Create past competitions (without deleting existing ones)
    create_past_competitions()
    
    print("=" * 70)
    print("🎉 Script completed!")
    print()
    print("📋 Summary:")
    print(f"   • Created {len(PAST_COMPETITIONS)} past competitions")
    
    # Count competitions by type
    competition_types = {}
    for comp in PAST_COMPETITIONS:
        comp_type = comp["type"]
        competition_types[comp_type] = competition_types.get(comp_type, 0) + 1
    
    print("   • Competition types:")
    for comp_type, count in competition_types.items():
        print(f"     - {comp_type.capitalize()}: {count} competitions")
    
    print()
    print("🎨 Features included:")
    print("   • Complete competition information with names and types")
    print("   • Team placement data with participant names")
    print("   • Event results with placements and 'out of' numbers")
    print("   • Overall team rankings")
    print("   • Duosmium links for all competitions")
    print("   • Support for both '23-'24 and '24-'25 event formats")
    print()
    print("📅 Competition timeline:")
    print("   • Earliest: Rickards '23-'24 (Nov 2023)")
    print("   • Latest: Lexington '24-'25 (Apr 2025)")
    print()
    print("🌐 Navigate to the Competitions page to see all the created competitions!")
    print("   • Note: Existing competitions were preserved")

if __name__ == "__main__":
    main()
