#!/usr/bin/env python3
"""
Script to push all events starting from August 2025 forward by 1 day
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
API_BASE = "http://localhost:8000/api"

def update_calendar_dates():
    """Push all events from August 2025 onwards forward by 1 day"""
    
    print("📅 Updating calendar dates...")
    print("=" * 50)
    
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
        
        # August 1, 2025 as the cutoff date
        cutoff_date = datetime(2025, 8, 1)
        updated_count = 0
        
        for event in events:
            if isinstance(event, dict):
                # Firebase returns {id: data} format
                event_id = list(event.keys())[0]
                event_data = event[event_id]
            else:
                event_data = event
                event_id = event.get('id')
            
            # Parse the event date
            try:
                event_date_str = event_data.get('date')
                if not event_date_str:
                    continue
                
                # Parse date (assuming format like "2025-09-01")
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                
                # Check if event is on or after August 1, 2025
                if event_date >= cutoff_date:
                    # Add 1 day to the event
                    new_date = event_date + timedelta(days=1)
                    new_date_str = new_date.strftime("%Y-%m-%d")
                    
                    # Update the event data
                    updated_event_data = event_data.copy()
                    updated_event_data['date'] = new_date_str
                    
                    # Send PUT request to update the event
                    update_response = requests.put(
                        f"{API_BASE}/CalendarEvents/{event_id}",
                        json=updated_event_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if update_response.status_code == 200:
                        print(f"✅ Updated: {event_data.get('title', 'Unknown')} - {event_date_str} → {new_date_str}")
                        updated_count += 1
                    else:
                        print(f"❌ Failed to update: {event_data.get('title', 'Unknown')} - {update_response.status_code}")
                        
            except Exception as e:
                print(f"⚠️ Error processing event {event_data.get('title', 'Unknown')}: {str(e)}")
                continue
        
        print("=" * 50)
        print(f"🎉 Successfully updated {updated_count} events!")
        print(f"📅 All events from August 1, 2025 onwards have been pushed forward by 1 day")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_calendar_dates() 