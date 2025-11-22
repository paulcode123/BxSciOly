"""
Script to create the WIDI event in the Events collection.
WIDI is scheduled for Thursday Block 1 and belongs to Chemistry & Inquiry subject.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def create_widi_event():
    """Create the WIDI event in Firebase"""
    
    event_data = {
        'eventName': 'WIDI',
        'description': 'Write It Do It - A chemistry and inquiry event where participants write descriptions of objects and then recreate them.',
        'subject': 'chemistry',
        'icon': 'fas fa-flask',
        'generalInfo': {
            'welcome': 'Welcome to WIDI!',
            'about': 'Write It Do It is an event where one team member writes a description of an object, and another team member uses that description to recreate the object.',
            'contentOverview': 'This event focuses on clear communication, spatial reasoning, and attention to detail.',
            'tips': 'Practice writing clear, concise descriptions. Pay attention to details like color, size, position, and orientation.',
            'resources': []
        },
        'meetingDay': 'Thursday',
        'meetingBlock': 1,
        'meetingRoom': 101,  # Default room, can be updated later
        'members': [],
        'eventManagers': [],
        'subjectDirectors': []
    }
    
    # Check if event already exists
    existing_query = db.collection('Events').where('eventName', '==', 'WIDI').limit(1).stream()
    existing_events = list(existing_query)
    
    if existing_events:
        # Update existing event
        doc_id = existing_events[0].id
        db.collection('Events').document(doc_id).update({
            'meetingDay': 'Thursday',
            'meetingBlock': 1,
            'subject': 'chemistry',
            'description': event_data['description']
        })
        print(f"Updated existing event: WIDI")
        print(f"  - Meeting Day: Thursday")
        print(f"  - Meeting Block: 1")
        print(f"  - Subject: chemistry")
    else:
        # Create new event
        doc_ref = db.collection('Events').document()
        doc_ref.set(event_data)
        print(f"Created new event: WIDI")
        print(f"  - Event ID: {doc_ref.id}")
        print(f"  - Meeting Day: Thursday")
        print(f"  - Meeting Block: 1")
        print(f"  - Subject: chemistry")
    
    print("\nWIDI event is now configured!")
    print("The event will automatically generate attendance codes on Thursdays when you click 'Generate Today's Codes' in the admin portal.")

if __name__ == '__main__':
    try:
        create_widi_event()
        print("\nSuccessfully created/updated WIDI event!")
    except Exception as e:
        print(f"\nError creating event: {e}")
        import traceback
        traceback.print_exc()


