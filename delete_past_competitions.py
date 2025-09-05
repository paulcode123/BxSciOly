#!/usr/bin/env python3
"""
Script to delete past Science Olympiad competitions that were just added
"""

import requests
import time

# API base URL
API_BASE = "http://localhost:8000/api"

# Names of competitions that were added
PAST_COMPETITION_NAMES = [
    "Rickards Satellite Invitational '24-'25",
    "Yale Invitational '23-'24",
    "States '23-'24",
    "SealSO '24-'25",
    "Lexington Satellite Invitational '24-'25",
    "Regionals '24-'25",
    "Regionals '23-'24",
    "States '24-'25",
    "BirdSO Satellite Invitational '23-'24",
    "Boyceville Satellite Invitational '23-'24",
    "Rickards Satellite Invitational '23-'24"
]

def delete_past_competitions():
    """Delete the past competitions that were just added"""
    print("🗑️  Deleting past competitions...")
    
    try:
        response = requests.get(f"{API_BASE}/Competitions")
        if response.status_code == 200:
            competitions = response.json()
            deleted_count = 0
            
            for competition_data in competitions:
                if isinstance(competition_data, dict):
                    # Handle Firebase format
                    competition_id = list(competition_data.keys())[0]
                    competition_info = competition_data[competition_id]
                else:
                    competition_id = competition_data.get('id')
                    competition_info = competition_data
                
                # Check if this is one of the past competitions we added
                if competition_info.get('name') in PAST_COMPETITION_NAMES:
                    delete_response = requests.delete(f"{API_BASE}/Competitions/{competition_id}")
                    if delete_response.status_code == 200:
                        deleted_count += 1
                        print(f"   ✅ Deleted: {competition_info.get('name')}")
                    else:
                        print(f"   ❌ Failed to delete: {competition_info.get('name')}")
                    time.sleep(0.1)  # Small delay
            
            print(f"✨ Deleted {deleted_count} past competitions!")
        else:
            print(f"❌ Failed to fetch competitions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during deletion: {e}")

def main():
    """Main execution function"""
    print("🎯 Past Science Olympiad Competitions Deletion Script")
    print("=" * 70)
    
    delete_past_competitions()
    
    print("=" * 70)
    print("🎉 Deletion completed!")

if __name__ == "__main__":
    main()
