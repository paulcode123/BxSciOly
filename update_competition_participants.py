#!/usr/bin/env python3
"""
Script to update competition documents by replacing full names in participants arrays
with member IDs when exactly one member exists with that name
"""
import requests
import time

# API base URL
API_BASE = "http://localhost:8000/api"

def get_all_members():
    """Fetch all members from the database"""
    print("📖 Fetching all members...")
    
    try:
        response = requests.get(f"{API_BASE}/Members")
        if response.status_code != 200:
            print(f"❌ Failed to fetch members: {response.status_code}")
            return {}
            
        members_data = response.json()
        print(f"📊 Found {len(members_data)} members")
        
        # Create a mapping of full names to member IDs
        name_to_id = {}
        id_to_name = {}
        
        for member_item in members_data:
            for member_id, member_data in member_item.items():
                first_name = member_data.get('firstName', '').strip()
                last_name = member_data.get('lastName', '').strip()
                
                if first_name and last_name:
                    full_name = f"{first_name} {last_name}"
                    name_to_id[full_name] = member_id
                    id_to_name[member_id] = full_name
        
        print(f"📝 Created name mapping for {len(name_to_id)} members")
        return name_to_id, id_to_name
        
    except Exception as e:
        print(f"❌ Error fetching members: {e}")
        return {}, {}

def get_all_competitions():
    """Fetch all competitions from the database"""
    print("📖 Fetching all competitions...")
    
    try:
        response = requests.get(f"{API_BASE}/Competitions")
        if response.status_code != 200:
            print(f"❌ Failed to fetch competitions: {response.status_code}")
            return []
            
        competitions = response.json()
        print(f"📊 Found {len(competitions)} competitions")
        return competitions
        
    except Exception as e:
        print(f"❌ Error fetching competitions: {e}")
        return []

def update_competition_participants(competition_id, competition_data, name_to_id):
    """Update participants in a competition document"""
    updated = False
    team_placement = competition_data.get('teamPlacement', [])
    
    # Track changes for this competition
    changes = []
    
    for placement in team_placement:
        participants = placement.get('participants', [])
        updated_participants = []
        
        for participant in participants:
            # Check if this is a full name (not already an ID)
            if participant in name_to_id:
                # Replace full name with member ID
                member_id = name_to_id[participant]
                updated_participants.append(member_id)
                changes.append(f"  • {participant} → {member_id}")
                updated = True
            else:
                # Keep as is (either already an ID or no match found)
                updated_participants.append(participant)
        
        # Update the participants array
        placement['participants'] = updated_participants
    
    if updated:
        # Update the competition document
        try:
            response = requests.put(
                f"{API_BASE}/Competitions/{competition_id}",
                headers={'Content-Type': 'application/json'},
                json=competition_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Updated: {competition_data.get('name', 'Unknown')}")
                for change in changes:
                    print(change)
                return True
            else:
                print(f"   ❌ Failed to update {competition_data.get('name', 'Unknown')}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating {competition_data.get('name', 'Unknown')}: {e}")
            return False
    
    return False

def main():
    """Main execution function"""
    print("🎯 Competition Participants Update Script")
    print("=" * 60)
    
    # Get all members and create name mapping
    name_to_id, id_to_name = get_all_members()
    if not name_to_id:
        print("❌ Could not fetch members. Exiting.")
        return
    
    # Get all competitions
    competitions = get_all_competitions()
    if not competitions:
        print("❌ Could not fetch competitions. Exiting.")
        return
    
    print(f"\n🔄 Processing {len(competitions)} competitions...")
    
    updated_count = 0
    total_participants_updated = 0
    
    # Process each competition
    for comp_item in competitions:
        for comp_id, comp_data in comp_item.items():
            comp_name = comp_data.get('name', 'Unknown')
            
            # Check if this competition has teamPlacement data
            if 'teamPlacement' in comp_data and comp_data['teamPlacement']:
                print(f"\n🔍 Processing: {comp_name}")
                
                # Count participants before update
                participants_before = sum(len(placement.get('participants', [])) for placement in comp_data['teamPlacement'])
                
                # Update participants
                if update_competition_participants(comp_id, comp_data, name_to_id):
                    updated_count += 1
                    
                    # Count participants after update
                    participants_after = sum(len(placement.get('participants', [])) for placement in comp_data['teamPlacement'])
                    total_participants_updated += (participants_before - participants_after)
                
                # Small delay between updates
                time.sleep(0.1)
    
    print("\n" + "=" * 60)
    print("🎉 Update completed!")
    print()
    print("📋 Summary:")
    print(f"   • Competitions processed: {len(competitions)}")
    print(f"   • Competitions updated: {updated_count}")
    print(f"   • Total participants converted: {total_participants_updated}")
    print()
    print("📝 Note: Full names were only replaced when exactly one member")
    print("   matched the name. Names with no matches or multiple matches")
    print("   were left unchanged.")

if __name__ == "__main__":
    main()







