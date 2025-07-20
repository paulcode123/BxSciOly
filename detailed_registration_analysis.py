#!/usr/bin/env python3
"""
Detailed analysis of individual registration form submissions
"""

from db_init import db
from datetime import datetime
import json

def detailed_analysis():
    """Show detailed analysis of individual registrations"""
    
    print("🔍 DETAILED REGISTRATION ANALYSIS")
    print("=" * 50)
    
    try:
        # Get all members
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        if not members:
            print("❌ No registrations found.")
            return
        
        print(f"📊 Total Registrations: {len(members)}")
        print()
        
        # Show all registrations with details
        print("📋 ALL REGISTRATION SUBMISSIONS")
        print("-" * 40)
        
        for i, member in enumerate(members, 1):
            data = member.to_dict()
            
            print(f"\n{i}. {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')}")
            print(f"   📧 DOE Email: {data.get('doeEmail', 'N/A')}")
            print(f"   📧 Personal Email: {data.get('personalEmail', 'N/A')}")
            print(f"   📱 Phone: {data.get('phoneNumber', 'N/A')}")
            print(f"   🎓 Grade: {data.get('grade', 'N/A')}")
            print(f"   👤 Member Type: {data.get('memberStatus', 'N/A')}")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            print(f"   👑 Admin Status: {data.get('adminStatus', 'N/A')}")
            
            # Events selected
            events = data.get('events', [])
            if events:
                print(f"   🎯 Events ({len(events)}): {', '.join(events)}")
            else:
                print(f"   🎯 Events: None selected")
            
            # Time commitments (for returning members)
            if data.get('memberStatus') == 'returning':
                preseason = data.get('preseasonHrs', 0)
                regseason = data.get('regseasonHrs', 0)
                postseason = data.get('postseasonHrs', 0)
                print(f"   ⏰ Time Commitments: Pre={preseason}h, Reg={regseason}h, Post={postseason}h")
            
            # Bio
            bio = data.get('bio', '')
            if bio:
                bio_preview = bio[:100] + "..." if len(bio) > 100 else bio
                print(f"   📝 Bio: {bio_preview}")
            
            # Member-specific fields
            if data.get('memberStatus') == 'new':
                interest_reason = data.get('interestReason', '')
                if interest_reason:
                    interest_preview = interest_reason[:100] + "..." if len(interest_reason) > 100 else interest_reason
                    print(f"   💭 Interest Reason: {interest_preview}")
                
                how_heard = data.get('howDidYouHearAboutUs', '')
                if how_heard:
                    print(f"   📢 How heard: {how_heard}")
            
            elif data.get('memberStatus') == 'returning':
                past_exp = data.get('pastExperience', '')
                if past_exp:
                    past_preview = past_exp[:100] + "..." if len(past_exp) > 100 else past_exp
                    print(f"   🏆 Past Experience: {past_preview}")
                
                return_reason = data.get('returnReason', '')
                if return_reason:
                    return_preview = return_reason[:100] + "..." if len(return_reason) > 100 else return_reason
                    print(f"   🔄 Return Reason: {return_preview}")
                
                years = data.get('yearsInTeam', 0)
                print(f"   📅 Years in Team: {years}")
            
            # Notification preferences
            important_notif = data.get('importantNotification', '')
            team_notif = data.get('teamNotification', '')
            event_notif = data.get('eventNotification', '')
            print(f"   🔔 Notifications: Important={important_notif}, Team={team_notif}, Event={event_notif}")
            
            # Contract and timestamps
            contract_accepted = data.get('contractAccepted', False)
            print(f"   📜 Contract Accepted: {contract_accepted}")
            
            created_at = data.get('createdAt', '')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_date = created_at
                    created_str = created_date.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"   🕒 Created: {created_str}")
                except:
                    print(f"   🕒 Created: {created_at}")
            
            print("   " + "-" * 50)
        
        # Show specific insights
        print("\n🔍 SPECIFIC INSIGHTS")
        print("-" * 20)
        
        # Find members with admin claims
        admin_members = [m for m in members if m.to_dict().get('adminStatus') == 'full']
        print(f"👑 Members claiming admin access: {len(admin_members)}")
        for member in admin_members:
            data = member.to_dict()
            print(f"   • {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')} ({data.get('doeEmail', 'N/A')})")
        
        # Find members who accepted contract
        contract_members = [m for m in members if m.to_dict().get('contractAccepted', False)]
        print(f"\n📜 Members who accepted contract: {len(contract_members)}")
        for member in contract_members:
            data = member.to_dict()
            print(f"   • {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')} ({data.get('doeEmail', 'N/A')})")
        
        # Find new members
        new_members = [m for m in members if m.to_dict().get('memberStatus') == 'new']
        print(f"\n🆕 New members: {len(new_members)}")
        for member in new_members:
            data = member.to_dict()
            print(f"   • {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')} ({data.get('doeEmail', 'N/A')})")
        
        # Find members with no events selected
        no_events = [m for m in members if not m.to_dict().get('events', [])]
        print(f"\n❌ Members with no events selected: {len(no_events)}")
        for member in no_events:
            data = member.to_dict()
            print(f"   • {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')} ({data.get('doeEmail', 'N/A')})")
        
        # Show grade distribution details
        print(f"\n📚 GRADE DISTRIBUTION DETAILS")
        print("-" * 30)
        grades = {}
        for member in members:
            grade = member.to_dict().get('grade', 'unknown')
            grades[grade] = grades.get(grade, 0) + 1
        
        for grade in sorted(grades.keys()):
            grade_members = [m for m in members if m.to_dict().get('grade') == grade]
            print(f"\nGrade {grade}: {grades[grade]} students")
            for member in grade_members:
                data = member.to_dict()
                print(f"   • {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')} ({data.get('doeEmail', 'N/A')})")
        
        # Export detailed data
        export_filename = f"detailed_registration_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'analysis_date': datetime.now().isoformat(),
            'total_registrations': len(members),
            'members': [{'id': m.id, **m.to_dict()} for m in members]
        }
        
        with open(export_filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed analysis exported to: {export_filename}")
        
    except Exception as e:
        print(f"❌ Error in detailed analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_analysis() 