#!/usr/bin/env python3
"""
Script to list all competitions in the database
"""
import requests

# API base URL
API_BASE = "http://localhost:8000/api"

def list_all_competitions():
    """List all competitions in the database"""
    print("📋 Listing all competitions in database...")
    
    try:
        # Get all competitions
        response = requests.get(f"{API_BASE}/Competitions")
        if response.status_code != 200:
            print(f"❌ Failed to fetch competitions: {response.status_code}")
            return
            
        competitions = response.json()
        print(f"📊 Found {len(competitions)} total competitions")
        print()
        
        # Group by type or show all
        for i, comp in enumerate(competitions, 1):
            comp_name = comp.get('name', 'Unknown')
            comp_type = comp.get('type', 'Unknown')
            comp_id = comp.get('id', 'Unknown')
            
            print(f"{i:2d}. {comp_name}")
            print(f"    Type: {comp_type}")
            print(f"    ID: {comp_id}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_all_competitions()







