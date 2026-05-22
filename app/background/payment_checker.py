# app/background/payment_checker.py
import time
from datetime import datetime
from app.utils.logger import logger

class PaymentChecker:
    def __init__(self, firebase_service, settings_service, shutdown_event):
        self.firebase_service = firebase_service
        self.settings_service = settings_service
        self.shutdown_event = shutdown_event
        self.check_interval = 300
    
    def run(self):
        logger.info("Payment status checker thread started")
        while not self.shutdown_event.is_set():
            try:
                self.check_pending_payments()
            except Exception as e:
                logger.error(f"Payment status checker error: {e}")
            self.shutdown_event.wait(self.check_interval)
    
    def check_pending_payments(self):
        try:
            logger.info("Checking pending payment statuses...")
            
            employees = self.firebase_service.get_employees()
            if not employees:
                return
            
            for key, details in employees.items():
                payment_status = details.get("payment_status")
                payout_id = details.get("payoutId")
                
                if payment_status == "PENDING" and payout_id:
                    self._check_single_payment(key, details, payout_id)
                    
        except Exception as e:
            logger.error(f"Error checking pending payments: {e}")
    
    def _check_single_payment(self, employee_id, details, payout_id):
        try:
            from app.services.payment_service import PaymentService
            
            payment_service = PaymentService(self.firebase_service, self.settings_service)
            result = payment_service.check_payment_status(payout_id)
            
            if result.get("success"):
                status = result.get("status")
                
                if status == "COMPLETED":
                    self.firebase_service.update_employee(employee_id, {
                        "paid": True,
                        "payment_status": "COMPLETED",
                        "payment_confirmed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    logger.info(f"Payment confirmed for employee {employee_id}")
                    
                elif status in ["FAILED", "REJECTED", "EXPIRED"]:
                    self.firebase_service.update_employee(employee_id, {
                        "paid": False,
                        "payment_status": status,
                        "payment_failed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    logger.warning(f"Payment failed for employee {employee_id}: {status}")
                    
        except Exception as e:
            logger.error(f"Error checking payment for {employee_id}: {e}")
