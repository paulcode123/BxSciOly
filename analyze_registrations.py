#!/usr/bin/env python3
"""
Script to analyze past registration form submissions from Firebase
"""

from db_init import db
from datetime import datetime
import json

def analyze_registrations():
    """Analyze all registration submissions from the Members collection"""
    
    print("🔍 Analyzing Bronx Science Olympiad Registration Submissions")
    print("=" * 60)
    
    try:
        # Get all members from the database
        members_ref = db.collection('Members')
        members = list(members_ref.stream())
        
        if not members:
            print("❌ No registration submissions found in the database.")
            return
        
        print(f"📊 Total Registration Submissions: {len(members)}")
        print()
        
        # Basic statistics
        stats = {
            'total': len(members),
            'new_members': 0,
            'returning_members': 0,
            'grades': {},
            'status': {},
            'admin_status': {},
            'events_selected': {},
            'contract_accepted': 0,
            'admin_claims': 0
        }
        
        # Detailed member data
        member_details = []
        
        for member in members:
            data = member.to_dict()
            data['id'] = member.id
            
            # Count member types
            member_status = data.get('memberStatus', 'unknown')
            if member_status == 'new':
                stats['new_members'] += 1
            elif member_status == 'returning':
                stats['returning_members'] += 1
            
            # Count grades
            grade = data.get('grade', 'unknown')
            stats['grades'][grade] = stats['grades'].get(grade, 0) + 1
            
            # Count status
            status = data.get('status', 'unknown')
            stats['status'][status] = stats['status'].get(status, 0) + 1
            
            # Count admin status
            admin_status = data.get('adminStatus', 'none')
            stats['admin_status'][admin_status] = stats['admin_status'].get(admin_status, 0) + 1
            
            # Count events
            events = data.get('events', [])
            for event in events:
                stats['events_selected'][event] = stats['events_selected'].get(event, 0) + 1
            
            # Count contract acceptance
            if data.get('contractAccepted', False):
                stats['contract_accepted'] += 1
            
            # Count admin claims
            if data.get('adminStatus') == 'full':
                stats['admin_claims'] += 1
            
            member_details.append(data)
        
        # Print statistics
        print("📈 REGISTRATION STATISTICS")
        print("-" * 30)
        print(f"New Members: {stats['new_members']}")
        print(f"Returning Members: {stats['returning_members']}")
        print(f"Contract Accepted: {stats['contract_accepted']}")
        print(f"Admin Claims: {stats['admin_claims']}")
        print()
        
        print("📚 GRADE DISTRIBUTION")
        print("-" * 20)
        for grade in sorted(stats['grades'].keys()):
            print(f"Grade {grade}: {stats['grades'][grade]}")
        print()
        
        print("🏷️ STATUS DISTRIBUTION")
        print("-" * 20)
        for status in stats['status'].keys():
            print(f"{status.title()}: {stats['status'][status]}")
        print()
        
        print("👑 ADMIN STATUS DISTRIBUTION")
        print("-" * 25)
        for admin_status in stats['admin_status'].keys():
            print(f"{admin_status.title()}: {stats['admin_status'][admin_status]}")
        print()
        
        print("🎯 TOP EVENTS SELECTED")
        print("-" * 20)
        sorted_events = sorted(stats['events_selected'].items(), key=lambda x: x[1], reverse=True)
        for event, count in sorted_events[:10]:  # Top 10 events
            print(f"{event}: {count} selections")
        print()
        
        # Recent submissions (last 10)
        print("🕒 RECENT SUBMISSIONS (Last 10)")
        print("-" * 30)
        
        # Sort by creation date
        recent_members = sorted(member_details, 
                              key=lambda x: x.get('createdAt', ''), 
                              reverse=True)[:10]
        
        for member in recent_members:
            name = f"{member.get('firstName', 'N/A')} {member.get('lastName', 'N/A')}"
            email = member.get('doeEmail', 'N/A')
            grade = member.get('grade', 'N/A')
            status = member.get('status', 'N/A')
            created = member.get('createdAt', 'N/A')
            
            if created != 'N/A':
                try:
                    if isinstance(created, str):
                        created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    else:
                        created_date = created
                    created_str = created_date.strftime('%Y-%m-%d %H:%M')
                except:
                    created_str = str(created)
            else:
                created_str = 'Unknown'
            
            print(f"• {name} ({email}) - Grade {grade} - {status} - {created_str}")
        
        print()
        
        # Export detailed data to JSON
        export_filename = f"registration_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'analysis_date': datetime.now().isoformat(),
            'statistics': stats,
            'members': member_details
        }
        
        with open(export_filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"💾 Detailed analysis exported to: {export_filename}")
        
        # Show some interesting insights
        print()
        print("💡 INSIGHTS")
        print("-" * 10)
        
        if stats['new_members'] > stats['returning_members']:
            print("• More new members than returning members")
        else:
            print("• More returning members than new members")
        
        most_popular_grade = max(stats['grades'].items(), key=lambda x: x[1])
        print(f"• Most popular grade: Grade {most_popular_grade[0]} ({most_popular_grade[1]} students)")
        
        most_popular_event = max(stats['events_selected'].items(), key=lambda x: x[1])
        print(f"• Most popular event: {most_popular_event[0]} ({most_popular_event[1]} selections)")
        
        admin_percentage = (stats['admin_claims'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"• Admin claims: {admin_percentage:.1f}% of registrations")
        
        contract_percentage = (stats['contract_accepted'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"• Contract acceptance: {contract_percentage:.1f}% of registrations")
        
    except Exception as e:
        print(f"❌ Error analyzing registrations: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_registrations() 