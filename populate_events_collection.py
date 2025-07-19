#!/usr/bin/env python3
"""
Script to populate the Events collection with all Science Olympiad events
This script creates event documents for all events listed in the planning document
"""

import requests
import json
import time
from datetime import datetime

# API base URL - adjust if needed
API_BASE = "http://localhost:8000/api"

# Event data organized by subject categories
EVENTS_DATA = {
    # Build Events
    "Construction Build": {
        "subject": "construction-build",
        "icon": "fas fa-hammer",
        "events": [
            {
                "eventName": "Helicopter",
                "description": "Teams design, construct, and test free flight rubber-powered helicopters to achieve maximum time aloft.",
                "meetingDay": "Monday",
                "meetingBlock": 1,
                "meetingRoom": 101
            },
            {
                "eventName": "Boomilever",
                "description": "Teams design and build a Boomilever meeting requirements to achieve the highest structural efficiency (load/build weight).",
                "meetingDay": "Monday",
                "meetingBlock": 2,
                "meetingRoom": 102
            }
        ]
    },
    "Precision Build": {
        "subject": "precision-build",
        "icon": "fas fa-cogs",
        "events": [
            {
                "eventName": "Bungee Drop",
                "description": "Teams design elastic cords to conduct drops at given heights, attempting to get a drop mass as close as possible to a landing surface without touching it.",
                "meetingDay": "Tuesday",
                "meetingBlock": 1,
                "meetingRoom": 103
            },
            {
                "eventName": "Hovercraft",
                "description": "Participants construct a self-propelled air-levitated vehicle that moves down a track, testing knowledge of classical mechanics.",
                "meetingDay": "Tuesday",
                "meetingBlock": 2,
                "meetingRoom": 104
            },
            {
                "eventName": "Electric Vehicle",
                "description": "Teams design, build, and test one vehicle that uses electrical energy as its sole means of propulsion to travel quickly and stop close to a Target Point.",
                "meetingDay": "Wednesday",
                "meetingBlock": 1,
                "meetingRoom": 105
            },
            {
                "eventName": "Robot Tour",
                "description": "Teams design, build, program and test one Robotic Vehicle to navigate a track to reach a target at a set amount of time as accurately and efficiently as possible.",
                "meetingDay": "Wednesday",
                "meetingBlock": 2,
                "meetingRoom": 106
            }
        ]
    },
    
    # Academic Events
    "Physics and Design": {
        "subject": "physics",
        "icon": "fas fa-atom",
        "events": [
            {
                "eventName": "Engineering CAD",
                "description": "Teams read engineering drawings and collaboratively create CAD parts and assemblies that match the drawings while incorporating provided components.",
                "meetingDay": "Thursday",
                "meetingBlock": 1,
                "meetingRoom": 201
            },
            {
                "eventName": "Machines",
                "description": "Teams complete a written test on compound machine concepts and construct a lever-based measuring device to determine the ratio between two masses.",
                "meetingDay": "Thursday",
                "meetingBlock": 2,
                "meetingRoom": 202
            },
            {
                "eventName": "Circuit Lab",
                "description": "Written test on circuit concepts with hands-on component testing various circuit elements to complete tasks like constructing a magnet or determining resistor values.",
                "meetingDay": "Friday",
                "meetingBlock": 1,
                "meetingRoom": 203
            }
        ]
    },
    "Earth Science": {
        "subject": "earth-science",
        "icon": "fas fa-globe-americas",
        "events": [
            {
                "eventName": "Water Quality",
                "description": "Participants assess understanding and evaluation of marine and estuary aquatic environments. Includes building a Salinometer (5% of grade).",
                "meetingDay": "Monday",
                "meetingBlock": 1,
                "meetingRoom": 204
            },
            {
                "eventName": "Dynamic Planet",
                "description": "Teams demonstrate knowledge of Earth's fresh water systems and processes.",
                "meetingDay": "Monday",
                "meetingBlock": 2,
                "meetingRoom": 205
            },
            {
                "eventName": "Remote Sensing",
                "description": "Participants use remote sensing imagery, data and computational process skills to complete tasks related to climate change processes in the Earth system.",
                "meetingDay": "Tuesday",
                "meetingBlock": 1,
                "meetingRoom": 206
            }
        ]
    },
    "Classification and Compilation": {
        "subject": "classification-compilation",
        "icon": "fas fa-search",
        "events": [
            {
                "eventName": "Rocks and Minerals",
                "description": "Teams identify rocks and minerals using various testing methods and reference materials.",
                "meetingDay": "Tuesday",
                "meetingBlock": 2,
                "meetingRoom": 207
            },
            {
                "eventName": "Entomology",
                "description": "Competitors assess knowledge of North American insect families, primarily through identification.",
                "meetingDay": "Wednesday",
                "meetingBlock": 1,
                "meetingRoom": 208
            },
            {
                "eventName": "Astronomy",
                "description": "Teams demonstrate understanding of Stellar Evolution: Star Formation & Exoplanets.",
                "meetingDay": "Wednesday",
                "meetingBlock": 2,
                "meetingRoom": 209
            }
        ]
    },
    "Biology": {
        "subject": "biology",
        "icon": "fas fa-dna",
        "events": [
            {
                "eventName": "Anatomy and Physiology",
                "description": "Participants assess understanding of the anatomy and physiology for the human Nervous, Sensory, and Endocrine systems.",
                "meetingDay": "Thursday",
                "meetingBlock": 1,
                "meetingRoom": 210
            },
            {
                "eventName": "Disease Detectives",
                "description": "Participants use investigative skills in the scientific study of disease, injury, health, and disability in populations or groups of people.",
                "meetingDay": "Thursday",
                "meetingBlock": 2,
                "meetingRoom": 211
            },
            {
                "eventName": "Designer Genes",
                "description": "Participants solve problems and analyze data or diagrams using knowledge of basic principles of genetics, molecular genetics and biotechnology.",
                "meetingDay": "Friday",
                "meetingBlock": 1,
                "meetingRoom": 212
            }
        ]
    },
    "Chemistry & Inquiry": {
        "subject": "chemistry",
        "icon": "fas fa-flask",
        "events": [
            {
                "eventName": "Chem Lab",
                "description": "Teams perform laboratory experiments focusing on Kinetics and Stoichiometry.",
                "meetingDay": "Friday",
                "meetingBlock": 2,
                "meetingRoom": 213
            },
            {
                "eventName": "Materials Science",
                "description": "Teams demonstrate knowledge of materials science concepts through laboratory experiments and theoretical analysis.",
                "meetingDay": "Monday",
                "meetingBlock": 1,
                "meetingRoom": 214
            },
            {
                "eventName": "Forensics",
                "description": "Teams analyze evidence using scientific methods to solve forensic science problems.",
                "meetingDay": "Monday",
                "meetingBlock": 2,
                "meetingRoom": 215
            },
            {
                "eventName": "Experimental Design",
                "description": "Teams design, conduct, analyze and write up an experiment based on a given topic.",
                "meetingDay": "Tuesday",
                "meetingBlock": 1,
                "meetingRoom": 216
            },
            {
                "eventName": "Codebusters",
                "description": "Teams decode encrypted messages using various cryptography techniques and mathematical analysis.",
                "meetingDay": "Tuesday",
                "meetingBlock": 2,
                "meetingRoom": 217
            }
        ]
    }
}

