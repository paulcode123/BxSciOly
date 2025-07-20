#!/usr/bin/env python3
"""
Script to verify admin access changes
"""

from db_init import db

def verify_admin_changes():
    """Verify that admin access was removed from specified users"""
    
    # List of users to check
    users_to_check = [
        "Katie Lim",
        "fake acct", 
        "Adeline Nurenie"
    ]
    
    print("🔍 Verifying Admin Access Changes")
    print("=" * 40)
    
    try:
        # Get all members from the database
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        print("📊 CURRENT ADMIN STATUS:")
        print("-" * 30)
        
        for member in members:
            data = member.to_dict()
            member_name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            
            if member_name in users_to_check:
                admin_status = data.get('adminStatus', 'none')
                email = data.get('doeEmail', 'N/A')
                print(f"• {member_name} ({email}): {admin_status}")
        
        # Count total admin users
        admin_users = [m for m in members if m.to_dict().get('adminStatus') == 'full']
        print(f"\n📈 Total users with admin access: {len(admin_users)}")
        
        if len(admin_users) == 0:
            print("✅ All admin access has been removed!")
        else:
            print(f"📋 Remaining admin users:")
            for member in admin_users:
                data = member.to_dict()
                name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
                email = data.get('doeEmail', 'N/A')
                print(f"   • {name} ({email})")
        
    except Exception as e:
        print(f"❌ Error verifying changes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_admin_changes() 