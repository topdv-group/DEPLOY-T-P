#!/usr/bin/env python
# run.py - Main entry point
import os
import sys
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from app package
from app import create_app
from app.utils.logger import logger, shutdown_event

# Create Flask app at module level (MUST be outside if __name__ block)
app = create_app()

def start_background_threads():
    """Start all background threads"""
    firebase_service = app.config.get('FIREBASE_SERVICE')
    settings_service = app.config.get('SETTINGS_SERVICE')
    
    if not firebase_service or not settings_service:
        logger.error("Cannot start background threads: services not initialized")
        return
    
    from app.background.attendance_timer import AttendanceTimer
    from app.background.payment_timer import PaymentTimer
    from app.background.payment_checker import PaymentChecker
    
    logger.info("Starting background threads...")
    
    # Start attendance reset timer
    attendance_timer = AttendanceTimer(firebase_service, settings_service, shutdown_event)
    attendance_thread = threading.Thread(
        target=attendance_timer.run,
        name="AttendanceResetThread",
        daemon=True
    )
    attendance_thread.start()
    
    # Start payment timer
    payment_timer = PaymentTimer(firebase_service, settings_service, shutdown_event)
    payment_thread = threading.Thread(
        target=payment_timer.run,
        name="PaymentThread",
        daemon=True
    )
    payment_thread.start()
    
    # Start payment checker thread
    payment_checker = PaymentChecker(firebase_service, settings_service, shutdown_event)
    checker_thread = threading.Thread(
        target=payment_checker.run,
        name="PaymentStatusCheckerThread",
        daemon=True
    )
    checker_thread.start()
    
    logger.info("All background threads started successfully")

def check_missed_events():
    """Check for missed events on startup"""
    try:
        firebase_service = app.config.get('FIREBASE_SERVICE')
        settings_service = app.config.get('SETTINGS_SERVICE')
        
        if not firebase_service:
            logger.warning("Firebase service not available")
            return
        
        from app.background.attendance_timer import AttendanceTimer
        from app.background.payment_timer import PaymentTimer
        
        attendance_timer = AttendanceTimer(firebase_service, settings_service, shutdown_event)
        payment_timer = PaymentTimer(firebase_service, settings_service, shutdown_event)
        
        attendance_timer.check_missed_on_startup()
        payment_timer.check_missed_on_startup()
        
        logger.info("Startup event check completed")
    except Exception as e:
        logger.error(f"Error checking missed events: {e}")

# Start background threads when the module loads (for Gunicorn)
# This runs when the app is imported, not just when run directly
if os.environ.get("PRODUCTION") == "true":
    # On Render, start background threads
    start_background_threads()
    check_missed_events()

if __name__ == "__main__":
    try:
        # Start background threads (for local development)
        start_background_threads()
        
        # Check for missed events
        check_missed_events()
        
        # Get port from environment
        port = int(os.environ.get("PORT", 5000))
        
        logger.info(f"Starting Flask server on http://0.0.0.0:{port}")
        logger.info(f"Open your browser and go to: http://localhost:{port}")
        
        # Use waitress for production
        from waitress import serve
        serve(app, host="0.0.0.0", port=port)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
