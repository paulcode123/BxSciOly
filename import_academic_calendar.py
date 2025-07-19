#!/usr/bin/env python3
"""
Script to import academic calendar events from the screenshot
All events from September 2025 to May 2026
"""

import requests
import json
from datetime import datetime, timedelta
import time

# API base URL
API_BASE = "http://localhost:8000/api"

def determine_event_type(title, description):
    """Determine event type based on title and description"""
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    
    # Holiday keywords
    if any(word in title_lower for word in ['holiday', 'closed', 'recess', 'rosh hashanah', 'yom kippur', 'diwali', 'eid', 'mlk', 'memorial day', 'veterans day', 'election day', 'indigenous people']):
        return 'holiday'
    
    # Competition keywords
    if any(word in title_lower for word in ['competition', 'invitational', 'regional', 'state', 'national', 'nysso']):
        return 'competition'
    
    # Deadline keywords
    if any(word in title_lower for word in ['deadline', 'due', 'submit', 'application', 'registration']):
        return 'deadline'
    
    # Exam keywords
    if any(word in title_lower for word in ['ap exam', 'exam', 'test']):
        return 'deadline'
    
    # School event keywords
    if any(word in title_lower for word in ['first day', 'rules day', 'schedule']):
        return 'meeting'
    
    # Default to meeting
    return 'meeting'

def create_multi_day_event(title, description, start_date, end_date, location, event_type):
    """Create multiple events for multi-day periods"""
    events = []
    current_date = start_date
    
    while current_date <= end_date:
        # Skip weekends for multi-day events (optional)
        if current_date.weekday() < 5:  # Monday to Friday
            events.append({
                'title': title,
                'description': description,
                'date': current_date.isoformat(),
                'location': location,
                'eventType': event_type,
                'isActive': True,
                'createdAt': datetime.now().isoformat()
            })
        current_date += timedelta(days=1)
    
    return events

def import_academic_calendar():
    """Import all academic calendar events"""
    
    # All events from the screenshot with corrected dates
    events_data = [
        # September 2025
        {
            'title': 'NYSSO Team Registration OPENS!',
            'description': 'Registration opens for NYSSO team members',
            'date': '2025-09-01',
            'location': 'Online',
            'eventType': 'deadline'
        },
        {
            'title': 'RULES DAY!',
            'description': 'Science Olympiad rules and guidelines discussion',
            'date': '2025-09-02',
            'location': 'Bronx Science',
            'eventType': 'meeting'
        },
        {
            'title': 'FIRST DAY OF SCHOOL!',
            'description': 'First day of the 2025-2026 academic year',
            'date': '2025-09-03',
            'location': 'Bronx Science',
            'eventType': 'meeting'
        },
        {
            'title': 'NYSSO State Schedule Released',
            'description': 'New York State Science Olympiad competition schedule released',
            'date': '2025-09-15',
            'location': 'Online',
            'eventType': 'deadline'
        },
        {
            'title': 'Rosh Hashanah',
            'description': 'Jewish New Year - School Closed',
            'date': '2025-09-23',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Rosh Hashanah',
            'description': 'Jewish New Year - School Closed',
            'date': '2025-09-24',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # October 2025
        {
            'title': 'Yom Kippur',
            'description': 'Day of Atonement - School Closed',
            'date': '2025-10-02',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Indigenous People\'s Day',
            'description': 'Indigenous People\'s Day - School Closed',
            'date': '2025-10-13',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Diwali',
            'description': 'Festival of Lights - School Closed',
            'date': '2025-10-20',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # November 2025
        {
            'title': 'Election Day',
            'description': 'Election Day - School Closed',
            'date': '2025-11-04',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Veterans Day',
            'description': 'Veterans Day - School Closed',
            'date': '2025-11-11',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Thanksgiving Recess',
            'description': 'Thanksgiving Break - School Closed',
            'date': '2025-11-27',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Thanksgiving Recess',
            'description': 'Thanksgiving Break - School Closed',
            'date': '2025-11-28',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # December 2025
        {
            'title': 'December Recess',
            'description': 'December Break - School Closed',
            'date': '2025-12-24',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'December Recess',
            'description': 'December Break - School Closed',
            'date': '2025-12-25',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'December Recess',
            'description': 'December Break - School Closed',
            'date': '2025-12-26',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'December Recess',
            'description': 'December Break - School Closed',
            'date': '2025-12-29',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'December Recess',
            'description': 'December Break - School Closed',
            'date': '2025-12-30',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'December Recess',
            'description': 'December Break - School Closed',
            'date': '2025-12-31',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # January 2026
        {
            'title': 'MLK Jr Day',
            'description': 'Martin Luther King Jr. Day - School Closed',
            'date': '2026-01-19',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # February 2026
        {
            'title': 'Midwinter Recess',
            'description': 'Midwinter Break - School Closed',
            'date': '2026-02-16',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Midwinter Recess',
            'description': 'Midwinter Break - School Closed',
            'date': '2026-02-17',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Midwinter Recess',
            'description': 'Midwinter Break - School Closed',
            'date': '2026-02-18',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Midwinter Recess',
            'description': 'Midwinter Break - School Closed',
            'date': '2026-02-19',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Midwinter Recess',
            'description': 'Midwinter Break - School Closed',
            'date': '2026-02-20',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # March 2026
        {
            'title': 'Eid al-Fitr',
            'description': 'End of Ramadan - School Closed',
            'date': '2026-03-20',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # April 2026
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-02',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-03',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-04',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-07',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-08',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-09',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Spring Recess',
            'description': 'Spring Break - School Closed',
            'date': '2026-04-10',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        
        # May 2026
        {
            'title': 'AP Exams Week 1',
            'description': 'Advanced Placement Exams - Week 1',
            'date': '2026-05-04',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 1',
            'description': 'Advanced Placement Exams - Week 1',
            'date': '2026-05-05',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 1',
            'description': 'Advanced Placement Exams - Week 1',
            'date': '2026-05-06',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 1',
            'description': 'Advanced Placement Exams - Week 1',
            'date': '2026-05-07',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 1',
            'description': 'Advanced Placement Exams - Week 1',
            'date': '2026-05-08',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 2',
            'description': 'Advanced Placement Exams - Week 2',
            'date': '2026-05-11',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 2',
            'description': 'Advanced Placement Exams - Week 2',
            'date': '2026-05-12',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 2',
            'description': 'Advanced Placement Exams - Week 2',
            'date': '2026-05-13',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 2',
            'description': 'Advanced Placement Exams - Week 2',
            'date': '2026-05-14',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'AP Exams Week 2',
            'description': 'Advanced Placement Exams - Week 2',
            'date': '2026-05-15',
            'location': 'Bronx Science',
            'eventType': 'deadline'
        },
        {
            'title': 'Memorial Day',
            'description': 'Memorial Day - School Closed',
            'date': '2026-05-25',
            'location': 'School Closed',
            'eventType': 'holiday'
        },
        {
            'title': 'Eid al-Adha',
            'description': 'Feast of Sacrifice - School Closed',
            'date': '2026-05-27',
            'location': 'School Closed',
            'eventType': 'holiday'
        }
    ]
    
    events_imported = 0
    events_skipped = 0
    
    print("📅 Importing Academic Calendar Events")
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
    print(f"📊 Importing {len(events_data)} events...")
    print()
    
    for event in events_data:
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

if __name__ == "__main__":
    import_academic_calendar() 