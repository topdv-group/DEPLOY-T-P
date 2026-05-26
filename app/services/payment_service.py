# app/services/payment_service.py - Payment processing
import os
import uuid
import time
import requests
from datetime import datetime

from app.utils.logger import logger

class PaymentService:
    def __init__(self, firebase_service, settings_service):
        self.firebase_service = firebase_service
        self.settings_service = settings_service
    
    def get_api_key(self):
        """Get PawaPay API key from environment"""
        return os.getenv("PAWAPAY_API_KEY")
    
    def get_headers(self):
        """Get API headers"""
        api_key = self.get_api_key()
        if not api_key:
            return None
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def format_phone_number(self, phone):
        """Format phone number for PawaPay"""
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        if len(clean_phone) < 9:
            return None
        # return f"250{clean_phone[-9:]}"
        return f"256{clean_phone[-9:]}"
    
    def request_payment(self, employee_id, employee_details):
        """Request a payment for an employee"""
        try:
            api_url = self.settings_service.get_setting("pawapayApiUrl")
            pay_amount = self.settings_service.get_setting("payAmount", 100)
            headers = self.get_headers()
            
            if not headers:
                return {"success": False, "error": "API key not configured"}
            
            phone = employee_details.get("phone")
            if not phone:
                return {"success": False, "error": "No phone number"}
            
            formatted_phone = self.format_phone_number(phone)
            if not formatted_phone:
                return {"success": False, "error": "Invalid phone number"}
            
            payout_id = str(uuid.uuid4())
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            payload = {
                "payoutId": payout_id,
                "amount": pay_amount,
                # "currency": "RWF",
                "currency": "UGX",
                "recipient": {
                    "type": "MMO",
                    "accountDetails": {
                        "phoneNumber": formatted_phone,
                        # "provider": "MTN_MOMO_RWA"
                        "provider": "MTN_MOMO_UGA" 
                    }
                }
            }
            
            logger.info(f"Requesting payment of {pay_amount} RWF to {formatted_phone}")
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response_data = response.json()
            
            if response.status_code in [200, 201, 202] and response_data.get("status") == "ACCEPTED":
                # Payment accepted - mark as PENDING
                self.firebase_service.update_employee(employee_id, {
                    "paid": False,
                    "payment_status": "PENDING",
                    "payment_request_date": current_date,
                    "payment_amount": pay_amount,
                    "payment_currency": "RWF",
                    "payoutId": payout_id,
                    "recipient_phone": formatted_phone
                })
                logger.info(f"✓ Payment request ACCEPTED for {formatted_phone}")
                return {"success": True, "status": "PENDING", "payout_id": payout_id}
            else:
                self.firebase_service.update_employee(employee_id, {
                    "payment_status": response_data.get("status", "FAILED"),
                    "payment_error": response_data.get("message", "Unknown error"),
                    "last_payment_attempt": current_date
                })
                logger.error(f"✗ Payment request FAILED for {formatted_phone}: {response_data}")
                return {"success": False, "error": response_data}
                
        except Exception as e:
            logger.error(f"Payment request error: {e}")
            return {"success": False, "error": str(e)}
    
    def check_payment_status(self, payout_id):
        """Check payment status with PawaPay API"""
        try:
            api_url = self.settings_service.get_setting("pawapayApiUrl")
            headers = self.get_headers()
            
            if not headers:
                return {"success": False, "error": "API key not configured"}
            
            response = requests.get(
                f"{api_url}/{payout_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                payout_data = response.json()
                return {"success": True, "status": payout_data.get("status"), "data": payout_data}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {"success": False, "error": str(e)}