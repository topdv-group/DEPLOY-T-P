# app/routes/payment_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.utils.logger import logger

payment_bp = Blueprint('payment', __name__, url_prefix='/api')

@payment_bp.route("/pawapay/webhook", methods=["POST"])
def pawapay_webhook():
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        payout_id = data.get("payoutId")
        status = data.get("status")
        
        if not payout_id:
            return jsonify({"error": "Missing payoutId"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        employee_id, employee_details = firebase_service.get_employees_by_payout_id(payout_id)
        
        if employee_id:
            firebase_service.update_employee(employee_id, {
                "payment_status": status,
                "webhook_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "webhook_data": data
            })
            
            if status == "COMPLETED":
                firebase_service.update_employee(employee_id, {"paid": True})
                logger.info(f"Payment CONFIRMED for employee {employee_id}")
            elif status in ["FAILED", "REJECTED", "EXPIRED"]:
                firebase_service.update_employee(employee_id, {"paid": False})
                logger.warning(f"Payment FAILED for employee {employee_id}: {status}")
        else:
            logger.warning(f"Webhook received for unknown payoutId: {payout_id}")
        
        return jsonify({"success": True, "message": "Webhook processed"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500