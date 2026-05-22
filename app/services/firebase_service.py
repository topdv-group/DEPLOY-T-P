# app/services/firebase_service.py - Firebase database operations
from firebase_admin import db
from app.utils.logger import logger

class FirebaseService:
    def __init__(self, firebase_app):
        self.firebase_app = firebase_app
    
    def get_reference(self, path):
        """Get a database reference"""
        return db.reference(path)
    
    def get_employees(self):
        """Get all employees"""
        try:
            ref = db.reference("EMPLOYEES")
            return ref.get()
        except Exception as e:
            logger.error(f"Error getting employees: {e}")
            return None
    
    def get_employee(self, employee_id):
        """Get a single employee"""
        try:
            ref = db.reference(f"EMPLOYEES/{employee_id}")
            return ref.get()
        except Exception as e:
            logger.error(f"Error getting employee {employee_id}: {e}")
            return None
    
    def update_employee(self, employee_id, data):
        """Update an employee"""
        try:
            ref = db.reference(f"EMPLOYEES/{employee_id}")
            ref.update(data)
            return True
        except Exception as e:
            logger.error(f"Error updating employee {employee_id}: {e}")
            return False
    
    def get_employees_by_payout_id(self, payout_id):
        """Find employee by payout ID"""
        try:
            employees = self.get_employees()
            if employees:
                for key, details in employees.items():
                    if details.get("payoutId") == payout_id:
                        return key, details
            return None, None
        except Exception as e:
            logger.error(f"Error finding employee by payout ID: {e}")
            return None, None
    
    def get_employee_by_rfid(self, rfid):
        """Find employee by RFID - returns (found, employee_id, employee_details)"""
        try:
            employees = self.get_employees()
            if employees:
                for key, details in employees.items():
                    if str(details.get("rfid")) == str(rfid):
                        return True, key, details
            return False, None, None
        except Exception as e:
            logger.error(f"Error finding employee by RFID: {e}")
            return False, None, None
    
    def check_duplicate_phone_or_rfid(self, phone, rfid):
        """Check for duplicate phone or RFID"""
        try:
            employees = self.get_employees()
            if employees:
                for details in employees.values():
                    if str(details.get("phone")) == str(phone):
                        return True, "phone"
                    if str(details.get("rfid")) == str(rfid):
                        return True, "rfid"
            return False, None
        except Exception as e:
            logger.error(f"Duplicate check error: {e}")
            return False, None
    
    def create_employee(self, data):
        """Create a new employee"""
        try:
            ref = db.reference("EMPLOYEES")
            new_ref = ref.push(data)
            return new_ref.key
        except Exception as e:
            logger.error(f"Error creating employee: {e}")
            return None
    
    def delete_employee(self, employee_id):
        """Delete an employee"""
        try:
            ref = db.reference(f"EMPLOYEES/{employee_id}")
            ref.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting employee {employee_id}: {e}")
            return False
    
    def reset_all_attendance(self):
        """Reset attendance for all employees"""
        try:
            employees = self.get_employees()
            if employees:
                for key in employees:
                    self.update_employee(key, {
                        "attended": False,
                        "paid": False
                    })
                logger.info(f"Attendance reset for {len(employees)} employees")
                return True
        except Exception as e:
            logger.error(f"Error resetting attendance: {e}")
            return False