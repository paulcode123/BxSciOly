#!/usr/bin/env python3
"""
Script to fix duplicate email issue
"""

from db_init import db

def fix_duplicate_email():
    """Remove the fake account that has a duplicate email"""
    
    print("🔧 Fixing Duplicate Email Issue")
    print("=" * 40)
    
    try:
        # Find the fake account with duplicate email
        duplicate_email = "pauln30@nycstudents.net"
        
        # Query for all members with this email
        query = db.collection('Members').where('doeEmail', '==', duplicate_email).stream()
        members_with_email = list(query)
        
        print(f"📧 Found {len(members_with_email)} members with email: {duplicate_email}")
        
        for member in members_with_email:
            data = member.to_dict()
            name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            print(f"  • {name} (ID: {member.id})")
        
        # Remove the fake account (the one with name "fake acct")
        fake_account = None
        for member in members_with_email:
            data = member.to_dict()
            name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            if name == "fake acct":
                fake_account = member
                break
        
        if fake_account:
            print(f"\n🗑️  Removing fake account: {fake_account.id}")
            db.collection('Members').document(fake_account.id).delete()
            print("✅ Fake account removed successfully!")
        else:
            print("❌ Fake account not found")
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        query = db.collection('Members').where('doeEmail', '==', duplicate_email).stream()
        remaining_members = list(query)
        
        if len(remaining_members) == 1:
            data = remaining_members[0].to_dict()
            name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            print(f"✅ Fixed! Only one member remains: {name}")
        else:
            print(f"❌ Still have {len(remaining_members)} members with this email")
        
    except Exception as e:
        print(f"❌ Error fixing duplicate email: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_duplicate_email() 