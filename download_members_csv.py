#!/usr/bin/env python3
"""
Script to download the entire Members collection from Firebase as CSV
with hashed passwords for security (doesn't modify the database)
"""

import firebase_admin
from firebase_admin import credentials, firestore
import csv
import hashlib
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

def hash_password(password):
    """Hash a password using SHA-256"""
    if not password:
        return ""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def convert_timestamp(timestamp):
    """Convert Firestore timestamp to string"""
    if timestamp:
        if hasattr(timestamp, 'isoformat'):
            return timestamp.isoformat()
        elif isinstance(timestamp, str):
            return timestamp
    return ""

def download_members_csv():
    """Download all members from Firebase and save as CSV with hashed passwords"""
    
    print("🔍 Downloading Bronx Science Olympiad Members Collection")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all members from the database
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        if not members:
            print("❌ No members found in the database.")
            return
        
        print(f"📊 Found {len(members)} members in the database")
        
        # Define CSV headers based on the database schema
        headers = [
            'id',
            'firstName',
            'lastName', 
            'doeEmail',
            'personalEmail',
            'phoneNumber',
            'grade',
            'password_hashed',  # Hashed version of password
            'memberStatus',
            'createdAt',
            'bio',
            'interestReason',
            'howDidYouHearAboutUs',
            'pastExperience',
            'returnReason',
            'yearsInTeam',
            'preseasonHrs',
            'regseasonHrs',
            'postseasonHrs',
            'profilePicUrl',
            'importantNotification',
            'teamNotification',
            'eventNotification',
            'adminStatus',
            'status',
            'agreementAccepted',
            'agreementAcceptedAt',
            'contractAccepted',
            'contractAcceptedAt'
        ]
        
        # Prepare data for CSV
        csv_data = []
        
        for member in members:
            member_data = member.to_dict()
            member_data['id'] = member.id
            
            # Hash the password
            original_password = member_data.get('password', '')
            member_data['password_hashed'] = hash_password(original_password)
            
            # Remove the original password from the data
            member_data.pop('password', None)
            
            # Convert timestamps to strings
            for timestamp_field in ['createdAt', 'agreementAcceptedAt', 'contractAcceptedAt']:
                if timestamp_field in member_data:
                    member_data[timestamp_field] = convert_timestamp(member_data[timestamp_field])
            
            # Handle arrays (like events) - convert to JSON string
            if 'events' in member_data and isinstance(member_data['events'], list):
                member_data['events'] = json.dumps(member_data['events'])
            
            # Ensure all fields exist in the row
            row = {}
            for header in headers:
                row[header] = member_data.get(header, '')
            
            csv_data.append(row)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"members_export_{timestamp}.csv"
        
        # Write to CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ Successfully exported {len(members)} members to {filename}")
        print(f"📁 File saved as: {os.path.abspath(filename)}")
        
        # Print summary statistics
        print("\n📊 Export Summary:")
        print(f"   • Total members: {len(members)}")
        
        # Count by member status
        new_members = sum(1 for row in csv_data if row['memberStatus'] == 'new')
        returning_members = sum(1 for row in csv_data if row['memberStatus'] == 'returning')
        print(f"   • New members: {new_members}")
        print(f"   • Returning members: {returning_members}")
        
        # Count by grade
        grade_counts = {}
        for row in csv_data:
            grade = row['grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        print("   • Grade distribution:")
        for grade in sorted(grade_counts.keys()):
            print(f"     - Grade {grade}: {grade_counts[grade]}")
        
        # Count by admin status
        admin_counts = {}
        for row in csv_data:
            admin_status = row['adminStatus']
            admin_counts[admin_status] = admin_counts.get(admin_status, 0) + 1
        
        print("   • Admin status distribution:")
        for status in sorted(admin_counts.keys()):
            print(f"     - {status}: {admin_counts[status]}")
        
        print(f"\n🔒 Security Note: All passwords have been hashed using SHA-256")
        print(f"   Original passwords remain unchanged in the database")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error downloading members: {str(e)}")
        return None

if __name__ == "__main__":
    download_members_csv() 