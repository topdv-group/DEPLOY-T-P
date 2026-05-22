# app/services/attendance_service.py
from datetime import datetime
from app.utils.logger import logger

class AttendanceService:
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
    
    def mark_attendance(self, rfid, custom_timestamp=None):
        found, employee_id, employee_details = self.firebase_service.get_employee_by_rfid(rfid)
        
        if not found:
            return {"success": False, "message": f"RFID {rfid} not found"}
        
        current_time = custom_timestamp if custom_timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today_date = current_time.split(" ")[0]
        
        employee = self.firebase_service.get_employee(employee_id)
        
        if not employee:
            return {"success": False, "message": "Employee data not found"}
        
        if "attendance" not in employee:
            employee["attendance"] = []
        
        already_marked = any(record.get("timestamp", "").startswith(today_date) for record in employee.get("attendance", []))
        
        if already_marked:
            return {"success": True, "already_marked": True, "message": f"{employee_details.get('name')} already attended today"}
        
        attendance_record = {"timestamp": current_time, "date": today_date}
        employee["attendance"].append(attendance_record)
        
        self.firebase_service.update_employee(employee_id, {
            "attendance": employee["attendance"],
            "attended": True,
            "last_attendance": current_time,
            "last_attendance_date": today_date
        })
        
        logger.info(f"Attendance marked for {employee_details.get('name')}")
        
        return {
            "success": True,
            "message": f"Attendance marked for {employee_details.get('name')}",
            "data": {"employee_id": employee_id, "name": employee_details.get("name"), "timestamp": current_time}
        }