def delete_all_events():
    """Delete all existing events"""
    try:
        print("🗑️  Deleting existing events...")
        response = requests.get(f"{API_BASE}/Events")
        if response.status_code == 200:
            events = response.json()
            for event_data in events:
                if isinstance(event_data, dict):
                    # Handle Firebase format
                    event_id = list(event_data.keys())[0]
                else:
                    event_id = event_data.get('id')
                
                if event_id:
                    delete_response = requests.delete(f"{API_BASE}/Events/{event_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted event {event_id}")
                    else:
                        print(f"   ❌ Failed to delete event {event_id}")
                    time.sleep(0.1)  # Small delay to avoid overwhelming the API
        print("✨ Cleanup complete!")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def create_event_document(event_data, subject_info):
    """Create a complete event document with all required fields"""
    event_name = event_data["eventName"]
    
    # Generate welcome message based on event type
    if subject_info["subject"] == "construction-build":
        welcome = f"Welcome to {event_name}! This construction build event will challenge your engineering and construction skills."
    elif subject_info["subject"] == "precision-build":
        welcome = f"Welcome to {event_name}! This precision build event will test your attention to detail and engineering precision."
    elif subject_info["subject"] == "physics":
        welcome = f"Welcome to {event_name}! This physics event combines theoretical knowledge with practical applications."
    elif subject_info["subject"] == "earth-science":
        welcome = f"Welcome to {event_name}! Explore Earth's systems and environmental processes."
    elif subject_info["subject"] == "biology":
        welcome = f"Welcome to {event_name}! Dive into the fascinating world of biological systems and processes."
    elif subject_info["subject"] == "chemistry":
        welcome = f"Welcome to {event_name}! Master chemical concepts through hands-on experimentation and analysis."
    elif subject_info["subject"] == "classification-compilation":
        welcome = f"Welcome to {event_name}! This classification and compilation event will test your research and analytical skills."
    else:
        welcome = f"Welcome to {event_name}! This event will test your knowledge and skills."
    
    # Generate about section
    about = f"{event_name} is part of the {list(EVENTS_DATA.keys())[list(EVENTS_DATA.values()).index(subject_info)]} category. {event_data['description']}"
    
    # Generate content overview
    content_overview = f"This event covers the fundamental concepts and skills needed for {event_name}. Participants will engage in both theoretical learning and practical applications."
    
    # Generate tips
    tips = f"• Review the official Science Olympiad rules for {event_name}\n• Practice regularly with your team\n• Attend all scheduled meetings\n• Ask questions and seek help when needed\n• Stay organized with your materials and notes"
    
    # Generate resources
    resources = [
        {
            "title": f"{event_name} Official Rules",
            "description": "Current year's official Science Olympiad rules and specifications",
            "url": f"https://www.soinc.org/{event_name.lower().replace(' ', '-')}"
        },
        {
            "title": f"{event_name} Study Guide",
            "description": "Comprehensive study materials and practice problems",
            "url": "https://example.com/study-guide"
        },
        {
            "title": "Science Olympiad Wiki",
            "description": "Community-maintained resource with tips and strategies",
            "url": f"https://scioly.org/wiki/index.php/{event_name.replace(' ', '_')}"
        }
    ]
    
    return {
        "eventName": event_name,
        "description": event_data["description"],
        "subject": subject_info["subject"],
        "icon": subject_info["icon"],
        "generalInfo": {
            "welcome": welcome,
            "about": about,
            "contentOverview": content_overview,
            "tips": tips,
            "resources": resources
        },
        "meetingDay": event_data["meetingDay"],
        "meetingBlock": event_data["meetingBlock"],
        "meetingRoom": event_data["meetingRoom"],
        "members": [],  # Will be populated as members join
        "eventManagers": [],  # Will be assigned by leadership
        "subjectDirectors": []  # Will be assigned by leadership
    }

