import os
from dotenv import load_dotenv;
load_dotenv()
class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    FIREBASE_CONFIG = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID')
    }
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_SECRET = os.getenv('PAYPAL_SECRET')
    PAYPAL_API_BASE = os.getenv('PAYPAL_API_BASE')
    