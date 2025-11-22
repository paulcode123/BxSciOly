"""
Script to analyze merch orders:
1. Tabulate ranked choice voting results for designs
2. Determine first and second place designs
3. Count orders for each product type
"""

import sys
import os

# Add parent directory to path to import firebase modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from db_init import db
except ImportError:
    try:
        from routes.firebase_routes import db
    except ImportError:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not firebase_admin._apps:
            cred = credentials.Certificate('service_key.json')
            firebase_admin.initialize_app(cred)
        db = firestore.client()

def ranked_choice_voting(votes):
    """
    Implement ranked choice voting to determine winners.
    votes is a list of lists, where each inner list is a ranked ballot.
    Prints vote totals after each round.
    """
    if not votes or len(votes) == 0:
        return None, None
    
    # Flatten to get all possible candidates
    all_candidates = set()
    for vote in votes:
        all_candidates.update(vote)
    
    if len(all_candidates) == 0:
        return None, None
    
    candidates = sorted(list(all_candidates))  # Sort for consistent display
    total_votes = len(votes)
    majority = total_votes / 2
    
    # Round 1: Count first-choice votes
    print(f"\n{'='*60}")
    print(f"ROUND 1 - Initial Vote Count")
    print(f"{'='*60}")
    print(f"Total Votes: {total_votes} | Majority Needed: {majority:.1f}")
    print()
    
    first_choice_votes = {}
    for candidate in candidates:
        first_choice_votes[candidate] = 0
    
    for vote in votes:
        if len(vote) > 0:
            first_choice = vote[0]
            first_choice_votes[first_choice] = first_choice_votes.get(first_choice, 0) + 1
    
    # Display Round 1 results
    sorted_first = sorted(first_choice_votes.items(), key=lambda x: x[1], reverse=True)
    for design_num, count in sorted_first:
        percentage = (count / total_votes) * 100
        majority_indicator = " [MAJORITY]" if count > majority else ""
        print(f"  Design Option {design_num}: {count} votes ({percentage:.1f}%){majority_indicator}")
    
    winner = sorted_first[0][0]
    winner_votes = sorted_first[0][1]
    
    if winner_votes > majority:
        # We have a majority winner
        print(f"\n>>> Design Option {winner} has majority ({winner_votes} > {majority:.1f})")
        # Find second place
        if len(sorted_first) > 1:
            second_place = sorted_first[1][0]
        else:
            second_place = None
        return winner, second_place
    
    # No majority, use instant runoff
    print(f"\n>>> No majority winner. Proceeding to instant runoff...")
    eliminated = []
    remaining_candidates = candidates.copy()
    round_num = 1
    
    while len(remaining_candidates) > 2:
        round_num += 1
        
        # Count current round votes (first choice among remaining)
        round_votes = {c: 0 for c in remaining_candidates}
        
        for vote in votes:
            # Find first choice that's still in the race
            for choice in vote:
                if choice in remaining_candidates:
                    round_votes[choice] += 1
                    break
        
        # Display round results
        print(f"\n{'='*60}")
        print(f"ROUND {round_num} - After Eliminations")
        print(f"{'='*60}")
        print(f"Remaining Candidates: {sorted(remaining_candidates)}")
        print(f"Eliminated So Far: {sorted(eliminated)}")
        print()
        
        sorted_round_display = sorted(round_votes.items(), key=lambda x: x[1], reverse=True)
        total_active_votes = sum(round_votes.values())
        
        for design_num, count in sorted_round_display:
            percentage = (count / total_active_votes) * 100 if total_active_votes > 0 else 0
            majority_indicator = " [MAJORITY]" if count > total_active_votes / 2 else ""
            print(f"  Design Option {design_num}: {count} votes ({percentage:.1f}%){majority_indicator}")
        
        # Eliminate candidate with fewest votes
        sorted_round = sorted(round_votes.items(), key=lambda x: x[1])
        eliminated_candidate = sorted_round[0][0]
        eliminated_votes = sorted_round[0][1]
        eliminated.append(eliminated_candidate)
        remaining_candidates.remove(eliminated_candidate)
        
        print(f"\n>>> Eliminating Design Option {eliminated_candidate} ({eliminated_votes} votes, lowest)")
        
        if total_active_votes == 0:
            break
            
        # Check if we have a majority
        for candidate, count in round_votes.items():
            if candidate in remaining_candidates and count > total_active_votes / 2:
                # Winner found
                print(f"\n>>> Design Option {candidate} has majority ({count} > {total_active_votes/2:.1f})")
                winner = candidate
                # Find second place from remaining
                remaining_candidates.remove(candidate)
                if remaining_candidates:
                    second_candidates = [(c, round_votes[c]) for c in remaining_candidates]
                    second_candidates.sort(key=lambda x: x[1], reverse=True)
                    second_place = second_candidates[0][0] if second_candidates else None
                else:
                    second_place = eliminated[-1] if eliminated else None
                return winner, second_place
    
    # Final round with 2 candidates
    print(f"\n{'='*60}")
    print(f"FINAL ROUND - Head-to-Head")
    print(f"{'='*60}")
    print(f"Remaining Candidates: {sorted(remaining_candidates)}")
    print()
    
    final_votes = {c: 0 for c in remaining_candidates}
    for vote in votes:
        for choice in vote:
            if choice in remaining_candidates:
                final_votes[choice] += 1
                break
    
    sorted_final = sorted(final_votes.items(), key=lambda x: x[1], reverse=True)
    for design_num, count in sorted_final:
        percentage = (count / total_votes) * 100
        print(f"  Design Option {design_num}: {count} votes ({percentage:.1f}%)")
    
    winner = sorted_final[0][0]
    second_place = sorted_final[1][0] if len(sorted_final) > 1 else None
    
    print(f"\n>>> Winner: Design Option {winner}")
    if second_place:
        print(f">>> Runner-up: Design Option {second_place}")
    
    return winner, second_place

