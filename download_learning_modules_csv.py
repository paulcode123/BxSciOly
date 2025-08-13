#!/usr/bin/env python3
"""
Script to download the entire LearningModules collection from Firebase as CSV
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
        elif isinstance(timestamp, str):
            return timestamp
    return ""

def download_learning_modules_csv():
    """Download all learning modules from Firebase and save as CSV"""
    
    print("🔍 Downloading Bronx Science Olympiad LearningModules Collection")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all learning modules from the database
        modules_ref = db.collection('LearningModules')
        modules = list(modules_ref.stream())
        
        if not modules:
            print("❌ No learning modules found in the database.")
            return
        
        print(f"📊 Found {len(modules)} learning modules in the database")
        
        # Define CSV headers based on the database schema
        headers = [
            'id',
            'eventName',
            'title',
            'duration',
            'unit',
            'order',
            'points',
            'prerequisites',
            'content_overview',
            'content_objectives',
            'content_resources',
            'validationType',
            'problems',
            'systemPrompt',
            'createdAt'
        ]
        
        # Prepare data for CSV
        csv_data = []
        
        for module in modules:
            module_data = module.to_dict()
            module_data['id'] = module.id
            
            # Convert timestamps to strings
            if 'createdAt' in module_data:
                module_data['createdAt'] = convert_timestamp(module_data['createdAt'])
            
            # Handle arrays - convert to JSON string
            for array_field in ['prerequisites', 'problems']:
                if array_field in module_data and isinstance(module_data[array_field], list):
                    module_data[array_field] = json.dumps(module_data[array_field])
            
            # Handle content object - extract specific fields
            if 'content' in module_data and isinstance(module_data['content'], dict):
                content = module_data['content']
                module_data['content_overview'] = content.get('overview', '')
                module_data['content_objectives'] = json.dumps(content.get('objectives', []))
                module_data['content_resources'] = json.dumps(content.get('resources', []))
            
            # Remove the original content object
            module_data.pop('content', None)
            
            # Ensure all fields exist in the row
            row = {}
            for header in headers:
                row[header] = module_data.get(header, '')
            
            csv_data.append(row)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"learning_modules_export_{timestamp}.csv"
        
        # Write to CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ Successfully exported {len(modules)} learning modules to {filename}")
        print(f"📁 File saved as: {os.path.abspath(filename)}")
        
        # Print summary statistics
        print("\n📊 Export Summary:")
        print(f"   • Total learning modules: {len(modules)}")
        
        # Count by event
        event_counts = {}
        for row in csv_data:
            event = row['eventName']
            event_counts[event] = event_counts.get(event, 0) + 1
        
        print("   • Event distribution:")
        for event in sorted(event_counts.keys()):
            print(f"     - {event}: {event_counts[event]}")
        
        # Count by validation type
        validation_counts = {}
        for row in csv_data:
            validation_type = row['validationType']
            validation_counts[validation_type] = validation_counts.get(validation_type, 0) + 1
        
        print("   • Validation type distribution:")
        for validation_type in sorted(validation_counts.keys()):
            print(f"     - {validation_type}: {validation_counts[validation_type]}")
        
        # Count by unit
        unit_counts = {}
        for row in csv_data:
            unit = row['unit']
            unit_counts[unit] = unit_counts.get(unit, 0) + 1
        
        print("   • Unit distribution:")
        for unit in sorted(unit_counts.keys()):
            print(f"     - {unit}: {unit_counts[unit]}")
        
        # Calculate total points
        total_points = sum(int(row['points']) for row in csv_data if str(row['points']).isdigit())
        print(f"   • Total points available: {total_points}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error downloading learning modules: {str(e)}")
        return None

if __name__ == "__main__":
    download_learning_modules_csv()
