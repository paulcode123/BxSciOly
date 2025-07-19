#!/usr/bin/env python3
"""
Script to populate the Meeting collection with sample Science Olympiad meeting data
This script creates meeting documents for various events and dates
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# API base URL - adjust if needed
API_BASE = "http://localhost:8000/api"

# Sample meeting data organized by event categories
MEETINGS_DATA = {
    # Build Events
    "Helicopter": {
        "eventName": "Helicopter",
        "meetings": [
            {
                "date": "2024-01-15",
                "block": 1,
                "room": "101",
                "attended": []  # Will be populated with member IDs
            },
            {
                "date": "2024-01-22",
                "block": 1,
                "room": "101",
                "attended": []
            },
            {
                "date": "2024-01-29",
                "block": 1,
                "room": "101",
                "attended": []
            }
        ]
    },
    "Boomilever": {
        "eventName": "Boomilever",
        "meetings": [
            {
                "date": "2024-01-15",
                "block": 2,
                "room": "102",
                "attended": []
            },
            {
                "date": "2024-01-22",
                "block": 2,
                "room": "102",
                "attended": []
            },
            {
                "date": "2024-01-29",
                "block": 2,
                "room": "102",
                "attended": []
            }
        ]
    },
    "Bungee Drop": {
        "eventName": "Bungee Drop",
        "meetings": [
            {
                "date": "2024-01-16",
                "block": 1,
                "room": "103",
                "attended": []
            },
            {
                "date": "2024-01-23",
                "block": 1,
                "room": "103",
                "attended": []
            },
            {
                "date": "2024-01-30",
                "block": 1,
                "room": "103",
                "attended": []
            }
        ]
    },
    "Hovercraft": {
        "eventName": "Hovercraft",
        "meetings": [
            {
                "date": "2024-01-16",
                "block": 2,
                "room": "104",
                "attended": []
            },
            {
                "date": "2024-01-23",
                "block": 2,
                "room": "104",
                "attended": []
            },
            {
                "date": "2024-01-30",
                "block": 2,
                "room": "104",
                "attended": []
            }
        ]
    },
    "Electric Vehicle": {
        "eventName": "Electric Vehicle",
        "meetings": [
            {
                "date": "2024-01-17",
                "block": 1,
                "room": "105",
                "attended": []
            },
            {
                "date": "2024-01-24",
                "block": 1,
                "room": "105",
                "attended": []
            },
            {
                "date": "2024-01-31",
                "block": 1,
                "room": "105",
                "attended": []
            }
        ]
    },
    "Robot Tour": {
        "eventName": "Robot Tour",
        "meetings": [
            {
                "date": "2024-01-17",
                "block": 2,
                "room": "106",
                "attended": []
            },
            {
                "date": "2024-01-24",
                "block": 2,
                "room": "106",
                "attended": []
            },
            {
                "date": "2024-01-31",
                "block": 2,
                "room": "106",
                "attended": []
            }
        ]
    },
    
    # Academic Events
    "Engineering CAD": {
        "eventName": "Engineering CAD",
        "meetings": [
            {
                "date": "2024-01-18",
                "block": 1,
                "room": "201",
                "attended": []
            },
            {
                "date": "2024-01-25",
                "block": 1,
                "room": "201",
                "attended": []
            },
            {
                "date": "2024-02-01",
                "block": 1,
                "room": "201",
                "attended": []
            }
        ]
    },
    "Machines": {
        "eventName": "Machines",
        "meetings": [
            {
                "date": "2024-01-18",
                "block": 2,
                "room": "202",
                "attended": []
            },
            {
                "date": "2024-01-25",
                "block": 2,
                "room": "202",
                "attended": []
            },
            {
                "date": "2024-02-01",
                "block": 2,
                "room": "202",
                "attended": []
            }
        ]
    },
    "Circuit Lab": {
        "eventName": "Circuit Lab",
        "meetings": [
            {
                "date": "2024-01-19",
                "block": 1,
                "room": "203",
                "attended": []
            },
            {
                "date": "2024-01-26",
                "block": 1,
                "room": "203",
                "attended": []
            },
            {
                "date": "2024-02-02",
                "block": 1,
                "room": "203",
                "attended": []
            }
        ]
    },
    "Water Quality": {
        "eventName": "Water Quality",
        "meetings": [
            {
                "date": "2024-01-15",
                "block": 1,
                "room": "204",
                "attended": []
            },
            {
                "date": "2024-01-22",
                "block": 1,
                "room": "204",
                "attended": []
            },
            {
                "date": "2024-01-29",
                "block": 1,
                "room": "204",
                "attended": []
            }
        ]
    },
    "Dynamic Planet": {
        "eventName": "Dynamic Planet",
        "meetings": [
            {
                "date": "2024-01-15",
                "block": 2,
                "room": "205",
                "attended": []
            },
            {
                "date": "2024-01-22",
                "block": 2,
                "room": "205",
                "attended": []
            },
            {
                "date": "2024-01-29",
                "block": 2,
                "room": "205",
                "attended": []
            }
        ]
    },
    "Remote Sensing": {
        "eventName": "Remote Sensing",
        "meetings": [
            {
                "date": "2024-01-16",
                "block": 1,
                "room": "206",
                "attended": []
            },
            {
                "date": "2024-01-23",
                "block": 1,
                "room": "206",
                "attended": []
            },
            {
                "date": "2024-01-30",
                "block": 1,
                "room": "206",
                "attended": []
            }
        ]
    },
    "Rocks and Minerals": {
        "eventName": "Rocks and Minerals",
        "meetings": [
            {
                "date": "2024-01-16",
                "block": 2,
                "room": "207",
                "attended": []
            },
            {
                "date": "2024-01-23",
                "block": 2,
                "room": "207",
                "attended": []
            },
            {
                "date": "2024-01-30",
                "block": 2,
                "room": "207",
                "attended": []
            }
        ]
    },
    "Entomology": {
        "eventName": "Entomology",
        "meetings": [
            {
                "date": "2024-01-17",
                "block": 1,
                "room": "208",
                "attended": []
            },
            {
                "date": "2024-01-24",
                "block": 1,
                "room": "208",
                "attended": []
            },
            {
                "date": "2024-01-31",
                "block": 1,
                "room": "208",
                "attended": []
            }
        ]
    },
    "Astronomy": {
        "eventName": "Astronomy",
        "meetings": [
            {
                "date": "2024-01-17",
                "block": 2,
                "room": "209",
                "attended": []
            },
            {
                "date": "2024-01-24",
                "block": 2,
                "room": "209",
                "attended": []
            },
            {
                "date": "2024-01-31",
                "block": 2,
                "room": "209",
                "attended": []
            }
        ]
    },
    "Anatomy and Physiology": {
        "eventName": "Anatomy and Physiology",
        "meetings": [
            {
                "date": "2024-01-18",
                "block": 1,
                "room": "210",
                "attended": []
            },
            {
                "date": "2024-01-25",
                "block": 1,
                "room": "210",
                "attended": []
            },
            {
                "date": "2024-02-01",
                "block": 1,
                "room": "210",
                "attended": []
            }
        ]
    },
    "Disease Detectives": {
        "eventName": "Disease Detectives",
        "meetings": [
            {
                "date": "2024-01-18",
                "block": 2,
                "room": "211",
                "attended": []
            },
            {
                "date": "2024-01-25",
                "block": 2,
                "room": "211",
                "attended": []
            },
            {
                "date": "2024-02-01",
                "block": 2,
                "room": "211",
                "attended": []
            }
        ]
    },
    "Designer Genes": {
        "eventName": "Designer Genes",
        "meetings": [
            {
                "date": "2024-01-19",
                "block": 1,
                "room": "212",
                "attended": []
            },
            {
                "date": "2024-01-26",
                "block": 1,
                "room": "212",
                "attended": []
            },
            {
                "date": "2024-02-02",
                "block": 1,
                "room": "212",
                "attended": []
            }
        ]
    },
    "Chem Lab": {
        "eventName": "Chem Lab",
        "meetings": [
            {
                "date": "2024-01-19",
                "block": 2,
                "room": "213",
                "attended": []
            },
            {
                "date": "2024-01-26",
                "block": 2,
                "room": "213",
                "attended": []
            },
            {
                "date": "2024-02-02",
                "block": 2,
                "room": "213",
                "attended": []
            }
        ]
    },
    "Materials Science": {
        "eventName": "Materials Science",
        "meetings": [
            {
                "date": "2024-01-15",
                "block": 1,
                "room": "214",
                "attended": []
            },
            {
                "date": "2024-01-22",
                "block": 1,
                "room": "214",
                "attended": []
            },
            {
                "date": "2024-01-29",
                "block": 1,
                "room": "214",
                "attended": []
            }
        ]
    },
    "Forensics": {
        "eventName": "Forensics",
        "meetings": [
            {
                "date": "2024-01-15",
                "block": 2,
                "room": "215",
                "attended": []
            },
            {
                "date": "2024-01-22",
                "block": 2,
                "room": "215",
                "attended": []
            },
            {
                "date": "2024-01-29",
                "block": 2,
                "room": "215",
                "attended": []
            }
        ]
    },
    "Experimental Design": {
        "eventName": "Experimental Design",
        "meetings": [
            {
                "date": "2024-01-16",
                "block": 1,
                "room": "216",
                "attended": []
            },
            {
                "date": "2024-01-23",
                "block": 1,
                "room": "216",
                "attended": []
            },
            {
                "date": "2024-01-30",
                "block": 1,
                "room": "216",
                "attended": []
            }
        ]
    },
    "Codebusters": {
        "eventName": "Codebusters",
        "meetings": [
            {
                "date": "2024-01-16",
                "block": 2,
                "room": "217",
                "attended": []
            },
            {
                "date": "2024-01-23",
                "block": 2,
                "room": "217",
                "attended": []
            },
            {
                "date": "2024-01-30",
                "block": 2,
                "room": "217",
                "attended": []
            }
        ]
    }
}

def delete_all_meetings():
    """Delete all existing meetings"""
    try:
        print("🗑️  Deleting existing meetings...")
        response = requests.get(f"{API_BASE}/Meeting")
        if response.status_code == 200:
            meetings = response.json()
            for meeting_data in meetings:
                if isinstance(meeting_data, dict):
                    # Handle Firebase format
                    meeting_id = list(meeting_data.keys())[0]
                else:
                    meeting_id = meeting_data.get('id')
                
                if meeting_id:
                    delete_response = requests.delete(f"{API_BASE}/Meeting/{meeting_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted meeting {meeting_id}")
                    else:
                        print(f"   ❌ Failed to delete meeting {meeting_id}")
                    time.sleep(0.1)  # Small delay to avoid overwhelming the API
        print("✨ Cleanup complete!")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def create_meeting_document(meeting_data, event_name):
    """Create a complete meeting document with all required fields"""
    # Convert date string to timestamp
    date_obj = datetime.strptime(meeting_data["date"], "%Y-%m-%d")
    timestamp = int(date_obj.timestamp())
    
    return {
        "date": {"seconds": timestamp},
        "eventName": event_name,
        "block": meeting_data["block"],
        "room": meeting_data["room"],
        "attended": meeting_data["attended"]  # Empty array initially
    }

def create_meetings():
    """Create all Science Olympiad meetings"""
    print("🚀 Creating Science Olympiad meetings...")
    
    total_meetings = 0
    created_meetings = 0
    
    for event_name, event_info in MEETINGS_DATA.items():
        print(f"\n📅 Creating meetings for {event_name}...")
        
        for meeting_data in event_info["meetings"]:
            total_meetings += 1
            try:
                # Create complete meeting document
                meeting_document = create_meeting_document(meeting_data, event_name)
                
                response = requests.post(
                    f"{API_BASE}/Meeting",
                    headers={'Content-Type': 'application/json'},
                    json=meeting_document
                )
                
                if response.status_code in [200, 201]:
                    created_meetings += 1
                    print(f"   ✅ Created: {event_name} - {meeting_data['date']} (Block {meeting_data['block']})")
                else:
                    print(f"   ❌ Failed to create: {event_name} - {meeting_data['date']} - {response.status_code}")
                    print(f"      Response: {response.text}")
                
                time.sleep(0.2)  # Small delay between requests
                
            except Exception as e:
                print(f"   ❌ Error creating {event_name} - {meeting_data['date']}: {e}")

def main():
    """Main execution function"""
    print("🎯 Science Olympiad Meetings Collection Population Script")
    print("=" * 60)
    
    # Step 1: Clean up existing meetings
    delete_all_meetings()
    
    # Step 2: Create new meetings
    create_meetings()
    
    print("=" * 60)
    print("🎉 Script completed!")
    print()
    print("📋 Summary:")
    print(f"   • Created meetings for {len(MEETINGS_DATA)} events")
    
    # Count meetings by event
    for event_name, event_info in MEETINGS_DATA.items():
        meeting_count = len(event_info["meetings"])
        print(f"   • {event_name}: {meeting_count} meetings")
    
    print()
    print("🎨 Features included:")
    print("   • Weekly meeting schedules for all events")
    print("   • Proper date formatting with timestamps")
    print("   • Block assignments (1 or 2)")
    print("   • Room assignments")
    print("   • Empty attended arrays ready for member IDs")
    print("   • Realistic meeting dates starting from January 2024")
    print()
    print("🌐 Navigate to the Attendance page to see all the created meetings!")

if __name__ == "__main__":
    main() 