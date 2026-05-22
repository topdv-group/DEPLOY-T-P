# app/background/attendance_timer.py
import time
from datetime import datetime
from app.utils.logger import logger
from app.utils.helpers import is_time_reached

class AttendanceTimer:
    def __init__(self, firebase_service, settings_service, shutdown_event):
        self.firebase_service = firebase_service
        self.settings_service = settings_service
        self.shutdown_event = shutdown_event
        self.last_reset_date = None
    
    def run(self):
        logger.info("Attendance reset timer thread started")
        while not self.shutdown_event.is_set():
            try:
                self.reset_attendance()
            except Exception as e:
                logger.error(f"Attendance timer error: {e}")
            self.shutdown_event.wait(30)
    
    def reset_attendance(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        shift_expire_time = self.settings_service.get_setting("shiftExpirelyTime", "17:00")
        
        if is_time_reached(shift_expire_time) and self.last_reset_date != current_date:
            logger.info("Starting attendance reset...")
            success = self.firebase_service.reset_all_attendance()
            if success:
                self.last_reset_date = current_date
                logger.info("Attendance reset complete")
    
    def check_missed_on_startup(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        shift_expire_time = self.settings_service.get_setting("shiftExpirelyTime", "17:00")
        
        if current_time >= shift_expire_time and self.last_reset_date != current_date:
            logger.info("Reset time already passed today - resetting on startup")
            self.reset_attendance()
