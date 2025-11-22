import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Try to import from existing initialization
        from db_init import db
        return db
    except ImportError:
        # If import fails, initialize Firebase here
        if not firebase_admin._apps:
            cred = credentials.Certificate('service_key.json')
            firebase_admin.initialize_app(cred)
        return firestore.client()

def get_house_distribution_by_event():
    """
    Get the number of people in each house for each event.
    """
    
    print("Analyzing House Distribution by Event")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all events
        events_ref = db.collection('Events')
        events = list(events_ref.stream())
        
        if not events:
            print("No events found in the database.")
            return
        
        print(f"Found {len(events)} events in the database\n")
        
        # Store house distribution per event
        event_house_counts = defaultdict(lambda: {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'No House': 0})
        
        # Track processed members to avoid duplicate fetches
        member_cache = {}
        
        print("Processing events and members...\n")
        
        for event in events:
            event_data = event.to_dict()
            event_name = event_data.get('eventName', 'Unknown Event')
            member_ids = event_data.get('members', [])
            
            print(f"Processing event: {event_name} ({len(member_ids)} members)")
            
            # Process each member in this event
            for member_id in member_ids:
                # Check if we already have this member's data
                if member_id in member_cache:
                    house = member_cache[member_id]
                else:
                    # Fetch member data from database
                    member_ref = db.collection('Members').document(member_id)
                    member_doc = member_ref.get()
                    
                    if member_doc.exists:
                        member_data = member_doc.to_dict()
                        house = member_data.get('house', 'No House')
                        member_cache[member_id] = house
                    else:
                        print(f"  Warning: Member {member_id} not found in database")
                        house = 'No House'
                        member_cache[member_id] = house
                
                # Count house membership
                if house in ['A', 'B', 'C', 'D']:
                    event_house_counts[event_name][house] += 1
                else:
                    event_house_counts[event_name]['No House'] += 1
        
        # Display results
        print("\n" + "=" * 60)
        print("HOUSE DISTRIBUTION BY EVENT")
        print("=" * 60 + "\n")
        
        # Sort events alphabetically
        sorted_events = sorted(event_house_counts.items())
        
        for event_name, counts in sorted_events:
            total = sum(counts.values())
            print(f"{event_name} (Total: {total})")
            print(f"   House A: {counts['A']}")
            print(f"   House B: {counts['B']}")
            print(f"   House C: {counts['C']}")
            print(f"   House D: {counts['D']}")
            if counts['No House'] > 0:
                print(f"   No House: {counts['No House']}")
            print()
        
        # Summary statistics
        print("=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        
        total_by_house = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'No House': 0}
        for counts in event_house_counts.values():
            for house in total_by_house:
                total_by_house[house] += counts[house]
        
        print("\nTotal members across all events:")
        for house in ['A', 'B', 'C', 'D']:
            print(f"   House {house}: {total_by_house[house]}")
        if total_by_house['No House'] > 0:
            print(f"   No House: {total_by_house['No House']}")
        
        print(f"\nTotal events: {len(event_house_counts)}")
        print(f"Total unique members processed: {len(member_cache)}")
        
        return event_house_counts
        
    except Exception as e:
        print(f"Error analyzing house distribution: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    get_house_distribution_by_event()

