import firebase_admin
from firebase_admin import credentials, firestore
import os

CREDENTIAL_FILE = 'serviceAccountKey.json' 

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIAL_FILE)
        firebase_admin.initialize_app(cred)
except FileNotFoundError:
    print(f"ERROR: File {CREDENTIAL_FILE} tidak ditemukan.")
except Exception as e:
    print(f"ERROR saat inisialisasi Firebase: {e}")

db = firestore.client()
USERS_COLLECTION = db.collection('users')