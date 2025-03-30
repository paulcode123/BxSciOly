from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
from datetime import datetime

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