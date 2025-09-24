#!/usr/bin/env python3
"""
Competition Results Discrepancy Checker

This script compares the original competitionResults.txt file with the 
standardized competitionResults_standardized.txt file to find discrepancies
in event placements, missing events, and incorrect event orders.

Usage: python check_competition_discrepancies.py
"""

import re
from typing import Dict, List, Tuple, Optional

def parse_events_line(line: str) -> List[str]:
    """Parse the events line and return a list of event names."""
    # Remove the "Events:" prefix and split by tabs
    events_text = line.replace("Events:", "").strip()
    events = [event.strip() for event in events_text.split('\t') if event.strip()]
    return events

def parse_team_results(lines: List[str], start_idx: int, team_name: str) -> Tuple[Dict[str, str], int]:
    """
    Parse team results from the original file format.
    Returns a dictionary of event_name -> placement and the next line index.
    """
    results = {}
    i = start_idx
    
    # Skip the team header line
    if i < len(lines) and team_name in lines[i]:
        i += 1
    
    # Read placement numbers until we hit "overall:" or another team
    while i < len(lines):
        line = lines[i].strip()
        
        # Stop if we hit overall ranking or another team
        if line.startswith("overall:") or line.startswith("Team ") or line == "":
            break
            
        # Skip empty lines
        if not line:
            i += 1
            continue
            
        # Extract placement number (handle special characters like *, ◊, ??)
        placement = line.strip()
        if placement:
            # Use the line number relative to team start as event index
            event_index = len(results)
            results[f"event_{event_index}"] = placement
            
        i += 1
    
    return results, i

def parse_standardized_team_results(lines: List[str], start_idx: int) -> Tuple[Dict[str, str], int]:
    """
    Parse team results from the standardized file format.
    Returns a dictionary of event_name -> placement and the next line index.
    """
    results = {}
    i = start_idx
    
    # Skip the team header line
    if i < len(lines) and "Results:" in lines[i]:
        i += 1
    
    # Read event placements until we hit "Overall:" or another team
    while i < len(lines):
        line = lines[i].strip()
        
        # Stop if we hit overall ranking or another team
        if line.startswith("Overall:") or line.startswith("Team ") or line == "":
            break
            
        # Skip empty lines and section dividers
        if not line or line.startswith("="):
            i += 1
            continue
            
        # Parse "Event Name: Placement" format
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                event_name = parts[0].strip()
                placement = parts[1].strip()
                results[event_name] = placement
                
        i += 1
    
    return results, i

def find_competition_sections(lines: List[str]) -> List[Dict]:
    """Find all competition sections in the file."""
    competitions = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for competition headers (various formats)
        if (line.startswith("'") and ("Invitational" in line or "States" in line or "Regionals" in line)) or \
           line.startswith("Regionals") or line.startswith("States") or \
           line.startswith("SealSO") or line.startswith("Lexington") or \
           line.startswith("Boyceville") or line.startswith("Rickards"):
            
            competition = {
                'name': line,
                'start_line': i,
                'events': [],
                'teams': []
            }
            
            # Find events line
            j = i + 1
            while j < len(lines) and j < i + 10:  # Look within next 10 lines
                if lines[j].strip().startswith("Events:"):
                    competition['events'] = parse_events_line(lines[j])
                    break
                j += 1
            
            # Find teams
            j += 1
            while j < len(lines):
                team_line = lines[j].strip()
                if team_line.startswith("Team ") and team_line.endswith(":"):
                    team_name = team_line
                    team_results, next_idx = parse_team_results(lines, j, team_name)
                    competition['teams'].append({
                        'name': team_name,
                        'results': team_results,
                        'start_line': j
                    })
                    j = next_idx
                elif (team_line.startswith("'") or team_line.startswith("Regionals") or \
                     team_line.startswith("States") or team_line.startswith("SealSO") or \
                     team_line.startswith("Lexington") or team_line.startswith("Boyceville") or \
                     team_line.startswith("Rickards") or team_line == ""):
                    break
                else:
                    j += 1
            
            competitions.append(competition)
            i = j
        else:
            i += 1
    
    return competitions

def find_standardized_competition_sections(lines: List[str]) -> List[Dict]:
    """Find all competition sections in the standardized file."""
    competitions = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for competition headers (standardized format)
        if line.isupper() and ("INVITATIONAL" in line or "CHAMPIONSHIP" in line or "REGIONAL" in line or "OLYMPIAD" in line):
            
            competition = {
                'name': line,
                'start_line': i,
                'teams': []
            }
            
            # Find teams
            j = i + 1
            while j < len(lines):
                team_line = lines[j].strip()
                if team_line.startswith("Team ") and "Results:" in team_line:
                    team_name = team_line
                    team_results, next_idx = parse_standardized_team_results(lines, j)
                    competition['teams'].append({
                        'name': team_name,
                        'results': team_results,
                        'start_line': j
                    })
                    j = next_idx
                elif team_line.isupper() and ("INVITATIONAL" in team_line or "CHAMPIONSHIP" in team_line or "REGIONAL" in team_line or "OLYMPIAD" in team_line):
                    break
                elif team_line.startswith("="):
                    break
                else:
                    j += 1
            
            competitions.append(competition)
            i = j
        else:
            i += 1
    
    return competitions

