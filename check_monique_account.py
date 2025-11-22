"""
Script to check if Monique has an account in the database.
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def check_monique_account():
    """Check if Monique has an account"""
    email = 'moniquec34@nycstudents.net'
    
    print(f"Searching for account with email: {email}")
    print("="*60)
    
    # Search by doeEmail
    member_query = db.collection('Members').where('doeEmail', '==', email).limit(1).stream()
    members = list(member_query)
    
    if members:
        member = members[0]
        member_data = member.to_dict()
        print(f"\n[FOUND] Account found!")
        print(f"  Document ID: {member.id}")
        print(f"  Name: {member_data.get('firstName', '')} {member_data.get('lastName', '')}")
        print(f"  DOE Email: {member_data.get('doeEmail', 'N/A')}")
        print(f"  Personal Email: {member_data.get('personalEmail', 'N/A')}")
        print(f"  Admin Status: {member_data.get('adminStatus', 'none')}")
        print(f"  Member Status: {member_data.get('memberStatus', 'N/A')}")
        return True
    else:
        # Try personalEmail
        member_query = db.collection('Members').where('personalEmail', '==', email).limit(1).stream()
        members = list(member_query)
        
        if members:
            member = members[0]
            member_data = member.to_dict()
            print(f"\n[FOUND] Account found (by personalEmail)!")
            print(f"  Document ID: {member.id}")
            print(f"  Name: {member_data.get('firstName', '')} {member_data.get('lastName', '')}")
            print(f"  DOE Email: {member_data.get('doeEmail', 'N/A')}")
            print(f"  Personal Email: {member_data.get('personalEmail', 'N/A')}")
            print(f"  Admin Status: {member_data.get('adminStatus', 'none')}")
            print(f"  Member Status: {member_data.get('memberStatus', 'N/A')}")
            return True
        else:
            # Try searching by first name "Monique"
            print("\n[NOT FOUND] No account found with that email.")
            print("\nSearching for accounts with first name 'Monique'...")
            print("="*60)
            
            all_members = db.collection('Members').stream()
            monique_accounts = []
            
            for member in all_members:
                member_data = member.to_dict()
                first_name = member_data.get('firstName', '').lower()
                if 'monique' in first_name:
                    monique_accounts.append({
                        'id': member.id,
                        'data': member_data
                    })
            
            if monique_accounts:
                print(f"\n[FOUND] Found {len(monique_accounts)} account(s) with 'Monique' in the name:")
                for i, acc in enumerate(monique_accounts, 1):
                    data = acc['data']
                    print(f"\n  Account {i}:")
                    print(f"    Document ID: {acc['id']}")
                    print(f"    Name: {data.get('firstName', '')} {data.get('lastName', '')}")
                    print(f"    DOE Email: {data.get('doeEmail', 'N/A')}")
                    print(f"    Personal Email: {data.get('personalEmail', 'N/A')}")
                    print(f"    Admin Status: {data.get('adminStatus', 'none')}")
            else:
                print("\n[NOT FOUND] No accounts found with 'Monique' in the name.")
            
            return False

if __name__ == '__main__':
    try:
        check_monique_account()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()



