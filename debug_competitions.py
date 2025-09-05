#!/usr/bin/env python3
"""
Script to debug the competitions API response
"""
import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api"

def debug_competitions():
    """Debug the competitions API response"""
    print("🔍 Debugging competitions API...")
    
    try:
        # Get all competitions
        response = requests.get(f"{API_BASE}/Competitions")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch competitions: {response.status_code}")
            print(f"Response text: {response.text}")
            return
            
        # Try to parse as JSON
        try:
            competitions = response.json()
            print(f"📊 Found {len(competitions)} competitions")
            print()
            
            # Show first few competitions with full structure
            for i, comp in enumerate(competitions[:3]):
                print(f"Competition {i+1}:")
                print(json.dumps(comp, indent=2))
                print("-" * 50)
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response.text[:500]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_competitions()