def compare_competitions(original_comp: Dict, standardized_comp: Dict) -> List[str]:
    """Compare a competition between original and standardized files."""
    discrepancies = []
    
    # Check if we have the same number of teams
    if len(original_comp['teams']) != len(standardized_comp['teams']):
        discrepancies.append(f"  ❌ Team count mismatch: Original has {len(original_comp['teams'])} teams, Standardized has {len(standardized_comp['teams'])} teams")
        return discrepancies
    
    # Compare each team
    for i, (orig_team, std_team) in enumerate(zip(original_comp['teams'], standardized_comp['teams'])):
        team_discrepancies = compare_team_results(orig_team, std_team, original_comp['events'])
        if team_discrepancies:
            discrepancies.extend([f"  {orig_team['name']}:"] + team_discrepancies)
    
    return discrepancies

def compare_team_results(orig_team: Dict, std_team: Dict, events: List[str]) -> List[str]:
    """Compare results for a single team."""
    discrepancies = []
    
    orig_results = orig_team['results']
    std_results = std_team['results']
    
    # Check if we have the same number of events
    if len(orig_results) != len(std_results):
        discrepancies.append(f"    ❌ Event count mismatch: Original has {len(orig_results)} events, Standardized has {len(std_results)} events")
    
    # Compare each event placement
    for i, event_name in enumerate(events):
        orig_key = f"event_{i}"
        std_key = event_name
        
        if orig_key in orig_results and std_key in std_results:
            orig_placement = orig_results[orig_key]
            std_placement = std_results[std_key]
            
            if orig_placement != std_placement:
                discrepancies.append(f"    ❌ {event_name}: Original '{orig_placement}' vs Standardized '{std_placement}'")
        elif orig_key in orig_results:
            discrepancies.append(f"    ❌ {event_name}: Missing in standardized (Original: '{orig_results[orig_key]}')")
        elif std_key in std_results:
            discrepancies.append(f"    ❌ {event_name}: Missing in original (Standardized: '{std_results[std_key]}')")
    
    return discrepancies

def main():
    """Main function to check for discrepancies."""
    print("🔍 Competition Results Discrepancy Checker")
    print("=" * 50)
    
    try:
        # Read original file
        with open("Planning/competitionResults.txt", "r", encoding="utf-8") as f:
            original_lines = f.readlines()
        
        # Read standardized file
        with open("Planning/competitionResults_standardized.txt", "r", encoding="utf-8") as f:
            standardized_lines = f.readlines()
        
        print(f"📖 Read {len(original_lines)} lines from original file")
        print(f"📖 Read {len(standardized_lines)} lines from standardized file")
        print()
        
        # Parse competitions
        print("🔍 Parsing competitions...")
        original_competitions = find_competition_sections(original_lines)
        standardized_competitions = find_standardized_competition_sections(standardized_lines)
        
        print(f"📊 Found {len(original_competitions)} competitions in original file")
        print(f"📊 Found {len(standardized_competitions)} competitions in standardized file")
        print()
        
        # Compare competitions
        total_discrepancies = 0
        
        for i, orig_comp in enumerate(original_competitions):
            print(f"🏆 Checking: {orig_comp['name']}")
            
            # Find matching standardized competition
            std_comp = None
            orig_name_upper = orig_comp['name'].upper()
            
            for std_comp_candidate in standardized_competitions:
                std_name_upper = std_comp_candidate['name'].upper()
                
                # More sophisticated matching
                match_score = 0
                
                # Check for key identifiers
                if "RICKARDS" in orig_name_upper and "RICKARDS" in std_name_upper:
                    match_score += 10
                if "YALE" in orig_name_upper and "YALE" in std_name_upper:
                    match_score += 10
                if "STATES" in orig_name_upper and "CHAMPIONSHIP" in std_name_upper:
                    match_score += 10
                if "REGIONALS" in orig_name_upper and "REGIONAL" in std_name_upper:
                    match_score += 10
                if "SEALSO" in orig_name_upper and ("SEALS" in std_name_upper or "OLYMPIAD" in std_name_upper):
                    match_score += 10
                if "LEXINGTON" in orig_name_upper and "LEXINGTON" in std_name_upper:
                    match_score += 10
                if "BIRDSO" in orig_name_upper and "BIRDSO" in std_name_upper:
                    match_score += 10
                if "BOYCEVILLE" in orig_name_upper and "BOYCEVILLE" in std_name_upper:
                    match_score += 10
                
                # Check for year patterns
                if "24-25" in orig_name_upper and "2024-25" in std_name_upper:
                    match_score += 5
                if "23-24" in orig_name_upper and "2023-24" in std_name_upper:
                    match_score += 5
                
                if match_score >= 10:  # High confidence match
                    std_comp = std_comp_candidate
                    break
            
            if std_comp is None:
                print(f"  ❌ No matching standardized competition found")
                print(f"    Available standardized competitions:")
                for std_comp_candidate in standardized_competitions:
                    print(f"      - {std_comp_candidate['name']}")
                total_discrepancies += 1
                continue
            
            # Compare the competitions
            discrepancies = compare_competitions(orig_comp, std_comp)
            
            if discrepancies:
                print(f"  ❌ Found {len(discrepancies)} discrepancies:")
                for disc in discrepancies:
                    print(disc)
                total_discrepancies += len(discrepancies)
            else:
                print(f"  ✅ No discrepancies found")
            
            # Debug info for team count issues
            if len(orig_comp['teams']) != len(std_comp['teams']):
                print(f"    Debug - Original teams: {[t['name'] for t in orig_comp['teams']]}")
                print(f"    Debug - Standardized teams: {[t['name'] for t in std_comp['teams']]}")
            
            print()
        
        # Summary
        print("=" * 50)
        if total_discrepancies == 0:
            print("🎉 SUCCESS: No discrepancies found!")
        else:
            print(f"⚠️  FOUND {total_discrepancies} DISCREPANCIES")
            print("Please review and fix the issues above.")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find file - {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
