# app/__init__.py - Flask app factory
import os
import threading
from datetime import datetime
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.utils.logger import logger, shutdown_event
from app.config import init_firebase
from app.services.firebase_service import FirebaseService
from app.services.settings_service import SettingsService

# Global instances
firebase_service = None
settings_service = None

def create_app():
    """Application factory"""
    global firebase_service, settings_service
    
    app = Flask(__name__, static_folder='../static', static_url_path='')
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize rate limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Initialize Firebase
    try:
        firebase_app = init_firebase()
        firebase_service = FirebaseService(firebase_app)
        settings_service = SettingsService(firebase_service)
        settings_service.load_settings()
        
        app.config['FIREBASE_SERVICE'] = firebase_service
        app.config['SETTINGS_SERVICE'] = settings_service
        
        logger.info("Firebase and Settings initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        try:
            # Check Firebase connection
            firebase_service.get_reference("/").get(shallow=True)
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            "status": "healthy" if db_status == "connected" else "degraded",
            "database": db_status,
            "timestamp": datetime.now().isoformat()
        }), 200 if db_status == "connected" else 503
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    return app

def register_blueprints(app):
    """Register all route blueprints"""
    from app.routes.employee_routes import employee_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.payment_routes import payment_bp
    from app.webhook_routes import webhook_bp
    
    app.register_blueprint(employee_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(webhook_bp)
    # Static file routes
    @app.route('/')
    def serve_index():
        return send_from_directory('../static', 'index.html')
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory('../static', filename)
    
    logger.info("All blueprints registered")