# app/utils/helpers.py
from datetime import datetime
from app.utils.logger import logger

def is_time_reached(target_time_str):
    """Check if current time has reached or passed target time"""
    try:
        now = datetime.now()
        target = datetime.strptime(target_time_str, "%H:%M").time()
        current = now.time()
        return current >= target
    except Exception as e:
        logger.error(f"Time comparison error: {e}")
        return False

def format_phone(phone):
    """Format phone number for payment"""
    clean_phone = ''.join(filter(str.isdigit, str(phone)))
    if len(clean_phone) < 9:
        return None
    return f"250{clean_phone[-9:]}"