def analyze_merch_orders():
    """Analyze all merch orders from Firestore"""
    
    print("Fetching merch orders from Firestore...")
    
    try:
        merch_collection = db.collection('MerchOrders')
        orders = merch_collection.stream()
        
        all_votes = []
        all_items = []
        total_orders = 0
        
        for order in orders:
            order_data = order.to_dict()
            total_orders += 1
            
            # Collect design votes
            if 'designVotes' in order_data and order_data['designVotes']:
                all_votes.append(order_data['designVotes'])
            
            # Collect items
            if 'items' in order_data and order_data['items']:
                for item in order_data['items']:
                    all_items.append(item.get('type', 'unknown'))
        
        print(f"\nTotal Orders: {total_orders}")
        print(f"Total Votes Collected: {len(all_votes)}")
        print(f"Total Items Ordered: {len(all_items)}")
        
        # Analyze design votes
        print("\n" + "="*60)
        print("DESIGN VOTING RESULTS (Ranked Choice Voting)")
        print("="*60)
        
        if len(all_votes) == 0:
            print("\nNo votes found!")
            return
        
        # Run ranked choice voting (will print round-by-round results)
        winner, second = ranked_choice_voting(all_votes)
        
        print("\n" + "-"*60)
        print("FINAL RESULTS")
        print("-"*60)
        if winner:
            print(f"FIRST PLACE: Design Option {winner}")
        else:
            print("FIRST PLACE: No winner determined")
        
        if second:
            print(f"SECOND PLACE: Design Option {second}")
        else:
            print("SECOND PLACE: No second place determined")
        print("-"*60)
        
        # Analyze product orders
        print("\n" + "="*60)
        print("PRODUCT ORDER COUNTS")
        print("="*60)
        
        if len(all_items) == 0:
            print("\nNo items ordered!")
            return
        
        # Count items by type
        item_counts = {}
        for item_type in all_items:
            item_counts[item_type] = item_counts.get(item_type, 0) + 1
        
        # Sort by count
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nTotal Items Ordered: {len(all_items)}")
        print("\nBreakdown by Product:")
        for item_type, count in sorted_items:
            percentage = (count / len(all_items)) * 100
            print(f"  {item_type.replace('-', ' ').title()}: {count} orders ({percentage:.1f}%)")
        
        # Show how many orders included each product
        print("\n" + "-"*60)
        print("Orders Including Each Product:")
        print("-"*60)
        
        merch_collection = db.collection('MerchOrders')
        orders = merch_collection.stream()
        
        product_in_orders = {}
        order_count = 0
        
        for order in orders:
            order_data = order.to_dict()
            order_count += 1
            if 'items' in order_data and order_data['items']:
                order_item_types = set(item.get('type', 'unknown') for item in order_data['items'])
                for item_type in order_item_types:
                    product_in_orders[item_type] = product_in_orders.get(item_type, 0) + 1
        
        sorted_product_orders = sorted(product_in_orders.items(), key=lambda x: x[1], reverse=True)
        for item_type, order_count in sorted_product_orders:
            percentage = (order_count / total_orders) * 100 if total_orders > 0 else 0
            print(f"  {item_type.replace('-', ' ').title()}: {order_count} out of {total_orders} orders ({percentage:.1f}%)")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"Error analyzing orders: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_merch_orders()
