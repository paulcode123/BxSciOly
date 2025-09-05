#!/usr/bin/env python3
"""
Script to delete the competitions that were just created by the populate script
"""
import requests
import time

# API base URL
API_BASE = "http://localhost:8000/api"

# Names of competitions that were created by our script
CREATED_COMPETITION_NAMES = [
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
    "RICKARDS SATELLITE INVITATIONAL 2023-24"
]

def delete_created_competitions():
    """Delete the competitions that were created by our populate script"""
    print("🎯 Deleting Created Past Science Olympiad Competitions")
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
        
        # Iterate through competitions list
        for comp_item in competitions:
            # Each item is a dict with one key (the doc ID) and the competition data
            for doc_id, comp_data in comp_item.items():
                comp_name = comp_data.get('name', '')
                
                # Check if this is one of our created competitions
                if comp_name in CREATED_COMPETITION_NAMES:
                    try:
                        delete_response = requests.delete(f"{API_BASE}/Competitions/{doc_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✅ Deleted: {comp_name} (ID: {doc_id})")
                            deleted_count += 1
                        else:
                            print(f"   ❌ Failed to delete {comp_name}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Error deleting {comp_name}: {e}")
                    
                    # Small delay between deletions
                    time.sleep(0.1)
        
        print(f"✨ Deleted {deleted_count} created competitions!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    delete_created_competitions()
    print("======================================================================")
    print("🎉 Deletion completed!")
    print()
    print("🌐 Database is now clean and ready for fresh competition data!")

if __name__ == "__main__":
    main()
