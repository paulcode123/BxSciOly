#!/usr/bin/env python3
"""
Script to populate the Competitions collection with Science Olympiad invitational competitions
This script creates competition documents for all invitational competitions listed in the planning document
"""

import requests
import json
import time
from datetime import datetime, timedelta

# API base URL - adjust if needed
API_BASE = "http://localhost:8000/api"

# Competition data from the invitational competitions table
COMPETITIONS_DATA = [
    {
        "name": "Rickards Invitational",
        "date": "2025-11-01",  # November 1-8, 2025 (using start date)
        "type": "satellite",
        "location": "Satellite",
        "description": "Rickards High School Science Olympiad Invitational - A satellite competition offering teams the opportunity to compete remotely.",
        "registrationOpens": "2025-09-15",
        "registrationDeadline": "2025-10-15",
        "teamsRelease": "2025-10-25",
        "numTeams": 60
    },
    {
        "name": "Cornell Invitational",
        "date": "2025-11-15",
        "type": "invitational",
        "location": "NY",
        "description": "Cornell University Science Olympiad Invitational - A prestigious competition hosted by Cornell University in New York.",
        "registrationOpens": "2025-09-01",
        "registrationDeadline": "2025-10-01",
        "teamsRelease": "2025-11-01",
        "numTeams": 80
    },
    {
        "name": "Mason Invitational",
        "date": "2025-11-15",  # November 15-23, 2025 (using start date)
        "type": "satellite",
        "location": "Satellite",
        "description": "Mason High School Science Olympiad Invitational - A satellite competition providing flexible participation options.",
        "registrationOpens": "2025-09-15",
        "registrationDeadline": "2025-10-15",
        "teamsRelease": "2025-11-01",
        "numTeams": 50
    },
    {
        "name": "Boyceville Invitational",
        "date": "2025-12-06",
        "type": "satellite",
        "location": "Satellite",
        "description": "Boyceville High School Science Olympiad Invitational - A satellite competition offering teams early-season competition experience.",
        "registrationOpens": "2025-10-01",
        "registrationDeadline": "2025-11-01",
        "teamsRelease": "2025-11-20",
        "numTeams": 40
    },
    {
        "name": "MIT Invitational",
        "date": "2026-01-24",
        "type": "invitational",
        "location": "MA",
        "description": "Massachusetts Institute of Technology Science Olympiad Invitational - One of the most prestigious invitational competitions, hosted by MIT.",
        "registrationOpens": "2025-10-01",
        "registrationDeadline": "2025-11-15",
        "teamsRelease": "2025-12-15",
        "numTeams": 100
    },
    {
        "name": "Columbia Invitational",
        "date": "2026-01-24",
        "type": "invitational",
        "location": "NY",
        "description": "Columbia University Science Olympiad Invitational - A competitive invitational hosted by Columbia University in New York.",
        "registrationOpens": "2025-10-01",
        "registrationDeadline": "2025-11-15",
        "teamsRelease": "2025-12-15",
        "numTeams": 70
    },
    {
        "name": "Harvard Invitational",
        "date": "2026-02-01",  # February 1-2, 2026 (using start date)
        "type": "invitational",
        "location": "MA",
        "description": "Harvard University Science Olympiad Invitational - A prestigious two-day competition hosted by Harvard University.",
        "registrationOpens": "2025-10-15",
        "registrationDeadline": "2025-12-01",
        "teamsRelease": "2026-01-01",
        "numTeams": 90
    },
    {
        "name": "Yale Invitational",
        "date": "2026-02-08",
        "type": "invitational",
        "location": "CT",
        "description": "Yale University Science Olympiad Invitational - A competitive invitational hosted by Yale University in Connecticut.",
        "registrationOpens": "2025-10-15",
        "registrationDeadline": "2025-12-01",
        "teamsRelease": "2026-01-15",
        "numTeams": 75
    },
    {
        "name": "Brown Invitational",
        "date": "2026-02-14",
        "type": "invitational",
        "location": "RI",
        "description": "Brown University Science Olympiad Invitational - A competitive invitational hosted by Brown University in Rhode Island.",
        "registrationOpens": "2025-10-15",
        "registrationDeadline": "2025-12-01",
        "teamsRelease": "2026-01-15",
        "numTeams": 65
    },
    {
        "name": "UPenn Invitational",
        "date": "2026-02-14",
        "type": "invitational",
        "location": "PA",
        "description": "University of Pennsylvania Science Olympiad Invitational - A competitive invitational hosted by UPenn in Pennsylvania.",
        "registrationOpens": "2025-10-15",
        "registrationDeadline": "2025-12-01",
        "teamsRelease": "2026-01-15",
        "numTeams": 70
    },
    {
        "name": "Dartmouth Invitational",
        "date": "2026-02-15",  # February 2026 (using approximate date)
        "type": "invitational",
        "location": "NH",
        "description": "Dartmouth College Science Olympiad Invitational - A competitive invitational hosted by Dartmouth College in New Hampshire.",
        "registrationOpens": "2025-10-15",
        "registrationDeadline": "2025-12-01",
        "teamsRelease": "2026-01-15",
        "numTeams": 60
    },
    {
        "name": "Princeton Invitational",
        "date": "2026-05-17",
        "type": "invitational",
        "location": "NJ",
        "description": "Princeton University Science Olympiad Invitational - A late-season invitational hosted by Princeton University in New Jersey.",
        "registrationOpens": "2026-01-01",
        "registrationDeadline": "2026-03-01",
        "teamsRelease": "2026-04-01",
        "numTeams": 80
    }
]

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

