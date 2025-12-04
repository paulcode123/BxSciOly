from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs
import logging
import secrets
from datetime import timedelta
import smtplib
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
import csv
from collections import defaultdict

# Import competition parser
try:
    from competition_parser import get_all_competitions
except ImportError:
    # Fallback if parser not available
    def get_all_competitions():
        return []

# Try to import from our initialization module
try:
    from db_init import db
except ImportError:
    # If import fails, initialize Firebase here
    if not firebase_admin._apps:
        cred = credentials.Certificate('service_key.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'bxscioly-455318.appspot.com'
        })
    db = firestore.client()

# Get Firebase Storage bucket
bucket = storage.bucket('bxscioly-455318.appspot.com')

firebase_routes = Blueprint('firebase_routes', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------- Password Reset ----------------
@firebase_routes.route('/api/auth/request-password-reset', methods=['POST'])
def request_password_reset():
    """Initiate a password reset by DOE email.
    Creates a one-time token stored in Firestore with 1-hour expiry.
    """
    try:
        data = request.get_json() or {}
        email = data.get('doeEmail') or data.get('email')
        if not email:
            return jsonify({"error": "doeEmail is required"}), 400

        # Find member by DOE email
        query = db.collection('Members').where('doeEmail', '==', email).limit(1).stream()
        results = list(query)
        if not results:
            # Do not reveal account existence
            return jsonify({"message": "If an account exists, a reset email was sent."}), 200

        member = results[0]
        user_id = member.id

        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = firestore.SERVER_TIMESTAMP  # placeholder; also store explicit ttl_seconds

        # Store token doc
        reset_ref = db.collection('PasswordResets').document(token)
        reset_ref.set({
            'userId': user_id,
            'doeEmail': email,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'expiresInSeconds': 3600,
            'used': False
        })

        # Build reset link
        base_url = request.host_url.rstrip('/')
        reset_link = f"{base_url}/reset-password?token={token}"

        # Attempt to send email
        try:
            _send_password_reset_email(to_email=email, reset_link=reset_link)
            logger.info(f"Password reset email sent to {email}")
        except Exception as send_err:
            logger.error(f"Failed to send password reset email: {send_err}")
            # Still respond generically to avoid information leakage

        return jsonify({
            "message": "If an account exists, a reset email was sent.",
            "token": token  # Exposed for development convenience
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@firebase_routes.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Complete password reset with token and new password."""
    try:
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('newPassword')
        if not token or not new_password:
            return jsonify({"error": "token and newPassword are required"}), 400

        # Fetch token doc
        token_doc = db.collection('PasswordResets').document(token).get()
        if not token_doc.exists:
            return jsonify({"error": "Invalid or expired token"}), 400
        token_data = token_doc.to_dict()

        if token_data.get('used'):
            return jsonify({"error": "Token already used"}), 400

        # Basic expiry check: if createdAt older than expiresInSeconds
        created_at = token_data.get('createdAt')
        ttl = int(token_data.get('expiresInSeconds', 3600))
        try:
            # Firestore timestamp has .timestamp() when running in server
            if created_at and hasattr(created_at, 'timestamp'):
                import time
                if time.time() - created_at.timestamp() > ttl:
                    return jsonify({"error": "Token expired"}), 400
        except Exception:
            # If we cannot compute, allow but still mark used
            pass

        user_id = token_data.get('userId')
        if not user_id:
            return jsonify({"error": "Invalid token data"}), 400

        # Update password on Member document
        user_ref = db.collection('Members').document(user_id)
        if not user_ref.get().exists:
            return jsonify({"error": "User not found"}), 404
        user_ref.update({'password': new_password, 'updatedAt': firestore.SERVER_TIMESTAMP})

        # Invalidate token
        db.collection('PasswordResets').document(token).update({'used': True, 'usedAt': firestore.SERVER_TIMESTAMP})

        return jsonify({"message": "Password has been reset successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _send_password_reset_email(to_email: str, reset_link: str) -> None:
    """Send a password reset email via SMTP using credentials in api_keys.json.

    Expected keys in api_keys.json:
      - SMTP_HOST (e.g., 'smtp.gmail.com')
      - SMTP_PORT (e.g., 587)
      - SMTP_USER
      - SMTP_PASSWORD
      - SMTP_FROM (optional; defaults to SMTP_USER)
      - SMTP_USE_TLS (optional; defaults True)
    """
    # Load SMTP configuration
    with open('api_keys.json', 'r') as f:
        cfg = json.load(f)

    host = cfg.get('SMTP_HOST')
    port = int(cfg.get('SMTP_PORT', 587))
    user = cfg.get('SMTP_USER')
    password = cfg.get('SMTP_PASSWORD')
    from_addr = cfg.get('SMTP_FROM') or user
    use_tls = cfg.get('SMTP_USE_TLS', True)

    if not all([host, port, user, password, from_addr]):
        raise RuntimeError('SMTP configuration missing in api_keys.json')

    subject = 'Reset your Bronx Science Olympiad password'
    text_body = (
        'You requested a password reset.\n\n'
        f'Click the link to reset your password: {reset_link}\n\n'
        'This link expires in 1 hour. If you did not request this, ignore this email.'
    )
    html_body = (
        '<div style="font-family:Arial,Helvetica,sans-serif; font-size:14px; color:#222">'
        '<p>You requested a password reset.</p>'
        f'<p><a href="{reset_link}" target="_blank" '
        'style="display:inline-block;padding:10px 16px;background:#2c3e50;color:#fff;text-decoration:none;border-radius:6px">'
        'Reset Password</a></p>'
        f'<p>If the button does not work, copy and paste this link into your browser:<br>{reset_link}</p>'
        '<p>This link expires in 1 hour. If you did not request this, you can safely ignore this email.</p>'
        '</div>'
    )

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype='html')

    with smtplib.SMTP(host, port, timeout=15) as server:
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.send_message(msg)

@firebase_routes.route('/api/Competitions', methods=['GET'])
def get_competitions():
    """Get all competitions from text files (not Firebase)"""
    try:
        competitions = get_all_competitions()
        # Format to match Firebase structure: [{id: data}, ...]
        # Convert datetime objects to ISO strings for JSON serialization
        items = []
        for comp in competitions:
            comp_data = {}
            for k, v in comp.items():
                if k != 'id':
                    # Convert datetime to ISO string if needed
                    if hasattr(v, 'isoformat'):
                        comp_data[k] = v.isoformat()
                    else:
                        comp_data[k] = v
            items.append({comp['id']: comp_data})
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error loading competitions: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/<collection>', methods=['GET'])
def get_all(collection):
    """Get all documents from a collection"""
    # Skip Competitions collection - handled by specific route
    if collection == 'Competitions':
        return get_competitions()
    
    try:
        docs = db.collection(collection).stream()
        items = [{doc.id: doc.to_dict()} for doc in docs]
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/<collection>/<document_id>', methods=['GET'])
def get_one(collection, document_id):
    """Get a specific document from a collection"""
    try:
        doc = db.collection(collection).document(document_id).get()
        if doc.exists:
            return jsonify({doc.id: doc.to_dict()}), 200
        return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/<collection>', methods=['POST'])
def create(collection):
    """Create a new document in a collection"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Special handling for Members collection - check for duplicate DOE email
        if collection == 'Members':
            doe_email = data.get('doeEmail')
            if doe_email:
                # Check if a member with this DOE email already exists
                existing_members = db.collection('Members').where('doeEmail', '==', doe_email).limit(1).stream()
                if list(existing_members):
                    return jsonify({"error": "Email already in use. Try again."}), 409
            
            # Extract selected events before creating member
            selected_events = data.get('events', [])
            
            # Remove events from member data since it's not part of the Members schema
            member_data = {k: v for k, v in data.items() if k != 'events'}
            
            # Create the member first
            doc_ref = db.collection(collection).document()
            doc_ref.set(member_data)
            member_id = doc_ref.id
            
            # Add member ID to each selected event's members array
            if selected_events:
                for event_name in selected_events:
                    # Find the event by eventName
                    events_query = db.collection('Events').where('eventName', '==', event_name).limit(1).stream()
                    event_docs = list(events_query)
                    
                    if event_docs:
                        event_doc = event_docs[0]
                        event_ref = db.collection('Events').document(event_doc.id)
                        
                        # Get current members array and add the new member ID
                        current_data = event_doc.to_dict()
                        current_members = current_data.get('members', [])
                        
                        # Only add if not already in the array
                        if member_id not in current_members:
                            current_members.append(member_id)
                            event_ref.update({'members': current_members})
            
            return jsonify({"id": member_id, "message": "Member created successfully and added to selected events"}), 201
        else:
            # Regular document creation for other collections
            doc_ref = db.collection(collection).document()
            doc_ref.set(data)
            
            return jsonify({"id": doc_ref.id, "message": "Document created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/<collection>/<document_id>', methods=['PUT', 'PATCH'])
def update(collection, document_id):
    """Update a document in a collection"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
        
        # For PATCH, only update specified fields
        # For PUT, replace entire document
        if request.method == 'PATCH':
            doc_ref.update(data)
            message = "Document updated successfully"
        else:
            doc_ref.set(data)
            message = "Document replaced successfully"
        
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Meeting/<meeting_id>/checkin', methods=['POST'])
def meeting_checkin(meeting_id):
    """Atomically add a member to meeting attendance (prevents race conditions)"""
    try:
        data = request.get_json()
        if not data or 'memberId' not in data:
            return jsonify({"error": "memberId is required"}), 400
        
        member_id = data['memberId']
        
        # Get meeting reference
        meeting_ref = db.collection('Meeting').document(meeting_id)
        meeting = meeting_ref.get()
        
        if not meeting.exists:
            return jsonify({"error": "Meeting not found"}), 404
        
        # Use arrayUnion for atomic update - prevents race conditions
        meeting_ref.update({
            'attended': firestore.ArrayUnion([member_id])
        })
        
        return jsonify({
            "message": "Attendance recorded successfully",
            "meetingId": meeting_id,
            "memberId": member_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Meeting/generate-today', methods=['POST'])
def generate_todays_meetings():
    """Generate meetings for all events scheduled today based on schedule.txt"""
    try:
        import random
        import string
        from datetime import datetime, timezone
        
        # Read schedule.txt
        schedule_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'schedule.txt')
        with open(schedule_path, 'r') as f:
            schedule_text = f.read()
        
        # Get current day of week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        today = days[datetime.now().weekday()]
        
        # Parse schedule for today's events
        todays_events = []
        lines = schedule_text.split('\n')
        current_day = None
        current_block = None
        current_time = None
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this is a day header
            if line_stripped.endswith(':') and any(day in line_stripped for day in days):
                current_day = line_stripped.replace(':', '').strip()
                continue
            
            # Check if this is a block header
            if 'Block' in line_stripped and '(' in line_stripped:
                import re
                block_match = re.search(r'Block (\d+)', line_stripped)
                time_match = re.search(r'\((.*?)\)', line_stripped)
                if block_match and time_match:
                    current_block = block_match.group(1)
                    current_time = time_match.group(1)
                continue
            
            # Check if this is an event (starts with -)
            if line_stripped.startswith('- ') and current_day == today:
                event_name = line_stripped[2:].strip()
                todays_events.append({
                    'eventName': event_name,
                    'block': current_block,
                    'time': current_time
                })
        
        # Always add build events on Tues/Wed/Thurs - they meet both blocks every day
        # Each build event gets TWO meetings (one per block)
        build_events = ['Boomilever', 'Helicopter', 'Electric Vehicle', 'Robot Tour', 'Bungee Drop', 'Hovercraft']
        
        if today in ['Tuesday', 'Wednesday', 'Thursday']:
            for build_event in build_events:
                # Add Block 1 meeting
                todays_events.append({
                    'eventName': build_event,
                    'block': '1',
                    'time': '3:45 - 4:20 PM'
                })
                # Add Block 2 meeting
                todays_events.append({
                    'eventName': build_event,
                    'block': '2',
                    'time': '4:25 - 5:00 PM'
                })
        
        if not todays_events:
            return jsonify({
                "message": f"No events scheduled for {today}",
                "meetings": []
            }), 200
        
        # Check if today's meetings already exist
        today_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        today_start = today_date.replace(hour=0, minute=0)
        today_end = today_date.replace(hour=23, minute=59)
        
        # Query meetings for today
        meetings_ref = db.collection('Meeting')
        existing_meetings = meetings_ref.where('date', '>=', today_start).where('date', '<=', today_end).stream()
        existing_event_names = set([m.to_dict().get('eventName') for m in existing_meetings])
        
        # Generate codes and create meetings
        created_meetings = []
        
        def generate_code():
            """Generate random 5-letter code"""
            return ''.join(random.choices(string.ascii_uppercase, k=5))
        
        for event_info in todays_events:
            event_name = event_info['eventName']
            
            # Skip if meeting already exists for this event today
            if event_name in existing_event_names:
                continue
            
            code = generate_code()
            
            meeting_data = {
                'eventName': event_name,
                'date': today_date,
                'code': code,
                'block': event_info.get('block', ''),
                'room': '',  # Can be updated later
                'attended': []
            }
            
            # Create meeting
            meeting_ref = meetings_ref.document()
            meeting_ref.set(meeting_data)
            
            created_meetings.append({
                'id': meeting_ref.id,
                **meeting_data,
                'time': event_info.get('time', '')
            })
        
        return jsonify({
            "message": f"Created {len(created_meetings)} meetings for {today}",
            "meetings": created_meetings,
            "day": today,
            "alreadyExisted": len(existing_event_names)
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/<collection>/<document_id>', methods=['DELETE'])
def delete(collection, document_id):
    """Delete a document from a collection"""
    try:
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
        
        doc_ref.delete()
        return jsonify({"message": "Document deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Members/find-by-email/<email>', methods=['GET'])
def find_member_by_email(email):
    """Find a member by email address (legacy endpoint)"""
    try:
        # Query the Members collection for documents where email equals the provided email
        query = db.collection('Members').where('email', '==', email).limit(1).stream()
        
        # Convert the query result to a list
        results = list(query)
        
        if not results:
            return jsonify({"error": "No member found with this email"}), 404
        
        # Get the first matching document
        doc = results[0]
        return jsonify({doc.id: doc.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Members/find-by-doe-email/<doe_email>', methods=['GET'])
def find_member_by_doe_email(doe_email):
    """Find a member by DOE email address"""
    try:
        # Query the Members collection for documents where doeEmail equals the provided email
        query = db.collection('Members').where('doeEmail', '==', doe_email).limit(1).stream()
        
        # Convert the query result to a list
        results = list(query)
        
        if not results:
            return jsonify({"error": "No member found with this DOE email"}), 404
        
        # Get the first matching document
        doc = results[0]
        return jsonify({doc.id: doc.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/user/<user_id>', methods=['GET'])
def get_user_data(user_id):
    """Get user data by Firebase Auth UID (which is also the Firestore document ID)"""
    try:
        doc = db.collection('Members').document(user_id).get()
        if doc.exists:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return jsonify(user_data), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/binder-content/<binder_id>/<section_title>', methods=['GET'])
def get_binder_content(binder_id, section_title):
    """
    Get content for a specific binder section
    """
    try:
        # Construct blob path
        safe_section_title = section_title.replace('/', '_')
        blob_path = f"binders/{binder_id}/{safe_section_title}.html"
        
        # Check if blob exists
        blob = bucket.blob(blob_path)
        if not blob.exists():
            # Return empty content if file doesn't exist yet
            return jsonify({"content": ""})
        
        # Get content
        content = blob.download_as_text()
        return jsonify({"content": content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/binder-content/<binder_id>/<section_title>', methods=['POST'])
def update_binder_content(binder_id, section_title):
    """
    Update content for a specific binder section
    """
    try:
        # Get content from request
        data = request.json
        if not data or 'content' not in data:
            return jsonify({"error": "No content provided"}), 400
        
        content = data['content']
        
        # Save content to Firebase Storage
        safe_section_title = section_title.replace('/', '_')
        blob_path = f"binders/{binder_id}/{safe_section_title}.html"
        
        # Create blob and upload content with HTML content type
        blob = bucket.blob(blob_path)
        blob.upload_from_string(content, content_type='text/html')
        
        # Update binder document's updatedAt timestamp
        binder_ref = db.collection('Binders').document(binder_id)
        binder_ref.update({
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/profile-photo', methods=['POST'])
def upload_profile_photo():
    """
    Upload a profile photo to Firebase Storage and update the user's profile
    """
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        # Get file and user ID
        file = request.files['file']
        user_id = request.form.get('userId')
        
        if not user_id:
            return jsonify({"error": "No user ID provided"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check file type (only allow images)
        if not file.content_type.startswith('image/'):
            return jsonify({"error": "Only image files are allowed"}), 400
        
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"profile_{user_id}_{timestamp}.{file.filename.split('.')[-1]}"
        
        # Upload to Firebase Storage
        blob_path = f"profile_photos/{filename}"
        blob = bucket.blob(blob_path)
        
        # Set appropriate content type
        blob.upload_from_file(file, content_type=file.content_type)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Get the public URL
        url = blob.public_url
        
        # Update user document with the profile picture URL
        user_ref = db.collection('Members').document(user_id)
        user_ref.update({
            'profilePicUrl': url,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"url": url, "success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/notes-upload', methods=['POST'])
def upload_notes_file():
    """
    Upload a notes file to Firebase Storage for module completion
    """
    print("Uploading notes file")
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        # Get file and user ID
        file = request.files['file']
        user_id = request.form.get('userId')
        module_id = request.form.get('moduleId')
        
        if not user_id or not module_id:
            return jsonify({"error": "User ID and Module ID are required"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check file type (allow common document formats and images)
        allowed_types = ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'text/plain', 'image/png', 'image/jpeg', 'image/jpg']
        if file.content_type not in allowed_types:
            return jsonify({"error": "Only PDF, DOC, DOCX, TXT, PNG, and JPG files are allowed"}), 400
        
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_extension = file.filename.split('.')[-1]
        filename = f"notes_{user_id}_{module_id}_{timestamp}.{file_extension}"
        
        # Upload to Firebase Storage
        blob_path = f"notes/{filename}"
        blob = bucket.blob(blob_path)
        
        # Set appropriate content type
        blob.upload_from_file(file, content_type=file.content_type)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Get the public URL
        url = blob.public_url
        
        return jsonify({"url": url, "success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Members/<user_id>/addCompetitionResult', methods=['POST'])
def add_competition_result(user_id):
    """Add a competition result to a user's profile."""
    try:
        # Get the competition result from the request body
        competition_result = request.json
        
        # Validate the competition result
        if not competition_result or 'competitionName' not in competition_result:
            return jsonify({'error': 'Invalid competition result data'}), 400
        
        # Get a reference to the user document
        user_ref = db.collection('Members').document(user_id)
        
        # Update the user document with the new competition result
        # Use arrayUnion to add to the existing array without duplicates
        user_ref.update({
            'competitionResults': firestore.ArrayUnion([competition_result])
        })
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Competition result added to profile',
            'result': competition_result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@firebase_routes.route('/api/parse-duosmium', methods=['GET'])
def parse_duosmium():
    """Parse Duosmium results and store in database"""
    try:
        # Get URL parameter
        url = request.args.get('url')
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Parse the URL to extract competition info
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Extract competition name from URL path
        path_parts = parsed_url.path.strip('/').split('/')
        competition_name = path_parts[-1] if path_parts else "Unknown Competition"
        
        # Make request to Duosmium
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract team results (this is a simplified example)
        teams = []
        team_elements = soup.find_all('tr', class_='team-row')  # Adjust selector based on actual HTML structure
        
        for i, team_elem in enumerate(team_elements[:10]):  # Limit to top 10 teams for demo
            team_name = team_elem.find('td', class_='team-name')
            team_rank = team_elem.find('td', class_='rank')
            
            if team_name and team_rank:
                teams.append({
                    'teamName': team_name.get_text(strip=True),
                    'rank': int(team_rank.get_text(strip=True)) if team_rank.get_text(strip=True).isdigit() else i + 1,
                    'totalScore': 0,  # Would need to extract from HTML
                    'events': []  # Would need to extract from HTML
                })
        
        # Create Duosmium document
        duosmium_data = {
            'url': url,
            'competitionName': competition_name,
            'date': firestore.SERVER_TIMESTAMP,
            'location': 'Unknown',  # Would need to extract from HTML
            'teams': teams,
            'parsedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Save to database
        doc_ref = db.collection('Duosmium').document()
        doc_ref.set(duosmium_data)
        
        return jsonify({
            "id": doc_ref.id,
            "message": "Duosmium results parsed and stored successfully",
            "teams_count": len(teams)
        }), 201
        
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Admin Authentication Routes
@firebase_routes.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password required"}), 400
        
        email = data['email']
        password = data['password']
        
        # Find member by email
        member_query = db.collection('Members').where('doeEmail', '==', email).limit(1).stream()
        members = list(member_query)
        
        if not members:
            return jsonify({"error": "Invalid credentials"}), 401
        
        member = members[0]
        member_data = member.to_dict()
        
        # Check if member has full admin status (only full admins can access admin console)
        admin_status = member_data.get('adminStatus', 'none')
        if admin_status != 'full':
            return jsonify({"error": "Access denied. Full admin privileges required."}), 403
        
        # In production, you should hash and verify passwords properly
        # For now, we'll do a simple check (replace with proper authentication)
        if member_data.get('password') != password:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Determine admin role and permissions based on adminStatus
        admin_role = admin_status
        permissions = []
        
        if admin_status == 'full':
            permissions = ['all']
        elif admin_status == 'EM':
            permissions = ['events', 'members', 'attendance']
        elif admin_status == 'SD/BD':
            permissions = ['content', 'learning_modules', 'calendar']
        
        return jsonify({
            "adminId": member.id,  # Use member ID as admin ID
            "userId": member.id,
            "role": admin_role,
            "permissions": permissions,
            "userInfo": {
                "firstName": member_data['firstName'],
                "lastName": member_data['lastName'],
                "email": member_data['doeEmail']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/check-auth', methods=['GET'])
def check_admin_auth():
    """Check if user has admin privileges"""
    try:
        # Get admin ID from request headers or session
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin ID required"}), 401
        
        # Check if member exists and has admin status
        member_doc = db.collection('Members').document(admin_id).get()
        if not member_doc.exists:
            return jsonify({"error": "Invalid admin session"}), 401
        
        member_data = member_doc.to_dict()
        admin_status = member_data.get('adminStatus', 'none')
        
        # Only full admins can access admin console
        if admin_status != 'full':
            return jsonify({"error": "Full admin privileges required"}), 401
        
        # Determine admin role and permissions based on adminStatus
        admin_role = admin_status
        permissions = []
        
        if admin_status == 'full':
            permissions = ['all']
        elif admin_status == 'EM':
            permissions = ['events', 'members', 'attendance']
        elif admin_status == 'SD/BD':
            permissions = ['content', 'learning_modules', 'calendar']
        
        return jsonify({
            "adminId": admin_id,
            "role": admin_role,
            "permissions": permissions
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Admin Management Routes
@firebase_routes.route('/api/admin/attendance-events', methods=['GET'])
def get_attendance_events():
    """Get all attendance events for admin"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        # Get attendance events
        events_query = db.collection('AttendanceEvents').order_by('date', direction=firestore.Query.DESCENDING).stream()
        events = []
        
        for event in events_query:
            event_data = event.to_dict()
            event_data['id'] = event.id
            events.append(event_data)
        
        return jsonify(events), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/attendance-events', methods=['POST'])
def create_attendance_event():
    """Create a new attendance event"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Generate unique check-in code
        import random
        import string
        check_in_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create attendance event
        event_data = {
            'name': data.get('name'),
            'date': datetime.fromisoformat(data.get('date')),
            'startTime': datetime.fromisoformat(data.get('startTime')),
            'endTime': datetime.fromisoformat(data.get('endTime')),
            'description': data.get('description', ''),
            'location': data.get('location', ''),
            'checkInCode': check_in_code,
            'eventType': data.get('eventType', 'meeting'),
            'eventFor': data.get('eventFor', ['all']),
            'createdBy': admin_id,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'isActive': data.get('isActive', True)
        }
        
        doc_ref = db.collection('AttendanceEvents').document()
        doc_ref.set(event_data)
        
        return jsonify({
            "id": doc_ref.id,
            "checkInCode": check_in_code,
            "message": "Attendance event created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/members', methods=['GET'])
def get_members():
    """Get all members for admin management"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        # Verify full admin status
        member_doc = db.collection('Members').document(admin_id).get()
        if not member_doc.exists:
            return jsonify({"error": "Invalid admin session"}), 401
        
        member_data = member_doc.to_dict()
        admin_status = member_data.get('adminStatus', 'none')
        if admin_status != 'full':
            return jsonify({"error": "Full admin privileges required"}), 403
        
        # Get members
        members_query = db.collection('Members').order_by('lastName').stream()
        members = []
        
        for member in members_query:
            member_data = member.to_dict()
            member_data['id'] = member.id
            # Remove sensitive data
            member_data.pop('password', None)
            members.append(member_data)
        
        return jsonify(members), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/members/search', methods=['GET'])
def search_members():
    """Search members by name for autocomplete"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        # Verify full admin status
        member_doc = db.collection('Members').document(admin_id).get()
        if not member_doc.exists:
            return jsonify({"error": "Invalid admin session"}), 401
        
        member_data = member_doc.to_dict()
        admin_status = member_data.get('adminStatus', 'none')
        if admin_status != 'full':
            return jsonify({"error": "Full admin privileges required"}), 403
        
        query = request.args.get('q', '').strip().lower()
        if not query or len(query) < 2:
            return jsonify([]), 200
        
        # Load team members from team_placement_solution.csv
        team_member_ids = set()
        try:
            with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    firebase_id = row.get('firebaseID', '').strip()
                    if firebase_id:
                        team_member_ids.add(firebase_id)
            logger.info(f"Loaded {len(team_member_ids)} team members from team_placement_solution.csv")
        except Exception as e:
            logger.warning(f"Could not load team members: {e}")
            # If we can't load the team file, fall back to all members
            team_member_ids = None
        
        # Get all members and filter
        members_query = db.collection('Members').stream()
        results = []
        
        for member in members_query:
            # Skip if not in team (unless we couldn't load the team file)
            if team_member_ids is not None and member.id not in team_member_ids:
                continue
            
            member_data = member.to_dict()
            first_name = (member_data.get('firstName', '') or '').lower()
            last_name = (member_data.get('lastName', '') or '').lower()
            full_name = f"{first_name} {last_name}".strip()
            
            if query in first_name or query in last_name or query in full_name:
                results.append({
                    'id': member.id,
                    'firstName': member_data.get('firstName', ''),
                    'lastName': member_data.get('lastName', ''),
                    'doeEmail': member_data.get('doeEmail', ''),
                    'displayName': f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                })
        
        # Sort by relevance (exact matches first, then by name)
        results.sort(key=lambda x: (
            0 if query in x['displayName'].lower() else 1,
            x['displayName'].lower()
        ))
        
        return jsonify(results[:20]), 200  # Limit to 20 results
        
    except Exception as e:
        logger.error(f"Error searching members: {e}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/members/<member_id>/debug-mason', methods=['GET'])
def debug_mason_data(member_id):
    """Debug endpoint to check Mason data for a member"""
    try:
        # Get member data
        member_doc = db.collection('Members').document(member_id).get()
        if not member_doc.exists:
            return jsonify({"error": "Member not found"}), 404
        
        member_data = member_doc.to_dict()
        member_name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
        
        # Read Mason placements
        mason_partners = {}
        all_events_parsed = []
        with open('Planning/Mason Invitational 2026 Placements - Team A.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames if reader else []
            logger.info(f"CSV Headers: {headers}")
            logger.info(f"Looking for member: '{member_name}'")
            
            for i, row in enumerate(reader):
                # Event name is in the first column
                first_key = list(row.keys())[0] if row.keys() else None
                event_name = row.get(first_key, '').strip() if first_key else None
                
                if not event_name:
                    continue
                
                all_events_parsed.append(event_name)
                
                # Get all COMPETITORS columns (first 2-3 columns after event name)
                competitors = []
                row_keys = list(row.keys())[1:7]
                logger.info(f"Row {i}: Event='{event_name}', Columns to check: {row_keys}")
                
                for key in row_keys:
                    comp_name = row.get(key, '').strip()
                    if comp_name and 'COMPETITOR' not in key.upper() and 'GRADE' not in key.upper():
                        competitors.append(comp_name)
                        logger.info(f"  - Added competitor: '{comp_name}' from column '{key}'")
                
                logger.info(f"Event: {event_name}, Competitors: {competitors}, Looking for: {member_name}")
                
                # Check if member is in this event (case-insensitive)
                for comp in competitors:
                    if member_name.lower() == comp.lower():
                        partners = [c for c in competitors if c.lower() != member_name.lower()]
                        mason_partners[event_name] = partners
                        logger.info(f"MATCH FOUND: {member_name} in {event_name} with partners: {partners}")
                        break
        
        return jsonify({
            'member_name': member_name,
            'all_events_parsed': all_events_parsed,
            'partner_events': mason_partners,
            'summary': f"{len(mason_partners)} events, parsed {len(all_events_parsed)} events total"
        }), 200
        
        # Read Mason feedback
        partner_feedback = {}
        feedback_count = 0
        
        with open('Planning/2026 Mason Invitational Feedback Form (Responses) - Form Responses 1.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_name = row.get('Name (First Last)', '').strip()
                partnership_response = row.get('How did you feel about your partnerships? Rate each from 1-5 and explain why you gave the rating. Do this for each event you competed in, with a brief explanation. (Would you compete with this partner again? How was the collaboration? How was the preparation and communication in the weeks leading up to competition day?)', '').strip()
                
                if not partnership_response:
                    continue
                
                # Check if this person is a partner
                for event_name, partners in mason_partners.items():
                    matched_partner_name = None
                    for partner_name in partners:
                        if row_name.lower().strip() == partner_name.lower().strip():
                            matched_partner_name = partner_name
                            break
                    
                    if matched_partner_name:
                        if event_name not in partner_feedback:
                            partner_feedback[event_name] = {}
                        partner_feedback[event_name][matched_partner_name] = {
                            'partnershipRating': partnership_response
                        }
                        feedback_count += 1
        
        return jsonify({
            'member_name': member_name,
            'partner_events': mason_partners,
            'partner_feedback': partner_feedback,
            'feedback_count': feedback_count,
            'summary': f"{len(mason_partners)} events, {feedback_count} feedback entries"
        }), 200
    except Exception as e:
        logger.error(f"Debug error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@firebase_routes.route('/api/admin/members/<member_id>/full', methods=['GET'])
def get_member_full_data(member_id):
    """Get comprehensive member data including CSV data, attendance, etc."""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        # Verify full admin status
        admin_doc = db.collection('Members').document(admin_id).get()
        if not admin_doc.exists:
            return jsonify({"error": "Invalid admin session"}), 401
        
        admin_data = admin_doc.to_dict()
        admin_status = admin_data.get('adminStatus', 'none')
        if admin_status != 'full':
            return jsonify({"error": "Full admin privileges required"}), 403
        
        # Get member from database
        member_doc = db.collection('Members').document(member_id).get()
        if not member_doc.exists:
            return jsonify({"error": "Member not found"}), 404
        
        member_data = member_doc.to_dict()
        member_data['id'] = member_doc.id
        
        # Remove password
        member_data.pop('password', None)
        
        # Get bxsciolyID from mapping CSV
        bxscioly_id = None
        bxscioly_number = None
        try:
            with open('Planning/SCIOLY MEMBER IDS - member_names_ids_20250929_074942.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['id'] == member_id:
                        bxscioly_number = row.get('bxscioly_number', '')
                        if bxscioly_number and bxscioly_number.startswith('bxscioly_'):
                            bxscioly_id = bxscioly_number.replace('bxscioly_', '')
                        break
        except Exception as e:
            logger.warning(f"Could not read member IDs CSV: {e}")
        
        result = {
            'basicInfo': {
                'id': member_data.get('id'),
                'firstName': member_data.get('firstName', ''),
                'lastName': member_data.get('lastName', ''),
                'doeEmail': member_data.get('doeEmail', ''),
                'personalEmail': member_data.get('personalEmail', ''),
                'bxsciEmail': member_data.get('bxsciEmail', ''),
                'bxsciolyID': bxscioly_number or '',
                'phoneNumber': member_data.get('phoneNumber', ''),
                'grade': member_data.get('grade', ''),
                'yearsInTeam': member_data.get('yearsInTeam', 0),
                'memberStatus': member_data.get('memberStatus', ''),
                'house': member_data.get('house', ''),
                'createdAt': member_data.get('createdAt'),
            },
            'eventSelectionForm': None,
            'diagnosticScores': [],
            'competitionPlacements': [],
            'events': [],
            'masonInvitational': None
        }
        
        # Get event selection form responses
        try:
            with open('Planning/BxSciOly \'25-\'26_ Event Selection Form  (Responses) - Form Responses 1 (1).csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Normalize member data for matching
                member_doe_email = (member_data.get('doeEmail', '') or '').strip().lower()
                member_personal_email = (member_data.get('personalEmail', '') or '').strip().lower()
                member_first_name = (member_data.get('firstName', '') or '').strip().lower()
                member_last_name = (member_data.get('lastName', '') or '').strip().lower()
                member_full_name = f"{member_first_name} {member_last_name}".strip()
                
                for row in reader:
                    # Try to get DOE email from CSV (handle column name with trailing space)
                    csv_doe_email = (row.get('DOE Email (Make sure there are no typos. We will be sending all important information to your DOE email.) ', '') or '').strip().lower()
                    if not csv_doe_email:
                        csv_doe_email = (row.get('DOE Email (Make sure there are no typos. We will be sending all important information to your DOE email.)', '') or '').strip().lower()
                    
                    # Try to get BXSCI email from CSV (check both BXSCI Email and Email Address columns)
                    csv_bxsci_email = (row.get('BXSCI Email', '') or '').strip().lower()
                    csv_email_address = (row.get('Email Address', '') or '').strip().lower()
                    if not csv_bxsci_email and csv_email_address:
                        csv_bxsci_email = csv_email_address
                    
                    # Try to get name from CSV (format: "Last, First" or "First Last")
                    csv_name = (row.get('Name (First, Last)', '') or '').strip()
                    csv_name_lower = csv_name.lower()
                    
                    # Match by DOE email
                    doe_email_match = csv_doe_email and member_doe_email and csv_doe_email == member_doe_email
                    
                    # Match by BXSCI email (check against personalEmail and doeEmail)
                    bxsci_email_match = csv_bxsci_email and (
                        csv_bxsci_email == member_personal_email or
                        csv_bxsci_email == member_doe_email
                    )
                    
                    # Match by name as fallback (handle "Last, First" format)
                    name_match = False
                    if csv_name_lower and member_full_name:
                        # Try direct match
                        if csv_name_lower == member_full_name:
                            name_match = True
                        # Try "Last, First" format
                        elif ',' in csv_name:
                            csv_parts = [p.strip() for p in csv_name_lower.split(',')]
                            if len(csv_parts) == 2:
                                csv_last, csv_first = csv_parts
                                if csv_last == member_last_name and csv_first == member_first_name:
                                    name_match = True
                        # Try reversed format
                        elif csv_name_lower == f"{member_last_name}, {member_first_name}":
                            name_match = True
                    
                    if doe_email_match or bxsci_email_match or name_match:
                        # Get all the form fields - use the exact column names from the CSV
                        doe_email_col = 'DOE Email (Make sure there are no typos. We will be sending all important information to your DOE email.) '
                        past_experience_col = 'If you have past SciOly experience (Division B/C), please list prior competition/medals. Use the template below to format your competitions.\n\n[Year] - [Invitational Name] - [Event Name (Place)]\nExample:\n2024 - Lexington Invitational - Anatomy (2nd), Disease Detectives (5th)\n2023 - BirdSO Invitational - Forensics (1st)\nIf you participated but did not receive a medal, you may still list the invitational and events. '
                        events_selected_col = 'What events would you like to take diagnostics for? Please select at least three (this is MANDATORY). We strongly recommend trying out for more than 3, as you may not be accepted to all the events you try out for. Keep in mind that each additional event comes with its own time commitment, and that you cannot select more than 6 events! The more events you select and take diagnostics for, the higher your chances of getting onto the team!'
                        qualifications_col = 'Please make a list of all qualifications that you have (classes, knowledge, experiences, extracurriculars, etc.) relevant to the events you are applying for. This is OPTIONAL, but may strengthen your application.\n\nFor example, a person applying to A&P might include:\n- AP Biology (5 on the AP)\n- Took Anatomy class at Hunter\n- Brain cancer research at Weill Cornell Medicine'
                        additional_info_col = 'Is there anything else you would like us to know? Any questions?'
                        
                        result['eventSelectionForm'] = {
                            'timestamp': row.get('Timestamp', ''),
                            'name': row.get('Name (First, Last)', ''),
                            'doeEmail': row.get(doe_email_col, '') or csv_doe_email,
                            'bxsciEmail': row.get('BXSCI Email', '') or row.get('Email Address', '') or csv_bxsci_email,
                            'grade': row.get('Grade', ''),
                            'memberType': row.get('New or returning member?', ''),
                            'yearsOnTeam': row.get('If returning, how many years have you been on the Bronx Science SciOly team for?', ''),
                            'pastExperience': row.get(past_experience_col, ''),
                            'eventsSelected': row.get(events_selected_col, ''),
                            'whyJoin': row.get('Why do you want to join the team? Be specific but concise. (1000 characters max)', ''),
                            'eventRankings': row.get('What draws you to the events that you selected? Why would you like to join said event? Please rank the events you chose (number them in order) with a concise explanation.', ''),
                            'qualifications': row.get(qualifications_col, ''),
                            'additionalInfo': row.get(additional_info_col, '')
                        }
                        logger.info(f"Matched event selection form for {member_id} ({member_data.get('firstName', '')} {member_data.get('lastName', '')}) by {'DOE email' if doe_email_match else 'BXSCI email' if bxsci_email_match else 'name'}")
                        break
        except Exception as e:
            logger.warning(f"Could not read event selection form CSV: {e}")
            import traceback
            logger.warning(traceback.format_exc())
        
        # Get diagnostic scores with rank and percentile
        if bxscioly_id:
            try:
                # First, get scores from consolidated_scores.csv
                diagnostic_events = []
                with open('Planning/consolidated_scores.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('bxsciolyID') == bxscioly_id:
                            for i in range(1, 9):
                                event_key = f'Event{i}'
                                score_key = f'Score{i}'
                                if row.get(event_key) and row.get(score_key):
                                    diagnostic_events.append({
                                        'event': row[event_key],
                                        'score': float(row[score_key]) if row[score_key] else 0
                                    })
                            break
                
                # Then, get rank and percentile from team_placement_by_event.csv
                event_rankings = {}
                try:
                    with open('Planning/team_placement_by_event.csv', 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('bxsciolyID') == bxscioly_id:
                                event_name = row.get('event', '').strip()
                                if event_name:
                                    event_rankings[event_name] = {
                                        'rank': int(row.get('eventRank', 0)) if row.get('eventRank') else None,
                                        'percentile': float(row.get('eventPercentile', 0)) if row.get('eventPercentile') else None
                                    }
                except Exception as e:
                    logger.warning(f"Could not read team placement by event CSV: {e}")
                
                # Merge rank and percentile data into diagnostic events
                for diag_event in diagnostic_events:
                    event_name = diag_event['event']
                    if event_name in event_rankings:
                        diag_event['rank'] = event_rankings[event_name]['rank']
                        diag_event['percentile'] = event_rankings[event_name]['percentile']
                    else:
                        # If not found in placement file, try to calculate from consolidated_scores
                        try:
                            event_scores = []
                            with open('Planning/consolidated_scores.csv', 'r', encoding='utf-8') as f:
                                reader = csv.DictReader(f)
                                for row in reader:
                                    for i in range(1, 9):
                                        if row.get(f'Event{i}') == event_name and row.get(f'Score{i}'):
                                            event_scores.append((float(row[f'Score{i}']), row.get('bxsciolyID', '')))
                            
                            if event_scores:
                                # Sort by score descending
                                event_scores.sort(key=lambda x: x[0], reverse=True)
                                total_participants = len(event_scores)
                                
                                # Find user's rank
                                user_rank = None
                                for idx, (score, bid) in enumerate(event_scores):
                                    if bid == bxscioly_id:
                                        user_rank = idx + 1
                                        break
                                
                                if user_rank:
                                    diag_event['rank'] = user_rank
                                    diag_event['percentile'] = round(((total_participants - user_rank + 1) / total_participants) * 100, 2) if total_participants > 0 else None
                        except Exception as e:
                            logger.warning(f"Could not calculate rank/percentile for {event_name}: {e}")
                
                result['diagnosticScores'] = diagnostic_events
            except Exception as e:
                logger.warning(f"Could not read consolidated scores CSV: {e}")
        
        # Get competition placements
        try:
            # First, get all members to create a name map for partner resolution
            members_map = {}
            members_query = db.collection('Members').stream()
            for m in members_query:
                m_data = m.to_dict()
                first_name = m_data.get('firstName', '')
                last_name = m_data.get('lastName', '')
                full_name = f"{first_name} {last_name}".strip()
                members_map[m.id] = full_name
            
            # Helper function to normalize names for comparison (matches competitions.html)
            def normalize_name(name):
                return str(name or '').strip().lower().replace('  ', ' ')
            
            # Get the current member's full name (normalized)
            member_full_name_normalized = normalize_name(f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}")
            
            logger.info(f"Looking for competitions for member {member_id} (name: {member_full_name_normalized})")
            
            # Get competitions and build placements list
            competitions_query = db.collection('Competitions').stream()
            placements_added = set()  # Track (comp_name, event, team) to avoid duplicates
            
            for comp in competitions_query:
                comp_data = comp.to_dict()
                comp_name = comp_data.get('name', '')
                comp_date = comp_data.get('date')
                
                # Check if member participated in this competition (by ID OR by name)
                member_participations = []
                if comp_data.get('teamPlacement'):
                    for placement in comp_data['teamPlacement']:
                        participants = placement.get('participants', [])
                        
                        # Check if member participated (by ID or by name)
                        member_participated = False
                        
                        # Check by ID
                        if member_id in participants:
                            member_participated = True
                        else:
                            # Check by name (resolve participant IDs to names and compare)
                            for p in participants:
                                # Resolve the participant to a name
                                if p in members_map:
                                    p_name_normalized = normalize_name(members_map[p])
                                else:
                                    # It might already be a name
                                    p_name_normalized = normalize_name(p)
                                
                                if p_name_normalized == member_full_name_normalized:
                                    member_participated = True
                                    break
                        
                        if member_participated:
                            member_participations.append({
                                'event': placement.get('event', ''),
                                'team': placement.get('team', ''),
                                'participants': participants
                            })
                
                # For each participation, try to find the result
                for participation in member_participations:
                    event_name = participation['event']
                    team = participation['team']
                    participants = participation['participants']
                    
                    # Create unique key to avoid duplicates
                    placement_key = (comp_name, event_name, team)
                    if placement_key in placements_added:
                        continue
                    
                    # Get result if available
                    placement_data = None
                    out_of = None
                    
                    if comp_data.get('results') and comp_data['results'].get('eventResults'):
                        for event_result in comp_data['results']['eventResults']:
                            # Case-insensitive event name matching
                            if (normalize_name(event_result.get('eventName', '')) == normalize_name(event_name) 
                                and event_result.get('team') == team):
                                placement_data = event_result.get('placement')
                                out_of = event_result.get('outOf')
                                break
                    
                    # Resolve partner names
                    partner_names = []
                    for p in participants:
                        # Skip the current member
                        p_is_current_member = False
                        if p == member_id:
                            p_is_current_member = True
                        elif p in members_map:
                            if normalize_name(members_map[p]) == member_full_name_normalized:
                                p_is_current_member = True
                        elif normalize_name(p) == member_full_name_normalized:
                            p_is_current_member = True
                        
                        if not p_is_current_member:
                            # Resolve to name
                            if p in members_map:
                                partner_names.append(members_map[p])
                            else:
                                # It might already be a name
                                partner_names.append(p)
                    
                    # Add to results
                    result['competitionPlacements'].append({
                        'competitionName': comp_name,
                        'competitionDate': comp_date,
                        'event': event_name,
                        'team': team,
                        'placement': placement_data,
                        'outOf': out_of,
                        'partners': partner_names
                    })
                    
                    placements_added.add(placement_key)
            
            logger.info(f"Found {len(result['competitionPlacements'])} competition placements for member {member_id}")
                    
        except Exception as e:
            logger.warning(f"Error getting competition placements: {e}")
            import traceback
            logger.warning(traceback.format_exc())
        
        # Get events the member is in
        try:
            events_query = db.collection('Events').stream()
            member_events = []
            for event in events_query:
                event_data = event.to_dict()
                if member_id in event_data.get('members', []):
                    member_events.append({
                        'id': event.id,
                        'eventName': event_data.get('eventName', ''),
                        'subject': event_data.get('subject', ''),
                        'meetingDay': event_data.get('meetingDay', ''),
                        'meetingBlock': event_data.get('meetingBlock', ''),
                        'meetingRoom': event_data.get('meetingRoom', '')
                    })
            result['events'] = member_events
        except Exception as e:
            logger.warning(f"Error getting member events: {e}")
        
        # Get attendance for each event
        build_events = ['Boomilever', 'Helicopter', 'Electric Vehicle', 'Robot Tour', 'Bungee Drop', 'Hovercraft']
        
        for event_info in result['events']:
            event_id = event_info['id']
            event_name = event_info['eventName']
            is_build_event = event_name in build_events
            
            # Get all meetings for this event - fetch all and filter in Python for case-insensitive matching
            try:
                # Get ALL meetings and filter by event name (case-insensitive) - matches meetings.html approach
                all_meetings_query = db.collection('Meeting').stream()
                meetings = []
                event_name_normalized = event_name.strip().lower()
                
                for meeting in all_meetings_query:
                    meeting_data = meeting.to_dict()
                    meeting_event_name = (meeting_data.get('eventName', '') or '').strip()
                    
                    # Case-insensitive matching (like meetings.html does)
                    if meeting_event_name.lower() != event_name_normalized:
                        continue
                    
                    # Handle date field - can be Firestore timestamp or datetime
                    meeting_date = meeting_data.get('date')
                    if meeting_date is None:
                        continue
                    
                    # Convert Firestore timestamp to datetime in UTC
                    from datetime import timezone
                    if hasattr(meeting_date, 'timestamp'):  # Firestore Timestamp object
                        meeting_date = meeting_date.timestamp()
                        meeting_date = datetime.fromtimestamp(meeting_date, tz=timezone.utc)
                    elif isinstance(meeting_date, dict):
                        if 'seconds' in meeting_date:
                            meeting_date = datetime.fromtimestamp(meeting_date['seconds'], tz=timezone.utc)
                        elif '_seconds' in meeting_date:
                            meeting_date = datetime.fromtimestamp(meeting_date['_seconds'], tz=timezone.utc)
                        else:
                            continue
                    elif isinstance(meeting_date, str):
                        try:
                            meeting_date = datetime.fromisoformat(meeting_date.replace('Z', '+00:00'))
                        except:
                            try:
                                meeting_date = datetime.fromisoformat(meeting_date)
                            except:
                                try:
                                    # Try RFC2822 format: "Tue, 25 Nov 2025 12:00:00 GMT"
                                    meeting_date = parsedate_to_datetime(meeting_date)
                                except:
                                    logger.warning(f"Could not parse meeting date: {meeting_date}")
                                    continue
                    
                    # Check if member attended
                    attended_list = meeting_data.get('attended', []) or []
                    attended = member_id in attended_list
                    
                    meetings.append({
                        'id': meeting.id,
                        'date': meeting_date.isoformat() if isinstance(meeting_date, datetime) else str(meeting_date),
                        'attended': attended,
                        'code': meeting_data.get('code', '')
                    })
                
                # Sort meetings by date
                meetings.sort(key=lambda x: x['date'])
                
                logger.info(f"Found {len(meetings)} meetings for event '{event_name}' (normalized: '{event_name_normalized}', member {member_id})")
                
                # Get excused absences for this event
                excused_query = db.collection('ExcusedAbsences').where('memberId', '==', member_id).where('eventId', '==', event_id).where('status', '==', 'approved').stream()
                excused_absences = []
                for absence in excused_query:
                    absence_data = absence.to_dict()
                    absence_date = absence_data.get('dateOfAbsence')
                    
                    if absence_date is None:
                        continue
                    
                    # Convert Firestore timestamp to UTC
                    from datetime import timezone
                    if hasattr(absence_date, 'timestamp'):
                        absence_date = datetime.fromtimestamp(absence_date.timestamp(), tz=timezone.utc)
                    elif isinstance(absence_date, dict):
                        if 'seconds' in absence_date:
                            absence_date = datetime.fromtimestamp(absence_date['seconds'], tz=timezone.utc)
                        elif '_seconds' in absence_date:
                            absence_date = datetime.fromtimestamp(absence_date['_seconds'], tz=timezone.utc)
                        else:
                            continue
                    elif isinstance(absence_date, str):
                        try:
                            absence_date = datetime.fromisoformat(absence_date.replace('Z', '+00:00'))
                        except:
                            try:
                                absence_date = datetime.fromisoformat(absence_date)
                            except:
                                try:
                                    # Try RFC2822 format: "Tue, 25 Nov 2025 12:00:00 GMT"
                                    absence_date = parsedate_to_datetime(absence_date)
                                except:
                                    logger.warning(f"Could not parse absence date: {absence_date}")
                                    continue
                    
                    excused_absences.append({
                        'date': absence_date.isoformat() if isinstance(absence_date, datetime) else str(absence_date),
                        'reason': absence_data.get('reason', ''),
                        'adminComments': absence_data.get('adminComments', '')
                    })
                
                if is_build_event:
                    # For build events: group by week
                    weekly_data = defaultdict(lambda: {'buildMeetings': 0, 'excused': []})
                    
                    for meeting in meetings:
                        try:
                            meeting_date = datetime.fromisoformat(meeting['date'].replace('Z', '+00:00')) if 'T' in meeting['date'] else datetime.fromisoformat(meeting['date'])
                            # Convert to UTC if needed to handle timezone-aware dates correctly
                            if meeting_date.tzinfo is not None:
                                from datetime import timezone as dt_timezone
                                meeting_date = meeting_date.astimezone(dt_timezone.utc)
                            year, week_num, _ = meeting_date.isocalendar()
                            week_key = f"{year}-W{week_num:02d}"
                            
                            if meeting['attended']:
                                weekly_data[week_key]['buildMeetings'] += 1
                        except Exception as e:
                            logger.warning(f"Error processing meeting date for build event: {e}")
                            continue
                    
                    for excused in excused_absences:
                        try:
                            excused_date = datetime.fromisoformat(excused['date'].replace('Z', '+00:00')) if 'T' in excused['date'] else datetime.fromisoformat(excused['date'])
                            # Convert to UTC if needed to handle timezone-aware dates correctly
                            if excused_date.tzinfo is not None:
                                from datetime import timezone as dt_timezone
                                excused_date = excused_date.astimezone(dt_timezone.utc)
                            year, week_num, _ = excused_date.isocalendar()
                            week_key = f"{year}-W{week_num:02d}"
                            weekly_data[week_key]['excused'].append(excused)
                        except Exception as e:
                            logger.warning(f"Error processing excused absence date: {e}")
                            continue
                    
                    event_info['attendance'] = {
                        'type': 'build',
                        'weeklyData': dict(weekly_data)
                    }
                else:
                    # For non-build events: show each meeting
                    meeting_attendance = []
                    for meeting in meetings:
                        try:
                            meeting_date = datetime.fromisoformat(meeting['date'].replace('Z', '+00:00')) if 'T' in meeting['date'] else datetime.fromisoformat(meeting['date'])
                            # Convert to UTC if needed to handle timezone-aware dates correctly
                            if meeting_date.tzinfo is not None:
                                from datetime import timezone as dt_timezone
                                meeting_date_only = meeting_date.astimezone(dt_timezone.utc).date()
                            else:
                                meeting_date_only = meeting_date.date()
                            
                            # Find matching excused absence
                            excused_match = None
                            for excused in excused_absences:
                                try:
                                    excused_date = datetime.fromisoformat(excused['date'].replace('Z', '+00:00')) if 'T' in excused['date'] else datetime.fromisoformat(excused['date'])
                                    # Convert to UTC if needed to handle timezone-aware dates correctly
                                    if excused_date.tzinfo is not None:
                                        from datetime import timezone as dt_timezone
                                        excused_date_only = excused_date.astimezone(dt_timezone.utc).date()
                                    else:
                                        excused_date_only = excused_date.date()
                                    if excused_date_only == meeting_date_only:
                                        excused_match = excused
                                        break
                                except Exception as e:
                                    continue
                            
                            status = 'present' if meeting['attended'] else ('excused' if excused_match else 'unexcused')
                            meeting_attendance.append({
                                'date': meeting['date'],
                                'status': status,
                                'excuse': excused_match['reason'] if excused_match else None,
                                'adminComments': excused_match['adminComments'] if excused_match else None
                            })
                        except Exception as e:
                            logger.warning(f"Error processing meeting: {e}")
                            continue
                    
                    event_info['attendance'] = {
                        'type': 'non-build',
                        'meetings': meeting_attendance
                    }
            except Exception as e:
                logger.warning(f"Error getting attendance for event {event_name}: {e}")
                import traceback
                logger.warning(traceback.format_exc())
                # Set empty attendance data
                if is_build_event:
                    event_info['attendance'] = {
                        'type': 'build',
                        'weeklyData': {}
                    }
                else:
                    event_info['attendance'] = {
                        'type': 'non-build',
                        'meetings': []
                    }
        
        # Get Mason Invitational data
        try:
            mason_partners = {}
            member_name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
            
            with open('Planning/Mason Invitational 2026 Placements - Team A.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Event name is in the first column
                    first_key = list(row.keys())[0] if row.keys() else None
                    event_name = row.get(first_key, '').strip() if first_key else None
                    
                    if not event_name:
                        continue
                    
                    # Get all COMPETITORS columns (first 2-3 columns after event name)
                    competitors = []
                    for key in list(row.keys())[1:7]:  # Check columns 2-7 (typical COMPETITORS columns)
                        comp_name = row.get(key, '').strip()
                        if comp_name and 'COMPETITOR' not in key.upper() and 'GRADE' not in key.upper():
                            competitors.append(comp_name)
                    
                    # Check if member is in this event (case-insensitive)
                    for comp in competitors:
                        if member_name.lower() == comp.lower():
                            partners = [c for c in competitors if c.lower() != member_name.lower()]
                            mason_partners[event_name] = partners
                            break
            
            # Read Mason feedback CSV
            mason_feedback = None
            partner_feedback = {}
            
            with open('Planning/2026 Mason Invitational Feedback Form (Responses) - Form Responses 1.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_name = row.get('Name (First Last)', '').strip()
                    row_doe_email = row.get('DOE Email', '').strip().lower()
                    row_bxsci_email = row.get('BXSCI Email', '').strip().lower()
                    
                    member_name_check = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                    member_doe_email = member_data.get('doeEmail', '').strip().lower()
                    member_bxsci_email = member_data.get('bxsciEmail', '').strip().lower()
                    
                    is_member = (row_name.lower() == member_name_check.lower() or 
                                row_doe_email == member_doe_email or 
                                row_bxsci_email == member_bxsci_email)
                    
                    if is_member:
                        mason_feedback = {
                            'eventsCompeted': row.get('What events were you programmed to compete in?', ''),
                            'eventsNotCompeted': row.get('Did you NOT compete in any of the events you were programmed for? List the events you didn\'t compete in and briefly explain why. If this question doesn\'t apply to you, write "N/A".', ''),
                            'examDifficulty': row.get('How did you feel about the exam difficulty? Feel free to talk about any event(s) you want.', ''),
                            'partnerships': row.get('How did you feel about your partnerships? Rate each from 1-5 and explain why you gave the rating. Do this for each event you competed in, with a brief explanation. (Would you compete with this partner again? How was the collaboration? How was the preparation and communication in the weeks leading up to competition day?)', ''),
                            'whatWentWell': row.get('For each of your events, outline what you were able to answer successfully from what you learned in meetings or studied individually. What worked well in preparation for Mason?', ''),
                            'roadToImprovement': row.get('Above all, Mason is a learning experience. The tests were difficult across the board, but this gives us the opportunity to see where we\'re at and where we need to be. Outline which areas you need to focus on. What\'s the game plan before South Windsor and regionals diagnostics in 3-4 weeks?', ''),
                            'primaryBoardFeedback': row.get('What could we (Primary Board) have done better? (Introducing you to the Scilympiad platform with greater detail? Any logistical placement concerns?)', ''),
                            'emSdFeedback': row.get('What could your event managers and subject directors have done better? How can we improve how we spend our time and yours both in and out of meetings?', ''),
                            'otherComments': row.get('Any other comments or concerns? Explain if necessary. If no other comments, write "N/A".', '')
                        }
                    else:
                        # Check if this person is a partner (case-insensitive matching)
                        partnership_response = row.get('How did you feel about your partnerships? Rate each from 1-5 and explain why you gave the rating. Do this for each event you competed in, with a brief explanation. (Would you compete with this partner again? How was the collaboration? How was the preparation and communication in the weeks leading up to competition day?)', '').strip()
                        
                        if not partnership_response:
                            continue
                        
                        for event_name, partners in mason_partners.items():
                            # Try case-insensitive matching with whitespace trimming
                            matched_partner_name = None
                            for partner_name in partners:
                                if row_name.lower().strip() == partner_name.lower().strip():
                                    matched_partner_name = partner_name
                                    break
                            
                            if matched_partner_name:
                                if event_name not in partner_feedback:
                                    partner_feedback[event_name] = {}
                                partner_feedback[event_name][matched_partner_name] = {
                                    'partnershipRating': partnership_response
                                }
                                logger.info(f"Stored feedback from {row_name} for {event_name} about member {member_name_check}")
            
            if mason_partners or mason_feedback or partner_feedback:
                result['masonInvitational'] = {
                    'partners': mason_partners,
                    'memberFeedback': mason_feedback,
                    'partnerFeedback': partner_feedback
                }
                logger.info(f"Mason data for {member_name_check}: partners={list(mason_partners.keys())}, feedback_count={sum(len(v) for v in partner_feedback.values())}")
        except Exception as e:
            logger.warning(f"Error getting Mason Invitational data: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting full member data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/EventContent', methods=['GET'])
def get_event_content():
    """Get all event content (flat dicts, not {id: {...}})"""
    try:
        docs = db.collection('EventContent').stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            items.append(data)
        logger.info(f"Fetched {len(items)} events from EventContent.")
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error fetching EventContent: {str(e)}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/learning-modules', methods=['GET'])
def get_learning_modules():
    """Get all learning modules for admin management"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        # Get learning modules (avoid composite index by not using both where and order_by)
        modules_query = db.collection('LearningModules').stream()
        modules = []
        for module in modules_query:
            module_data = module.to_dict()
            module_data['id'] = module.id
            modules.append(module_data)
        # Sort by 'order' in Python
        modules.sort(key=lambda x: x.get('order', 0))
        return jsonify(modules), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningModules', methods=['POST'])
def create_learning_module():
    """Create a new learning module"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['eventName', 'title', 'order']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create module document
        module_data = {
            'eventName': data['eventName'],
            'title': data['title'],
            'duration': data.get('duration', ''),
            'unit': data.get('unit', 'Unit 1'),
            'order': int(data['order']),
            'points': data.get('points', 10),
            'prerequisites': data.get('prerequisites', []),
            'content': data.get('content', {
                'overview': data.get('overview', ''),
                'objectives': data.get('objectives', []),
                'resources': data.get('resources', [])
            }),
            'validationType': data.get('validationType', 'none'),
            'problems': data.get('problems', []),
            'systemPrompt': data.get('systemPrompt', ''),
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('LearningModules').document()
        doc_ref.set(module_data)
        
        return jsonify({
            "id": doc_ref.id,
            "message": "Learning module created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningModules/<module_id>', methods=['PUT'])
def update_learning_module(module_id):
    """Update a learning module"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get existing module
        module_ref = db.collection('LearningModules').document(module_id)
        if not module_ref.get().exists:
            return jsonify({"error": "Module not found"}), 404
        
        # Update module data
        update_data = {
            'eventName': data.get('eventName'),
            'title': data.get('title'),
            'description': data.get('description', ''),
            'duration': data.get('duration', ''),
            'unit': data.get('unit', 'Unit 1'),
            'order': int(data.get('order', 1)),
            'points': data.get('points', 10),
            'prerequisites': data.get('prerequisites', []),
            'content': data.get('content', {
                'overview': data.get('overview', ''),
                'objectives': data.get('objectives', []),
                'resources': data.get('resources', [])
            }),
            'validationType': data.get('validationType', 'none'),
            'problems': data.get('problems', []),
            'systemPrompt': data.get('systemPrompt', ''),
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        module_ref.update(update_data)
        
        return jsonify({
            "id": module_id,
            "message": "Learning module updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningModules/<module_id>', methods=['DELETE'])
def delete_learning_module(module_id):
    """Delete a learning module"""
    try:
        # Get existing module
        module_ref = db.collection('LearningModules').document(module_id)
        if not module_ref.get().exists:
            return jsonify({"error": "Module not found"}), 404
        
        # Hard delete the module
        module_ref.delete()
        
        return jsonify({
            "id": module_id,
            "message": "Learning module deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningModules/event/<event_name>', methods=['GET'])
def get_learning_modules_by_event(event_name):
    """Get learning modules for a specific event"""
    try:
        # Get learning modules for the event (using single where clause to avoid index requirement)
        modules_query = db.collection('LearningModules').where('eventName', '==', event_name).stream()
        modules = []
        
        for module in modules_query:
            module_data = module.to_dict()
            module_data['id'] = module.id
            modules.append(module_data)
        
        # Sort by order in Python instead of Firestore
        modules.sort(key=lambda x: x.get('order', 0))
        
        return jsonify(modules), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningModules/<module_id>/complete', methods=['POST'])
def mark_module_complete(module_id):
    """Mark a learning module as completed for a user"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
        
        # Check if module exists
        module_ref = db.collection('LearningModules').document(module_id)
        if not module_ref.get().exists:
            return jsonify({"error": "Module not found"}), 404
        
        # Create or update completion record
        completion_data = {
            'userId': user_id,
            'moduleId': module_id,
            'completedAt': firestore.SERVER_TIMESTAMP,
            'progress': 100
        }
        
        # Use composite key for completion tracking
        completion_id = f"{user_id}_{module_id}"
        db.collection('ModuleCompletions').document(completion_id).set(completion_data)
        
        return jsonify({
            "message": "Module marked as complete",
            "completionId": completion_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningModules/user/<user_id>/progress', methods=['GET'])
def get_user_module_progress(user_id):
    """Get learning module progress for a user"""
    try:
        # Get user's module completions
        completions_query = db.collection('ModuleCompletions').where('userId', '==', user_id).stream()
        completions = []
        
        for completion in completions_query:
            completion_data = completion.to_dict()
            completion_data['id'] = completion.id
            completions.append(completion_data)
        
        return jsonify(completions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ModuleCompletions', methods=['POST'])
def create_module_completion():
    """Create a new module completion with verification"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        module_id = data.get('moduleId')
        event_name = data.get('eventName')
        
        if not all([user_id, module_id, event_name]):
            return jsonify({"error": "userId, moduleId, and eventName are required"}), 400
        
        # Get module to check validation type and total points
        module_ref = db.collection('LearningModules').document(module_id)
        module_doc = module_ref.get()
        
        if not module_doc.exists:
            return jsonify({"error": "Module not found"}), 404
        
        module_data = module_doc.to_dict()
        validation_type = module_data.get('validationType', 'none')
        total_points = module_data.get('points', 10)
        
        # Create completion data
        completion_data = {
            'userId': user_id,
            'moduleId': module_id,
            'eventName': event_name,
            'totalPoints': total_points,
            'pointsGiven': total_points,  # Default to full points
            'completed': False,  # Will be set to True after verification
            'completedAt': None,
            'c3certified': False,
            'c2certified': False,
            'timeSpent': data.get('timeSpent', 0),
            'c3method': validation_type,
            'notesFileUrl': None,
            'problemResponses': [],
            'aiConversation': []
        }
        
        # Handle different validation types
        if validation_type == 'notesUpload':
            if 'notesFile' not in data:
                return jsonify({"error": "Notes file required for notesUpload validation"}), 400
            # Handle file upload (simplified for now)
            completion_data['notesFileUrl'] = data.get('notesFileUrl', '')
            completion_data['completed'] = True  # Auto-complete for notes upload
            
        elif validation_type == 'problems':
            if 'problemResponses' not in data:
                return jsonify({"error": "Problem responses required for problems validation"}), 400
            completion_data['problemResponses'] = data['problemResponses']
            completion_data['completed'] = True  # Auto-complete for problems
            
        elif validation_type == 'AIconversation':
            if 'aiConversation' not in data:
                return jsonify({"error": "AI conversation required for AIconversation validation"}), 400
            completion_data['aiConversation'] = data['aiConversation']
            completion_data['completed'] = True  # Auto-complete for AI conversation
            
        elif validation_type == 'none':
            completion_data['completed'] = True  # Auto-complete for no validation
            completion_data['completedAt'] = firestore.SERVER_TIMESTAMP
        
        # Set completion timestamp if completed
        if completion_data['completed']:
            completion_data['completedAt'] = firestore.SERVER_TIMESTAMP
        
        # Use composite key for completion tracking
        completion_id = f"{user_id}_{module_id}"
        db.collection('ModuleCompletions').document(completion_id).set(completion_data)
        
        return jsonify({
            "id": completion_id,
            "message": "Module completion created successfully",
            "completed": completion_data['completed'],
            "pointsEarned": completion_data['pointsGiven'] if completion_data['completed'] else 0
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ModuleCompletions/<completion_id>', methods=['PUT', 'PATCH'])
def update_module_completion(completion_id):
    """Update a module completion (for admin review)"""
    try:
        data = request.get_json()
        
        completion_ref = db.collection('ModuleCompletions').document(completion_id)
        completion_doc = completion_ref.get()
        
        if not completion_doc.exists:
            return jsonify({"error": "Module completion not found"}), 404
        
        # For PATCH, only update specified fields
        if request.method == 'PATCH':
            completion_ref.update(data)
            message = "Module completion updated successfully"
        else:
            completion_ref.set(data)
            message = "Module completion replaced successfully"
        
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Learning Artifacts (Portfolio) ----------------

@firebase_routes.route('/api/learning-artifacts', methods=['POST'])
def create_learning_artifact():
    """Create a new learning artifact (link or metadata-only).
    Expects JSON with: userId, eventName, type ('link'|'file'|'note'), title?, url?
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        user_id = data.get('userId')
        event_name = data.get('eventName')
        artifact_type = data.get('type')
        if not all([user_id, event_name, artifact_type]):
            return jsonify({"error": "userId, eventName, and type are required"}), 400
        doc = {
            'userId': user_id,
            'eventName': event_name,
            'type': artifact_type,
            'title': data.get('title', ''),
            'url': data.get('url', ''),
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('LearningArtifacts').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Artifact saved'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/learning-artifacts/upload', methods=['POST'])
def upload_learning_artifact_file():
    """Upload a learning artifact file to Storage and create an artifact doc.
    Multipart form fields: file, userId, eventName, title?
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files['file']
        user_id = request.form.get('userId')
        event_name = request.form.get('eventName')
        title = request.form.get('title', '')
        if not user_id or not event_name:
            return jsonify({"error": "userId and eventName are required"}), 400
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Store under learning_artifacts/{userId}/{timestamp}/filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_name = file.filename.replace('..','_')
        blob_path = f"learning_artifacts/{user_id}/{timestamp}/{safe_name}"
        blob = bucket.blob(blob_path)
        blob.upload_from_file(file, content_type=file.content_type)
        blob.make_public()
        url = blob.public_url

        artifact_doc = {
            'userId': user_id,
            'eventName': event_name,
            'type': 'file',
            'title': title,
            'url': url,
            'storagePath': blob_path,
            'contentType': file.content_type,
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('LearningArtifacts').document()
        ref.set(artifact_doc)
        return jsonify({'id': ref.id, 'url': url, 'message': 'File uploaded'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/learning-artifacts/user/<user_id>', methods=['GET'])
def list_learning_artifacts_for_user(user_id):
    """List all learning artifacts for a user."""
    try:
        docs = db.collection('LearningArtifacts').where('userId', '==', user_id).stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ModuleCompletions/event/<event_name>', methods=['GET'])
def get_module_completions_by_event(event_name):
    """Get all module completions for an event (for admin review)"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        completions_query = db.collection('ModuleCompletions').where('eventName', '==', event_name).stream()
        completions = []
        
        for completion in completions_query:
            completion_data = completion.to_dict()
            completion_data['id'] = completion.id
            completions.append(completion_data)
        
        return jsonify(completions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ModuleCompletions/user/<user_id>/event/<event_name>', methods=['GET'])
def get_user_module_completions_for_event(user_id, event_name):
    """Get a user's module completions for a specific event"""
    try:
        completions_query = db.collection('ModuleCompletions').where('userId', '==', user_id).where('eventName', '==', event_name).stream()
        completions = []
        
        for completion in completions_query:
            completion_data = completion.to_dict()
            completion_data['id'] = completion.id
            completions.append(completion_data)
        
        return jsonify(completions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/leaderboard/event/<event_name>', methods=['GET'])
def get_event_leaderboard(event_name):
    """Get leaderboard for an event based on module completion points"""
    try:
        # Get all module completions for this event
        completions_query = db.collection('ModuleCompletions').where('eventName', '==', event_name).where('completed', '==', True).stream()
        
        # Group by user and calculate total points
        user_points = {}
        for completion in completions_query:
            completion_data = completion.to_dict()
            user_id = completion_data['userId']
            points = completion_data.get('pointsGiven', 0)
            
            if user_id not in user_points:
                user_points[user_id] = 0
            user_points[user_id] += points
        
        # Get user details for leaderboard
        leaderboard = []
        for user_id, total_points in user_points.items():
            # Get user details
            user_doc = db.collection('Members').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                leaderboard.append({
                    'userId': user_id,
                    'firstName': user_data.get('firstName', ''),
                    'lastName': user_data.get('lastName', ''),
                    'totalPoints': total_points
                })
        
        # Sort by points (descending)
        leaderboard.sort(key=lambda x: x['totalPoints'], reverse=True)
        
        return jsonify(leaderboard), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Learning Conversations ----------------

@firebase_routes.route('/api/LearningConversations', methods=['POST'])
def create_learning_conversation():
    """Create a new learning conversation submission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['userId', 'eventName', 'moduleIds', 'shareUrl', 'transcript']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        conversation_data = {
            'userId': data['userId'],
            'eventName': data['eventName'],
            'moduleIds': data.get('moduleIds', []),
            'title': data.get('title', ''),
            'shareUrl': data['shareUrl'],
            'transcript': data['transcript'],
            'tokenCount': data.get('tokenCount', 0),
            'totalPoints': data.get('totalPoints', 0),
            'pointsGiven': 0,
            'status': 'pending',
            'adminComments': '',
            'reviewerId': None,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'reviewedAt': None
        }

        doc_ref = db.collection('LearningConversations').document()
        doc_ref.set(conversation_data)

        return jsonify({
            'id': doc_ref.id,
            'message': 'Conversation submitted successfully'
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningConversations/user/<user_id>', methods=['GET'])
def get_user_learning_conversations(user_id):
    """Get conversations for a specific user; optional eventName filter via query param"""
    try:
        event_name = request.args.get('eventName')
        query = db.collection('LearningConversations').where('userId', '==', user_id)
        if event_name:
            query = query.where('eventName', '==', event_name)
        docs = query.stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            items.append(data)
        # Sort newest first by createdAt if present
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningConversations/user/<user_id>/event/<event_name>', methods=['GET'])
def get_user_learning_conversations_for_event(user_id, event_name):
    """Get conversations for a user filtered by event"""
    try:
        docs = db.collection('LearningConversations')\
            .where('userId', '==', user_id)\
            .where('eventName', '==', event_name).stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            items.append(data)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningConversations/<conversation_id>', methods=['PATCH', 'PUT'])
def update_learning_conversation(conversation_id):
    """Update a learning conversation (user can edit before review; admin can review)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        conv_ref = db.collection('LearningConversations').document(conversation_id)
        conv_doc = conv_ref.get()
        if not conv_doc.exists:
            return jsonify({"error": "Conversation not found"}), 404

        if request.method == 'PATCH':
            # If admin review fields present, set reviewedAt and reviewerId when status or pointsGiven change
            updates = dict(data)
            if any(k in updates for k in ['status', 'pointsGiven', 'adminComments', 'reviewerId']):
                updates['reviewedAt'] = firestore.SERVER_TIMESTAMP
            conv_ref.update(updates)
            message = 'Conversation updated successfully'
        else:
            conv_ref.set(data)
            message = 'Conversation replaced successfully'
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/learning-conversations', methods=['GET'])
def admin_get_learning_conversations():
    """Admin: list learning conversations with optional filters. Requires X-Admin-ID header."""
    try:
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401

        # Optional filters
        event_name = request.args.get('eventName')
        status = request.args.get('status')

        query = db.collection('LearningConversations')
        if event_name:
            query = query.where('eventName', '==', event_name)
        if status:
            query = query.where('status', '==', status)

        docs = query.stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            items.append(data)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ai/conversation', methods=['POST'])
def ai_conversation():
    """Handle AI conversation for module validation"""
    try:
        data = request.get_json()
        message = data.get('message')
        system_prompt = data.get('systemPrompt', '')
        conversation_history = data.get('conversationHistory', [])
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Load OpenAI API key
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)
            openai_api_key = api_keys.get('OpenAiAPIKey')
        
        if not openai_api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        # Prepare conversation for OpenAI
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": "user" if msg.get('role') == 'user' else "assistant",
                "content": msg.get('content', '')
            })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI API
        import openai
        openai.api_key = openai_api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            "response": ai_response,
            "conversation": conversation_history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": ai_response}
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/calendar-events', methods=['GET'])
def get_calendar_events():
    """Get all calendar events for admin management"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        
        # Get calendar events (no order_by to avoid index requirement)
        events_query = db.collection('CalendarEvents').where('isActive', '==', True).stream()
        events = []
        
        for event in events_query:
            event_data = event.to_dict()
            event_data['id'] = event.id
            events.append(event_data)
        
        # Sort events by date in Python (ascending)
        def get_date_as_iso(event):
            date_val = event.get('date', '')
            if hasattr(date_val, 'isoformat'):
                return date_val.isoformat()
            return str(date_val)
        events.sort(key=get_date_as_iso)
        
        return jsonify(events), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500 

# ---------------- Unified Portfolio ----------------

@firebase_routes.route('/api/Portfolio', methods=['POST'])
def create_portfolio_item():
    """Create a unified Portfolio item.
    Expects JSON with at least: { userId, kind }
    kind in ['artifact', 'weekly', 'diagnostic', 'competition', 'app_question']
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        kind = data.get('kind')
        if not user_id or not kind:
            return jsonify({"error": "userId and kind are required"}), 400

        base = {
            'userId': user_id,
            'kind': kind,
            'eventName': data.get('eventName', ''),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }

        # Build kind-specific fields
        if kind == 'artifact':
            artifact_type = data.get('artifactType')  # 'file' | 'link' | 'conversation'
            if artifact_type not in ['file', 'link', 'conversation']:
                return jsonify({"error": "artifactType must be file, link, or conversation"}), 400
            doc = {
                **base,
                'artifactType': artifact_type,
                'title': data.get('title', ''),
                'url': data.get('url', ''),
                'storagePath': data.get('storagePath', ''),
                'contentType': data.get('contentType', ''),
                'moduleIds': data.get('moduleIds', []),
                'shareUrl': data.get('shareUrl', ''),
                'transcript': data.get('transcript', '')
            }
        elif kind == 'weekly':
            content = (data.get('content') or '').strip()
            if not content:
                return jsonify({"error": "content is required for weekly"}), 400
            doc = {
                **base,
                'dateISO': data.get('dateISO', ''),
                'content': content
            }
        elif kind == 'diagnostic':
            reflection = (data.get('reflection') or '').strip()
            if not reflection:
                return jsonify({"error": "reflection is required for diagnostic"}), 400
            doc = {
                **base,
                'diagnosticDateISO': data.get('diagnosticDateISO', ''),
                'reflection': reflection
            }
        elif kind == 'competition':
            competition_name = (data.get('competitionName') or '').strip()
            reflection = (data.get('reflection') or '').strip()
            if not competition_name or not reflection:
                return jsonify({"error": "competitionName and reflection are required for competition"}), 400
            doc = {
                **base,
                'competitionName': competition_name,
                'whatWentWell': data.get('whatWentWell', ''),
                'whatToImprove': data.get('whatToImprove', ''),
                'reflection': reflection
            }
        elif kind == 'app_question':
            question_id = data.get('questionId')
            answer = (data.get('answer') or '').strip()
            question_text = data.get('questionText')
            if not question_id or not answer:
                return jsonify({"error": "questionId and answer are required for app_question"}), 400
            doc = {
                **base,
                'questionId': question_id,
                'questionText': question_text or '',
                'answer': answer
            }
        else:
            return jsonify({"error": "Unsupported kind"}), 400

        ref = db.collection('Portfolio').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Portfolio item saved'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/portfolio/upload', methods=['POST'])
def upload_portfolio_file():
    """Upload a file for a Portfolio artifact and create the Portfolio document.
    Multipart fields: file, userId, eventName?, title?
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files['file']
        user_id = request.form.get('userId')
        event_name = request.form.get('eventName', '')
        title = request.form.get('title', '')
        if not user_id:
            return jsonify({"error": "userId is required"}), 400
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_name = file.filename.replace('..','_')
        blob_path = f"portfolio/{user_id}/{timestamp}/{safe_name}"
        blob = bucket.blob(blob_path)
        blob.upload_from_file(file, content_type=file.content_type)
        blob.make_public()
        url = blob.public_url

        doc = {
            'userId': user_id,
            'kind': 'artifact',
            'artifactType': 'file',
            'title': title,
            'url': url,
            'storagePath': blob_path,
            'contentType': file.content_type,
            'eventName': event_name,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('Portfolio').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'url': url, 'message': 'File uploaded'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Portfolio/user/<user_id>', methods=['GET'])
def list_portfolio_items(user_id):
    """List Portfolio items for a user. Optional filter via kind query param.
    Multiple kinds can be comma-separated.
    """
    try:
        kind = request.args.get('kind')
        query = db.collection('Portfolio').where('userId', '==', user_id)
        # Can't filter by multiple kinds without an index; do client-side filter if provided
        docs = query.stream()
        items = []
        filter_kinds = None
        if kind:
            filter_kinds = set([k.strip() for k in kind.split(',') if k.strip()])
        for doc in docs:
            d = doc.to_dict()
            if filter_kinds and d.get('kind') not in filter_kinds:
                continue
            d['id'] = doc.id
            items.append(d)
        # Sort by createdAt desc best-effort
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Portfolio/<item_id>', methods=['PATCH', 'PUT'])
def update_portfolio_item(item_id):
    try:
        data = request.get_json() or {}
        ref = db.collection('Portfolio').document(item_id)
        if not ref.get().exists:
            return jsonify({"error": "Portfolio item not found"}), 404
        updates = dict(data)
        updates['updatedAt'] = firestore.SERVER_TIMESTAMP
        if request.method == 'PATCH':
            ref.update(updates)
        else:
            ref.set(updates)
        return jsonify({"message": "Portfolio item saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Questions & Reflections ----------------

@firebase_routes.route('/api/weekly-updates', methods=['POST'])
def create_weekly_update():
    """Create a weekly update entry.
    Expects JSON: { userId, weekStartISO, eventName?, content }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        content = data.get('content', '').strip()
        if not user_id or not content:
            return jsonify({"error": "userId and content are required"}), 400
        doc = {
            'userId': user_id,
            'weekStartISO': data.get('weekStartISO', ''),
            'eventName': data.get('eventName', ''),
            'content': content,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('WeeklyUpdates').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Weekly update saved'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/weekly-updates/user/<user_id>', methods=['GET'])
def list_weekly_updates_for_user(user_id):
    """List weekly updates for the given user (newest first if timestamp available)."""
    try:
        docs = db.collection('WeeklyUpdates').where('userId', '==', user_id).stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        # Sort by createdAt desc if present
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/weekly-updates/<doc_id>', methods=['PATCH', 'PUT'])
def update_weekly_update(doc_id):
    try:
        data = request.get_json() or {}
        ref = db.collection('WeeklyUpdates').document(doc_id)
        if not ref.get().exists:
            return jsonify({"error": "Weekly update not found"}), 404
        updates = dict(data)
        updates['updatedAt'] = firestore.SERVER_TIMESTAMP
        if request.method == 'PATCH':
            ref.update(updates)
        else:
            ref.set(updates)
        return jsonify({"message": "Weekly update saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/diagnostic-reflections', methods=['POST'])
def create_diagnostic_reflection():
    """Create a diagnostic reflection.
    Expects JSON: { userId, eventName?, diagnosticDateISO?, reflection }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        reflection = data.get('reflection', '').strip()
        if not user_id or not reflection:
            return jsonify({"error": "userId and reflection are required"}), 400
        doc = {
            'userId': user_id,
            'eventName': data.get('eventName', ''),
            'diagnosticDateISO': data.get('diagnosticDateISO', ''),
            'reflection': reflection,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('DiagnosticReflections').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Diagnostic reflection saved'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/diagnostic-reflections/user/<user_id>', methods=['GET'])
def list_diagnostic_reflections_for_user(user_id):
    try:
        docs = db.collection('DiagnosticReflections').where('userId', '==', user_id).stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/diagnostic-reflections/<doc_id>', methods=['PATCH', 'PUT'])
def update_diagnostic_reflection(doc_id):
    try:
        data = request.get_json() or {}
        ref = db.collection('DiagnosticReflections').document(doc_id)
        if not ref.get().exists:
            return jsonify({"error": "Diagnostic reflection not found"}), 404
        updates = dict(data)
        updates['updatedAt'] = firestore.SERVER_TIMESTAMP
        if request.method == 'PATCH':
            ref.update(updates)
        else:
            ref.set(updates)
        return jsonify({"message": "Diagnostic reflection saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/competition-reflections', methods=['POST'])
def create_competition_reflection():
    """Create a competition reflection.
    Expects JSON: { userId, competitionName, eventName?, reflection, whatWentWell?, whatToImprove? }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        competition_name = data.get('competitionName', '').strip()
        reflection = data.get('reflection', '').strip()
        if not user_id or not competition_name or not reflection:
            return jsonify({"error": "userId, competitionName, and reflection are required"}), 400
        doc = {
            'userId': user_id,
            'competitionName': competition_name,
            'eventName': data.get('eventName', ''),
            'reflection': reflection,
            'whatWentWell': data.get('whatWentWell', ''),
            'whatToImprove': data.get('whatToImprove', ''),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('CompetitionReflections').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Competition reflection saved'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/competition-reflections/user/<user_id>', methods=['GET'])
def list_competition_reflections_for_user(user_id):
    try:
        docs = db.collection('CompetitionReflections').where('userId', '==', user_id).stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/competition-reflections/<doc_id>', methods=['PATCH', 'PUT'])
def update_competition_reflection(doc_id):
    try:
        data = request.get_json() or {}
        ref = db.collection('CompetitionReflections').document(doc_id)
        if not ref.get().exists:
            return jsonify({"error": "Competition reflection not found"}), 404
        updates = dict(data)
        updates['updatedAt'] = firestore.SERVER_TIMESTAMP
        if request.method == 'PATCH':
            ref.update(updates)
        else:
            ref.set(updates)
        return jsonify({"message": "Competition reflection saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/application-responses/user/<user_id>', methods=['GET'])
def get_application_responses(user_id):
    """Get the application questions and responses for a user.
    Document ID is the userId for convenience.
    """
    try:
        ref = db.collection('ApplicationResponses').document(user_id)
        doc = ref.get()
        if not doc.exists:
            return jsonify({ 'userId': user_id, 'questions': [] }), 200
        data = doc.to_dict() or {}
        data['userId'] = user_id
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/application-responses/user/<user_id>', methods=['PUT', 'PATCH'])
def upsert_application_responses(user_id):
    """Create or update the application questions/answers for a user.
    Expects JSON: { questions: [{ id, text, answer }] }
    """
    try:
        data = request.get_json() or {}
        questions = data.get('questions', [])
        if not isinstance(questions, list):
            return jsonify({"error": "questions must be an array"}), 400
        ref = db.collection('ApplicationResponses').document(user_id)
        payload = {
            'questions': questions,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        if request.method == 'PATCH':
            ref.set(payload, merge=True)
        else:
            ref.set(payload)
        return jsonify({"message": "Application responses saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/admin/calendar-events/<event_id>', methods=['PATCH', 'PUT'])
def update_calendar_event(event_id):
    """Update a calendar event for admin management"""
    try:
        # Check admin auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({"error": "Admin authentication required"}), 401
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        event_ref = db.collection('CalendarEvents').document(event_id)
        event_doc = event_ref.get()
        if not event_doc.exists:
            return jsonify({"error": "Event not found"}), 404
        if request.method == 'PATCH':
            event_ref.update(data)
            message = "Event updated successfully"
        else:
            event_ref.set(data)
            message = "Event replaced successfully"
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# --- ADMIN-FRIENDLY API ENDPOINTS FOR ADMIN COMPETITIONS PAGE ---

# Competitions
@firebase_routes.route('/api/admin/competitions', methods=['GET'])
def admin_get_competitions():
    """Get all competitions from text files (not Firebase)"""
    return get_competitions()

@firebase_routes.route('/api/admin/competitions', methods=['POST'])
def admin_create_competition():
    return create('Competitions')

@firebase_routes.route('/api/admin/competitions/<competition_id>', methods=['PUT', 'PATCH'])
def admin_update_competition(competition_id):
    return update('Competitions', competition_id)

@firebase_routes.route('/api/admin/competitions/<competition_id>', methods=['DELETE'])
def admin_delete_competition(competition_id):
    return delete('Competitions', competition_id)

# Applications
@firebase_routes.route('/api/admin/applications', methods=['GET'])
def admin_get_applications():
    return get_all('Applications')

# Members
@firebase_routes.route('/api/admin/members', methods=['GET'])
def admin_get_members():
    return get_all('Members')

# Events
@firebase_routes.route('/api/admin/events', methods=['GET'])
def admin_get_events():
    return get_all('Events')

# ---------------- House Cup Theme Voting ----------------

@firebase_routes.route('/api/housecup/suggestion', methods=['POST'])
def submit_house_cup_suggestion():
    """Submit a House Cup theme suggestion"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('userId')
        user_name = data.get('userName')
        theme = data.get('theme')
        house_names = data.get('houseNames')
        
        # Validation
        if not all([user_id, user_name, theme, house_names]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if len(theme) > 25:
            return jsonify({"error": "Theme must be 25 characters or less"}), 400
        
        if len(house_names) != 4:
            return jsonify({"error": "Must provide exactly 4 house names"}), 400
        
        for name in house_names:
            if len(name) > 20:
                return jsonify({"error": "House names must be 20 characters or less"}), 400
        
        # Check if user already submitted
        existing = db.collection('HouseCupThemes').where('userId', '==', user_id).limit(1).stream()
        if list(existing):
            return jsonify({"error": "You have already submitted a suggestion"}), 400
        
        # Create suggestion
        suggestion_data = {
            'userId': user_id,
            'userName': user_name,
            'theme': theme,
            'houseNames': house_names,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'votes': {
                'first': 0,
                'second': 0,
                'third': 0
            }
        }
        
        doc_ref = db.collection('HouseCupThemes').add(suggestion_data)
        suggestion_data['id'] = doc_ref[1].id
        
        return jsonify(suggestion_data), 200
        
    except Exception as e:
        logger.error(f"Error submitting suggestion: {str(e)}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/housecup/suggestion/<user_id>', methods=['GET'])
def get_user_suggestion(user_id):
    """Get a user's theme suggestion"""
    try:
        suggestions = db.collection('HouseCupThemes').where('userId', '==', user_id).limit(1).stream()
        suggestion_list = list(suggestions)
        
        if not suggestion_list:
            return jsonify({"suggestion": None}), 200
        
        suggestion = suggestion_list[0]
        suggestion_data = suggestion.to_dict()
        suggestion_data['id'] = suggestion.id
        
        return jsonify({"suggestion": suggestion_data}), 200
        
    except Exception as e:
        logger.error(f"Error getting user suggestion: {str(e)}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/housecup/suggestions', methods=['GET'])
def get_all_suggestions():
    """Get all House Cup theme suggestions"""
    try:
        suggestions_ref = db.collection('HouseCupThemes').order_by('createdAt').stream()
        
        suggestions = []
        for doc in suggestions_ref:
            suggestion_data = doc.to_dict()
            suggestion_data['id'] = doc.id
            suggestions.append(suggestion_data)
        
        return jsonify({"suggestions": suggestions}), 200
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/housecup/vote', methods=['POST'])
def submit_house_cup_vote():
    """Submit or update House Cup votes"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('userId')
        votes = data.get('votes')  # {first: suggestionId, second: suggestionId, third: suggestionId}
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
        
        # Get or create vote document
        vote_ref = db.collection('HouseCupVotes').document(user_id)
        existing_vote = vote_ref.get()
        
        # Get old votes to decrement counts
        old_votes = {}
        if existing_vote.exists:
            old_votes = existing_vote.to_dict().get('votes', {})
        
        # Update vote counts
        # First, decrement old votes
        for place, suggestion_id in old_votes.items():
            if suggestion_id:
                suggestion_ref = db.collection('HouseCupThemes').document(suggestion_id)
                suggestion_ref.update({
                    f'votes.{place}': firestore.Increment(-1)
                })
        
        # Then, increment new votes
        for place, suggestion_id in votes.items():
            if suggestion_id:
                suggestion_ref = db.collection('HouseCupThemes').document(suggestion_id)
                suggestion_ref.update({
                    f'votes.{place}': firestore.Increment(1)
                })
        
        # Save user's votes
        vote_data = {
            'userId': user_id,
            'votes': votes,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        vote_ref.set(vote_data)
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"Error submitting vote: {str(e)}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/housecup/votes/<user_id>', methods=['GET'])
def get_user_votes(user_id):
    """Get a user's votes"""
    try:
        vote_doc = db.collection('HouseCupVotes').document(user_id).get()
        
        if not vote_doc.exists:
            return jsonify({"votes": {"first": None, "second": None, "third": None}}), 200
        
        vote_data = vote_doc.to_dict()
        return jsonify({"votes": vote_data.get('votes', {})}), 200
        
    except Exception as e:
        logger.error(f"Error getting user votes: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ---------------- Excused Absences ----------------

@firebase_routes.route('/api/ExcusedAbsences', methods=['POST'])
def create_excused_absence():
    """Create a new excused absence request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['memberId', 'eventId', 'dateOfAbsence', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Parse date and ensure it's stored correctly to avoid timezone shifts
        date_str = data['dateOfAbsence']
        # If format is YYYY-MM-DD, parse it and create datetime at midnight UTC
        if len(date_str) == 10 and date_str.count('-') == 2:
            from datetime import timezone
            date_parts = date_str.split('-')
            date_obj = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), 0, 0, 0, tzinfo=timezone.utc)
        else:
            # Fallback to isoformat parsing, ensure UTC if Z is present or add timezone
            if 'Z' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Try to parse and assume UTC if no timezone
                try:
                    date_obj = datetime.fromisoformat(date_str)
                    if date_obj.tzinfo is None:
                        from datetime import timezone
                        date_obj = date_obj.replace(tzinfo=timezone.utc)
                except:
                    # Last resort: try as naive and add UTC
                    from datetime import timezone
                    date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        
        # Create excused absence document
        absence_data = {
            'memberId': data['memberId'],
            'eventId': data['eventId'],
            'dateOfAbsence': date_obj,
            'requestedTimestamp': firestore.SERVER_TIMESTAMP,
            'reason': data['reason'],
            'documentationFileId': data.get('documentationFileId', None),
            'type': data.get('type', 'excused'),  # 'excused' | 'attendance_correction'
            'status': 'pending',  # pending, approved, denied
            'reviewedBy': None,
            'reviewedAt': None,
            'adminComments': ''
        }
        
        doc_ref = db.collection('ExcusedAbsences').document()
        doc_ref.set(absence_data)
        
        return jsonify({
            "id": doc_ref.id,
            "message": "Excused absence request submitted successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ExcusedAbsences/member/<member_id>', methods=['GET'])
def get_member_excused_absences(member_id):
    """Get all excused absences for a specific member"""
    try:
        absences_query = db.collection('ExcusedAbsences').where('memberId', '==', member_id).order_by('dateOfAbsence', direction=firestore.Query.DESCENDING).stream()
        absences = []
        
        for absence in absences_query:
            absence_data = absence.to_dict()
            absence_data['id'] = absence.id
            absences.append(absence_data)
        
        return jsonify(absences), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ExcusedAbsences/event/<event_id>', methods=['GET'])
def get_event_excused_absences(event_id):
    """Get all excused absences for a specific event"""
    try:
        absences_query = db.collection('ExcusedAbsences').where('eventId', '==', event_id).order_by('dateOfAbsence', direction=firestore.Query.DESCENDING).stream()
        absences = []
        
        for absence in absences_query:
            absence_data = absence.to_dict()
            absence_data['id'] = absence.id
            absences.append(absence_data)
        
        return jsonify(absences), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ExcusedAbsences/<absence_id>', methods=['PATCH', 'PUT'])
def update_excused_absence(absence_id):
    """Update an excused absence (for admin review)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        absence_ref = db.collection('ExcusedAbsences').document(absence_id)
        absence_doc = absence_ref.get()
        
        if not absence_doc.exists:
            return jsonify({"error": "Excused absence not found"}), 404
        
        # For PATCH, only update specified fields
        if request.method == 'PATCH':
            # If status is being updated, set reviewed timestamp
            if 'status' in data and data['status'] != 'pending':
                data['reviewedAt'] = firestore.SERVER_TIMESTAMP
            absence_ref.update(data)
            message = "Excused absence updated successfully"
        else:
            absence_ref.set(data)
            message = "Excused absence replaced successfully"
        
        return jsonify({"message": message}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ExcusedAbsences/upload-documentation', methods=['POST'])
def upload_absence_documentation():
    """Upload documentation file for excused absence"""
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        # Get file and user ID
        file = request.files['file']
        member_id = request.form.get('memberId')
        
        if not member_id:
            return jsonify({"error": "No member ID provided"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check file type (allow common document formats and images)
        allowed_types = ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'text/plain', 'image/png', 'image/jpeg', 'image/jpg']
        if file.content_type not in allowed_types:
            return jsonify({"error": "Only PDF, DOC, DOCX, TXT, PNG, and JPG files are allowed"}), 400
        
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_extension = file.filename.split('.')[-1]
        filename = f"absence_docs_{member_id}_{timestamp}.{file_extension}"
        
        # Upload to Firebase Storage
        blob_path = f"absence_documentation/{filename}"
        blob = bucket.blob(blob_path)
        
        # Set appropriate content type
        blob.upload_from_file(file, content_type=file.content_type)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Get the public URL
        url = blob.public_url
        
        return jsonify({
            "fileId": filename,
            "url": url,
            "success": True
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/ExcusedAbsences/download-documentation/<file_id>', methods=['GET'])
def download_absence_documentation(file_id):
    """Download documentation file for excused absence"""
    try:
        # Construct the blob path
        blob_path = f"absence_documentation/{file_id}"
        blob = bucket.blob(blob_path)
        
        # Check if the blob exists
        if not blob.exists():
            return jsonify({"error": "File not found"}), 404
        
        # Get the blob content
        blob_content = blob.download_as_bytes()
        
        # Determine content type based on file extension
        file_extension = file_id.split('.')[-1].lower()
        content_type_map = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Create response with file content
        from flask import Response
        return Response(
            blob_content,
            mimetype=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{file_id}"',
                'Content-Length': str(len(blob_content))
            }
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# ---------------- House Cup Points ----------------

@firebase_routes.route('/api/HouseCupPoints', methods=['POST'])
def create_house_cup_points():
    """Create a new House Cup points entry"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['points', 'house', 'reason', 'awardedBy']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate house
        if data['house'] not in ['A', 'B', 'C', 'D']:
            return jsonify({"error": "Invalid house. Must be A, B, C, or D"}), 400
        
        point_entry = {
            'points': data['points'],
            'house': data['house'],
            'eventName': data.get('eventName'),  # Optional
            'date': data.get('date', firestore.SERVER_TIMESTAMP),
            'reason': data['reason'],
            'awardedBy': data['awardedBy'],
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('HouseCupPoints').document()
        doc_ref.set(point_entry)
        
        return jsonify({
            'id': doc_ref.id,
            'message': 'House Cup points added successfully'
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/HouseCupPoints', methods=['GET'])
def get_house_cup_points():
    """Get all House Cup points (with optional filtering)"""
    try:
        house = request.args.get('house')
        eventName = request.args.get('eventName')
        
        query = db.collection('HouseCupPoints')
        
        if house:
            query = query.where('house', '==', house)
        if eventName:
            query = query.where('eventName', '==', eventName)
        
        docs = query.stream()
        points = [{doc.id: doc.to_dict()} for doc in docs]
        
        return jsonify(points), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/HouseCupPoints/<point_id>', methods=['DELETE'])
def delete_house_cup_points(point_id):
    """Delete a House Cup points entry"""
    try:
        doc_ref = db.collection('HouseCupPoints').document(point_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Point entry not found"}), 404
        
        doc_ref.delete()
        return jsonify({"message": "Point entry deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/HouseCupPoints/leaderboard', methods=['GET'])
def get_house_cup_leaderboard():
    """Get House Cup leaderboard for all events combined or specific event"""
    try:
        eventName = request.args.get('eventName')  # Optional filter
        
        # Query HouseCupPoints
        query = db.collection('HouseCupPoints')
        if eventName:
            query = query.where('eventName', '==', eventName)
        
        docs = query.stream()
        
        # Calculate points per house
        house_points = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for doc in docs:
            data = doc.to_dict()
            house = data.get('house')
            points = data.get('points', 0)
            if house in house_points:
                house_points[house] += points
        
        # Convert to sorted list for leaderboard
        leaderboard = [
            {'house': house, 'points': points, 'rank': 0}
            for house, points in sorted(house_points.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Assign ranks (handle ties)
        for i, entry in enumerate(leaderboard):
            if i > 0 and entry['points'] == leaderboard[i-1]['points']:
                entry['rank'] = leaderboard[i-1]['rank']
            else:
                entry['rank'] = i + 1
        
        return jsonify(leaderboard), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Merch ordering and design voting routes
@firebase_routes.route('/api/merch/check-eligibility/<user_id>', methods=['GET'])
def check_merch_eligibility(user_id):
    """Check if user is eligible (in team_placement_solution.csv or has admin access) and if they've already submitted"""
    try:
        import csv
        
        # First check if user has admin status (admins can access even if not in CSV)
        is_admin = False
        try:
            member_doc = db.collection('Members').document(user_id).get()
            if member_doc.exists:
                member_data = member_doc.to_dict()
                admin_status = member_data.get('adminStatus', 'none')
                if admin_status != 'none':
                    is_admin = True
        except Exception as e:
            logger.warning(f"Error checking admin status for {user_id}: {e}")
        
        # If not admin, check if user is in team_placement_solution.csv
        if not is_admin:
            in_team = False
            with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['firebaseID'] == user_id:
                        in_team = True
                        break
            
            if not in_team:
                return jsonify({
                    'eligible': False,
                    'message': 'You must be on the team roster or have admin access to access this page.'
                }), 403
        
        # Check if user has already submitted
        merch_collection = db.collection('MerchOrders')
        user_submissions = merch_collection.where('firebaseID', '==', user_id).limit(1).stream()
        
        already_submitted = len(list(user_submissions)) > 0
        
        return jsonify({
            'eligible': True,
            'alreadySubmitted': already_submitted,
            'isAdmin': is_admin
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking merch eligibility: {e}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/merch/submit', methods=['POST'])
def submit_merch_order():
    """Submit design votes and merch order"""
    try:
        import csv
        
        data = request.get_json()
        user_id = data.get('firebaseID')
        
        if not user_id:
            return jsonify({"error": "firebaseID is required"}), 400
        
        # Verify user is in team_placement_solution.csv OR has admin access
        in_team = False
        is_admin = False
        member_data = {}
        
        # Check admin status first
        try:
            member_doc = db.collection('Members').document(user_id).get()
            if member_doc.exists:
                firestore_member_data = member_doc.to_dict()
                admin_status = firestore_member_data.get('adminStatus', 'none')
                if admin_status != 'none':
                    is_admin = True
                    # For admins, use data from Firestore
                    member_data = {
                        'bxsciolyID': firestore_member_data.get('bxsciolyID', ''),
                        'firstName': firestore_member_data.get('firstName', ''),
                        'lastName': firestore_member_data.get('lastName', ''),
                        'house': firestore_member_data.get('house', '')
                    }
        except Exception as e:
            logger.warning(f"Error checking admin status for {user_id}: {e}")
        
        # If not admin, check CSV
        if not is_admin:
            with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['firebaseID'] == user_id:
                        in_team = True
                        member_data = row
                        break
            
            if not in_team:
                return jsonify({"error": "User not on team roster and does not have admin access"}), 403
        
        # Check if already submitted
        merch_collection = db.collection('MerchOrders')
        existing = merch_collection.where('firebaseID', '==', user_id).limit(1).stream()
        if len(list(existing)) > 0:
            return jsonify({"error": "You have already submitted an order"}), 400
        
        # Validate required fields
        design_votes = data.get('designVotes', [])
        items = data.get('items', [])
        spend_limit = data.get('spendLimit')
        
        if not design_votes or len(design_votes) == 0:
            return jsonify({"error": "Design votes are required"}), 400
        
        if not items or len(items) == 0:
            return jsonify({"error": "At least one merch item is required"}), 400
        
        # Check if they selected a required item (t-shirt, hoodie, or sweatshirt)
        required_items = ['t-shirt', 'hoodie', 'sweatshirt']
        has_required = any(item.get('type') in required_items for item in items)
        
        if not has_required:
            return jsonify({"error": "You must select at least one of: T-shirt, Hoodie, or Sweatshirt to attend tournaments"}), 400
        
        # Store in Firestore
        order_data = {
            'firebaseID': user_id,
            'bxsciolyID': member_data.get('bxsciolyID', ''),
            'firstName': member_data.get('firstName', ''),
            'lastName': member_data.get('lastName', ''),
            'house': member_data.get('house', ''),
            'designVotes': design_votes,  # Array of design numbers in ranked order
            'items': items,  # Array of {type, rank} - prices not stored as they depend on team orders
            'spendLimit': spend_limit,
            'submittedAt': firestore.SERVER_TIMESTAMP,
            'status': 'pending'
        }
        
        merch_collection.add(order_data)
        
        return jsonify({
            "success": True,
            "message": "Your order has been submitted successfully!"
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting merch order: {e}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/merch/get-order/<user_id>', methods=['GET'])
def get_merch_order(user_id):
    """Get existing merch order for a user"""
    try:
        merch_collection = db.collection('MerchOrders')
        orders = merch_collection.where('firebaseID', '==', user_id).limit(1).stream()
        
        order_list = []
        for order in orders:
            order_data = order.to_dict()
            order_data['id'] = order.id
            # Convert Firestore timestamp to string if needed
            if 'submittedAt' in order_data:
                timestamp = order_data['submittedAt']
                if hasattr(timestamp, 'isoformat'):
                    order_data['submittedAt'] = timestamp.isoformat()
            order_list.append(order_data)
        
        if len(order_list) > 0:
            return jsonify(order_list[0]), 200
        else:
            return jsonify({"error": "No order found"}), 404
            
    except Exception as e:
        logger.error(f"Error getting merch order: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------- Learning Resources ----------------

@firebase_routes.route('/api/LearningResources/classroom-code', methods=['GET'])
def get_classroom_code():
    """Get the Google Classroom join code for an event"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        doc_ref = db.collection('LearningResources').document('classroom-codes').collection('events').document(event_name)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return jsonify({"code": data.get('code', '')}), 200
        else:
            return jsonify({"code": ""}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/classroom-code', methods=['POST'])
def update_classroom_code():
    """Update the Google Classroom join code for an event"""
    try:
        data = request.get_json() or {}
        code = data.get('code', '').strip()
        event_name = data.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        doc_ref = db.collection('LearningResources').document('classroom-codes').collection('events').document(event_name)
        doc_ref.set({
            'code': code,
            'eventName': event_name,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }, merge=True)
        return jsonify({"message": "Classroom code updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/topics', methods=['GET'])
def get_topics():
    """Get all topics for an event"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        docs = db.collection('LearningResources').document('topics').collection('events').document(event_name).collection('items').stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/topics', methods=['POST'])
def create_topic():
    """Create a new topic for an event"""
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        event_name = data.get('eventName')
        if not name:
            return jsonify({"error": "Topic name is required"}), 400
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        doc = {
            'name': name,
            'description': data.get('description', ''),
            'links': data.get('links', []),
            'parentId': data.get('parentId'),
            'eventName': event_name,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('LearningResources').document('topics').collection('events').document(event_name).collection('items').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Topic created'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/topics/<topic_id>', methods=['PUT'])
def update_topic(topic_id):
    """Update a topic"""
    try:
        data = request.get_json() or {}
        event_name = data.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('topics').collection('events').document(event_name).collection('items').document(topic_id)
        if not ref.get().exists:
            return jsonify({"error": "Topic not found"}), 404
        
        updates = {
            'name': data.get('name', '').strip(),
            'description': data.get('description', ''),
            'links': data.get('links', []),
            'parentId': data.get('parentId'),
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref.update(updates)
        return jsonify({"message": "Topic updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/topics/<topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    """Delete a topic"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('topics').collection('events').document(event_name).collection('items').document(topic_id)
        if not ref.get().exists:
            return jsonify({"error": "Topic not found"}), 404
        
        # Also delete any subtopics
        subtopics = db.collection('LearningResources').document('topics').collection('events').document(event_name).collection('items').where('parentId', '==', topic_id).stream()
        for subtopic in subtopics:
            subtopic.reference.delete()
        
        ref.delete()
        return jsonify({"message": "Topic deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/notes', methods=['GET'])
def get_notes():
    """Get all notes for an event"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        docs = db.collection('LearningResources').document('notes').collection('events').document(event_name).collection('items').stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        # Sort by createdAt desc
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/notes', methods=['POST'])
def create_note():
    """Create a new note for an event"""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        event_name = data.get('eventName')
        if not title:
            return jsonify({"error": "Note title is required"}), 400
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        doc = {
            'title': title,
            'description': data.get('description', ''),
            'link': data.get('link', ''),
            'eventName': event_name,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('LearningResources').document('notes').collection('events').document(event_name).collection('items').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Note created'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note"""
    try:
        data = request.get_json() or {}
        event_name = data.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('notes').collection('events').document(event_name).collection('items').document(note_id)
        if not ref.get().exists:
            return jsonify({"error": "Note not found"}), 404
        
        updates = {
            'title': data.get('title', '').strip(),
            'description': data.get('description', ''),
            'link': data.get('link', ''),
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref.update(updates)
        return jsonify({"message": "Note updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('notes').collection('events').document(event_name).collection('items').document(note_id)
        if not ref.get().exists:
            return jsonify({"error": "Note not found"}), 404
        
        ref.delete()
        return jsonify({"message": "Note deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Tests endpoints
@firebase_routes.route('/api/LearningResources/tests', methods=['GET'])
def get_tests():
    """Get all tests for an event"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        docs = db.collection('LearningResources').document('tests').collection('events').document(event_name).collection('items').stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        # Sort by createdAt desc
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/tests', methods=['POST'])
def create_test():
    """Create a new test for an event"""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        event_name = data.get('eventName')
        if not title:
            return jsonify({"error": "Test title is required"}), 400
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        doc = {
            'title': title,
            'description': data.get('description', ''),
            'link': data.get('link', ''),
            'eventName': event_name,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('LearningResources').document('tests').collection('events').document(event_name).collection('items').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Test created'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/tests/<test_id>', methods=['PUT'])
def update_test(test_id):
    """Update a test"""
    try:
        data = request.get_json() or {}
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('tests').collection('events').document(event_name).collection('items').document(test_id)
        if not ref.get().exists:
            return jsonify({"error": "Test not found"}), 404
        
        updates = {
            'title': data.get('title', '').strip(),
            'description': data.get('description', ''),
            'link': data.get('link', ''),
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref.update(updates)
        return jsonify({"message": "Test updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/tests/<test_id>', methods=['DELETE'])
def delete_test(test_id):
    """Delete a test"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('tests').collection('events').document(event_name).collection('items').document(test_id)
        if not ref.get().exists:
            return jsonify({"error": "Test not found"}), 404
        
        ref.delete()
        return jsonify({"message": "Test deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Resources endpoints
@firebase_routes.route('/api/LearningResources/resources', methods=['GET'])
def get_resources():
    """Get all resources for an event"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        docs = db.collection('LearningResources').document('resources').collection('events').document(event_name).collection('items').stream()
        items = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            items.append(d)
        # Sort by createdAt desc
        def get_ts(d):
            ts = d.get('createdAt')
            try:
                return ts.timestamp() if hasattr(ts, 'timestamp') else 0
            except Exception:
                return 0
        items.sort(key=get_ts, reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/resources', methods=['POST'])
def create_resource():
    """Create a new resource for an event"""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        event_name = data.get('eventName')
        if not title:
            return jsonify({"error": "Resource title is required"}), 400
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        doc = {
            'title': title,
            'description': data.get('description', ''),
            'link': data.get('link', ''),
            'eventName': event_name,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref = db.collection('LearningResources').document('resources').collection('events').document(event_name).collection('items').document()
        ref.set(doc)
        return jsonify({'id': ref.id, 'message': 'Resource created'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/resources/<resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update a resource"""
    try:
        data = request.get_json() or {}
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('resources').collection('events').document(event_name).collection('items').document(resource_id)
        if not ref.get().exists:
            return jsonify({"error": "Resource not found"}), 404
        
        updates = {
            'title': data.get('title', '').strip(),
            'description': data.get('description', ''),
            'link': data.get('link', ''),
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        ref.update(updates)
        return jsonify({"message": "Resource updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/resources/<resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Delete a resource"""
    try:
        event_name = request.args.get('eventName')
        if not event_name:
            return jsonify({"error": "eventName is required"}), 400
        
        ref = db.collection('LearningResources').document('resources').collection('events').document(event_name).collection('items').document(resource_id)
        if not ref.get().exists:
            return jsonify({"error": "Resource not found"}), 404
        
        ref.delete()
        return jsonify({"message": "Resource deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/topics-content/<event_name>', methods=['GET'])
def get_topics_content(event_name):
    """Get topics content for an event"""
    try:
        # Construct blob path
        safe_event_name = event_name.replace('/', '_')
        blob_path = f"topics/{safe_event_name}/content.html"
        
        print(f"[GET topics-content] Event: {event_name}, Safe: {safe_event_name}, Path: {blob_path}")
        
        # Check if blob exists
        blob = bucket.blob(blob_path)
        exists = blob.exists()
        print(f"[GET topics-content] Blob exists: {exists}")
        
        if not exists:
            return jsonify({"content": ""}), 200
        
        # Get content
        content = blob.download_as_text(encoding='utf-8')
        print(f"[GET topics-content] Content length: {len(content)}, Preview: {content[:100]}")
        return jsonify({"content": content}), 200
    
    except Exception as e:
        print(f"[GET topics-content] ERROR for {event_name}: {e}")
        logger.error(f"Error getting topics content for {event_name}: {e}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/LearningResources/topics-content/<event_name>', methods=['POST'])
def update_topics_content(event_name):
    """Update topics content for an event"""
    try:
        # Get content from request
        data = request.json
        print(f"[POST topics-content] Event: {event_name}, Data: {data}")
        
        if not data or 'content' not in data:
            print(f"[POST topics-content] ERROR: No content provided")
            return jsonify({"error": "No content provided"}), 400
        
        content = data.get('content', '')
        print(f"[POST topics-content] Content length: {len(content)}, Preview: {content[:100]}")
        
        # Save content to Firebase Storage
        safe_event_name = event_name.replace('/', '_')
        blob_path = f"topics/{safe_event_name}/content.html"
        print(f"[POST topics-content] Safe name: {safe_event_name}, Blob path: {blob_path}")
        
        # Create blob and upload content with HTML content type
        blob = bucket.blob(blob_path)
        print(f"[POST topics-content] Bucket name: {bucket.name}, Blob: {blob.name}")
        
        # Upload as string directly (Quill content is already a string)
        blob.upload_from_string(content, content_type='text/html; charset=utf-8')
        print(f"[POST topics-content] Upload completed")
        
        # Verify it was saved
        blob.reload()  # Refresh blob metadata
        exists = blob.exists()
        print(f"[POST topics-content] Blob exists after upload: {exists}")
        
        if exists:
            # Double check by trying to read it back
            saved_content = blob.download_as_text(encoding='utf-8')
            print(f"[POST topics-content] Verified saved content length: {len(saved_content)}")
            return jsonify({"success": True, "message": "Content saved successfully", "contentLength": len(saved_content)}), 200
        else:
            print(f"[POST topics-content] ERROR: Failed to verify blob exists after upload")
            logger.error(f"Failed to verify blob exists after upload: {blob_path}")
            return jsonify({"error": "Failed to verify content was saved"}), 500
    
    except Exception as e:
        print(f"[POST topics-content] EXCEPTION for {event_name}: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error updating topics content for {event_name}: {e}")
        return jsonify({"error": str(e)}), 500