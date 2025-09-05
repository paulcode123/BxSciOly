#!/usr/bin/env python3
"""
Script to check the exact API response structure
"""
import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api"

def check_api_structure():
    """Check the exact API response structure"""
    print("🔍 Checking API response structure...")
    
    try:
        # Get all competitions
        response = requests.get(f"{API_BASE}/Competitions")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch competitions: {response.status_code}")
            return
            
        competitions = response.json()
        print(f"Response type: {type(competitions)}")
        print(f"Length: {len(competitions)}")
        
        # Check if it's a list or dict
        if isinstance(competitions, list):
            print("✅ Response is a list")
            if len(competitions) > 0:
                print("First item structure:")
                print(json.dumps(competitions[0], indent=2))
        elif isinstance(competitions, dict):
            print("✅ Response is a dictionary")
            first_key = list(competitions.keys())[0] if competitions else None
            if first_key:
                print(f"First key: {first_key}")
                print("First item structure:")
                print(json.dumps(competitions[first_key], indent=2))
        else:
            print(f"❌ Unexpected response type: {type(competitions)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api_structure()







