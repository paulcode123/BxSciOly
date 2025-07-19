#!/usr/bin/env python3
"""
Script to import calendar data from CSV into the CalendarEvents collection
"""

import csv
import requests
import json
from datetime import datetime
import time

# API base URL
API_BASE = "http://localhost:8000/api"

def parse_date(date_str):
    """Parse various date formats from Excel/CSV"""
    if not date_str or date_str.strip() == '':
        return None
    
    # Common Excel date formats
    date_formats = [
        '%m/%d/%Y',    # 12/25/2024
        '%m/%d/%y',    # 12/25/24
        '%Y-%m-%d',    # 2024-12-25
        '%d/%m/%Y',    # 25/12/2024
        '%B %d, %Y',   # December 25, 2024
        '%b %d, %Y',   # Dec 25, 2024
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    print(f"Warning: Could not parse date '{date_str}'")
    return None

def determine_event_type(title, description):
    """Determine event type based on title and description"""
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    
    # Competition keywords
    if any(word in title_lower for word in ['competition', 'invitational', 'regional', 'state', 'national']):
        return 'competition'
    
    # Meeting keywords
    if any(word in title_lower for word in ['meeting', 'practice', 'session']):
        return 'meeting'
    
    # Workshop keywords
    if any(word in title_lower for word in ['workshop', 'training', 'lesson']):
        return 'workshop'
    
    # Deadline keywords
    if any(word in title_lower for word in ['deadline', 'due', 'submit', 'application']):
        return 'deadline'
    
    # Practice keywords
    if any(word in title_lower for word in ['practice', 'rehearsal', 'prep']):
        return 'practice'
    
    # Default to meeting if no clear type
    return 'meeting'

def import_calendar_data(csv_file_path):
    """Import calendar data from CSV file"""
    
    events_imported = 0
    events_skipped = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Extract data from CSV row
                # Adjust these field names based on your CSV structure
                title = row.get('Title', row.get('Event', row.get('Name', '')))
                description = row.get('Description', row.get('Details', ''))
                date_str = row.get('Date', row.get('Event Date', ''))
                location = row.get('Location', row.get('Venue', ''))
                
                # Skip if no title or date
                if not title or not date_str:
                    print(f"Skipping row with missing title or date: {row}")
                    events_skipped += 1
                    continue
                
                # Parse date
                event_date = parse_date(date_str)
                if not event_date:
                    print(f"Skipping row with invalid date '{date_str}': {row}")
                    events_skipped += 1
                    continue
                
                # Determine event type
                event_type = determine_event_type(title, description)
                
                # Create event data
                event_data = {
                    'title': title.strip(),
                    'description': description.strip() if description else '',
                    'date': event_date.isoformat(),
                    'location': location.strip() if location else '',
                    'eventType': event_type,
                    'isActive': True,
                    'createdAt': datetime.now().isoformat()
                }
                
                # Send to API
                try:
                    response = requests.post(
                        f"{API_BASE}/CalendarEvents",
                        json=event_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 201:
                        print(f"✅ Imported: {title} ({event_date.strftime('%m/%d/%Y')})")
                        events_imported += 1
                    else:
                        print(f"❌ Failed to import {title}: {response.status_code} - {response.text}")
                        events_skipped += 1
                    
                    # Small delay to avoid overwhelming the server
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"❌ Error importing {title}: {str(e)}")
                    events_skipped += 1
    
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file_path}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        return
    
    print(f"\n📊 Import Summary:")
    print(f"✅ Events imported: {events_imported}")
    print(f"❌ Events skipped: {events_skipped}")
    print(f"📅 Total processed: {events_imported + events_skipped}")

if __name__ == "__main__":
    # Update this path to match your CSV file location
    csv_file_path = "calendar_data.csv"
    
    print("📅 Science Olympiad Calendar Data Import")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/Events")
        if response.status_code != 200:
            print("❌ Server not responding properly. Make sure Flask app is running on localhost:8000")
            exit(1)
    except:
        print("❌ Cannot connect to server. Make sure Flask app is running on localhost:8000")
        exit(1)
    
    print("✅ Server connection confirmed")
    print(f"📁 Looking for CSV file: {csv_file_path}")
    
    import_calendar_data(csv_file_path) 