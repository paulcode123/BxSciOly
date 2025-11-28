#!/usr/bin/env python3
"""Test script for competition parser"""

from competition_parser import get_all_competitions, clear_cache
from datetime import datetime
import json

def test_parser():
    """Test the competition parser"""
    print("Testing competition parser...")
    print("=" * 70)
    
    # Clear cache to force fresh parse
    clear_cache()
    
    # Get all competitions
    competitions = get_all_competitions()
    
    print(f"\nFound {len(competitions)} competitions\n")
    
    # Display first few competitions
    for i, comp in enumerate(competitions[:3]):
        print(f"Competition {i+1}:")
        print(f"  Name: {comp['name']}")
        print(f"  Date: {comp.get('date', 'N/A')}")
        print(f"  Type: {comp.get('type', 'N/A')}")
        print(f"  Teams: {len(set(p['team'] for p in comp.get('teamPlacement', [])))}")
        print(f"  Team Placement entries: {len(comp.get('teamPlacement', []))}")
        print(f"  Event Results: {len(comp.get('results', {}).get('eventResults', []))}")
        print(f"  Team Rank: {comp.get('results', {}).get('teamRank', 'N/A')}")
        print()
    
    # Check for any issues (excluding upcoming competitions)
    issues = []
    now = datetime.now()
    for comp in competitions:
        if not comp.get('name'):
            issues.append(f"Competition missing name: {comp}")
        if not comp.get('date'):
            issues.append(f"Competition missing date: {comp.get('name', 'Unknown')}")
        # Check if competition is upcoming (date in future)
        comp_date_str = comp.get('date')
        is_upcoming = False
        if comp_date_str:
            try:
                comp_date = datetime.fromisoformat(comp_date_str.replace('Z', '+00:00'))
                is_upcoming = comp_date > now
            except:
                pass
        # Only flag missing team placement for past competitions
        if not comp.get('teamPlacement') and not is_upcoming:
            issues.append(f"Past competition missing team placement: {comp.get('name', 'Unknown')}")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("OK - No issues found!")
    
    # Test JSON serialization
    print("\nTesting JSON serialization...")
    try:
        json_str = json.dumps(competitions, indent=2, default=str)
        print("OK - JSON serialization successful")
        print(f"  JSON length: {len(json_str)} characters")
    except Exception as e:
        print(f"ERROR - JSON serialization failed: {e}")
    
    print("\n" + "=" * 70)
    print("Test complete!")

if __name__ == "__main__":
    test_parser()

