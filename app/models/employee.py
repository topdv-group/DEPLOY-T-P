# app/models/employee.py - Employee model
from datetime import datetime

class Employee:
    """Employee model class"""
    
    def __init__(self, employee_id=None, data=None):
        self.id = employee_id
        self.rfid = data.get('rfid') if data else None
        self.name = data.get('name') if data else None
        self.phone = data.get('phone') if data else None
        self.register_time = data.get('registerTime') if data else None
        self.attended = data.get('attended', False)
        self.paid = data.get('paid', False)
        self.attendance = data.get('attendance', [])
        self.payment_status = data.get('payment_status')
        self.payout_id = data.get('payoutId')
        self.payment_amount = data.get('payment_amount')
        self.last_attendance = data.get('last_attendance')
        self.last_attendance_date = data.get('last_attendance_date')
    
    def to_dict(self):
        """Convert employee to dictionary"""
        return {
            'id': self.id,
            'rfid': self.rfid,
            'name': self.name,
            'phone': self.phone,
            'registerTime': self.register_time,
            'attended': self.attended,
            'paid': self.paid,
            'attendance': self.attendance,
            'payment_status': self.payment_status,
            'payoutId': self.payout_id,
            'payment_amount': self.payment_amount,
            'last_attendance': self.last_attendance,
            'last_attendance_date': self.last_attendance_date
        }
