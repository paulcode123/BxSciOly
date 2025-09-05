#!/usr/bin/env python3
"""
Script to delete all past Science Olympiad competitions that were just added
"""
import requests
import time

# API base URL
API_BASE = "http://localhost:8000/api"

# Names of competitions that were added (both old and new formats)
COMPETITION_NAMES_TO_DELETE = [
    # New standardized format names
    "RICKARDS SATELLITE INVITATIONAL 2024-25",
    "YALE INVITATIONAL 2023-24",
    "NEW YORK STATE CHAMPIONSHIP 2023-24",
    "SEALS OLYMPIAD 2024-25",
    "LEXINGTON SATELLITE INVITATIONAL 2024-25",
    "NYC NORTH REGIONAL 2024-25",
    "NYC NORTH REGIONAL 2023-24",
    "NEW YORK STATE CHAMPIONSHIP 2024-25",
    "BIRDSO SATELLITE INVITATIONAL 2023-24",
    "BOYCEVILLE SATELLITE INVITATIONAL 2023-24",
    "RICKARDS SATELLITE INVITATIONAL 2023-24",
    
    # Old format names (in case any remain)
    "'24-'25 Rickards Satellite Invitational",
    "'23-'24 Yale Invitational",
    "'23-'24 States",
    "SealSO '24-'25",
    "Lexington '24-'25 Satellite Invitational",
    "Regionals '24-'25:",
    "Regionals '23-'24:",
    "'24-'25 States",
    "'23-'24 BirdSO Satellite Invitational",
    "Boyceville '23-'24 Satellite Invitational",
    "Rickards '23-'24 Satellite Invitational",
    
    # Any other variations
    "Rickards Satellite Invitational '24-'25",
    "Yale Invitational '23-'24",
    "States '23-'24",
    "States '24-'25",
    "BirdSO Satellite Invitational '23-'24",
    "Boyceville Satellite Invitational '23-'24",
    "Rickards Satellite Invitational '23-'24"
]

def delete_all_past_competitions():
    """Delete all past competitions by fetching all and filtering by name"""
    print("🎯 Comprehensive Past Science Olympiad Competitions Deletion Script")
    print("🗑️  Fetching all competitions...")
    
    try:
        # Get all competitions
        response = requests.get(f"{API_BASE}/Competitions")
        if response.status_code != 200:
            print(f"❌ Failed to fetch competitions: {response.status_code}")
            return
            
        competitions = response.json()
        print(f"📊 Found {len(competitions)} total competitions in database")
        
        deleted_count = 0
        
        # Delete competitions that match our criteria
        for comp in competitions:
            comp_name = comp.get('name', '')
            comp_id = comp.get('id', '')
            
            # Check if this competition should be deleted
            should_delete = False
            
            # Check exact name matches
            if comp_name in COMPETITION_NAMES_TO_DELETE:
                should_delete = True
            
            # Check if it contains keywords that indicate it's a past competition we added
            past_keywords = [
                "SATELLITE INVITATIONAL",
                "STATE CHAMPIONSHIP", 
                "REGIONAL",
                "OLYMPIAD",
                "2023-24",
                "2024-25",
                "'23-'24",
                "'24-'25"
            ]
            
            if any(keyword in comp_name.upper() for keyword in past_keywords):
                should_delete = True
            
            if should_delete:
                try:
                    delete_response = requests.delete(f"{API_BASE}/Competitions/{comp_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted: {comp_name}")
                        deleted_count += 1
                    else:
                        print(f"   ❌ Failed to delete {comp_name}: {delete_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error deleting {comp_name}: {e}")
                
                # Small delay between deletions
                time.sleep(0.1)
        
        print(f"✨ Deleted {deleted_count} past competitions!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    delete_all_past_competitions()
    print("======================================================================")
    print("🎉 Deletion completed!")
    print()
    print("🌐 You can now re-run the population script to create clean competition data!")

if __name__ == "__main__":
    main()







