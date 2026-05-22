# app/config.py - Configuration and Firebase initialization
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

from app.utils.logger import logger

# Load environment variables
load_dotenv()

def parse_firebase_json():
    """Parse Firebase service account JSON from environment variable"""
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    
    if not firebase_json:
        return None
    
    # Remove any BOM characters
    if firebase_json.startswith('\ufeff'):
        firebase_json = firebase_json[1:]
    
    # Strip whitespace
    firebase_json = firebase_json.strip()
    
    # Remove surrounding single or double quotes if present
    if firebase_json.startswith("'") and firebase_json.endswith("'"):
        firebase_json = firebase_json[1:-1]
    elif firebase_json.startswith('"') and firebase_json.endswith('"'):
        firebase_json = firebase_json[1:-1]
    
    # Parse JSON
    try:
        return json.loads(firebase_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Firebase JSON: {e}")
        logger.error(f"First 200 chars: {firebase_json[:200]}...")
        raise

def init_firebase():
    """Initialize Firebase with credentials from environment"""
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
    database_url = os.getenv("DATABASE_URL")
    
    # Validate environment variables
    if not firebase_key_path and not firebase_json:
        logger.error("Either FIREBASE_KEY_PATH or FIREBASE_SERVICE_ACCOUNT must be set")
        raise ValueError("Firebase configuration missing")
    
    if not database_url:
        logger.error("DATABASE_URL missing in environment")
        raise ValueError("DATABASE_URL missing")
    
    # Initialize Firebase credentials
    if firebase_key_path and os.path.exists(firebase_key_path):
        # Load from file
        cred = credentials.Certificate(firebase_key_path)
        logger.info(f"Firebase credentials loaded from file: {firebase_key_path}")
    elif firebase_json:
        # Parse JSON from environment variable
        cred_dict = parse_firebase_json()
        if not cred_dict:
            raise ValueError("Invalid FIREBASE_SERVICE_ACCOUNT JSON format")
        
        # Fix private key newlines if needed
        if 'private_key' in cred_dict:
            cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
        
        cred = credentials.Certificate(cred_dict)
        logger.info("Firebase credentials loaded from environment variable")
    else:
        raise FileNotFoundError(f"Firebase key file not found: {firebase_key_path}")
    
    # Initialize Firebase SDK
    try:
        if not firebase_admin._apps:
            firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            logger.info(f"Firebase initialized successfully")
        else:
            firebase_app = firebase_admin.get_app()
            logger.info("Firebase already initialized")
        return firebase_app
    except Exception as e:
        logger.error(f"Firebase initialization error: {e}")
        raise

def get_firebase_app():
    """Get the existing Firebase app"""
    return firebase_admin.get_app() if firebase_admin._apps else None