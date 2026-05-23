# app/routes/admin_routes.py
from flask import Blueprint, request, jsonify, current_app, make_response
from datetime import datetime
import json
import os
from app.utils.logger import logger
from flask_limiter import Limiter  # ← ADD THIS
from flask_limiter.util import get_remote_address  # ← ADD THIS

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/settings', methods=['GET'])
def get_admin_settings():
    try:
        settings_service = current_app.config['SETTINGS_SERVICE']
        
        settings = {
            'paymentTime': settings_service.get_setting('paymentTime', '17:30'),
            'payAmount': int(settings_service.get_setting('payAmount', 100)),
            'shiftExpirelyTime': settings_service.get_setting('shiftExpirelyTime', '17:00'),
            'pawapayApiUrl': settings_service.get_setting('pawapayApiUrl', 'https://api.sandbox.pawapay.io/v2/payouts'),
            'environment': 'production' if os.getenv('PRODUCTION') == 'true' else 'development'
        }
        
        return jsonify(settings), 200
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/settings/payment', methods=['POST'])
def update_payment_settings():
    try:
        data = request.get_json()
        updates = {}
        
        if 'paymentTime' in data:
            updates['paymentTime'] = data['paymentTime']
        if 'payAmount' in data:
            updates['payAmount'] = int(data['payAmount'])
        if 'shiftExpireTime' in data:
            updates['shiftExpirelyTime'] = data['shiftExpireTime']
        if 'pawapayApiUrl' in data:
            updates['pawapayApiUrl'] = data['pawapayApiUrl']
        
        if updates:
            settings_service = current_app.config['SETTINGS_SERVICE']
            settings_service.save_settings(updates)
            logger.info(f"Payment settings updated: {updates}")
        
        return jsonify({"success": True, "message": "Settings updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating payment settings: {e}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
# @Limiter.exempt  # ← ADD THIS LINE
def get_stats():
    try:
        firebase_service = current_app.config['FIREBASE_SERVICE']
        employees = firebase_service.get_employees()
        
        if not employees:
            return jsonify({
                "total_employees": 0,
                "attended_today": 0,
                "paid_today": 0
            }), 200
        
        total = len(employees)
        attended = sum(1 for emp in employees.values() if emp.get("attended", False))
        paid = sum(1 for emp in employees.values() if emp.get("paid", False))
        
        return jsonify({
            "total_employees": total,
            "attended_today": attended,
            "paid_today": paid,
            "attendance_percentage": round((attended / total * 100) if total > 0 else 0, 2),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500