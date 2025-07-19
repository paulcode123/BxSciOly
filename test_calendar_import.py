#!/usr/bin/env python3
"""
Test script to verify calendar import functionality
"""

import requests
import json
from datetime import datetime

# API base URL
API_BASE = "http://localhost:8000/api"

def test_calendar_api():
    """Test the calendar API endpoints"""
    
    print("🧪 Testing Calendar API Endpoints")
    print("=" * 40)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{API_BASE}/Events")
        print(f"✅ Server connection: {response.status_code}")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Test 2: Test CalendarEvents endpoint
    try:
        response = requests.get(f"{API_BASE}/CalendarEvents")
        print(f"✅ CalendarEvents GET: {response.status_code}")
        if response.status_code == 200:
            events = response.json()
            print(f"   📅 Found {len(events)} existing calendar events")
    except Exception as e:
        print(f"❌ CalendarEvents GET failed: {e}")
    
    # Test 3: Test creating a sample event
    test_event = {
        'title': 'Test Event',
        'description': 'This is a test event for import verification',
        'date': datetime.now().isoformat(),
        'location': 'Test Location',
        'eventType': 'meeting',
        'isActive': True,
        'createdAt': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/CalendarEvents",
            json=test_event,
            headers={'Content-Type': 'application/json'}
        )
        print(f"✅ CalendarEvents POST: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Test event created successfully")
            
            # Clean up: delete the test event
            event_id = response.json().get('id')
            if event_id:
                delete_response = requests.delete(f"{API_BASE}/CalendarEvents/{event_id}")
                if delete_response.status_code == 200:
                    print("   🧹 Test event cleaned up")
        else:
            print(f"   ❌ Failed to create test event: {response.text}")
    except Exception as e:
        print(f"❌ CalendarEvents POST failed: {e}")
    
    print("\n📋 Next Steps:")
    print("1. Export your Excel file as CSV")
    print("2. Save it as 'calendar_data.csv' in this directory")
    print("3. Run: python import_calendar_data.py")
    print("4. Check the calendar at: http://localhost:8000/calendar")

if __name__ == "__main__":
    test_calendar_api() 