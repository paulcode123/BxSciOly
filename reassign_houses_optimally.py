import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict
import sys
import csv
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        from db_init import db
        return db
    except ImportError:
        if not firebase_admin._apps:
            cred = credentials.Certificate('service_key.json')
            firebase_admin.initialize_app(cred)
        return firestore.client()

def calculate_imbalance(event_counts):
    """Calculate the imbalance (variance) of house distribution for an event"""
    houses = ['A', 'B', 'C', 'D']
    counts = [event_counts.get(h, 0) for h in houses]
    if not counts:
        return 0
    mean = sum(counts) / len(counts)
    variance = sum((x - mean) ** 2 for x in counts) / len(counts)
    return variance

def load_team_members():
    """Load team members from team_placement_solution.csv"""
    team_member_ids = set()
    
    csv_path = 'Planning/team_placement_solution.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return team_member_ids
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            firebase_id = row.get('firebaseID', '').strip()
            if firebase_id:  # Some rows might have empty firebaseID
                team_member_ids.add(firebase_id)
    
    return team_member_ids

def reassign_all_team_members_optimally():
    """
    Reassign ALL team members to houses optimally to balance distribution across events.
    Only processes members listed in team_placement_solution.csv.
    """
    
    print("Optimal House Reassignment for All Team Members")
    print("=" * 60)
    
    try:
        # Load team members from CSV
        print("Loading team members from team_placement_solution.csv...")
        team_member_ids = load_team_members()
        print(f"Found {len(team_member_ids)} team members in CSV\n")
        
        if not team_member_ids:
            print("No team members found in CSV!")
            return
        
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all events
        events_ref = db.collection('Events')
        events = list(events_ref.stream())
        
        if not events:
            print("No events found in the database.")
            return
        
        print(f"Found {len(events)} events in the database\n")
        
        # Get all members (only team members)
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        member_data = {}
        all_team_members = []
        
        for member in members:
            member_id = member.id
            # Only process team members
            if member_id not in team_member_ids:
                continue
                
            member_info = member.to_dict()
            member_data[member_id] = {
                'house': None,  # Start with no house assignment
                'info': member_info
            }
            all_team_members.append(member_id)
        
        print(f"Found {len(all_team_members)} team members in database\n")
        
        # Build event -> members mapping (only include team members)
        event_members = {}
        member_events = defaultdict(list)  # member_id -> list of event names
        
        for event in events:
            event_data = event.to_dict()
            event_name = event_data.get('eventName', 'Unknown Event')
            member_ids = event_data.get('members', [])
            # Filter to only include team members that exist in database
            valid_member_ids = [mid for mid in member_ids if mid in member_data and mid in team_member_ids]
            event_members[event_name] = valid_member_ids
            
            for member_id in valid_member_ids:
                member_events[member_id].append(event_name)
        
        # Calculate current distribution per event (starts empty)
        def get_current_distribution():
            dist = defaultdict(lambda: {'A': 0, 'B': 0, 'C': 0, 'D': 0})
            # Initialize all events
            for event_name in event_members.keys():
                dist[event_name] = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            
            for event_name, member_ids in event_members.items():
                for member_id in member_ids:
                    house = member_data[member_id]['house']
                    if house in ['A', 'B', 'C', 'D']:
                        dist[event_name][house] += 1
            return dist
        
        # Assign houses using a greedy approach
        # Process members in order of number of events (more events first for better balancing)
        assignments = {}
        
        print("Calculating optimal house assignments for all team members...\n")
        
        # Sort members by number of events (descending) to prioritize balancing those with more events
        sorted_members = sorted(all_team_members, key=lambda mid: len(member_events.get(mid, [])), reverse=True)
        
        for member_id in sorted_members:
            events_for_member = member_events.get(member_id, [])
            
            if not events_for_member:
                # Member not in any events, assign to least populated house overall
                current_dist = get_current_distribution()
                totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                for event_dist in current_dist.values():
                    for house in totals:
                        totals[house] += event_dist[house]
                # Assign to house with lowest total
                best_house = min(totals.keys(), key=lambda h: totals[h])
                assignments[member_id] = best_house
                member_data[member_id]['house'] = best_house  # Update for next iteration
                member_name = member_data[member_id]['info'].get('firstName', '') + ' ' + \
                             member_data[member_id]['info'].get('lastName', '')
                print(f"Member {member_id[:8]}... ({member_name.strip() or 'Unknown'}) -> House {best_house} (not in any events)")
                continue
            
            # Calculate imbalance for each possible house assignment
            best_house = None
            best_score = float('inf')
            
            current_dist = get_current_distribution()
            
            for candidate_house in ['A', 'B', 'C', 'D']:
                # Simulate assigning this member to candidate_house
                temp_dist = {}
                for event_name, counts in current_dist.items():
                    temp_dist[event_name] = counts.copy()
                
                # Update counts for events this member is in
                for event_name in events_for_member:
                    if event_name not in temp_dist:
                        # This shouldn't happen, but safety check
                        temp_dist[event_name] = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                    temp_dist[event_name][candidate_house] += 1
                
                # Calculate total imbalance across all events this member is in
                total_imbalance = sum(calculate_imbalance(temp_dist[event]) for event in events_for_member)
                
                # Also consider overall balance (prefer more balanced overall distribution)
                overall_imbalance = sum(calculate_imbalance(temp_dist[event]) for event in temp_dist.keys())
                
                # Combined score: prioritize balancing the member's events, but also consider overall
                score = total_imbalance + 0.1 * overall_imbalance
                
                if score < best_score:
                    best_score = score
                    best_house = candidate_house
            
            assignments[member_id] = best_house
            
            # Update member_data for next iteration (so get_current_distribution reflects changes)
            member_data[member_id]['house'] = best_house
            
            member_name = member_data[member_id]['info'].get('firstName', '') + ' ' + \
                         member_data[member_id]['info'].get('lastName', '')
            print(f"Member {member_id[:8]}... ({member_name.strip() or 'Unknown'}) -> House {best_house} "
                  f"(in {len(events_for_member)} events)")
        
        # Show preview of new distribution
        print("\n" + "=" * 60)
        print("PREVIEW OF OPTIMAL DISTRIBUTION")
        print("=" * 60 + "\n")
        
        # Calculate new distribution
        new_dist = get_current_distribution()
        
        sorted_events = sorted(new_dist.items())
        for event_name, counts in sorted_events:
            total = sum(counts.values())
            mean = total / 4
            variance = sum((counts[h] - mean) ** 2 for h in ['A', 'B', 'C', 'D']) / 4
            
            print(f"{event_name} (Total: {total}, Variance: {variance:.2f})")
            print(f"   House A: {counts['A']}")
            print(f"   House B: {counts['B']}")
            print(f"   House C: {counts['C']}")
            print(f"   House D: {counts['D']}")
            print()
        
        # Summary statistics
        print("=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        
        total_by_house = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for counts in new_dist.values():
            for house in total_by_house:
                total_by_house[house] += counts[house]
        
        print("\nTotal members across all events:")
        for house in ['A', 'B', 'C', 'D']:
            print(f"   House {house}: {total_by_house[house]}")
        
        # Calculate average variance per event
        variances = [calculate_imbalance(counts) for counts in new_dist.values()]
        avg_variance = sum(variances) / len(variances) if variances else 0
        print(f"\nAverage variance per event: {avg_variance:.2f}")
        print(f"(Lower is better - 0 means perfectly balanced)")
        
        # Show which members changed houses
        print("\n" + "=" * 60)
        print("HOUSE CHANGES")
        print("=" * 60)
        
        # Get original houses from Firebase
        changed_count = 0
        unchanged_count = 0
        for member in members:
            member_id = member.id
            if member_id not in team_member_ids:
                continue
            
            original_house = member.to_dict().get('house', 'No House')
            new_house = assignments.get(member_id)
            
            if original_house != new_house:
                changed_count += 1
                member_name = member_data[member_id]['info'].get('firstName', '') + ' ' + \
                             member_data[member_id]['info'].get('lastName', '')
                print(f"{member_name.strip() or member_id[:8]}: {original_house} -> {new_house}")
            else:
                unchanged_count += 1
        
        print(f"\nChanged: {changed_count} members")
        print(f"Unchanged: {unchanged_count} members")
        
        # Ask for confirmation
        print("\n" + "=" * 60)
        skip_confirm = '--yes' in sys.argv or '-y' in sys.argv
        
        if not skip_confirm:
            response = input("\nDo you want to apply these optimal assignments to Firebase? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Operation cancelled.")
                return
        
        # Update Firebase
        print("\nUpdating members in Firebase...")
        updated_count = 0
        error_count = 0
        
        for member_id, house in assignments.items():
            try:
                member_ref = db.collection('Members').document(member_id)
                member_ref.update({'house': house})
                updated_count += 1
            except Exception as e:
                print(f"Error updating member {member_id}: {e}")
                error_count += 1
        
        print("\n" + "=" * 60)
        print("UPDATE SUMMARY")
        print("=" * 60)
        print(f"Successfully updated: {updated_count}")
        print(f"Errors: {error_count}")
        print("\nDone!")
        
    except Exception as e:
        print(f"Error reassigning houses: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    reassign_all_team_members_optimally()

