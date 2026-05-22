# app/routes/employee_routes.py - Employee management routes
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.utils.logger import logger
from app.utils.validators import validate_phone, validate_name

employee_bp = Blueprint('employee', __name__, url_prefix='/api')

@employee_bp.route("/register", methods=["POST"])
def register():
    """Register a new employee"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        rfid = data.get("rfid", "").strip()
        
        if not all([name, phone, rfid]):
            return jsonify({
                "error": "Missing required fields: name, phone, and rfid are required"
            }), 400
        
        if not validate_name(name):
            return jsonify({"error": "Invalid name"}), 400
        
        if not validate_phone(phone):
            return jsonify({
                "error": "Invalid phone number. Must contain only digits and be at least 9 digits"
            }), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        duplicate_found, duplicate_type = firebase_service.check_duplicate_phone_or_rfid(phone, rfid)
        
        if duplicate_found:
            return jsonify({
                "status": "fail",
                "message": f"Registration failed. The {duplicate_type} already exists."
            }), 409
        
        employee_data = {
            'rfid': rfid,
            'name': name,
            'phone': phone,
            'registerTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'attended': False,
            'paid': False,
            'attendance': []
        }
        
        employee_id = firebase_service.create_employee(employee_data)
        
        if not employee_id:
            return jsonify({"error": "Failed to create employee"}), 500
        
        logger.info(f"New employee registered: {name} (ID: {employee_id})")
        
        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "id": employee_id,
                "name": name,
                "phone": phone,
                "rfid": rfid
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@employee_bp.route("/get_employees", methods=["GET"])
def get_employees():
    """Retrieve all employees"""
    try:
        firebase_service = current_app.config['FIREBASE_SERVICE']
        employees = firebase_service.get_employees()
        
        if not employees:
            return jsonify({
                "status": "success",
                "message": "No employees found in database",
                "employees": [],
                "count": 0
            }), 200
        
        employee_list = []
        for key, details in employees.items():
            employee_list.append({
                "id": key,
                "details": details
            })
        
        logger.info(f"Retrieved {len(employee_list)} employees")
        
        return jsonify({
            "status": "success",
            "employees": employee_list,
            "count": len(employee_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Retrieval error: {str(e)}")
        return jsonify({"error": f"Failed to retrieve employee data: {str(e)}"}), 500

@employee_bp.route("/get_employee/<employee_id>", methods=["GET"])
def get_employee(employee_id):
    """Retrieve a single employee by ID"""
    try:
        firebase_service = current_app.config['FIREBASE_SERVICE']
        employee_data = firebase_service.get_employee(employee_id)
        
        if not employee_data:
            return jsonify({"error": "Employee not found"}), 404
        
        return jsonify({
            "status": "success",
            "employee": {
                "id": employee_id,
                "details": employee_data
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving employee: {str(e)}")
        return jsonify({"error": f"Failed to retrieve employee: {str(e)}"}), 500

@employee_bp.route("/update_employee/<employee_id>", methods=["PUT"])
def update_employee(employee_id):
    """Update employee information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        existing = firebase_service.get_employee(employee_id)
        
        if not existing:
            return jsonify({"error": "Employee not found"}), 404
        
        updates = {}
        allowed_fields = ["name", "phone", "rfid"]
        for field in allowed_fields:
            if field in data and data[field]:
                updates[field] = data[field].strip()
        
        if updates:
            updates["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            firebase_service.update_employee(employee_id, updates)
            logger.info(f"Employee {employee_id} updated")
        
        return jsonify({
            "status": "success",
            "message": "Employee updated successfully",
            "updated_fields": list(updates.keys())
        }), 200
        
    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        return jsonify({"error": f"Failed to update employee: {str(e)}"}), 500

@employee_bp.route("/delete_employee/<employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        firebase_service = current_app.config['FIREBASE_SERVICE']
        existing = firebase_service.get_employee(employee_id)
        
        if not existing:
            return jsonify({"error": "Employee not found"}), 404
        
        firebase_service.delete_employee(employee_id)
        logger.info(f"Employee {employee_id} deleted")
        
        return jsonify({
            "status": "success",
            "message": "Employee deleted successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Deletion error: {str(e)}")
        return jsonify({"error": f"Failed to delete employee: {str(e)}"}), 500