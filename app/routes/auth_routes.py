# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import hashlib
import secrets
from app.utils.logger import logger

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')  # Note: /api/auth prefix

@auth_bp.route('/login', methods=['POST'])  # ← This handles POST to /api/auth/login
def auth_login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('rememberMe', False)
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        users_ref = firebase_service.get_reference("USERS")
        users = users_ref.get()
        
        if not users:
            users = {}
        
        user_id = None
        user_data = None
        
        for key, user in users.items():
            if user.get('email', '').lower() == email:
                user_id = key
                user_data = user
                break
        
        if not user_data:
            logger.warning(f"User not found: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        salt = user_data.get('salt')
        stored_hash = str(user_data.get('password_hash', ''))
        
        if not salt or not stored_hash:
            return jsonify({"error": "Invalid credentials"}), 401
        
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        
        if computed_hash != stored_hash:
            logger.warning(f"Invalid password for {email}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        token = secrets.token_urlsafe(32)
        
        sessions_ref = firebase_service.get_reference("SESSIONS")
        expiry = datetime.now() + timedelta(days=7 if remember_me else 1)
        
        session_data = {
            'user_id': user_id,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'expires_at': expiry.isoformat(),
            'remember_me': remember_me
        }
        
        sessions_ref.child(token).set(session_data)
        
        logger.info(f"User logged in successfully: {email}")
        
        return jsonify({
            "success": True,
            "token": token,
            "email": email,
            "message": "Login successful"
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
def auth_verify():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({"valid": False}), 401
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        sessions_ref = firebase_service.get_reference("SESSIONS")
        session = sessions_ref.child(token).get()
        
        if not session:
            return jsonify({"valid": False}), 401
        
        expires_at = datetime.fromisoformat(session['expires_at'])
        if expires_at < datetime.now():
            sessions_ref.child(token).delete()
            return jsonify({"valid": False}), 401
        
        return jsonify({"valid": True, "email": session['email']}), 200
        
    except Exception as e:
        logger.error(f"Verify error: {e}")
        return jsonify({"valid": False}), 401

@auth_bp.route('/logout', methods=['POST'])
def auth_logout():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            firebase_service = current_app.config['FIREBASE_SERVICE']
            sessions_ref = firebase_service.get_reference("SESSIONS")
            sessions_ref.child(token).delete()
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"success": False}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def auth_forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        import secrets
        reset_token = secrets.token_urlsafe(32)
        
        from datetime import datetime, timedelta
        base_url = request.host_url.rstrip('/')
        reset_link = f"{base_url}/reset-password.html?token={reset_token}"
        
        return jsonify({
            "success": True,
            "message": "Reset link generated",
            "reset_link": reset_link
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
