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
        
        # Add document with auto-generated ID
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
    """Find a member by email address"""
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
    """Parse results from a Duosmium URL and extract Bronx Science team data"""
    try:
        url = request.args.get('url')
        if not url or 'duosmium.org/results' not in url:
            return jsonify({'error': 'Invalid Duosmium URL'}), 400
        
        # Fetch the HTML content from the URL
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return jsonify({'error': f'Failed to fetch Duosmium page (status code {response.status_code})'}), 400
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract competition name, date, and location
        competition_name = soup.h1.text.strip() if soup.h1 else 'Unknown Competition'
        
        # Extract date from the page content
        date_text = soup.find('p').text.strip() if soup.find('p') else ''
        date_match = re.search(r'([A-Z][a-z]+day,\s+)?([A-Z][a-z]+\s+\d{1,2},\s+\d{4})', date_text)
        competition_date = date_match.group(2) if date_match else None
        
        # Convert date to standardized format
        if competition_date:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(competition_date, '%B %d, %Y')
                competition_date = date_obj.strftime('%Y-%m-%d')
            except Exception:
                competition_date = None
        
        # Extract location if available
        location_match = re.search(r'@\s+(.+)$', date_text)
        location = location_match.group(1).strip() if location_match else 'Unknown Location'
        
        # Extract total number of teams from the table
        team_rows = soup.select('table tr')
        total_teams = len(team_rows) - 1 if team_rows else 0  # Subtract header row
        
        # Extract Bronx Science teams and their results
        bronx_teams = []
        
        # Find all table rows after the header
        team_rows = team_rows[1:] if len(team_rows) > 1 else []
        
        for row in team_rows:
            cells = row.find_all('td')
            if not cells or len(cells) < 5:
                continue
            
            team_cell = cells[1]  # Team name cell
            team_name = team_cell.text.strip()
            
            # Check if this is a Bronx Science team
            if 'Bronx' in team_name and 'Science' in team_name:
                # Extract team rank and total score
                rank_text = cells[2].text.strip().split('✧')[0].strip()  # Remove any qualification marker
                try:
                    rank = int(rank_text)
                except ValueError:
                    rank = 0
                
                try:
                    total_score = int(cells[3].text.strip())
                except ValueError:
                    total_score = 0
                
                # Extract event results
                events = []
                event_columns = cells[4:]  # All cells after the total score are events
                
                # Get event names from table header
                header_row = soup.select('table tr')[0] if soup.select('table tr') else None
                event_headers = header_row.find_all('th')[4:] if header_row else []
                
                for i, event_cell in enumerate(event_columns):
                    if i >= len(event_headers):
                        break
                    
                    event_name = event_headers[i].text.strip()
                    # Remove any bullet points or special characters
                    event_name = re.sub(r'^[•\s]+', '', event_name)
                    
                    # Skip team penalties column
                    if event_name.lower() == 'team penalties':
                        continue
                    
                    # Extract place from the cell
                    place_text = event_cell.text.strip()
                    # Remove any suffix like ◊ or *
                    place_text = re.sub(r'[◊*]+$', '', place_text)
                    
                    try:
                        place = int(place_text)
                        # Only add events that have valid placements
                        events.append({
                            'eventName': event_name,
                            'place': place
                        })
                    except ValueError:
                        # Skip events without valid placements
                        pass
                
                # Add team to the results
                bronx_teams.append({
                    'teamName': team_name,
                    'rank': rank,
                    'totalScore': total_score,
                    'events': events
                })
        
        # Create the result object
        result = {
            'competitionName': competition_name,
            'date': competition_date,
            'location': location,
            'url': url,
            'teams': bronx_teams,
            'totalTeams': total_teams
        }
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@firebase_routes.route('/api/Tests', methods=['POST'])
def create_test():
    """Create a new test with PDF upload to Firebase Storage"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if required fields are present
        required_fields = ['testName', 'eventName', 'year', 'competitionType', 'uploadedBy', 'fileBase64', 'fileName', 'fileSize']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract file data
        file_base64 = data.pop('fileBase64')  # Remove from data to not store in Firestore
        file_name = data['fileName']
        file_extension = file_name.split('.')[-1].lower()
        
        # Only allow PDF files
        if file_extension != 'pdf':
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Create a unique file name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{data['eventName']}_{data['year']}_{timestamp}.{file_extension}"
        safe_filename = unique_filename.replace(' ', '_').replace('/', '_')
        
        # Upload the file to Firebase Storage
        import base64
        decoded_file = base64.b64decode(file_base64)
        blob_path = f"tests/{safe_filename}"
        blob = bucket.blob(blob_path)
        
        # Upload with appropriate content type
        blob.upload_from_string(decoded_file, content_type='application/pdf')
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Get the public URL
        file_url = blob.public_url
        
        # Add the URL to the data
        data['fileUrl'] = file_url
        
        # Create document in Firestore
        doc_ref = db.collection('Tests').document()
        doc_ref.set(data)
        
        return jsonify({"id": doc_ref.id, "fileUrl": file_url, "message": "Test uploaded successfully"}), 201
    
    except Exception as e:
        print(f"Error uploading test: {str(e)}")
        return jsonify({"error": str(e)}), 500

@firebase_routes.route('/api/Tests/<test_id>/view', methods=['POST'])
def increment_test_view_count(test_id):
    """Increment the view count for a test"""
    try:
        test_ref = db.collection('Tests').document(test_id)
        test_doc = test_ref.get()
        
        if not test_doc.exists:
            return jsonify({"error": "Test not found"}), 404
        
        # Get current view count or default to 0
        test_data = test_doc.to_dict()
        current_views = test_data.get('viewCount', 0)
        
        # Increment view count
        test_ref.update({
            'viewCount': current_views + 1
        })
        
        return jsonify({"success": True, "viewCount": current_views + 1}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 