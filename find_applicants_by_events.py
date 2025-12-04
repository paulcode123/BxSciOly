#!/usr/bin/env python3
"""
Script to find all applicants who can do 3/4 or 4/4 of the events:
Astronomy, Dynamic Planet, Remote Sensing, Rocks and Minerals
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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

def find_applicants_by_events():
    """Find applicants who can do 3/4 or 4/4 of the target events"""
    
    # Target events
    target_events = ['Astronomy', 'Dynamic Planet', 'Remote Sensing', 'Rocks and Minerals']
    
    print("Finding applicants who can do 3/4 or 4/4 of:")
    print("  - Astronomy")
    print("  - Dynamic Planet")
    print("  - Remote Sensing")
    print("  - Rocks and Minerals")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all applications from the database
        applications_ref = db.collection('Applications')
        applications = list(applications_ref.stream())
        
        if not applications:
            print("No applications found in the database.")
            return
        
        print(f"Found {len(applications)} applications in the database")
        
        # Get all members for name lookup
        print("Loading member data...")
        members_ref = db.collection('Members')
        members = {doc.id: doc.to_dict() for doc in members_ref.stream()}
        print(f"   Found {len(members)} members")
        
        # Get all competitions for name lookup
        print("Loading competition data...")
        competitions_ref = db.collection('Competitions')
        competitions = {doc.id: doc.to_dict() for doc in competitions_ref.stream()}
        print(f"   Found {len(competitions)} competitions")
        
        # Process applications
        matching_applicants = []
        
        for app in applications:
            app_data = app.to_dict()
            user_id = app_data.get('userId', '')
            
            # Get events from application
            # Check both 'events' array and 'eventRankings' array
            events = []
            if 'events' in app_data and app_data['events']:
                events = app_data['events']
            elif 'eventRankings' in app_data and app_data['eventRankings']:
                # Extract event names from eventRankings
                events = [r.get('eventName', '') for r in app_data['eventRankings'] if r.get('eventName')]
            
            if not events:
                continue
            
            # Count how many target events are in this application's events
            # Use case-insensitive comparison to handle variations
            matching_count = 0
            matched_events = []
            
            for target_event in target_events:
                # Check for exact match (case-insensitive)
                if any(target_event.lower() == event.lower() for event in events):
                    matching_count += 1
                    matched_events.append(target_event)
            
            # If applicant has 3 or 4 of the target events, add them
            if matching_count >= 3:
                # Get member information
                member_info = members.get(user_id, {})
                member_name = f"{member_info.get('firstName', '')} {member_info.get('lastName', '')}".strip()
                member_email = member_info.get('doeEmail', '') or member_info.get('personalEmail', '')
                member_grade = member_info.get('grade', '')
                
                # Get competition information
                competition_id = app_data.get('competitionId', '')
                competition_info = competitions.get(competition_id, {})
                competition_name = competition_info.get('name', 'Unknown Competition')
                
                matching_applicants.append({
                    'name': member_name,
                    'email': member_email,
                    'grade': member_grade,
                    'userId': user_id,
                    'applicationId': app.id,
                    'competition': competition_name,
                    'matching_count': matching_count,
                    'matched_events': matched_events,
                    'all_events': events
                })
        
        # Sort by matching count (4/4 first, then 3/4), then by name
        matching_applicants.sort(key=lambda x: (-x['matching_count'], x['name']))
        
        # Print results
        print(f"\n{'='*60}")
        print(f"Found {len(matching_applicants)} applicants matching criteria:")
        print(f"{'='*60}\n")
        
        # Group by matching count
        four_four = [a for a in matching_applicants if a['matching_count'] == 4]
        three_four = [a for a in matching_applicants if a['matching_count'] == 3]
        
        if four_four:
            print(f"4/4 Events ({len(four_four)} applicants):")
            print("-" * 60)
            for applicant in four_four:
                print(f"  • {applicant['name']} ({applicant['grade']})")
                print(f"    Email: {applicant['email']}")
                print(f"    Competition: {applicant['competition']}")
                print(f"    Matched Events: {', '.join(applicant['matched_events'])}")
                print(f"    All Events: {', '.join(applicant['all_events'])}")
                print()
        
        if three_four:
            print(f"\n3/4 Events ({len(three_four)} applicants):")
            print("-" * 60)
            for applicant in three_four:
                print(f"  • {applicant['name']} ({applicant['grade']})")
                print(f"    Email: {applicant['email']}")
                print(f"    Competition: {applicant['competition']}")
                print(f"    Matched Events: {', '.join(applicant['matched_events'])}")
                print(f"    All Events: {', '.join(applicant['all_events'])}")
                print()
        
        # Summary
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"  Total matching applicants: {len(matching_applicants)}")
        print(f"  4/4 events: {len(four_four)}")
        print(f"  3/4 events: {len(three_four)}")
        print(f"{'='*60}")
        
        return matching_applicants
        
    except Exception as e:
        print(f"Error finding applicants: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    find_applicants_by_events()

