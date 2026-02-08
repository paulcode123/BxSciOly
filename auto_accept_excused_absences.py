"""
Script to auto-accept all pending excused absence requests.
Updates all excused absences with status 'pending' to 'approved'.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def auto_accept_pending_absences():
    """Auto-accept all pending excused absence requests"""
    results = {
        'updated': [],
        'errors': []
    }
    
    try:
        # Query all excused absences with status 'pending'
        print("Querying pending excused absence requests...")
        pending_query = db.collection('ExcusedAbsences').where('status', '==', 'pending').stream()
        pending_absences = list(pending_query)
        
        print(f"Found {len(pending_absences)} pending excused absence requests.\n")
        
        if len(pending_absences) == 0:
            print("No pending requests to approve.")
            return results
        
        # Update each pending absence to approved
        for absence_doc in pending_absences:
            try:
                absence_id = absence_doc.id
                absence_data = absence_doc.to_dict()
                
                # Update status to approved and set reviewed timestamp
                db.collection('ExcusedAbsences').document(absence_id).update({
                    'status': 'approved',
                    'reviewedAt': firestore.SERVER_TIMESTAMP
                })
                
                # Get member info for display
                member_id = absence_data.get('memberId', 'Unknown')
                event_id = absence_data.get('eventId', 'Unknown')
                date_of_absence = absence_data.get('dateOfAbsence', 'Unknown')
                
                # Format date for display
                if isinstance(date_of_absence, datetime):
                    date_str = date_of_absence.strftime('%Y-%m-%d')
                else:
                    date_str = str(date_of_absence)
                
                print(f"  [APPROVED] Absence ID: {absence_id}")
                print(f"    Member: {member_id}, Event: {event_id}, Date: {date_str}")
                
                results['updated'].append({
                    'id': absence_id,
                    'memberId': member_id,
                    'eventId': event_id,
                    'dateOfAbsence': date_str
                })
                
            except Exception as e:
                print(f"  [ERROR] Error updating absence {absence_doc.id}: {e}")
                results['errors'].append({
                    'id': absence_doc.id,
                    'error': str(e)
                })
        
        # Print summary
        print("\n" + "="*60)
        print("Summary:")
        print("="*60)
        print(f"Successfully approved: {len(results['updated'])} requests")
        print(f"Errors: {len(results['errors'])} requests")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - Absence ID {error['id']}: {error['error']}")
        
        print("="*60)
        
    except Exception as e:
        print(f"\nError querying pending absences: {e}")
        import traceback
        traceback.print_exc()
        results['errors'].append({'error': str(e)})
    
    return results

if __name__ == '__main__':
    import sys
    
    try:
        print("="*60)
        print("Auto-Accept Pending Excused Absence Requests")
        print("="*60)
        print()
        
        # Skip confirmation if --yes flag is provided
        skip_confirmation = '--yes' in sys.argv or '-y' in sys.argv
        
        if not skip_confirmation:
            # Confirm before proceeding
            try:
                response = input("This will approve ALL pending excused absence requests. Continue? (yes/no): ")
                if response.lower() != 'yes':
                    print("Operation cancelled.")
                    exit(0)
            except EOFError:
                # If running non-interactively, proceed automatically
                print("Running in non-interactive mode. Proceeding with auto-accept...")
        
        print()
        results = auto_accept_pending_absences()
        print("\nAuto-accept operation completed!")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

