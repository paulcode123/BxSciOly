"""
Script to create admin user accounts for Mallory Womer, John Powell, and Jennifer Zhang.
Generates random 6-letter passwords and sets adminStatus to 'full'.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import secrets
import string
from datetime import datetime

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def generate_password(length=6):
    """Generate a random password with the specified length"""
    alphabet = string.ascii_letters  # Both uppercase and lowercase
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Define the three users
users = [
    {
        'firstName': 'Mallory',
        'lastName': 'Womer',
        'doeEmail': 'mwomer@schools.nyc.gov',
        'personalEmail': 'mwomer@schools.nyc.gov',  # Using same email as personal
        'phoneNumber': '',  # Optional field
        'grade': '',  # Optional field
        'adminStatus': 'full',
        'createdAt': datetime.now().isoformat(),
        'memberStatus': 'returning',  # Default status
        'status': 'registered'
    },
    {
        'firstName': 'John',
        'lastName': 'Powell',
        'doeEmail': 'JPowell27@schools.nyc.gov',
        'personalEmail': 'JPowell27@schools.nyc.gov',
        'phoneNumber': '',
        'grade': '',
        'adminStatus': 'full',
        'createdAt': datetime.now().isoformat(),
        'memberStatus': 'returning',
        'status': 'registered'
    },
    {
        'firstName': 'Jennifer',
        'lastName': 'Zheng',
        'doeEmail': 'jzheng8@schools.nyc.gov',
        'personalEmail': 'jzheng8@schools.nyc.gov',
        'phoneNumber': '',
        'grade': '',
        'adminStatus': 'full',
        'createdAt': datetime.now().isoformat(),
        'memberStatus': 'returning',
        'status': 'registered'
    }
]

def create_users():
    """Create the admin users in Firebase"""
    passwords = {}
    
    for user_data in users:
        # Generate random 6-letter password
        password = generate_password(6)
        passwords[user_data['doeEmail']] = password
        
        # Add password to user data
        user_data['password'] = password
        
        # Check if user already exists
        existing_query = db.collection('Members').where('doeEmail', '==', user_data['doeEmail']).limit(1).stream()
        existing_users = list(existing_query)
        
        if existing_users:
            # Update existing user
            doc_id = existing_users[0].id
            db.collection('Members').document(doc_id).update({
                'adminStatus': 'full',
                'password': password
            })
            print(f"Updated existing user: {user_data['firstName']} {user_data['lastName']} ({user_data['doeEmail']})")
        else:
            # Create new user
            doc_ref = db.collection('Members').document()
            doc_ref.set(user_data)
            print(f"Created new user: {user_data['firstName']} {user_data['lastName']} ({user_data['doeEmail']})")
    
    # Print passwords
    print("\n" + "="*60)
    print("Generated Passwords:")
    print("="*60)
    for email, password in passwords.items():
        print(f"{email}: {password}")
    print("="*60)
    print("\nPlease save these passwords securely!")

if __name__ == '__main__':
    try:
        create_users()
        print("\nSuccessfully created/updated admin users!")
    except Exception as e:
        print(f"\nError creating users: {e}")
        import traceback
        traceback.print_exc()

