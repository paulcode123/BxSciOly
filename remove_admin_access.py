#!/usr/bin/env python3
"""
Script to remove admin access from specific users
"""

from db_init import db
from datetime import datetime

def remove_admin_access():
    """Remove admin access from specified users"""
    
    # List of users to remove admin access from
    users_to_update = [
        "Katie Lim",
        "fake acct", 
        "Adeline Nurenie"
    ]
    
    print("🔧 Removing Admin Access from Specified Users")
    print("=" * 50)
    
    try:
        # Get all members from the database
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        if not members:
            print("❌ No members found in the database.")
            return
        
        print(f"📊 Total members in database: {len(members)}")
        print()
        
        updated_count = 0
        
        for member in members:
            data = member.to_dict()
            member_name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            
            # Check if this member is in our list to update
            if member_name in users_to_update:
                current_admin_status = data.get('adminStatus', 'none')
                
                print(f"🔍 Found: {member_name}")
                print(f"   📧 Email: {data.get('doeEmail', 'N/A')}")
                print(f"   👑 Current Admin Status: {current_admin_status}")
                
                if current_admin_status == 'full':
                    # Update the member's admin status to 'none'
                    member_ref = db.collection('Members').document(member.id)
                    member_ref.update({
                        'adminStatus': 'none',
                        'updatedAt': datetime.now().isoformat()
                    })
                    
                    print(f"   ✅ Admin access REMOVED")
                    updated_count += 1
                else:
                    print(f"   ℹ️  Already has no admin access")
                
                print()
        
        print("📋 SUMMARY")
        print("-" * 20)
        print(f"Users processed: {len(users_to_update)}")
        print(f"Admin access removed: {updated_count}")
        
        # Show final status of all users
        print("\n📊 FINAL STATUS OF TARGETED USERS:")
        print("-" * 40)
        
        for member in members:
            data = member.to_dict()
            member_name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            
            if member_name in users_to_update:
                admin_status = data.get('adminStatus', 'none')
                print(f"• {member_name}: {admin_status}")
        
        print(f"\n✅ Admin access removal completed successfully!")
        
    except Exception as e:
        print(f"❌ Error removing admin access: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    remove_admin_access() 