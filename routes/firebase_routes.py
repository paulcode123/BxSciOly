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

@firebase_routes.route('/api/<collection>', methods=['GET'])
def get_all(collection):
    """Get all documents from a collection"""
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
        
        # Check if member has admin status
        admin_status = member_data.get('adminStatus', 'none')
        if admin_status == 'none':
            return jsonify({"error": "Access denied. Admin privileges required."}), 403
        
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
        
        if admin_status == 'none':
            return jsonify({"error": "Admin privileges not found"}), 401
        
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
    return get_all('Competitions')

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