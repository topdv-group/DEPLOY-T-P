# app/background/payment_timer.py
import time
from datetime import datetime
from app.utils.logger import logger
from app.utils.helpers import is_time_reached
from app.services.payment_service import PaymentService

class PaymentTimer:
    def __init__(self, firebase_service, settings_service, shutdown_event):
        self.firebase_service = firebase_service
        self.settings_service = settings_service
        self.shutdown_event = shutdown_event
        self.last_payment_date = None
    
    def run(self):
        logger.info("Payment timer thread started")
        while not self.shutdown_event.is_set():
            try:
                self.process_payments()
            except Exception as e:
                logger.error(f"Payment timer error: {e}")
            self.shutdown_event.wait(30)
    
    def process_payments(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        payment_time = self.settings_service.get_setting("paymentTime", "17:30")
        
        if is_time_reached(payment_time) and self.last_payment_date != current_date:
            logger.info("Starting employee payment requests...")
            
            employees = self.firebase_service.get_employees()
            if not employees:
                logger.info("No employees found")
                self.last_payment_date = current_date
                return
            
            payment_service = PaymentService(self.firebase_service, self.settings_service)
            
            successful = 0
            failed = 0
            skipped = 0
            
            for key, details in employees.items():
                if details.get("paid") is True:
                    skipped += 1
                    continue
                
                if details.get("payment_status") == "PENDING":
                    skipped += 1
                    continue
                
                if details.get("attended") is False:
                    skipped += 1
                    continue
                
                result = payment_service.request_payment(key, details)
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
            
            self.last_payment_date = current_date
            logger.info(f"Payment request complete. Accepted={successful}, Failed={failed}, Skipped={skipped}")
    
    def check_missed_on_startup(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        payment_time = self.settings_service.get_setting("paymentTime", "17:30")
        
        if current_time >= payment_time and self.last_payment_date != current_date:
            logger.info("Payment time already passed today - processing payments on startup")
            self.process_payments()