def create_competition_document(competition_data):
    """Create a complete competition document with all required fields"""
    # Convert date strings to timestamps
    date_obj = datetime.strptime(competition_data["date"], "%Y-%m-%d")
    registration_opens_obj = datetime.strptime(competition_data["registrationOpens"], "%Y-%m-%d")
    registration_deadline_obj = datetime.strptime(competition_data["registrationDeadline"], "%Y-%m-%d")
    teams_release_obj = datetime.strptime(competition_data["teamsRelease"], "%Y-%m-%d")
    
    return {
        "name": competition_data["name"],
        "date": date_obj.isoformat(),
        "type": competition_data["type"],
        "location": competition_data["location"],
        "description": competition_data["description"],
        "registrationOpens": registration_opens_obj.isoformat(),
        "registrationDeadline": registration_deadline_obj.isoformat(),
        "teamsRelease": teams_release_obj.isoformat(),
        "numTeams": competition_data["numTeams"]
        # Note: teamPlacement, results, and duosmium are optional and will be added post-competition
    }

def create_competitions():
    """Create all Science Olympiad competitions"""
    print("🚀 Creating Science Olympiad competitions...")
    
    total_competitions = len(COMPETITIONS_DATA)
    created_competitions = 0
    
    for competition_data in COMPETITIONS_DATA:
        try:
            # Create complete competition document
            competition_document = create_competition_document(competition_data)
            
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
    print("🎯 Science Olympiad Competitions Collection Population Script")
    print("=" * 70)
    
    # Step 1: Clean up existing competitions
    delete_all_competitions()
    
    # Step 2: Create new competitions
    create_competitions()
    
    print("=" * 70)
    print("🎉 Script completed!")
    print()
    print("📋 Summary:")
    print(f"   • Created {len(COMPETITIONS_DATA)} competitions")
    
    # Count competitions by type
    competition_types = {}
    for comp in COMPETITIONS_DATA:
        comp_type = comp["type"]
        competition_types[comp_type] = competition_types.get(comp_type, 0) + 1
    
    print("   • Competition types:")
    for comp_type, count in competition_types.items():
        print(f"     - {comp_type.capitalize()}: {count} competitions")
    
    print()
    print("🎨 Features included:")
    print("   • Complete competition information with descriptions")
    print("   • Competition types (invitational, satellite)")
    print("   • Location information")
    print("   • Registration timeline (opens, deadline, teams release)")
    print("   • Team capacity information")
    print("   • ISO format timestamps for all dates")
    print("   • Empty optional fields for post-competition data")
    print()
    print("📅 Competition timeline:")
    print("   • Earliest: Rickards Invitational (Nov 1-8, 2025)")
    print("   • Latest: Princeton Invitational (May 17, 2026)")
    print()
    print("🌐 Navigate to the Competitions page to see all the created competitions!")

if __name__ == "__main__":
    main() 