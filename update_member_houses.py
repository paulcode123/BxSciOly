#!/usr/bin/env python3
"""
Script to add house property to members in Firebase and assign them to their houses.
Uses team_placement_solution.csv for firebaseIDs and roster_placement_solution.csv for houses.
"""

import csv
import sys
from db_init import db

def load_team_placement():
    """Load firebase IDs from team_placement_solution.csv"""
    firebase_ids = {}
    with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['bxsciolyID'] and row['firebaseID']:
                bxscioly_id = row['bxsciolyID']
                firebase_id = row['firebaseID']
                firebase_ids[bxscioly_id] = firebase_id
    return firebase_ids

def load_roster_placement():
    """Load house assignments from roster_placement_solution.csv"""
    houses = {}
    with open('Planning/roster_placement_solution.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['bxsciolyID'] and row['house']:
                bxscioly_id = row['bxsciolyID']
                house = row['house']
                houses[bxscioly_id] = house
    return houses

def update_member_houses():
    """Update Firebase members with their house assignments"""
    
    print("Loading team placement data...")
    firebase_ids = load_team_placement()
    print(f"Loaded {len(firebase_ids)} firebase IDs")
    
    print("\nLoading roster placement data...")
    houses = load_roster_placement()
    print(f"Loaded {len(houses)} house assignments")
    
    # Match bxsciolyIDs and update Firebase
    print("\nUpdating members in Firebase...")
    updated_count = 0
    not_found_count = 0
    error_count = 0
    
    for bxscioly_id, house in houses.items():
        firebase_id = firebase_ids.get(bxscioly_id)
        
        if not firebase_id:
            print(f"[WARN] No Firebase ID found for bxsciolyID {bxscioly_id}")
            not_found_count += 1
            continue
        
        try:
            # Update the member document with the house field
            member_ref = db.collection('Members').document(firebase_id)
            member_ref.update({'house': house})
            print(f"[OK] Updated {firebase_id} (bxsciolyID: {bxscioly_id}) -> House {house}")
            updated_count += 1
        except Exception as e:
            print(f"[ERROR] Error updating {firebase_id} (bxsciolyID: {bxscioly_id}): {e}")
            error_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Successfully updated: {updated_count}")
    print(f"Firebase ID not found: {not_found_count}")
    print(f"Errors: {error_count}")
    print(f"Total members in roster: {len(houses)}")

if __name__ == '__main__':
    print("="*60)
    print("UPDATING MEMBER HOUSES IN FIREBASE")
    print("="*60)
    print("\nThis script will:")
    print("1. Read firebaseIDs from team_placement_solution.csv")
    print("2. Read house assignments from roster_placement_solution.csv")
    print("3. Update each member in Firebase with their house")
    print("\n" + "="*60 + "\n")
    
    # Check for --yes flag to skip confirmation
    skip_confirm = '--yes' in sys.argv or '-y' in sys.argv
    
    if not skip_confirm:
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Operation cancelled.")
            exit(0)
    
    print()
    update_member_houses()
    print("\nDone!")

