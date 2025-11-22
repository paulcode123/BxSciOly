"""
Script to update admin statuses for specified users.
Sets adminStatus to 'full' or 'marketing' based on the provided lists.
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Users to give "full" admin status
full_admin_emails = [
    'nicholasc534@nycstudents.net',
    'isabela50@nycstudents.net',
    'linah12@nycstudents.net',
    'maggied7@nycstudents.net'
]

# Users to give "marketing" admin status
marketing_admin_emails = [
    'alexanderm454@nycstudents.net',
    'helenh34@nycstudents.net',
    'moniquec34@nycstudents.net',
    'iank34@nycstudents.net',
    'brandonl436@nycstudents.net',
    'marcusy9@nycstudents.net',
    'erinr27@nycstudents.net',
    'katiel50@nycstudents.net',
    'sennas2@nycstudents.net',
    'adelinen@nycstudents.net'
]

def update_admin_statuses():
    """Update admin statuses for the specified users"""
    results = {
        'updated': [],
        'not_found': [],
        'errors': []
    }
    
    # Update full admin statuses
    print("Updating 'full' admin statuses...")
    for email in full_admin_emails:
        try:
            # Find member by doeEmail first
            member_query = db.collection('Members').where('doeEmail', '==', email).limit(1).stream()
            members = list(member_query)
            
            # If not found, try personalEmail
            if not members:
                member_query = db.collection('Members').where('personalEmail', '==', email).limit(1).stream()
                members = list(member_query)
            
            if members:
                doc_id = members[0].id
                member_data = members[0].to_dict()
                db.collection('Members').document(doc_id).update({
                    'adminStatus': 'full'
                })
                name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                print(f"  [OK] Updated {email} ({name}) to 'full' admin")
                results['updated'].append({'email': email, 'status': 'full', 'name': name})
            else:
                print(f"  [NOT FOUND] User not found: {email}")
                results['not_found'].append(email)
        except Exception as e:
            print(f"  [ERROR] Error updating {email}: {e}")
            results['errors'].append({'email': email, 'error': str(e)})
    
    print("\nUpdating 'marketing' admin statuses...")
    # Update marketing admin statuses
    for email in marketing_admin_emails:
        try:
            # Find member by doeEmail first
            member_query = db.collection('Members').where('doeEmail', '==', email).limit(1).stream()
            members = list(member_query)
            
            # If not found, try personalEmail
            if not members:
                member_query = db.collection('Members').where('personalEmail', '==', email).limit(1).stream()
                members = list(member_query)
            
            if members:
                doc_id = members[0].id
                member_data = members[0].to_dict()
                db.collection('Members').document(doc_id).update({
                    'adminStatus': 'marketing'
                })
                name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                print(f"  [OK] Updated {email} ({name}) to 'marketing' admin")
                results['updated'].append({'email': email, 'status': 'marketing', 'name': name})
            else:
                print(f"  [NOT FOUND] User not found: {email}")
                results['not_found'].append(email)
        except Exception as e:
            print(f"  [ERROR] Error updating {email}: {e}")
            results['errors'].append({'email': email, 'error': str(e)})
    
    # Print summary
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    print(f"Successfully updated: {len(results['updated'])} users")
    print(f"Not found: {len(results['not_found'])} users")
    print(f"Errors: {len(results['errors'])} users")
    
    if results['not_found']:
        print("\nUsers not found:")
        for email in results['not_found']:
            print(f"  - {email}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error['email']}: {error['error']}")
    
    print("="*60)

if __name__ == '__main__':
    try:
        update_admin_statuses()
        print("\nAdmin status update completed!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

