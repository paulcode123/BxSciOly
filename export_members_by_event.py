import firebase_admin
from firebase_admin import credentials, firestore
import csv
from datetime import datetime
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

def export_members_by_event():
    """
    Export member information organized by event to a CSV file.
    Each row contains: eventName, firstName, lastName, doeEmail, personalEmail, grade
    Members in multiple events will appear in multiple rows.
    """
    
    print("🔍 Exporting Bronx Science Olympiad Members by Event")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all events
        events_ref = db.collection('Events')
        events = list(events_ref.stream())
        
        if not events:
            print("❌ No events found in the database.")
            return
        
        print(f"📊 Found {len(events)} events in the database")
        
        # Prepare data for CSV
        csv_data = []
        
        # Track processed members to avoid duplicate fetches
        member_cache = {}
        
        print("Processing events and members...")
        
        for event in events:
            event_data = event.to_dict()
            event_name = event_data.get('eventName', 'Unknown Event')
            member_ids = event_data.get('members', [])
            
            print(f"Processing event: {event_name} with {len(member_ids)} members")
            
            # Process each member in this event
            for member_id in member_ids:
                # Check if we already have this member's data
                if member_id in member_cache:
                    member_data = member_cache[member_id]
                else:
                    # Fetch member data from database
                    member_ref = db.collection('Members').document(member_id)
                    member_doc = member_ref.get()
                    
                    if member_doc.exists:
                        member_data = member_doc.to_dict()
                        member_cache[member_id] = member_data
                    else:
                        print(f"⚠️  Warning: Member {member_id} not found in database")
                        continue
                
                # Extract required fields
                csv_data.append({
                    'eventName': event_name,
                    'firstName': member_data.get('firstName', ''),
                    'lastName': member_data.get('lastName', ''),
                    'doeEmail': member_data.get('doeEmail', ''),
                    'personalEmail': member_data.get('personalEmail', ''),
                    'grade': member_data.get('grade', '')
                })
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"members_by_event_{timestamp}.csv"
        
        # Write to CSV file
        if csv_data:
            fieldnames = ['eventName', 'firstName', 'lastName', 'doeEmail', 'personalEmail', 'grade']
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"\n✅ Export completed successfully!")
            print(f"📁 File saved as: {os.path.abspath(filename)}")
            print(f"📊 Total records: {len(csv_data)}")
            print(f"👥 Unique members: {len(member_cache)}")
            print(f"🎯 Unique events: {len(set(row['eventName'] for row in csv_data))}")
            
            # Show summary by event
            event_counts = {}
            for row in csv_data:
                event = row['eventName']
                event_counts[event] = event_counts.get(event, 0) + 1
            
            print("\n📋 Members per event:")
            for event, count in sorted(event_counts.items()):
                print(f"   • {event}: {count} members")
                
        else:
            print("❌ No data found to export.")
            
    except Exception as e:
        print(f"❌ Error exporting members by event: {str(e)}")
        return None

if __name__ == "__main__":
    export_members_by_event() 