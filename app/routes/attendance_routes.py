# app/routes/attendance_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.utils.logger import logger
from app.services.attendance_service import AttendanceService

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api')

# app/routes/attendance_routes.py

# app/routes/attendance_routes.py

@attendance_bp.route('/markAttendance', methods=["POST"])
def mark_attendance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        rfid = data.get("rfid")
        if not rfid:
            return jsonify({"error": "RFID is required"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        attendance_service = AttendanceService(firebase_service)
        
        timestamp = data.get("time")
        result = attendance_service.mark_attendance(rfid, timestamp)
        
        # Log the result for debugging
        logger.info(f"Attendance result: {result}")
        
        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Attendance marking error: {str(e)}")
        return jsonify({"error": f"Failed to mark attendance: {str(e)}"}), 500

@attendance_bp.route("/get_attendance", methods=["GET"])
def get_attendance():
    try:
        date = request.args.get("date")
        employee_id = request.args.get("employee_id")
        
        if not date and not employee_id:
            return jsonify({"error": "Provide either date or employee_id"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        if employee_id:
            employee_data = firebase_service.get_employee(employee_id)
            if not employee_data:
                return jsonify({"error": "Employee not found"}), 404
            
            attendance = employee_data.get("attendance", [])
            return jsonify({
                "status": "success",
                "employee_id": employee_id,
                "employee_name": employee_data.get("name"),
                "attendance": attendance,
                "total_days": len(attendance)
            }), 200
        else:
            employees = firebase_service.get_employees()
            if not employees:
                return jsonify({"attendance": []}), 200
            
            attendance_list = []
            for key, details in employees.items():
                for record in details.get("attendance", []):
                    if record.get("date") == date:
                        attendance_list.append({
                            "employee_id": key,
                            "name": details.get("name"),
                            "timestamp": record.get("timestamp")
                        })
            
            return jsonify({
                "status": "success",
                "date": date,
                "attendance": attendance_list,
                "count": len(attendance_list)
            }), 200
            
    except Exception as e:
        logger.error(f"Error retrieving attendance: {str(e)}")
        return jsonify({"error": f"Failed to retrieve attendance: {str(e)}"}), 500