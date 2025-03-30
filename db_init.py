import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate('service_key.json')
firebase_admin.initialize_app(cred)

# Get Firestore database instance
db = firestore.client() 