#!/usr/bin/env python3
"""
Script to download all Competition Applications from Firebase as CSV
Includes member names and competition names by joining with Members and Competitions collections
"""

import firebase_admin
from firebase_admin import credentials, firestore
import csv
import os
from datetime import datetime
import json

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

def convert_timestamp(timestamp):
    """Convert Firestore timestamp to string"""
    if timestamp:
        if hasattr(timestamp, 'isoformat'):
            return timestamp.isoformat()
        elif hasattr(timestamp, 'timestamp'):
            # Firestore Timestamp object
            return timestamp.to_datetime().isoformat()
        elif isinstance(timestamp, str):
            return timestamp
    return ""

def download_competition_applications_csv():
    """Download all competition applications from Firebase and save as CSV"""
    
    print("Downloading Bronx Science Olympiad Competition Applications")
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
        
        
        # Define CSV headers - simplified to only requested fields
        headers = [
            'name',
            'email',
            'event_rankings',
            'why_compete',
            'preparation_plan',
            'question_3',
            'fee_waiver_request'
        ]
        
        # Prepare data for CSV
        csv_data = []
        
        for app in applications:
            app_data = app.to_dict()
            app_id = app.id
            
            # Get member information
            user_id = app_data.get('userId', '')
            member_info = members.get(user_id, {})
            member_name = f"{member_info.get('firstName', '')} {member_info.get('lastName', '')}".strip()
            member_email = member_info.get('doeEmail', '') or member_info.get('personalEmail', '')
            
            # Process event rankings - format as ordered list
            event_rankings = app_data.get('eventRankings', [])
            if event_rankings:
                # Sort by rank and extract event names
                sorted_rankings = sorted(event_rankings, key=lambda x: x.get('rank', 999))
                rankings_list = [r.get('eventName', '') for r in sorted_rankings if r.get('eventName')]
                rankings_str = ', '.join(rankings_list)
            else:
                # Fallback to events list if no rankings
                events = app_data.get('events', [])
                rankings_str = ', '.join(events) if isinstance(events, list) else str(events)
            
            # Process questions
            questions = app_data.get('questions', {})
            why_compete = questions.get('whyCompete', '')
            preparation_plan = questions.get('preparationPlan', '')
            first_time_prep = questions.get('firstTimePrep', '')
            past_influence = questions.get('pastInfluence', '')
            
            # Combine question 3 - use whichever one is filled out
            question_3 = first_time_prep or past_influence
            
            # Fee waiver request
            fee_waiver_request = 'Yes' if app_data.get('feeWaiverRequest', False) else 'No'
            
            # Create row with only requested fields
            row = {
                'name': member_name,
                'email': member_email,
                'event_rankings': rankings_str,
                'why_compete': why_compete,
                'preparation_plan': preparation_plan,
                'question_3': question_3,
                'fee_waiver_request': fee_waiver_request
            }
            
            csv_data.append(row)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"competition_applications_export_{timestamp}.csv"
        
        # Write to CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"\nSuccessfully exported {len(applications)} applications to {filename}")
        print(f"File saved as: {os.path.abspath(filename)}")
        
        # Print summary statistics
        print("\nExport Summary:")
        print(f"   - Total applications: {len(applications)}")
        
        # Count fee waiver requests
        fee_waiver_count = sum(1 for row in csv_data if row['fee_waiver_request'] == 'Yes')
        print(f"   - Fee waiver requests: {fee_waiver_count}")
        
        return filename
        
    except Exception as e:
        print(f"Error downloading applications: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    download_competition_applications_csv()

