# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import hashlib
import secrets
import os
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
    """Send password reset link via email"""
    try:
        import secrets
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from datetime import datetime, timedelta
        
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        users_ref = firebase_service.get_reference("USERS")
        users = users_ref.get()
        
        # Check if user exists (for security, don't reveal if user exists)
        user_exists = False
        if users:
            for key, user in users.items():
                if user.get('email') == email:
                    user_exists = True
                    break
        
        # Generate reset token (always generate, even if user doesn't exist)
        reset_token = secrets.token_urlsafe(32)
        
        # Only store reset request if user exists
        if user_exists:
            resets_ref = firebase_service.get_reference("PASSWORD_RESETS")
            resets_ref.child(reset_token).set({
                'email': email,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
            })
        
        # Create reset link
        base_url = request.host_url.rstrip('/')
        reset_link = f"{base_url}/reset-password.html?token={reset_token}"
        
        # Try to send email
        email_sent = send_reset_email_via_smtp(email, reset_link)
        
        if email_sent:
            return jsonify({
                "success": True,
                "message": "Password reset link has been sent to your email address."
            }), 200
        else:
            # Fallback: show link on screen for development
            return jsonify({
                "success": True,
                "message": "Email could not be sent. Please use the link below to reset your password.",
                "reset_link": reset_link
            }), 200
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def auth_reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({"error": "Token and password required"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        # Verify reset token
        resets_ref = firebase_service.get_reference("PASSWORD_RESETS")
        reset_data = resets_ref.child(token).get()
        
        if not reset_data:
            return jsonify({"error": "Invalid or expired reset token"}), 400
        
        # Check expiry
        expires_at = datetime.fromisoformat(reset_data['expires_at'])
        if expires_at < datetime.now():
            resets_ref.child(token).delete()
            return jsonify({"error": "Reset token has expired"}), 400
        
        # Find user by email
        email = reset_data['email']
        users_ref = firebase_service.get_reference("USERS")
        users = users_ref.get()
        
        user_key = None
        for key, user in users.items():
            if user.get('email') == email:
                user_key = key
                break
        
        if not user_key:
            return jsonify({"error": "User not found"}), 404
        
        # Hash new password
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', new_password.encode(), salt.encode(), 100000)
        
        # Update password
        users_ref.child(user_key).update({
            'password_hash': hashed.hex(),
            'salt': salt,
            'updated_at': datetime.now().isoformat()
        })
        
        # Delete used reset token
        resets_ref.child(token).delete()
        
        # Delete all sessions for this user
        sessions_ref = firebase_service.get_reference("SESSIONS")
        all_sessions = sessions_ref.get()
        if all_sessions:
            for session_token, session in all_sessions.items():
                if session.get('email') == email:
                    sessions_ref.child(session_token).delete()
        
        logger.info(f"Password reset for user: {email}")
        
        return jsonify({"success": True, "message": "Password reset successful"}), 200
        
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return jsonify({"error": str(e)}), 500

def send_reset_email_via_smtp(to_email, reset_link):
    """Send password reset email using SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Check if SMTP is enabled
        smtp_enabled = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
        
        if not smtp_enabled:
            logger.info(f"SMTP disabled. Reset link for {to_email}: {reset_link}")
            return False
        
        # Get SMTP configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
        smtp_from_name = os.getenv('SMTP_FROM_NAME', 'Tap & Pay System')
        
        if not smtp_username or not smtp_password:
            logger.error("SMTP credentials missing")
            return False
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = f"{smtp_from_name} <{smtp_from_email}>"
        msg['To'] = to_email
        msg['Subject'] = 'Tap & Pay - Password Reset Request'
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; background: #f9fafb; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>You requested to reset your password for your Tap & Pay account.</p>
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    <p>Or copy this link: <a href="{reset_link}">{reset_link}</a></p>
                    <p><strong>⚠️ This link expires in 1 hour.</strong></p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Tap & Pay System - Automated Attendance & Payment Management</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        logger.info(f"Sending password reset email to {to_email}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"✅ Password reset email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")
        return False