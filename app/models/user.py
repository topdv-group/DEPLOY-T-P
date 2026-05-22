# app/models/user.py - User model for authentication
from datetime import datetime, timedelta
import hashlib
import secrets

class User:
    """User model for authentication"""
    
    def __init__(self, user_id=None, data=None):
        self.id = user_id
        self.email = data.get('email') if data else None
        self.password_hash = data.get('password_hash') if data else None
        self.salt = data.get('salt') if data else None
        self.role = data.get('role', 'user')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self):
        """Convert user to dictionary (without sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash a password with PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            salt.encode(), 
            100000
        )
        
        return salt, hashed.hex()
    
    @staticmethod
    def verify_password(password, salt, stored_hash):
        """Verify a password against stored hash"""
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            salt.encode(), 
            100000
        ).hex()
        
        return computed_hash == stored_hash
