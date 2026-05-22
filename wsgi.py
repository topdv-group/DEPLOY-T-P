# wsgi.py - Entry point for Gunicorn
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from run.py
from run import app

# This is what Gunicorn will use
application = app

# For debugging
print(f"✅ WSGI loaded successfully. App type: {type(app)}")