def create_events():
    """Create all Science Olympiad events"""
    print("🚀 Creating Science Olympiad events...")
    
    total_events = 0
    created_events = 0
    
    for subject_name, subject_info in EVENTS_DATA.items():
        print(f"\n📚 Creating events for {subject_name}...")
        
        for event_data in subject_info["events"]:
            total_events += 1
            try:
                # Create complete event document
                event_document = create_event_document(event_data, subject_info)
                
                response = requests.post(
                    f"{API_BASE}/Events",
                    headers={'Content-Type': 'application/json'},
                    json=event_document
                )
                
                if response.status_code in [200, 201]:
                    created_events += 1
                    print(f"   ✅ Created: {event_data['eventName']}")
                else:
                    print(f"   ❌ Failed to create: {event_data['eventName']} - {response.status_code}")
                    print(f"      Response: {response.text}")
                
                time.sleep(0.2)  # Small delay between requests
                
            except Exception as e:
                print(f"   ❌ Error creating {event_data['eventName']}: {e}")

def main():
    """Main execution function"""
    print("🎯 Science Olympiad Events Collection Population Script")
    print("=" * 60)
    
    # Step 1: Clean up existing events
    delete_all_events()
    
    # Step 2: Create new events
    create_events()
    
    print("=" * 60)
    print("🎉 Script completed!")
    print()
    print("📋 Summary:")
    print(f"   • Created events for {len(EVENTS_DATA)} subject categories")
    
    # Count events by category
    for subject_name, subject_info in EVENTS_DATA.items():
        event_count = len(subject_info["events"])
        print(f"   • {subject_name}: {event_count} events")
    
    print()
    print("🎨 Features included:")
    print("   • Complete event information with descriptions")
    print("   • Subject categorization (construction-build, precision-build, physics, earth-science, biology, chemistry, classification-compilation)")
    print("   • FontAwesome icons for visual representation")
    print("   • Meeting schedules with days, blocks, and rooms")
    print("   • Welcome messages and content overviews")
    print("   • Study tips and resource links")
    print("   • Empty arrays for members, event managers, and subject directors")
    print()
    print("🌐 Navigate to the Events page to see all the created events!")

if __name__ == "__main__":
    main() 