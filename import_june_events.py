#!/usr/bin/env python3
"""
Script to import June 2026 calendar events from the screenshot
"""

import requests
import json
from datetime import datetime
import time

# API base URL
API_BASE = "http://localhost:8000/api"

def import_june_events():
    """Import June 2026 calendar events"""
    
    # June 2026 events from the screenshot
    june_events = [
        {
            'title': 'Anniversary Day/Staff Development Day',
            'description': 'Staff Development Day - School Closed',
            'date': '2026-06-04',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Juneteenth',
            'description': 'Juneteenth National Independence Day - School Closed',
            'date': '2026-06-19',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'LAST DAY OF SCHOOL!',
            'description': 'Final day of the 2025-2026 academic year',
            'date': '2026-06-26',
            'location': 'Bronx Science',
            'eventType': 'meeting'
        }
    ]
    
    events_imported = 0
    events_skipped = 0
    
    print("📅 Importing June 2026 Calendar Events")
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
    print(f"📊 Importing {len(june_events)} June events...")
    print()
    
    for event in june_events:
        try:
            response = requests.post(
                f"{API_BASE}/CalendarEvents",
                json=event,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                print(f"✅ Imported: {event['title']} ({event['date']})")
                events_imported += 1
            else:
                print(f"❌ Failed to import {event['title']}: {response.status_code} - {response.text}")
                events_skipped += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error importing {event['title']}: {str(e)}")
            events_skipped += 1
    
    print(f"\n📊 Import Summary:")
    print(f"✅ Events imported: {events_imported}")
    print(f"❌ Events skipped: {events_skipped}")
    print(f"📅 Total processed: {events_imported + events_skipped}")
    print(f"\n🎉 Check your calendar at: http://localhost:8000/calendar")
    print(f"📅 Your complete academic year now spans: September 2025 - June 2026")

if __name__ == "__main__":
    import_june_events() 