"""
Script to find who hasn't submitted merch orders and get their contact info
"""

import sys
import os
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

import csv

# Get all admins from Firestore
print('Fetching admins from Firestore Members collection...')
admins = []
members_collection = db.collection('Members')
members = members_collection.stream()

for member in members:
    member_data = member.to_dict()
    admin_status = member_data.get('adminStatus', 'none')
    if admin_status != 'none':
        email = member_data.get('doeEmail', member_data.get('email', 'N/A'))
        name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}"
        admins.append({
            'firebase_id': member.id,
            'name': name.strip(),
            'email': email,
            'admin_status': admin_status
        })

print(f'Total admins: {len(admins)}')
for admin in admins:
    print(f'  - {admin["name"]} ({admin["email"]}) - {admin["admin_status"]}')

# Get team members from CSV
print(f'\nFetching team members from team_placement_solution.csv...')
team_members = []
try:
    with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_members.append({
                'firebase_id': row.get('firebaseID', ''),
                'name': f"{row.get('firstName', '')} {row.get('lastName', '')}"
            })
except Exception as e:
    print(f'Error reading CSV: {e}')

print(f'Total team members: {len(team_members)}')

# Get merch orders
print(f'\nFetching MerchOrders from Firestore...')
merch_collection = db.collection('MerchOrders')
orders = merch_collection.stream()
submitted_ids = set()
for order in orders:
    order_data = order.to_dict()
    submitted_ids.add(order_data.get('firebaseID', ''))

print(f'Total submitted orders: {len(submitted_ids)}')

# Find who hasn't submitted
all_eligible_ids = set()

# Add all admin IDs
for admin in admins:
    all_eligible_ids.add(admin['firebase_id'])

# Add all team member IDs
for member in team_members:
    if member['firebase_id']:
        all_eligible_ids.add(member['firebase_id'])

print(f'\nTotal eligible (admins + team members): {len(all_eligible_ids)}')

not_submitted_ids = all_eligible_ids - submitted_ids
print(f'Total who HAVE NOT submitted: {len(not_submitted_ids)}')

# Get email info for those who haven't submitted
print('\nPeople who have NOT submitted merch orders:')
print('=' * 80)

not_submitted_list = []

# Check admins who haven't submitted
for admin in admins:
    if admin['firebase_id'] in not_submitted_ids:
        not_submitted_list.append({
            'name': admin['name'],
            'email': admin['email'],
            'type': 'Admin'
        })

# Check team members who haven't submitted
for member in team_members:
    if member['firebase_id'] in not_submitted_ids:
        # Try to get email from Firestore
        try:
            member_doc = db.collection('Members').document(member['firebase_id']).get()
            if member_doc.exists:
                member_data = member_doc.to_dict()
                email = member_data.get('doeEmail', member_data.get('email', 'N/A'))
                not_submitted_list.append({
                    'name': member['name'],
                    'email': email,
                    'type': 'Team Member'
                })
        except:
            not_submitted_list.append({
                'name': member['name'],
                'email': 'N/A',
                'type': 'Team Member'
            })

# Sort by name
not_submitted_list.sort(key=lambda x: x['name'])

for item in not_submitted_list:
    print(f'{item["name"]:<35} | {item["email"]:<40} | {item["type"]}')

# Save to CSV
with open('merch_not_submitted.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'email', 'type'])
    writer.writeheader()
    writer.writerows(not_submitted_list)

print(f'\n[OK] Saved to merch_not_submitted.csv')
print(f'\nSummary:')
print(f'  Admins: {len(admins)}')
print(f'  Team Members: {len(team_members)}')
print(f'  Total Eligible: {len(all_eligible_ids)}')
print(f'  Submitted: {len(submitted_ids)}')
print(f'  NOT Submitted: {len(not_submitted_ids)}')

