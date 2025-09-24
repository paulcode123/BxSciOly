#!/usr/bin/env python3
"""
Script to export member first name, last name, and IDs to CSV
"""

import firebase_admin
from firebase_admin import credentials, firestore
import csv
from datetime import datetime
import os
import hashlib

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

def convert_id_to_5_digit(firebase_id):
    """Convert Firebase ID to a deterministic 5-digit number"""
    # Use SHA-256 hash of the Firebase ID to ensure deterministic conversion
    hash_object = hashlib.sha256(firebase_id.encode())
    hex_dig = hash_object.hexdigest()
    
    # Take the first 8 characters of the hash and convert to integer
    # Then mod by 100000 to get a 5-digit number (00000-99999)
    hash_int = int(hex_dig[:8], 16)
    five_digit = hash_int % 100000
    
    # Ensure it's always 5 digits with leading zeros if needed
    return f"{five_digit:05d}"

def export_member_names_ids():
    """
    Export member first name, last name, Firebase ID, and bxscioly_5digit_number to a CSV file.
    """
    
    print("🔍 Exporting Bronx Science Olympiad Member Names and IDs")
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
        
        # Define CSV headers
        headers = ['firstName', 'lastName', 'id', 'bxscioly_number']
        
        # Prepare data for CSV
        csv_data = []
        
        for member in members:
            member_data = member.to_dict()
            member_id = member.id
            
            # Convert Firebase ID to 5-digit number
            five_digit_number = convert_id_to_5_digit(member_id)
            bxscioly_number = f"bxscioly_{five_digit_number}"
            
            # Extract required fields
            csv_data.append({
                'firstName': member_data.get('firstName', ''),
                'lastName': member_data.get('lastName', ''),
                'id': member_id,
                'bxscioly_number': bxscioly_number
            })
        
        # Sort by last name, then first name
        csv_data.sort(key=lambda x: (x['lastName'], x['firstName']))
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"member_names_ids_{timestamp}.csv"
        
        # Write to CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ Successfully exported {len(members)} members to {filename}")
        print(f"📁 File saved as: {os.path.abspath(filename)}")
        
        # Print summary
        print("\n📊 Export Summary:")
        print(f"   • Total members: {len(members)}")
        print(f"   • File format: CSV with columns: firstName, lastName, id, bxscioly_number")
        print(f"   • Data sorted by: last name, then first name")
        print(f"   • 5-digit numbers generated deterministically from Firebase IDs")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting member names and IDs: {str(e)}")
        return None

if __name__ == "__main__":
    export_member_names_ids()
