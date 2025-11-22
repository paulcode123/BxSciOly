"""
Script to add members to the WIDI event.
Finds members by name and adds their IDs to the WIDI event's members array.
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# List of members to add (first name, last name)
members_to_add = [
    ('Karis', 'Lau'),
    ('Adeline', 'Nurenie'),
    ('Jerry', 'Zhu'),
    ('Vincent', 'Lin'),
    ('Ian', 'Kim'),
    ('Linwang', 'Li'),
    ('Maliha', 'Noreen'),
    ('Chase', 'Li')
]

def find_member_by_name(first_name, last_name):
    """Find a member by first and last name"""
    # Try exact match first
    members = db.collection('Members').where('firstName', '==', first_name).where('lastName', '==', last_name).limit(1).stream()
    results = list(members)
    
    if results:
        return results[0]
    
    # Try case-insensitive search with trimmed names (handles spaces)
    all_members = db.collection('Members').stream()
    for member in all_members:
        member_data = member.to_dict()
        member_first = member_data.get('firstName', '').strip().lower()
        member_last = member_data.get('lastName', '').strip().lower()
        if (member_first == first_name.strip().lower() and 
            member_last == last_name.strip().lower()):
            return member
    
    return None

def find_member_by_email(email):
    """Find a member by email address"""
    # Try doeEmail first
    members = db.collection('Members').where('doeEmail', '==', email).limit(1).stream()
    results = list(members)
    if results:
        return results[0]
    
    # Try personalEmail
    members = db.collection('Members').where('personalEmail', '==', email).limit(1).stream()
    results = list(members)
    if results:
        return results[0]
    
    return None

def add_members_to_widi():
    """Add members to the WIDI event"""
    
    # Find the WIDI event
    events_query = db.collection('Events').where('eventName', '==', 'WIDI').limit(1).stream()
    events = list(events_query)
    
    if not events:
        print("Error: WIDI event not found!")
        return
    
    widi_event = events[0]
    widi_event_id = widi_event.id
    widi_data = widi_event.to_dict()
    
    # Get current members
    current_members = widi_data.get('members', [])
    print(f"Current WIDI members: {len(current_members)}")
    
    # Find and add each member
    found_members = []
    not_found = []
    
    # Special handling for Chase Li - try email lookup
    chase_email = 'chasel49@nycstudents.net'
    
    for first_name, last_name in members_to_add:
        member_doc = find_member_by_name(first_name, last_name)
        
        # If not found and it's Chase Li, try email lookup
        if not member_doc and first_name == 'Chase' and last_name == 'Li':
            member_doc = find_member_by_email(chase_email)
        
        if member_doc:
            member_id = member_doc.id
            member_data = member_doc.to_dict()
            
            if member_id not in current_members:
                current_members.append(member_id)
                found_members.append(f"{first_name} {last_name} (ID: {member_id[:8]}...)")
                print(f"[+] Found and added: {first_name} {last_name} ({member_data.get('doeEmail', 'no email')})")
            else:
                found_members.append(f"{first_name} {last_name} (already in event)")
                print(f"[*] Already in event: {first_name} {last_name}")
        else:
            not_found.append(f"{first_name} {last_name}")
            print(f"[-] Not found: {first_name} {last_name}")
    
    # Update the event with new members list
    if found_members or not_found:
        db.collection('Events').document(widi_event_id).update({
            'members': current_members
        })
        print(f"\n[+] Updated WIDI event with {len(current_members)} total members")
    
    # Summary
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    print(f"Total members in WIDI event: {len(current_members)}")
    print(f"\nSuccessfully added/found: {len(found_members)}")
    for member in found_members:
        print(f"  - {member}")
    
    if not_found:
        print(f"\nNot found in database: {len(not_found)}")
        for member in not_found:
            print(f"  - {member}")
    print("="*60)

if __name__ == '__main__':
    try:
        add_members_to_widi()
        print("\nSuccessfully updated WIDI event members!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

