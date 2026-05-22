# app/services/settings_service.py
from firebase_admin import db
from app.utils.logger import logger

DEFAULT_SETTINGS = {
    "shiftExpirelyTime": "17:00",
    "paymentTime": "17:30",
    "payAmount": 100,
    "pawapayApiUrl": "https://api.sandbox.pawapay.io/v2/payouts"
}

class SettingsService:
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.settings = DEFAULT_SETTINGS.copy()
    
    def load_settings(self):
        try:
            settings_ref = db.reference("SYSTEM_SETTINGS")
            firebase_settings = settings_ref.get()
            
            if firebase_settings:
                for key in DEFAULT_SETTINGS.keys():
                    if key in firebase_settings:
                        self.settings[key] = firebase_settings[key]
                logger.info(f"Settings loaded from Firebase: {self.settings}")
            else:
                self.save_settings(self.settings)
                logger.info("Default settings saved to Firebase")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self, new_settings):
        try:
            settings_ref = db.reference("SYSTEM_SETTINGS")
            settings_ref.update(new_settings)
            self.settings.update(new_settings)
            logger.info(f"Settings saved to Firebase: {new_settings}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)
