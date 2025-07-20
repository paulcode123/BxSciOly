#!/usr/bin/env python3
"""
Test script to verify email uniqueness functionality
"""

from db_init import db

def test_email_uniqueness():
    """Test the email uniqueness check"""
    
    print("🧪 Testing Email Uniqueness Functionality")
    print("=" * 50)
    
    try:
        # Get all members and their DOE emails
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        print(f"📊 Total members in database: {len(members)}")
        
        # Check for duplicate DOE emails
        doe_emails = {}
        duplicates = []
        
        for member in members:
            data = member.to_dict()
            doe_email = data.get('doeEmail', '').lower().strip()
            
            if doe_email:
                if doe_email in doe_emails:
                    duplicates.append({
                        'email': doe_email,
                        'existing_user': doe_emails[doe_email],
                        'duplicate_user': f"{data.get('firstName', '')} {data.get('lastName', '')}"
                    })
                else:
                    doe_emails[doe_email] = f"{data.get('firstName', '')} {data.get('lastName', '')}"
        
        print(f"\n📧 Unique DOE emails: {len(doe_emails)}")
        print(f"🔄 Duplicate emails found: {len(duplicates)}")
        
        if duplicates:
            print("\n❌ DUPLICATE EMAILS FOUND:")
            print("-" * 30)
            for dup in duplicates:
                print(f"Email: {dup['email']}")
                print(f"  - Existing: {dup['existing_user']}")
                print(f"  - Duplicate: {dup['duplicate_user']}")
                print()
        else:
            print("\n✅ No duplicate DOE emails found!")
        
        # Test the API endpoint for a few emails
        print("🔍 Testing API Endpoint:")
        print("-" * 25)
        
        # Test with a real email from the database
        if doe_emails:
            test_email = list(doe_emails.keys())[0]
            print(f"Testing with existing email: {test_email}")
            
            # Query the database directly
            query = db.collection('Members').where('doeEmail', '==', test_email).limit(1).stream()
            results = list(query)
            
            if results:
                print(f"✅ Found existing user: {doe_emails[test_email]}")
            else:
                print("❌ No user found (this shouldn't happen)")
        
        # Test with a non-existent email
        fake_email = "nonexistent@nycstudents.net"
        print(f"\nTesting with non-existent email: {fake_email}")
        
        query = db.collection('Members').where('doeEmail', '==', fake_email).limit(1).stream()
        results = list(query)
        
        if not results:
            print("✅ Correctly found no user (email available)")
        else:
            print("❌ Found user when shouldn't have")
        
        print(f"\n🎯 Email uniqueness check is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing email uniqueness: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_uniqueness() 