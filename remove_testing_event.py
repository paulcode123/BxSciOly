#!/usr/bin/env python3
"""
Script to remove the Testing345 event from the calendar
"""

import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api"

def remove_testing_event():
    """Find and remove the Testing345 event"""
    
    print("🔍 Searching for Testing345 event...")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/Events")
        if response.status_code != 200:
            print("❌ Server not responding properly. Make sure Flask app is running on localhost:8000")
            return
    except:
        print("❌ Cannot connect to server. Make sure Flask app is running on localhost:8000")
        return
    
    print("✅ Server connection confirmed")
    
    # Get all calendar events
    try:
        response = requests.get(f"{API_BASE}/CalendarEvents")
        if response.status_code != 200:
            print("❌ Failed to fetch calendar events")
            return
        
        events = response.json()
        print(f"📊 Found {len(events)} total calendar events")
        
        # Find the Testing345 event
        testing_event = None
        for event in events:
            if isinstance(event, dict):
                # Firebase returns {id: data} format
                event_id = list(event.keys())[0]
                event_data = event[event_id]
            else:
                event_data = event
                event_id = event.get('id')
            
            if event_data.get('title') == 'Testing345':
                testing_event = {'id': event_id, 'data': event_data}
                break
        
        if testing_event:
            event_id = testing_event['id']
            print(f"✅ Found Testing345 event with ID: {event_id}")
            
            # Delete the event
            delete_response = requests.delete(f"{API_BASE}/CalendarEvents/{event_id}")
            
            if delete_response.status_code == 200:
                print(f"✅ Successfully removed Testing345 event")
            else:
                print(f"❌ Failed to remove event: {delete_response.status_code} - {delete_response.text}")
        else:
            print("ℹ️ Testing345 event not found in calendar")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    remove_testing_event() 