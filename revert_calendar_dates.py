#!/usr/bin/env python3
"""
Script to revert all events starting from August 2025 back by 1 day
(Reverse the previous update)
"""

import requests
import json
from datetime import datetime, timedelta
import re

# API base URL
API_BASE = "http://localhost:8000/api"

def parse_date_flexible(date_str):
    """Parse date string in various formats"""
    if not date_str:
        return None
    
    # Try different date formats
    formats = [
        "%Y-%m-%d",  # 2025-09-01
        "%a, %d %b %Y %H:%M:%S GMT",  # Thu, 05 Jun 2025 00:00:00 GMT
        "%Y-%m-%d %H:%M:%S",  # 2025-09-01 00:00:00
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def revert_calendar_dates():
    """Revert all events from August 2025 onwards back by 1 day"""
    
    print("🔄 Reverting calendar dates...")
    print("=" * 60)
    
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
        reverted_count = 0
        skipped_count = 0
        
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
                    skipped_count += 1
                    continue
                
                # Parse date with flexible format
                event_date = parse_date_flexible(event_date_str)
                if not event_date:
                    print(f"⚠️ Could not parse date for: {event_data.get('title', 'Unknown')} - {event_date_str}")
                    skipped_count += 1
                    continue
                
                # Check if event is on or after August 1, 2025
                if event_date >= cutoff_date:
                    # Subtract 1 day from the event (revert the previous change)
                    original_date = event_date - timedelta(days=1)
                    original_date_str = original_date.strftime("%Y-%m-%d")
                    
                    # Update the event data
                    updated_event_data = event_data.copy()
                    updated_event_data['date'] = original_date_str
                    
                    # Send PUT request to update the event
                    update_response = requests.put(
                        f"{API_BASE}/CalendarEvents/{event_id}",
                        json=updated_event_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if update_response.status_code == 200:
                        print(f"✅ Reverted: {event_data.get('title', 'Unknown')} - {event_date_str} → {original_date_str}")
                        reverted_count += 1
                    else:
                        print(f"❌ Failed to revert: {event_data.get('title', 'Unknown')} - {update_response.status_code}")
                        skipped_count += 1
                else:
                    print(f"⏭️ Skipped (before Aug 2025): {event_data.get('title', 'Unknown')} - {event_date_str}")
                    skipped_count += 1
                        
            except Exception as e:
                print(f"⚠️ Error processing event {event_data.get('title', 'Unknown')}: {str(e)}")
                skipped_count += 1
                continue
        
        print("=" * 60)
        print(f"🎉 Successfully reverted {reverted_count} events!")
        print(f"⏭️ Skipped {skipped_count} events (before Aug 2025 or errors)")
        print(f"📅 All events from August 1, 2025 onwards have been reverted to their original dates")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    revert_calendar_dates() 