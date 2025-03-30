import firebase_admin
from firebase_admin import credentials, firestore
import json

def test_firebase_connection():
    """Test connection to Firebase"""
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate('service_key.json')
        firebase_admin.initialize_app(cred)
        
        # Get Firestore database instance
        db = firestore.client()
        
        print("Successfully connected to Firebase!")
        
        # Test writing a document
        test_ref = db.collection('test').document('test_doc')
        test_ref.set({
            'message': 'This is a test document',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        print("Successfully wrote to Firestore!")
        
        # Test reading the document
        doc = test_ref.get()
        print(f"Document data: {doc.to_dict()}")
        
        # Test deleting the document
        test_ref.delete()
        print("Successfully deleted test document!")
        
        return True
    except Exception as e:
        print(f"Error connecting to Firebase: {str(e)}")
        return False

if __name__ == "__main__":
    test_firebase_connection() 